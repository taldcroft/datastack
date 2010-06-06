.. include:: references.rst

.. |datastack| replace:: *datastack*
.. |Datastack| replace:: *Datastack*

Contents:

.. toctree::
   :maxdepth: 2

Datastack
====================

|Datastack| is a `CIAO`_ `Sherpa`_ extension package for manipulating and
fitting a stack of related datasets.  It provides stack-enabled
(i.e. vectorized) versions of the key `Sherpa`_ commands used to load
data, set source models, get and set parameters, fit, and plot.  

For X-ray spectral analysis this means that a group of related datasets, for
instance 10 observations of the same source taken at different times, can be
analyzed as if they were a single merged dataset.  This has the important
advantage of using the appropriate individual response functions while hiding
the complexity (or tedium) of defining models and parameters for all the
datasets. 

Quick look
==========

The example below shows what is required to simultaneously fit three spectra of
a source taken from different epochs.  Bear in mind that these commands would
also work in the case of 20 or even 100 spectra, at which point the utility of
|datastack| becomes more obvious.  ::

  from datastack import *
  load_pha([], 'data/acis_1_pha3.fits') 
  load_pha([], 'data/acis_2_pha3.fits') 
  load_pha([], 'data/acis_3_pha3.fits') 
  subtract([])
  group_counts([], 10)
  notice([], 0.5, 7)
  set_source([], 'xsphabs.gal * powlaw1d.pow#')
  link([], 'pow.gamma')
  set_par([], 'gal.nh', 0.04)
  fit([])
  plot_fit_resid([])

That's all it takes.  To try this out go into the |datastack| installation source
directory (`Installation`_)::

  cd examples  
  sherpa

Then cut and paste the example commands and watch it go.  

Download
=========

The |datastack| package is available for download at
`<http://cxc.harvard.edu/contrib/datastack/downloads>`_.  That directory also
contains the example data files ``examples_data.tar.gz``.

Installation
=============

The |datastack| package includes a single module that must be made
available to the CIAO python so that *Sherpa* can import it.  The first step
is to untar the package tarball, change into the source directory, and initialize
the CIAO environment::

  tar zxvf datastack-<version>.tar.gz
  tar zxvf examples_data.tar.gz -C datastack-<version>/
  cd datastack-<version>
  source /PATH/TO/ciao/bin/ciao.csh

There are three methods for installing.  Choose ONE of the three.

**Best:**

The following command installs the ``datastack`` module to
``$HOME/.local/lib/python2.6``::

  python setup.py install --user

Using the ``--user`` switch you can make a local repository of packages that
will run within Sherpa and/or the system python 2.6.

**Also good:**

If you have write access to the CIAO installation you can just use the CIAO
python to install the modules into the CIAO python library.  Assuming you are
in the CIAO environment do::

  python setup.py install

This puts the new modules straight in to the CIAO python library so that any
time you (or others in the case of a system-wide installation) enter the CIAO
environment then ``datastack`` will be available.  You do NOT need to set
``PYTHONPATH``.  The only downside is that the module will likely need to be
re-installed after a new CIAO release.

**Quick and dirty:**

An alternate and simple installation strategy is to just leave the module file in
the source directory and set the ``PYTHONPATH`` environment variable to point
to the source directory::

  setenv PYTHONPATH $PWD

This method is fine in the short term but you always have to make sure
``PYTHONPATH`` is set appropriately (perhaps in your ~/.cshrc file).  And if you
start doing much with Python you will have ``PYTHONPATH`` conflicts and things
will get messy.

Test
=======

To test the installation change to the source distribution directory and do the
following::

  cd examples  
  sherpa
  execfile("fit_spectra.py")

This should run through in a reasonable time and produce output indicating the
simultaneous fit of four spectra.  

Example: fit spectra
====================

