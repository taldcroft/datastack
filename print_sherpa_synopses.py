import types
import sherpa.astro.ui as ui

for attr in sorted(dir(ui)):
    func = getattr(ui, attr)
    if type(func) == types.FunctionType:
        try:
            lines = func.__doc__.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('SYNOPSIS'):
                    synopsis = lines[i+1].strip()
        except AttributeError:
            synopsis = ''
        print '{0:25s} {1}'.format(func.__name__, synopsis)
