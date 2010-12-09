import sys
import sherpa.astro.ui as ui
import numpy as np
import datastack

x1 = np.arange(50)+2
y1 = x1**2 
x2 = np.arange(10)
y2 = x2**1.9 * 2
x3 = np.arange(60)
y3 = x3**2.1 * 4

ds = datastack.DataStack()
ds[1].load_arrays(x1, y1)  # ID required (autonumbering possible but potential problems)
ds[2].load_arrays(x2, y2)
ds[3].load_arrays(x3, y3)

ds.set_source(ui.const1d.constID * ui.polynom1d.poly)
#ds.set_source('const1d.constID * polynom1d.poly')

ds.freeze('poly')
ds.thaw('poly.c0')
ds.thaw('poly.c1')
ds.thaw('poly.c2')
ds.thaw('const')
ds[1].freeze('const')

ds[2].set_par('poly.c1', 0.45)
ds.set_par('const.c0', 1.0)
ds.set_par('const.integrate', False)

mins = ds.get_par('poly.c1.min')
vals = ds.get_par('poly.c1.val')
pars = ds.get_par('const.c0')

ds[2,3].link('poly.c0')
ds.unlink('poly.c0')


ds.fit()
ds.plot_fit_resid()