The script ``examples/fit_spectra.py`` shows an example of simultanously
fitting four X-ray spectra with a power law and Galactic absorption::

  from datastack import *

  clear_stack([])

  load_pha([], 'data/acis_1_pha3.fits') 
  load_pha([], 'data/acis_2_pha3.fits') 
  load_pha([], 'data/acis_3_pha3.fits') 
  load_pha([], 'data/acis_4_pha3.fits') 

  group_counts([], 15)
  ignore([], None, 0.5)
  ignore([], 7, None)
  subtract([])

  set_source([], 'xsphabs.gal * powlaw1d.pow#')
  link([], 'pow.gamma')
  set_par([], 'gal.nh', 0.04)
  freeze([], "gal.nh")

  fit([])
  print 'pow.ampl:', get_par([], 'pow.ampl')
  plot_fit_resid([])

Let's break this down.
::

  from datastack import *

This line overrides a subset of the native Sherpa commands with the
stack-enabled versions.  The section `Overloading the Sherpa commands`_
describes this a little more carefully and
shows why this isn't so scary.  The section `Object-oriented datastacks`_ 
shows how to avoid the ``import *`` which will bother Pythonistas.

Next the script clears any existing datasets in the data stack.  This is a good
idea if you are running a script over and over to debug.  Without clearing the
stack the subsequent load data commands will put another copy of all the
datasets onto the stack.
::

  clear_stack([])

Next we load a few datasets into the stack.  This introduces the appearance of
``[]`` (a Python empty list) as the first argument of stack-enabled commands.  It
informs the command to operate on the stack of data instead of a single dataset
like normal.  This will load datasets and automatically assign ``id`` values of
1, 2, 3, and 4 respectively::

  load_pha([], "data/acis_1_pha3.fits") 
  load_pha([], "data/acis_2_pha3.fits") 
  load_pha([], "data/acis_3_pha3.fits") 
  load_pha([], "data/acis_4_pha3.fits") 

Now we tell Sherpa to group by counts, ignore data outside 0.5 to 7 keV, and
subtract the background for each dataset in the stack.  Underneath this just
runs the corresponding native Sherpa command on each dataset.::

  group_counts([], 15)
  ignore([], None, 0.5)
  ignore([], 7, None)
  subtract([])

In this case we are using ``[]`` to apply the command to all datasets.  But it is
possible to specify subsets of the stack by providing a list of the dataset
IDs, for instance ``subtract([1,2])`` or ``ignore([3], None, 0.5)``.

Next is setting the source model for fitting.  This is where the |datastack|
module is doing more than simply iterating over the native Sherpa
commands::

  set_source([], "xsphabs.gal * powlaw1d.pow#")

In this example there is a common galactic absorption that applies for all
datasets but we want an independent power law component for each.  We use the
usual Sherpa model syntax but insert the ``#`` character in the model component
name to tell ``set_source()`` to create an independent powerlaw component for each
dataset. The above command is essentially equivalent to the following::

  set_source(1, "xsphabs.gal * powlaw1d.pow1")
  set_source(2, "xsphabs.gal * powlaw1d.pow2")
  set_source(3, "xsphabs.gal * powlaw1d.pow3")
  set_source(4, "xsphabs.gal * powlaw1d.pow4")

To support this extended syntax the model definition *must* be a
Python string, unlike the native Sherpa command that allows for a Python
expression e.g. ``set_source(1, xsphabs.gal * powlaw1d.pow1)``.

Now let's say that we want to fit just a single powerlaw photon index gamma
for the data stack but leave the normalizations independent.  This is done by
linking the gamma parameters::

  link([], "pow.gamma")

Notice that the ``#`` is only needed when setting the source model.  In all the
other commands that refer to model components there is no need for the ``#``.

Now we need to set the initial powerlaw index and then set the Galactic
absorption and freeze it::

  set_par([], "gal.nh", 0.04)
  freeze([], "gal.nh")

Finally we fit, print some fit values, and plot the fit with residuals::

  fit([])
  print "pow.ampl:", get_par([], "pow.ampl.val")
  plot_fit_resid([])

