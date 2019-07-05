#!/usr/bin/make
# WARN: gmake syntax
########################################################
# Makefile for $(NAME)
#
# useful targets:
#	make check -- manifest checks
#	make clean -- clean distutils
#	make coverage_report -- code coverage report
#	make flake8 -- flake8 checks
#	make pylint -- source code checks
#	make rpm -- build RPM package
#	make sdist -- build python source distribution
#	make systest -- runs the system tests
#	make tests -- run all of the tests
#	make unittest -- runs the unit tests
#
# Notes:
# 1) flake8 is a wrapper around pep8, pyflakes, and McCabe.
########################################################
# variable section

NAME = "PyBitmessage"

PYTHON=python
COVERAGE=coverage
NOSE_OPTS = --with-coverage --cover-package=$(NAME)
SITELIB = $(shell $(PYTHON) -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")

VERSION := $(shell awk '/__version__/{print $$NF}' $(NAME)/__init__.py | sed "s/'//g")

RPMSPECDIR = .
RPMSPEC = $(RPMSPECDIR)/$(NAME).spec
RPMRELEASE = 1
RPMNVR = "$(NAME)-$(VERSION)-$(RPMRELEASE)"

FLAKE8_IGNORE = E302,E203,E261

########################################################

all: clean check flake8 pylint tests

flake8:
	flake8 --ignore=$(FLAKE8_IGNORE) $(NAME)/
	flake8 --ignore=$(FLAKE8_IGNORE),E402 tests/

pylint:
	find ./$(NAME) ./tests -name \*.py | xargs pylint --rcfile .pylintrc

check:
	@echo "Check-manifest disabled pending https://github.com/mgedmin/check-manifest/issues/68"
	#check-manifest

clean:
	@echo "Cleaning up distutils stuff"
	rm -rf build
	rm -rf dist
	rm -rf MANIFEST
	rm -rf *.egg-info
	@echo "Cleaning up byte compiled python stuff"
	find . -type f -regex ".*\.py[co]$$" -delete
	@echo "Cleaning up doc builds"
	rm -rf docs/_build
	rm -rf docs/api_modules
	rm -rf docs/client_modules
	@echo "Cleaning up test reports"
	rm -rf report/*

rpmcommon: sdist
	@mkdir -p rpmbuild
	@cp dist/*.gz rpmbuild/
	@cp -R conf/* rpmbuild/
	@sed -e 's#^Version:.*#Version: $(VERSION)#' -e 's#^Release:.*#Release: $(RPMRELEASE)#' $(RPMSPEC) >rpmbuild/$(NAME).spec

rpm: rpmcommon
	@rpmbuild --define "_topdir %(pwd)/rpmbuild" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define "_specdir $(RPMSPECDIR)" \
	--define "_sourcedir %{_topdir}" \
	--define "_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm" \
	--define "__python /usr/bin/python" \
	-ba rpmbuild/$(NAME).spec
	@rm -f rpmbuild/$(NAME).spec

sdist: clean
	$(PYTHON) setup.py sdist

tests: unittest systest coverage_report

unittest: clean
	nosetests $(NOSE_OPTS) tests/unit/*

systest: clean
	nosetests $(NOSE_OPTS) tests/system/*

coverage_report:
	$(COVERAGE) report --rcfile=".coveragerc"
