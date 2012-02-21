import datastack

ds = datastack.DataStack()

ds.load_pha('data/acis_1_pha3.fits')
ds.load_pha('data/acis_2_pha3.fits')
ds.load_pha('data/acis_3_pha3.fits')
ds.load_pha('data/acis_4_pha3.fits')

ds.group_counts(20)

ds.ignore(None, 0.5)
ds.ignore(7, None)
ds[3,4].ignore(6.0, None)  # Ignore more for datasets 3, 4

ds.subtract()

ds[1,3].set_source(xsphabs.gal * powlaw1d.powID)
ds[2,4].set_source(xsphabs.gal * powlaw1d.powID + gauss1d.gaussID)

ds.set_par('gauss.fwhm', 0.5)
ds.set_par('gauss.pos', 5)
ds.freeze('gauss.fwhm')
ds.freeze('gauss.pos')

ds.link('pow.gamma')
ds.set_par('gal.nh', 0.04)

ds.fit()
print 'pow.gamma:', ds.get_par('pow.gamma.val')
print 'pow.ampl:', ds.get_par('pow.ampl.val')

ds.plot_fit_resid()