This brings up four plot windows with the fit residuals for each dataset in a
separate window.

By default |datastack| is chatty about what it's doing but you can disable this with::

  set_stack_verbose(False)

Datastack details
======================

The data stack
--------------

When the |datastack| module is imported it automatically creates a default (or
"session") data stack that is used whenever a stack-enabled command is called
with a ``stack specifier`` as the first argument.  The data stack itself is
just a list of dataset ids plus a little extra information mostly pertaining to
the source model expression.

Some non-Sherpa commands are available for data stack manipulation:

=================  ===================================
Command            Description
=================  ===================================
clear_stack        Clear the stack 
show_stack         Show synopsis for stack elements 
get_stack_ids      Get a list of the ids in the stack
set_stack_verbose  Set verbose mode (False => quiet)
=================  ===================================

Non-default or multiple data stacks are supported using ``object-oriented datastacks``.

Stack specifier
---------------

The |datastack| module overrides certain Sherpa commands so that they can
accept a stack specifier as the first argument.  A stack specifier is a Python
list that gives the dataset ids within the stack on which to operate.  An empty
list ``[]`` implies operating on *all* elements of the stack.  Examples of
valid stack specifiers are::

  []        # All elements
  [1,3,4]   # Dataset ids 1, 3, and 4 within stack
  ["pha1", "pha2", 3]  # Dataset ids can be strings

If an ``id`` is given that it is not a member of the stack then an error will
be reported.

The stack specifier is what distinguishes between a stack command and a native
Sherpa command.  If the first argument to a function is a list then the
stack-enabled version is called, otherwise the native Sherpa command is called.
Within a Sherpa session these can be mixed freely::

  subtract([2,3,4])  # Subtract bkg for ids=2,3,4 in stack
  subtract(5)        # Subtract bkg for id=5 (native Sherpa)

This distinction is generally sufficient.  Nevertheless some users may prefer
to use ``object-oriented datastacks`` to keep everything tidy from the Python
programmer perspective.

Data loading
------------

A subset of Sherpa data loading commands are supported.  These commands will
execute the native Sherpa command and add the dataset to the stack.  The stack
specifier defines the ``id`` of the new dataset.  If an empty list ``[]`` is
given then the first available integer ``id`` will be used (starting from 1 and
incrementing until an unused dataset ``id`` is found).  Available commands are:

=============  ==========================================
Command        Description
=============  ==========================================
load_arrays    Load NumPy arrays into a dataset
load_ascii     Load ASCII data by id
load_data      Load spectrum, table, or ASCII data by id
load_image     Load image data by id
load_pha       Load PHA data by id
=============  ==========================================

Model definition
----------------

The |datastack| module supports three model definition commands:

=============  ==========================================
Command        Description
=============  ==========================================
set_model      Set a Sherpa model by model id
set_source     Set a Sherpa model by model id (alias)
set_bkg_model  Set a bkg model by data id and bkg id
=============  ==========================================

For each of these commands |datastack| extends the Sherpa model definition
language to substitute the dataeset ``id`` for any instance the ``#`` symbol
within the model component name.  To support this extended syntax the model
definition *must* be a quoted Python string, unlike the native Sherpa command that
allows for a Python expression e.g. ``set_source(1, xsphabs.gal *
powlaw1d.pow1)``.

Consider this example::

  set_source([], "xsphabs.gal * powlaw1d.pow_#")

Here there is a common model (``gal``) that applies for all datasets
and an independent model ``pow#`` for each dataset.  The above command
is essentially equivalent to the following::

  set_source(1, "xsphabs.gal * powlaw1d.pow_1")
  set_source(2, "xsphabs.gal * powlaw1d.pow_2")
  set_source(3, "xsphabs.gal * powlaw1d.pow_3")

Parameter manipulation
-----------------------

