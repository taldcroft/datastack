"""
Manipulate a stack of data in Sherpa.

The methods in the DataStack class provide a way to automatically apply
familiar Sherpa commands such as `set_par`_ or `freeze`_ or `plot_fit`_
to a stack of datasets.  This simplifies simultaneous fitting of
multiple datasets.

:Copyright: Smithsonian Astrophysical Observatory (2010)
:Author: Tom Aldcroft (aldcroft@head.cfa.harvard.edu)
"""
import sys
import types
import re
import ConfigParser
import numpy
import sherpa
import sherpa.astro.ui as ui
import clogging

# Get plot package
_cp = ConfigParser.ConfigParser()
_cp.read(sherpa.get_config())
_plot_pkg =  _cp.get('options', 'plot_pkg')
if _plot_pkg == 'pylab':
    import matplotlib.pyplot as plt
elif _plot_pkg == 'chips':
    import pychips
else:
    raise ValueError('Unknown plot package {0}'.format(_plot_pkg))

logger = clogging.config_logger(__name__, level=clogging.DEBUG)

# Global list of dataset ids in use
_all_dataset_ids = {}

def _null_func(*args, **kwargs):
    pass

class DataStack(object):
    """
    Manipulate a stack of data in Sherpa.
    """
    def __init__(self):
        self.getitem_ids = None
        self.datasets = []
        self.dataset_ids = {}           # Access datasets by ID
        self.srcmodel_comps = []        # Generic model components in source model expression
        self.bkgmodel_comps = []        # Generic model components in background model expression

    def __getitem__(self, item):
        """Overload datastack getitem ds[item(s)] to set self.filter_ids to a tuple
        corresponding to the specified items.  
        """
        try:
            ids = (item + '',)
        except TypeError:
            try:
                ids = tuple(item)
            except TypeError:
                ids = (item, )
        self.getitem_ids = ids
        return self

