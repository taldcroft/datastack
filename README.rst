Datastack
====================

``Datastack`` is a `CIAO`_ `Sherpa`_ extension package for manipulating and
fitting a stack of related datasets.  It provides stack-enabled
(i.e. vectorized) versions of the key `Sherpa`_ commands used to load
data, set source models, get and set parameters, fit, and plot.  

For X-ray spectral analysis this means that a group of related datasets, for
instance 10 observations of the same source taken at different times, can be
analyzed as if they were a single merged dataset.  This has the important
advantage of using the appropriate individual response functions while hiding
the complexity (or tedium) of defining models and parameters for all the
datasets. 

Quick look
==========

The example below shows what is required to simultaneously fit three spectra of
a source taken from different epochs.  Bear in mind that these commands would
also work in the case of 20 or even 100 spectra, at which point the utility of
``datastack`` becomes more obvious.  ::

  from datastack import *
  load_pha([], 'data/acis_1_pha3.fits') 
  load_pha([], 'data/acis_2_pha3.fits') 
  load_pha([], 'data/acis_3_pha3.fits') 
  subtract([])
  group_counts([], 10)
  notice([], 0.5, 7)
  set_source([], xsphabs.gal * powlaw1d.powID)
  link([], 'pow.gamma')
  set_par([], 'gal.nh', 0.04)
  fit([])
  plot_fit_resid([])

That's all it takes.  To try this out go into the ``datastack`` installation source
directory::

  cd examples  
  sherpa

Then cut and paste the example commands and watch it go.  
