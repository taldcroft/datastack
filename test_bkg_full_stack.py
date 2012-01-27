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
bkg_rmfs = get_bkg_rmf([])

rsps = get_response([])
bkg_scales = get_bkg_scale([])
bkg_models = [const1d.c1 * acis_bkg_model('acis7s'),
              const1d.c2 * acis_bkg_model('acis7s')]
bkg_rsps = get_response([], bkg_id=1)

if 0:
    bkg_model = scale1d.bkg_constID * acis_bkg_model('acis2i')
    src_model = const1d.src_constID * xsphabs.abs1 * powlaw1d.pow1

    ids = get_stack_ids()
    rsps = get_response([])
    bkg_scales = get_bkg_scale([])

for i in range(2):
    id_ = i + 1
    bkg_arfs[i].specresp = bkg_arfs[i].specresp * 0 + 1.
    set_bkg_full_model(id_, bkg_rsps[i](bkg_models[i]))

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

# Final fit statistic   = -11105.6 at function evaluation 64
# Data points           = 1028
# Degrees of freedom    = 1026
# Change in statistic   = 0
#    c1.c0          1659.79     
#    c2.c0          21.7327     
# Datasets              = 1, 2
# Method                = neldermead
# Statistic             = cash
# Initial fit statistic = -12502.7
# Final fit statistic   = -12502.7 at function evaluation 299
# Data points           = 2056
# Degrees of freedom    = 2054
# Change in statistic   = 0
#    pow1.gamma     1.86691     
#    pow1.ampl      4.38031e-05 
