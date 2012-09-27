import numpy as np
from sherpa.astro.ui import *

load_pha('examples/data/acisf04938_000N002_r0043_pha3.fits')


rmf = get_rmf()
arf = get_arf()

load_arf(arf.name)
src_bkg_arf = get_arf()
src_bkg_arf.specresp = np.ones_like(src_bkg_arf.specresp)
load_rmf(rmf.name)
src_bkg_rmf = get_rmf()

load_bkg_arf(arf.name)
load_bkg_rmf(rmf.name)
bkg_arf = get_bkg_arf()
bkg_rmf = get_bkg_rmf()

src_model = rmf(arf(powlaw1d.pow1))
bkg_model = bkg_rmf(bkg_arf(const1d.bkg_constID))
src_bkg_model = src_bkg_rmf(src_bkg_arf(const1d.bkg_constID))
bkg_scale = get_data().sum_background_data(lambda x,y:1)

set_full_model(src_model + bkg_scale * src_bkg_model)
set_bkg_full_model(bkg_model)

print 'First fit on unbinned data'
fit()

print 'Fit on grouped data (notice all)'
ignore(None, 0.5)
ignore(7, None)
fit()

print 'Fit on grouped data (notice 0.5-7)'
group_counts(16)
ignore(None, 0.5)
ignore(7, None)
plot_fit()
fit()

