from datastack import *
from acis_bkg_model import acis_bkg_model

clear_stack()
load_pha([], 'acisf04938_000N002_r0043_pha3.fits')
load_pha([], 'acisf07867_000N001_r0002_pha3.fits')

bkg_model = scale1d.bkg_constID * acis_bkg_model('acis2i')
src_model = const1d.src_constID * xsphabs.abs1 * powlaw1d.pow1

ids = get_stack_ids()
src_bkg_rmfs = [unpack_rmf(x.name) for x in get_bkg_rmf([])]
bkg_bkg_rmfs = [unpack_rmf(x.name) for x in get_bkg_rmf([])]
rsps = get_response([])
bkg_scales = get_bkg_scale([])

for id_, src_bkg_rmf, bkg_bkg_rmf, rsp, bkg_scale in zip(
    ids, src_bkg_rmfs, bkg_bkg_rmfs, rsps, bkg_scales):
    # set_bkg_rmf([id_], bkg_rmf)
    set_full_model([id_], rsp(src_model) + bkg_scale * src_bkg_rmf(bkg_model))
    set_bkg_full_model([id_], bkg_bkg_rmf(bkg_model))

set_par([1], 'src_const.c0', 1.0)
freeze([1], 'src_const')

ignore([], None, 0.5)
ignore([], 7, None)
fit([])
group_counts([], 16)
ignore([], None, 0.5)
ignore([], 7, None)
plot_fit([])

