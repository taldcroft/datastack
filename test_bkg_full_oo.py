import os
from itertools import count, izip

import numpy as np
import sherpa.astro.ui as ui
import datastack
from acis_bkg_model import acis_bkg_model

## load_pha('examples/data/acisf04938_000N002_r0043_pha3.fits')

ds = datastack.DataStack()
phafiles = ['acisf04938_000N002_r0043_pha3.fits',
            'acisf07867_000N001_r0002_pha3.fits']
datadir = 'examples/data/'

for i, phafile in enumerate(phafiles):
    ds[i + 1].load_pha(os.path.join(datadir, phafile))

## rmf = get_rmf(id=1)
## arf = get_arf(id=1)

rmfs = ds.get_rmf()
arfs = ds.get_arf()

## load_bkg_rmf(rmf.name)
## load_bkg_arf(arf.name)

for i, rmf, arf in zip(count(1), rmfs, arfs):
    ds[i].load_bkg_rmf(rmf.name)
    ds[i].load_bkg_arf(arf.name)

## bkg_rmf = get_bkg_rmf()
## bkg_arf = get_bkg_arf()
## bkg_arf.specresp = np.ones_like(bkg_arf.specresp)
## bkg_model = bkg_rmf(bkg_arf(const1d.bkg_constID * acis_bkg_model('acis7s')))

# Define background models
acis_bkg = acis_bkg_model('acis7s')
bkg_models = []
c1 = ui.const1d.c1
c2 = ui.const1d.c2
for const, bkg_rmf, bkg_arf in zip((c1, c2),
                                   ds.get_bkg_rmf(),
                                   ds.get_bkg_arf()):
    bkg_arf.specresp = np.ones_like(bkg_arf.specresp)
    bkg_models.append(bkg_rmf(bkg_arf(const * acis_bkg)))

## src_model = rmf(arf(powlaw1d.pow1))
## bkg_scale = get_bkg_scale()
## set_full_model(src_model + bkg_scale * bkg_model)
## set_bkg_full_model(bkg_model)

## Define source models
abs1 = ui.xsphabs.abs1
pow1 = ui.powlaw1d.pow1
src_model1 = abs1 * pow1
src_models = [src_model1,
              src_model1 * ui.const1d.ratio_12]

vals_iter = izip(count(1),
                 src_models,
                 ds.get_response(),
                 bkg_models,
                 ds.get_bkg_scale())
for i, src_model, rsp, bkg_model, bkg_scale in vals_iter:
    ds[i].set_full_model(rsp(src_model) + bkg_scale * bkg_model)
    ds[i].set_bkg_full_model(bkg_model)

## Fit background
ds.notice(0.5, 8.)
ui.set_method("neldermead")
ui.set_stat("cash")

ui.thaw(c1.c0)
ui.thaw(c2.c0)
ui.fit_bkg()
ui.freeze(c1.c0)
ui.freeze(c2.c0)

ui.set_par(abs1.nh, 0.0398)
ui.freeze(abs1)
ui.fit()
ds.plot_fit()
# ds.plot_bkg_fit()

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