##    __del__ behaves unpredictably, skip this.
##    def __del__(self):
##        print 'here', self.dataset_ids
##        for dataid in self.dataset_ids:
##            logger.debug('Deleting dataset {0}'.format(dataid))
##            # print _all_dataset_ids[dataid]

    @property
    def ids(self):
        """List of ids corresponding to stack datasets"""
        return [x['id'] for x in self.datasets]

    def _load_func_factory(load_func):
        def _load(self, *args, **kwargs):
            """
            Load a dataset and add to the datasets for stacked analysis.
            """
            if self.getitem_ids:
                dataid = self.getitem_ids[0]
                self.getitem_ids = None
            else:
                dataid = 1
                while dataid in _all_dataset_ids:
                    dataid += 1
                
            if dataid in self.dataset_ids:
                raise ValueError('Data ID = {0} is already in the DataStack'.format(dataset['id']))

            logger.debug('Loading dataset id %s' % dataid)
            out = load_func(dataid, *args, **kwargs)

            dataset = dict(id=dataid, args=args, model_comps={})
            dataset.update(kwargs)  # no sherpa load func 'args' keyword so no conflict
            _all_dataset_ids[dataid] = dataset
            self.dataset_ids[dataid] = dataset
            self.datasets.append(dataset)

            return out

        _load.__name__ = load_func.__name__
        _load.__doc__ = load_func.__doc__
        return _load

    load_arrays = _load_func_factory(ui.load_arrays)
    load_ascii = _load_func_factory(ui.load_ascii)
    load_data = _load_func_factory(ui.load_data)
    load_image = _load_func_factory(ui.load_image)
    load_pha = _load_func_factory(ui.load_pha)
    load_id = _load_func_factory(_null_func)

    def _set_model(self, model_expr, set_model_func, model_expr_attr):
        """
        Create a source or background model for each dataset.

        Defines::

            self.{srcmodel,bkgmodel}_comps: list of dicts with info for each
            component of the global srcmodel used as the source expression.

        :param model_expr: string expression defining src/bkg model
        :param set_model_func: either ui.set_source or ui.set_bkg_model
        :param model_expr_attr: either 'srcmodel' or 'bkgmodel'
        :rtype: None
        """
        setattr(self, model_expr_attr, model_expr)
        model_expr_comps = getattr(self, model_expr_attr + '_comps')

        # Find the components in model expression, for instance
        # xspowerlaw.pow is a model expression component
        RE_model = re.compile(r'\b (\w+) \. ([\w#]+)', re.VERBOSE)
        for match in RE_model.finditer(model_expr):
            model_expr_comps.append(dict(type=match.group(1),
                                         name=match.group(2),
                                         start=match.start(),
                                         end=match.end()))
        
        # Create all model expression components so they can be used later
        # to create composite source models for each dataset
        for dataset in self.datasets:
            model_expr = getattr(self, model_expr_attr)
            for model_expr_comp in reversed(model_expr_comps):
                model_comp = {}
                model_comp['type'] = model_expr_comp['type']
                model_comp['name'] = re.sub(r'#', '', model_expr_comp['name'])
                model_comp['uniq_name'] = re.sub(r'#', str(dataset['id']), model_expr_comp['name'])
                model_comp['type.uniq_name'] = '{0}.{1}'.format(model_comp['type'], model_comp['uniq_name'])
                dataset['model_comps'][model_comp['name']] = model_comp

                i0 = model_expr_comp['start']
                i1 = model_expr_comp['end']
                model_comp_name = re.sub(r'#', '', model_expr_comp['name'])
                model_expr = model_expr[:i0] + model_comp['type.uniq_name'] + model_expr[i1:]

            logger.debug('Setting %s for dataset %d = %s' % (model_expr_attr, dataset['id'], model_expr))
            set_model_func(dataset['id'], model_expr)
        
    def set_source(self, model_expr):
        self._set_model(model_expr, ui.set_source, 'srcmodel')
    set_model = set_source

    def set_bkg_model(self, model_expr):
        self._set_model(model_expr, ui.set_bkg_model, 'bkgmodel')

    def filter_datasets(self):
        if self.getitem_ids is None:
            return self.datasets

        filter_ids = self.getitem_ids
        self.getitem_ids = None

        try:
            return [self.dataset_ids[x] for x in filter_ids]
        except KeyError:
            raise ValueError('IDs = {0} not contained in dataset IDs = {1}'.format(ids, self.ids))

    def _sherpa_cmd_factory(sherpa_func):
        def _sherpa_cmd(self, *args, **kwargs):
            """
            Apply an arbitrary Sherpa function to each of the datasets.  
            :rtype: List of results
            """
            datasets = self.filter_datasets()
            logger.debug('Running {0} with args={1} and kwargs={2} for ids={3}'.format(
                sherpa_func.__name__, args, kwargs, [x['id'] for x in datasets]))
            return [sherpa_func(x['id'], *args, **kwargs) for x in datasets]

        _sherpa_cmd.__name__ = sherpa_func.__name__
        _sherpa_cmd.__doc__ = sherpa_func.__doc__
        return _sherpa_cmd

    def _sherpa_no_loop_factory(sherpa_func):
        def _sherpa_cmd(self, *args, **kwargs):
            """
            Run an arbitrary Sherpa function and produce debug output.
            :rtype: List of results
            """
            logger.debug('Running {0} with args={1} and kwargs={2}'.format(
                sherpa_func.__name__, args, kwargs))
            return sherpa_func(*args, **kwargs)

        _sherpa_cmd.__name__ = sherpa_func.__name__
        _sherpa_cmd.__doc__ = sherpa_func.__doc__
        return _sherpa_cmd

    subtract = _sherpa_cmd_factory(ui.subtract)
    notice = _sherpa_cmd_factory(ui.notice_id)
    ignore = _sherpa_cmd_factory(ui.ignore_id)
    get_bkg = _sherpa_cmd_factory(ui.get_bkg)
    get_source = _sherpa_cmd_factory(ui.get_source)
    get_bkg_model = _sherpa_cmd_factory(ui.get_bkg_model)
    get_conf_results = _sherpa_no_loop_factory(ui.get_conf_results)
    get_fit_results = _sherpa_no_loop_factory(ui.get_fit_results)
    conf = _sherpa_no_loop_factory(ui.conf)

    def _sherpa_par(self, func, par, msg, *args, **kwargs):
        """Apply ``func(*args)`` to all model component or model component parameters named ``mcpar``.

        See thaw(), freeze(), set_par() and get_par() for examples.

        :param func: Sherpa function that takes a full parameter name specification and
                     optional args, e.g. set_par() used as set_par('mekal_7.kt', 2.0)
        :param par: Param name or model compoent name ('mekal.kt' or 'mekal')
        :param msg: Format string to indicate action.
        :param *args: Optional function arguments

        :rtype: numpy array of function return values ordered by shell
        """
        vals = par.split('.')
        name = vals[0]
        parname = (vals[1] if len(vals) > 1 else None)
        if len(vals) > 2:
            raise ValueError('Invalid parameter name specification "%s"' % par)

        processed_already = set()
        retvals = []                       # return values
        for dataset in self.filter_datasets():
            model_comps = dataset['model_comps']
            if name in model_comps:
                uniqname = model_comps[name]['uniq_name']
                fullparname = '{0}.{1}'.format(uniqname, parname) if parname else uniqname
                if fullparname not in processed_already:
                    if msg is not None:
                        logger.debug(msg % fullparname)
                    retvals.append(func(fullparname, *args, **kwargs))
                    processed_already.add(fullparname)

        return retvals

    def thaw(self, par):
        """Apply thaw command to specified parameter for each dataset.

        :param par: parameter specifier in format <model_type>.<par_name>
        :param ids: list of dataset ids
        :rtype: None
        """
        self._sherpa_par(ui.thaw, par, 'Thawing %s')

    def freeze(self, par):
        """Apply freeze command to specified parameter for each dataset.

        :param par: parameter specifier in format <model_type>.<par_name>
        :param ids: list of dataset ids
        :rtype: None
        """
        self._sherpa_par(ui.freeze, par, 'Freezing %s')

    def _get_parname_attr_pars(self, par, msg):
        parts = par.split('.')
        if len(parts) == 1:
            raise ValueError('par="%s" must be in the form "name.par" or "name.par.attr"' % par)
        parname = '.'.join(parts[:-1])
        attr = parts[-1]
        return parname, attr, self._sherpa_par(eval, parname, msg % attr)

    def get_par(self, par):
        """Get parameter attribute value for each dataset.

        :param par: parameter specifier in format <model_type>.<par_name>
        :rtype: None
        """
        parname, attr, pars = self._get_parname_attr_pars(par, 'Getting %%s.%s')
        return numpy.array([getattr(x, attr) for x in pars])

    def set_par(self, par, val):
        """Set parameter attribute value for each dataset.

        :param par: parameter spec: <model_type>.<attr> or <model_type>.<par>.<attr>
        :param val: parameter value
        :rtype: None
        """
        parname, attr, pars = self._get_parname_attr_pars(par, 'Setting %%%%s.%%s = %s' % val)
        for x in pars:
            setattr(x, attr, val)

    def link(self, par):
        datasets = self.filter_datasets()
        name, parname = par.split('.')

        fullparname0 = '{0}.{1}'.format(datasets[0]['model_comps'][name]['uniq_name'], parname)
        for dataset in datasets[1:]:
            fullparname = '{0}.{1}'.format(dataset['model_comps'][name]['uniq_name'], parname)
            if fullparname != fullparname0:
                logger.debug('Linking {0} => {1}'.format(fullparname, fullparname0))
                ui.link(fullparname, fullparname0)

    def unlink(self, par):
        self._sherpa_par(ui.unlink, par, 'Unlinking %s')

    def _sherpa_fit_func(func):
        def _fit(self, *args, **kwargs):
            """Fit simultaneously all the datasets in the stack using the current
            source models. 

            :args: additional args that get passed to the sherpa fit() routine
            :kwargs: additional keyword args that get passed to the sherpa fit() routine
            :rtype: None
            """
            ids = tuple(x['id'] for x in self.filter_datasets())
            func(*(ids + args), **kwargs)

        _fit.__name__ = func.__name__
        _fit.__doc__ = func.__doc__

        return _fit

    fit_bkg = _sherpa_fit_func(ui.fit_bkg)
    fit = _sherpa_fit_func(ui.fit)

    def plot_print_window(self, *args, **kwargs):
        """Save figure for each dataset.

        :param args: list arguments to pass to print_window
        :param kwargs: named (keyword) arguments to pass to print_window
        :rtype: None
        """
        orig_args = args
        for dataset in self.filter_datasets():
            args = orig_args
            if len(args) > 0:
                filename = re.sub(r'#', str(dataset['id']), args[0])
                args = tuple([filename]) + args[1:]

            if _plot_pkg == 'pychips':
                pychips.set_current_window(window_id)
                func = pychips.plot_window
            elif _plot_pkg == 'pylab':
                plt.figure(self.ids.index(dataset['id']) + 1)
                func = plt.savefig
            else:
                raise ValueError('Unknown plot package')

            func(*args, **kwargs)

    plot_savefig = plot_print_window              # matplotlib alias for print_window

    def _sherpa_plot_func(func):
        def _sherpa_plot(self, *args, **kwargs):
            """Call Sherpa plot ``func`` for each dataset.

            :param func: Sherpa plot function
            :param args: plot function list arguments
            :param kwargs: plot function named (keyword) arguments
            :rtype: None
            """
            for dataset in self.filter_datasets():
                if _plot_pkg == 'pychips':
                    try:
                        pychips.add_window(['id', dataset['id']])
                    except RuntimeError:
                        pass  # already exists
                    pychips.set_current_window(window_id)
                elif _plot_pkg == 'pylab':
                    plt.figure(self.ids.index(dataset['id']) + 1)
                else:
                    raise ValueError('Unknown plot package')

                func(dataset['id'], *args, **kwargs)
        return _sherpa_plot

    # log_scale = _sherpa_plot_func(pychips.log_scale)
    # linear_scale = _sherpa_plot_func(pychips.linear_scale)

    plot_fit = _sherpa_plot_func(ui.plot_fit)
    plot_arf = _sherpa_plot_func(ui.plot_arf)
    plot_bkg_fit = _sherpa_plot_func(ui.plot_bkg_fit)
    plot_bkg_ratio = _sherpa_plot_func(ui.plot_bkg_ratio)
    plot_chisqr = _sherpa_plot_func(ui.plot_chisqr)
    plot_fit_delchi = _sherpa_plot_func(ui.plot_fit_delchi)
    plot_psf = _sherpa_plot_func(ui.plot_psf)
    plot_bkg = _sherpa_plot_func(ui.plot_bkg)
    plot_bkg_fit_delchi = _sherpa_plot_func(ui.plot_bkg_fit_delchi)
    plot_bkg_resid = _sherpa_plot_func(ui.plot_bkg_resid)
    plot_data = _sherpa_plot_func(ui.plot_data)
    plot_fit_resid = _sherpa_plot_func(ui.plot_fit_resid)
    plot_ratio = _sherpa_plot_func(ui.plot_ratio)
    plot_bkg_chisqr = _sherpa_plot_func(ui.plot_bkg_chisqr)
    plot_bkg_fit_resid = _sherpa_plot_func(ui.plot_bkg_fit_resid)
    plot_bkg_source = _sherpa_plot_func(ui.plot_bkg_source)
    plot_delchi = _sherpa_plot_func(ui.plot_delchi)
    plot_model = _sherpa_plot_func(ui.plot_model)
    plot_resid = _sherpa_plot_func(ui.plot_resid)
    plot_bkg_delchi = _sherpa_plot_func(ui.plot_bkg_delchi)
    plot_bkg_model = _sherpa_plot_func(ui.plot_bkg_model)
    plot_bkg_unconvolved = _sherpa_plot_func(ui.plot_bkg_unconvolved)
    plot_fit = _sherpa_plot_func(ui.plot_fit)
    plot_order = _sherpa_plot_func(ui.plot_order)
    plot_source = _sherpa_plot_func(ui.plot_source)

    def _matplotlib_func(func, axis_cmd=False):
        def _matplotlib(self, *args, **kwargs):
            """Call matplotlib plot ``func`` for each dataset.

            :param func: Sherpa plot function
            :param args: plot function list arguments
            :param kwargs: plot function named (keyword) arguments
            :rtype: None
            """
            orig_args = args
            for dataset in self.filter_datasets():
                args = orig_args
                if _plot_pkg != 'pylab':
                    raise ValueError('Plot package must be pylab')

                if len(args) > 0:
                    try:
                        arg0 = re.sub(r'#', str(dataset['id']), args[0])
                        args = tuple([arg0]) + args[1:]
                    except TypeError:
                        pass

                plt.figure(self.ids.index(dataset['id']) + 1)
                if axis_cmd:
                    ax = plt.gca()
                    getattr(ax, func)(*args, **kwargs)
                else:
                    func(*args, **kwargs)

        return _matplotlib

    plot_xlabel = _matplotlib_func(plt.xlabel)
    plot_ylabel = _matplotlib_func(plt.ylabel)
    plot_title = _matplotlib_func(plt.title)
    plot_xlim = _matplotlib_func(plt.xlim)
    plot_ylim = _matplotlib_func(plt.ylim)
    plot_set_xscale = _matplotlib_func('set_xscale', axis_cmd=True)
    plot_set_yscale = _matplotlib_func('set_yscale', axis_cmd=True)

# Use this and subsequent loop to wrap every function in sherpa.astro.ui with a datastack version
def datastack_wrap(func):
    def wrap(*args, **kwargs):
        if args:
            if isinstance(args[0], DataStack): 
                datastack, args = args[0], args[1:]
            elif isinstance(args[0], list):
                datastack, args = (DATASTACK[args[0]] if args[0] else DATASTACK), args[1:]
            try:
                newfunc = getattr(datastack, func.__name__)
            except AttributeError:
                newfunc = func
            return newfunc(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    wrap.__name__ = func.__name__
    wrap.__doc__ = func.__doc__
    return wrap

DATASTACK = DataStack()  # Default datastack
_module = sys.modules[__name__]
for attr in dir(ui):
    func = getattr(ui, attr)
    if type(func) == types.FunctionType:
        setattr(_module, attr, datastack_wrap(func))
        
