import numpy as np
from sherpa.astro.ui import *
from acis_bkg_model import acis_bkg_model

load_pha('examples/data/acisf04938_000N002_r0043_pha3.fits')

rmf = get_rmf(id=1)
arf = get_arf(id=1)

load_bkg_rmf(rmf.name)
load_bkg_arf(arf.name)

bkg_rmf = get_bkg_rmf()
bkg_arf = get_bkg_arf()
bkg_arf.specresp = np.ones_like(bkg_arf.specresp)
bkg_model = bkg_rmf(bkg_arf(const1d.bkg_constID * acis_bkg_model('acis7s')))

src_model = rmf(arf(powlaw1d.pow1))
bkg_scale = get_bkg_scale()

set_full_model(src_model + bkg_scale * bkg_model)
set_bkg_full_model(bkg_model)

print 'Fit on unbinned data (notice 0.5-7)'
ignore(None, 0.5)
ignore(7, None)
fit()
plot_fit()

print 'Fit on grouped data (notice 0.5-7)'
group_counts(16)
ignore(None, 0.5)
ignore(7, None)
fit()
plot_fit()
