from datastack import *
from acis_bkg_model import acis_bkg_model

clear_stack()
datadir = 'data/'
load_pha([], datadir + 'acisf04938_000N002_r0043_pha3.fits')
load_pha([], datadir + 'acisf07867_000N001_r0002_pha3.fits')

load_bkg_rmf([], datadir + "acisf04938_000N002_r0043_rmf3.fits")
load_bkg_rmf([], datadir + "acisf07867_000N001_r0002_rmf3.fits")

load_bkg_arf([], datadir + "acisf04938_000N002_r0043_arf3.fits")
load_bkg_arf([], datadir + "acisf07867_000N001_r0002_arf3.fits")


# Define background models
bkg_arfs = get_bkg_arf([])
bkg_scales = get_bkg_scale([])
bkg_models = [const1d.c1 * acis_bkg_model('acis7s'),
              const1d.c2 * acis_bkg_model('acis7s')]
bkg_rsps = get_response([], bkg_id=1)
for i in range(2):
    id_ = i + 1
    # Make the ARF spectral response flat.  This is required for using
    # the acis_bkg_model.
    bkg_arfs[i].specresp = bkg_arfs[i].specresp * 0 + 1.
    set_bkg_full_model(id_, bkg_rsps[i](bkg_models[i]))

# Fit background
notice(0.5, 8.)
set_method("neldermead")
set_stat("cash")

thaw(c1.c0)
thaw(c2.c0)
fit_bkg()
freeze(c1.c0)
freeze(c2.c0)

# Define source models
rsps = get_response([])
src_model = xsphabs.abs1 * powlaw1d.pow1
src_models = [src_model,
              src_model * const1d.ratio_12]
for i in range(2):
    id_ = i + 1
    set_full_model(id_, (rsps[i](src_models[i])
                         + bkg_scales[i] * bkg_rsps[i](bkg_models[i])))

set_par(abs1.nh, 0.0398)
freeze(abs1)
fit()
plot_fit([])
# plot_bkg_fit([])

# FIT OUTPUT:
# 
# Datasets              = 1, 2
# Method                = neldermead
# Statistic             = cash
# Initial fit statistic = -11105.6
# Final fit statistic   = -11105.6 at function evaluation 64
# Data points           = 1028
# Degrees of freedom    = 1026
# Change in statistic   = 0
#    c1.c0          1659.79     
#    c2.c0          21.7327     
# Datasets              = 1, 2
# Method                = neldermead
# Statistic             = cash
# Initial fit statistic = -12455
# Final fit statistic   = -13249.7 at function evaluation 433
# Data points           = 2056
# Degrees of freedom    = 2053
# Change in statistic   = 794.728
#    pow1.gamma     2.00686     
#    pow1.ampl      8.04141e-05 
#    ratio_12.c0    17.6        
