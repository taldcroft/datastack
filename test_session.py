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

load_arrays([], x1, y1) 
load_arrays([], x2, y2)
load_arrays([], x3, y3)

set_source([], 'const1d.const# * polynom1d.poly')
freeze([], 'poly')
thaw([], 'poly.c0')
thaw([], 'poly.c1')
thaw([], 'poly.c2')
thaw([], 'const')

set_par([], 'poly.c1', 0.45)
set_par([], 'const.c0', 1.0)
set_par([], 'const.integrate', False)
freeze([1], 'const.c0')

mins = get_par([2,3], 'poly.c1.min')
vals = get_par([], 'poly.c1.val')
pars = get_par([], 'const.c0')

link([2,3], 'const.c0')
unlink([], 'const.c0')

# set_bkg_model([], 'polynom1d.bpoly')

fit([])
plot_fit_resid([])

