WWW = /proj/web-cxc/htdocs/contrib/datastack

.PHONY: doc dist

dist:
	python setup.py sdist

examples_data: 
	tar zcvf examples_data.tar.gz examples/data

doc:
	cd doc; \
	make html

install:
	rsync -av doc/_build/html/ $(WWW)/
	rsync -av dist/datastack-*.tar.gz examples_data.tar.gz $(WWW)/downloads/
