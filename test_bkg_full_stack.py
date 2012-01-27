from datastack import *
from acis_bkg_model import acis_bkg_model

clear_stack()
load_pha([], 'acisf04938_000N002_r0043_pha3.fits')
load_pha([], 'acisf07867_000N001_r0002_pha3.fits')

load_bkg_rmf([], "acisf04938_000N002_r0043_rmf3.fits")
load_bkg_rmf([], "acisf07867_000N001_r0002_rmf3.fits")

load_bkg_arf([], "acisf04938_000N002_r0043_arf3.fits")
load_bkg_arf([], "acisf07867_000N001_r0002_arf3.fits")

bkg_arfs = get_bkg_arf([])

if 0:
    bkg_model = scale1d.bkg_constID * acis_bkg_model('acis2i')
    src_model = const1d.src_constID * xsphabs.abs1 * powlaw1d.pow1

    ids = get_stack_ids()
    src_bkg_rmfs = [unpack_rmf(x.name) for x in get_bkg_rmf([])]
    bkg_bkg_rmfs = [unpack_rmf(x.name) for x in get_bkg_rmf([])]
    rsps = get_response([])
    bkg_scales = get_bkg_scale([])


# background for the 1 data set

bkg_arf_1 = bkg_arfs[0]
bkg_arf_1.specresp = bkg_arf_1.specresp * 0 + 1.
bkg_rmf_1= get_bkg_rmf(1)
bkg_scale_1 = get_bkg_scale(1)
rsp_1 = get_response(1)
bkg_rsp_1 = get_response(bkg_id=1)
bkg_model_1 = const1d.c1 * acis_bkg_model('acis7s')
set_bkg_full_model(1,bkg_rsp_1(bkg_model_1))

# background for the 2 data set
bkg_arf_2 = bkg_arfs[1]
bkg_arf_2.specresp = bkg_arf_2.specresp * 0 + 1.
bkg_rmf_2= get_bkg_rmf(2)
bkg_scale_2 = get_bkg_scale(2)
rsp_2 = get_response(2)
bkg_rsp_2=get_response(2,bkg_id=1)
bkg_model_2= const1d.c2 * acis_bkg_model('acis7s')
set_bkg_full_model(2,bkg_rsp_2(bkg_model_2))

# Fitting Background:
set_method("neldermead")
set_stat("cash")
notice(0.5,8.)

thaw(c1.c0)
thaw(c2.c0)
fit_bkg()
freeze(c1.c0)
freeze(c2.c0)

src_model = xsphabs.abs1 * powlaw1d.pow1
set_full_model(1,rsp_1(src_model) + bkg_scale_1 * bkg_rsp_1(bkg_model_1))
set_full_model(2,rsp_2(src_model) + bkg_scale_2 * bkg_rsp_2(bkg_model_2))

set_par(abs1.nh,0.0398)
freeze(abs1)
fit()
# plot_fit([])
