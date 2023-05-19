test:
	python setup.py test

install:
	python setup.py install

clean:
	rm -rf build dist *.egg-info images/*

PYVER ?= 3.7.1
REQ ?= requirements.txt
NAME ?= easy_rate
prepare_virutalenv:
	pyenv install $(PYVER) -s
	-pyenv virtualenv $(PYVER) ${NAME}
	source `pyenv virtualenv-prefix ${NAME}`/envs/${NAME}/bin/activate
	`pyenv virtualenv-prefix ${NAME}`/envs/${NAME}/bin/pip install -r $(REQ)
