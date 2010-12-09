import sys
import re
import sherpa.astro.ui
import sherpa.astro.instrument
import sherpa.models.model

def load49():
    sherpa.astro.ui.load_pha('acisf04938_000N002_r0043_pha3.fits')

def sstack_mod(model, level=0):
    print '  '*level, repr(model)
    if hasattr(model, 'parts'):
        newparts = []
        for part in model.parts:
            newparts.append(stack_mod(part, level+1))
    else:
        print '  '*(level+1), model.type, model.name, model.type
        return model.name + 'XX'
        
attrs = ('arf', 'calc', 'model', 'name', 'parts', 'lhs', 'rhs', 'op', 'type', '__call__')

def print_model(model, level=0):
    indent = '   '*level
    print indent, repr(model)
    for attr in attrs:
        if hasattr(model, attr):
            print indent, "  {0}: {1}".format(attr, repr(getattr(model, attr)))
    print 

    if hasattr(model, 'parts'):
        for part in model.parts:
            print_model(part, level+1)


def stack_model_print(model, level=0, id_=1):
    indent = "    " * level
    indent2 = indent + "  "
    print indent, repr(model)
    for attr in attrs:
        if hasattr(model, attr):
            print indent2 + "{0}: {1}".format(attr, repr(getattr(model, attr)))
    print id_

    if hasattr(model, 'parts'):
        newparts = []
        for part in model.parts:
            newparts.append(stack_model_print(part, level+1, id_))
        if hasattr(model, 'op'):
            print indent2 + "Returning op(newparts) = {0}({1})".format(repr(model.op), repr(newparts))
            return model.op(*newparts)
        elif isinstance(model, sherpa.astro.instrument.RMFModel):
            print indent2 + "Returning model.rmf(newparts) = {0}({1})".format(repr(model.rmf), repr(newparts))
            return sherpa.astro.instrument.RMFModel(rmf=model.rmf, model=newparts[0], arf=model.arf, pha=model.pha)
        elif isinstance(model, sherpa.astro.instrument.ARFModel):
            print indent2 + "Returning model.arf(newparts) = {0}({1})".format(repr(model.rmf), repr(newparts))
            return sherpa.astro.instrument.ARFModel(rmf=model.rmf, model=newparts[0], arf=model.arf, pha=model.pha)
    else:
        print model.name
        return eval(re.sub(r'_ID', str(id_), model.name))

def stack_model(model, id_=1, model_comps=None):
    if model_comps is None:
        model_comps = []
        
    if hasattr(model, 'parts'):
        # Recursively descend through model and create new parts (as needed)
        # corresponding to the stacked model components.
        newparts = []
        for part in model.parts:
            newparts.append(stack_model(part, id_, model_comps))

        if hasattr(model, 'op'):
            return model.op(*newparts)
        elif isinstance(model, sherpa.astro.instrument.RMFModel):
            return sherpa.astro.instrument.RMFModel(rmf=model.rmf, model=newparts[0], arf=model.arf, pha=model.pha)
        elif isinstance(model, sherpa.astro.instrument.ARFModel):
            return sherpa.astro.instrument.ARFModel(rmf=model.rmf, model=newparts[0], arf=model.arf, pha=model.pha)
        else:
            raise ValueError("Unexpected composite model {0} (not operator, ARF or RMF)".format(repr(model)))
    else:
        if isinstance(model, sherpa.models.model.ArithmeticConstantModel):
            return model.val
        
        if '_ID' not in model.name:
            model_comps.append((model, 'plain'))
            return model
        
        try:
            model_type, model_name = model.name.split('.')
        except ValueError:
            raise ValueError('Model name "{0}" must be in format <model_type>.<name>'.format(model.name))
        model_name = re.sub('_ID', str(id_), model_name)
        try:
            newmodel = getattr(getattr(sherpa.astro.ui, model_type), model_name)
        except AttributeError:
            # Must be a user model, so use add_model to put a modelwrapper function into namespace
            sherpa.astro.ui.add_model(type(model))
            newmodel = eval('{0}.{1}'.format(model_type, model_name))

        model_comps.append((newmodel, 'stacked'))
        return newmodel
    
def create_stack_model(model, id_, id_str='ID'):
    model_comps = []
    def _get_new_model(model, level=0):
        if hasattr(model, 'parts'):
            # Recursively descend through model and create new parts (as needed)
            # corresponding to the stacked model components.
            newparts = []
            for part in model.parts:
                newparts.append(_get_new_model(part, level+1))

            if hasattr(model, 'op'):
                return model.op(*newparts)
            elif isinstance(model, sherpa.astro.instrument.RMFModel):
                return sherpa.astro.instrument.RMFModel(rmf=model.rmf, model=newparts[0],
                                                        arf=model.arf, pha=model.pha)
            elif isinstance(model, sherpa.astro.instrument.ARFModel):
                return sherpa.astro.instrument.ARFModel(rmf=model.rmf, model=newparts[0],
                                                        arf=model.arf, pha=model.pha)
            else:
                raise ValueError("Unexpected composite model {0} (not operator, ARF or RMF)".format(repr(model)))
        else:
            if isinstance(model, sherpa.models.model.ArithmeticConstantModel):
                return model.val

            if id_str not in model.name:
                model_comps.append((model, 'plain'))
                return model

            try:
                model_type, model_name = model.name.split('.')
            except ValueError:
                raise ValueError('Model name "{0}" must be in format <model_type>.<name>'.format(model.name))
            model_name = re.sub(id_str, str(id_), model_name)
            try:
                newmodel = getattr(getattr(sherpa.astro.ui, model_type), model_name)
            except AttributeError:
                # Must be a user model, so use add_model to put a modelwrapper function into namespace
                sherpa.astro.ui.add_model(type(model))
                newmodel = eval('{0}.{1}'.format(model_type, model_name))

            model_comps.append((newmodel, 'stacked'))
            return newmodel

    return _get_new_model(model), model_comps
