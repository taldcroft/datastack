import datastack
from acis_bkg_model import acis_bkg_model
import sherpa.astro.ui as ui

ds = datastack.DataStack()

ds[1].load_pha('acisf04938_000N002_r0043_pha3.fits')
ds[2].load_pha('acisf07867_000N001_r0002_pha3.fits')

bkg_model = scale1d.bkg_constID * acis_bkg_model('acis2i')
src_model = const1d.src_constID * xsphabs.absID * powlaw1d.powID

ids = ds.ids
bkg_rmfs = ds.get_bkg_rmf()
rsps = ds.get_response()
bkg_scales = ds.get_bkg_scale()

for id_, bkg_rmf, rsp, bkg_scale in zip(ids, bkg_rmfs, rsps, bkg_scales):
    ds[id_].set_full_model(rsp(src_model) + bkg_scale * bkg_rmf(bkg_model))
    ds[id_].set_bkg_full_model(bkg_rmf(bkg_model))

ds[1].set_par('src_const.c0', 1.0)
ds[1].freeze('src_const')

ds.ignore(None, 0.5)
ds.ignore(7, None)
ds.fit()
ds.plot_fit()
ds.group_counts(16)
ds.ignore(None, 0.5)
ds.ignore(7, None)
ds.plot_fit()

