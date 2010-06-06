from datastack import *

ds = DataStack()

load_pha(ds, 'data/acis_1_pha3.fits') 
load_pha(ds, 'data/acis_2_pha3.fits') 
load_pha(ds, 'data/acis_3_pha3.fits') 
load_pha(ds, 'data/acis_4_pha3.fits') 

group_counts(ds, 20)

ignore(ds, None, 0.5)
ignore(ds, 7, None)
ignore(ds[3,4], 6.0, None) # Ignore more for datasets 3, 4

subtract(ds)

set_source(ds[1,3], 'xsphabs.gal * powlaw1d.pow#')
set_source(ds[2,4], 'xsphabs.gal * powlaw1d.pow# + gauss1d.gauss#')

set_par(ds, 'gauss.fwhm', 0.5)
set_par(ds, 'gauss.pos', 5)
freeze(ds, 'gauss.fwhm')
freeze(ds, 'gauss.pos')

link(ds, 'pow.gamma')
set_par(ds, 'gal.nh', 0.04)

fit(ds)
print 'pow.gamma:', get_par(ds, 'pow.gamma.val')
print 'pow.ampl:', get_par(ds, 'pow.ampl.val')

plot_fit_resid(ds)