|Datastack| supports the following commands for manipulating model parameters:

=============  ==========================================
Command        Description
=============  ==========================================
get_par        Return a list of model parameters
set_par        Set initial values for a model parameter
thaw           Thaw a list of parameters
freeze         Freeze a list of parameters
link           Link a parameter with an associated value
unlink         Unlink a parameter
=============  ==========================================

The `get_par`_ and `set_par`_ commands are extended in |datastack| to accept
*any* attribute of a model component and not just a parameter name.  For
instance::

  set_source([], "gauss1d.gauss#")       # create model components "gauss#"
  set_par([], "gauss.integrate", False)  # disable model integration for stack
  set_par([], "gauss.fwhm.min", 2.0)     # set min for gauss.fwhm parameter
  set_par([], "gauss.pos", 5.0)          # set gauss.pos parameter value
  pars = get_par([], "gauss.pos")        # get a list of parameter objects
  parvals = get_par([], "gauss.pos.val") # get the position values

The `get_par`_ command returns a list of the corresponding attribute values.
The `set_par`_ command only accepts a single value and applies this to all
elements in the stack.  To set a parameter value to a corresponding list use
code like the following::

  parname = "gauss.pos"
  parvals = [1.2, 3.0, 5.6]
  for i in get_stack_ids():
      set_par([i], parname, parvals[i])

The `link`_ command has a different behavior in the |datastack|
context.  It only accepts a single parameter name and links the first stack
dataset with all subsequent ones.  Assume that the current data stack has 3
datasets with ``ids`` 1, 2, and 3.  Then both of the commands::

  link([1,2,3], "gauss.fwhm")
  link([], "gauss.fwhm")

are equivalent to::

  link("gauss2.fwhm", "gauss1.fwhm")
  link("gauss3.fwhm", "gauss1.fwhm")

The ability within the native Sherpa `link`_ command to link a parameter to an
arbitrary model expression is not currently supported within the |datastack|
module.

Plotting commands
------------------

Plotting of data stacks is supported by opening a new plot window for each
dataset in the stack and then running the native Sherpa command accordingly.
The plot window will be identified by the dataset ``id``.  

The following plotting commands are supported.  There is no |datastack| support
for most `ChIPS`_ commands.

===================      ==========================================================================
Command                  Description
===================      ==========================================================================
plot_arf                 Plot ancillary response data
plot_bkg                 Plot background counts
plot_bkg_chisqr          Plot background chi squared contributions
plot_bkg_delchi          Plot background delta chi
plot_bkg_fit             Plot background counts with fitted background model
plot_bkg_fit_delchi      Send background fit and background delta chi plots to the visualizer
plot_bkg_fit_resid       Send background fit and background residuals plots to the visualizer
plot_bkg_model           Plot background convolved model
plot_bkg_ratio           Plot background ratio
plot_bkg_resid           Plot background residuals
plot_bkg_source          Plot the unconvolved background model
plot_chisqr              Send a chi^2 plot to the visualizer
plot_data                Send a data plot to the visualizer
plot_delchi              Send a delta chi plot to the visualizer
plot_energy_flux         Send a energy flux distribution to the visualizer
plot_fit                 Send a fit plot to the visualizer
plot_fit_delchi          Send fit and delta chi plots to the visualizer
plot_fit_resid           Send fit and residuals plots to the visualizer
plot_model               Send a model plot to the visualizer
plot_order               Plot convolved source model by multiple response order
plot_psf                 Send a PSF plot to the visualizer
plot_ratio               Send a ratio plot to the visualizer
plot_resid               Send a residuals plot to the visualizer
plot_source              Plot unconvolved source model
===================      ==========================================================================

Other commands
--------------

The following commands are also available within |datastack|.  These simply
apply the native command to each of the stack datasets, passing along any
arguments and returning a list corresponding the return value for each dataset.

