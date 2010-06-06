from datastack import *

clear_stack([])

load_pha([], "data/acis_1_pha3.fits") 
load_pha([], "data/acis_2_pha3.fits") 
load_pha([], "data/acis_3_pha3.fits") 
load_pha([], "data/acis_4_pha3.fits") 

group_counts([], 20)
ignore([], None, 0.5)
ignore([], 7, None)
subtract([])

set_source([], "xsphabs.gal * powlaw1d.pow#")
link([], "pow.gamma")
set_par([], "gal.nh", 0.04)
freeze([], "gal.nh")

fit([])
print "pow.ampl:", get_par([], "pow.ampl.val")
plot_fit_resid([])
