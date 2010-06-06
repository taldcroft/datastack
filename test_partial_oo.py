import sys
import sherpa.astro.ui as ui
import numpy as np
from datastack import *

x1 = np.arange(50)+2
y1 = x1**2 
x2 = np.arange(10)
y2 = x2**1.9 * 2
x3 = np.arange(60)
y3 = x3**2.1 * 4

ds = DataStack()
load_arrays(ds[1], x1, y1)  # ID required (autonumbering possible but potential problems)
load_arrays(ds[2], x2, y2)
load_arrays(ds[3], x3, y3)

set_source(ds, 'const1d.const# * polynom1d.poly')
freeze(ds, 'poly')
thaw(ds, 'poly.c0')
thaw(ds, 'poly.c1')
thaw(ds, 'poly.c2')
thaw(ds, 'const')

set_par(ds, 'poly.c1', 0.45)
set_par(ds, 'const.c0', 1.0)
set_par(ds, 'const.integrate', False)
freeze(ds[1], 'const.c0')

mins = get_par(ds[2,3], 'poly.c1.min')
vals = get_par(ds, 'poly.c1.val')
pars = get_par(ds, 'const.c0')

# link(ds, 'poly.c0', [2,3])
# unlink(ds, 'poly.c0')

# set_bkg_model(ds, 'polynom1d.bpoly')

fit(ds)
# conf(ds)
# plot_fit_resid(ds)