===================      ==========================================================================
Command                  Description
===================      ==========================================================================
get_bkg                  Return an background PHA dataset by data id and bkg_id
get_bkg_model            Return the background convolved model by data id and bkg id
get_source               Return a Sherpa model by model id
group_adapt              Create and set grouping flags adaptively so that each group contains
group_adapt_snr          Create and set grouping flags adaptively so that each group contains
group_bins               Create and set grouping flags by number of bins with equal-widths
group_counts             Create and set grouping flags using minimum number of counts per bin
group_snr                Create and set grouping flags so each group has a signal-to-noise
group_width              Create and set grouping flags by a bin width.
ignore                   Exclusive 1D ignore on interval(s) for all available
notice                   Exclusive 1D notice on interval(s) for all available
subtract                 Subtract background counts
===================      ==========================================================================

This list is a small subset of Sherpa commands where stacking could be
utilized.  Most commands which can take a dataset ``id`` as the first argument
are likely to function properly within the |datastack| context.  The
``create_stack_func`` is expected in a near-term release to create a
stacking-enabled version of any appropriate Sherpa command.

Object-oriented datastacks
---------------------------

The |Datastack| functionality is largely implemented with a single
``DataStack`` class.  Users may work with a ``DataStack`` object instead of the
session-based syntax shown in most of the examples. 

Partial object-oriented
^^^^^^^^^^^^^^^^^^^^^^^

The first level up from the pure session-based syntax (where a stack specifier
is a Python list) is to explicitly create the datastack as an object and
consistently use that object as the stack specifier::

  from datastack import *
  ds = DataStack()
  load_pha(ds, 'data/acis_1_pha3.fits') 
  load_pha(ds, 'data/acis_2_pha3.fits') 
  group_counts(ds, 20)
  ignore(ds[3,4], 6.0, None) # Ignore for datasets 3, 4

This is illustrated in more detail in ``examples/partial_object.py``.

Fully object-oriented
^^^^^^^^^^^^^^^^^^^^^^^

The next level is to use a fully object-oriented approach::

  import datastack
  ds = datastack.DataStack()
  ds.load_pha('data/acis_1_pha3.fits') 
  ds.load_pha('data/acis_2_pha3.fits') 
  ds.group_counts(20)
  ds[3,4].ignore(6.0, None) # Ignore for datasets 3, 4

This gets rid of the undesirable ``from datastack import *`` line that is
needed in the session-based view.  This object-oriented approach is what is
really happening under the hood.  The default session-based version uses these
methods with a special internal ``DATASTACK`` object that gets created when the
module is imported.  See ``examples/object_oriented.py`` for a working example.

Overloading the Sherpa commands
--------------------------------

Most people won't care, but here is the code that is used to wrap every Sherpa
user function (i.e. every function in ``sherpa.astro.ui``) for the
session-based interface.

In a nutshell, the code first checks if there are any ``args``.  If not, then
it runs the native Sherpa function.  Otherwise check to see if
the first one is a stack specifier (a list or a DataStack).  If not, then again
just run the native Sherpa function.  At this point the user is trying to call
a stack function, so try calling the like-named method for the appropriate
DataStack object.  If this fails then raise an exception.
::

  def _sherpa_ui_wrap(func):
      def wrap(*args, **kwargs):
          wrapfunc = func
          if args:
              if isinstance(args[0], DataStack): 
                  datastack, args = args[0], args[1:]
              elif isinstance(args[0], list):
                  datastack, args = (DATASTACK[args[0]] if args[0] else DATASTACK), args[1:]
              else:
                  return func(*args, **kwargs) # No stack specifier so use native sherpa func

              try:
                  wrapfunc = getattr(datastack, func.__name__)
              except AttributeError:
                  raise AttributeError(
                      '{0} is not a stack-enabled function.'.format(func.__name__))

          return wrapfunc(*args, **kwargs)

      wrap.__name__ = func.__name__
      wrap.__doc__ = func.__doc__
      return wrap

