import datastack
from acis_bkg_model import acis_bkg_model
import sherpa.astro.ui as ui

ds = datastack.DataStack()

ds[1].load_pha('acisf04938_000N002_r0043_pha3.fits')
ds[2].load_pha('acisf07867_000N001_r0002_pha3.fits')

detnam = 'acis2i'
for dataset in ds.datasets:
    id_ = dataset['id']
    rmf = ui.get_rmf(id_)
    arf = ui.get_arf(id_)
    ui.load_bkg_arf(id_, arf.name)
    bkg_arf = ui.get_bkg_arf(id_)
    bkg_rmf = ui.get_bkg_rmf(id_)
    bkg_arf.specresp = bkg_arf.specresp * 0 + 100.0

    bkg_scale = ui.get_data(id_).sum_background_data(lambda x,y:1)
    bkg_model = bkg_rmf(bkg_arf(ui.const1d.bkg_constID * acis_bkg_model(detnam)))
    src_model = rmf(arf(ui.const1d.src_constID * ui.powlaw1d.powlaw))
    ds[id_].set_full_model(src_model + bkg_scale * bkg_model)
    ds[id_].set_bkg_full_model(bkg_model)

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

