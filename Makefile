TAG=`python setup.py --version`
SPHINX_BUILD ?= sphinx-build
SPHINX_SOURCEDIR=.
SPHINX_BUILDDIR=_build

lint:
	@printf "==> linting...\n"
	@python3 -m flake8 --select=DUO pymstodo
	@python3 -m mypy --ignore-missing-imports --strict pymstodo

tag:
	@printf "==> tagging...\n"
	@git tag -a "v$(TAG)" -m "Release $(TAG)"

pub:
	@printf "==> git push...\n"
	@git push origin "v$(TAG)"

docs_gen:
	@printf "==> gen docs...\n"
	@mkdocs build

docs_pub:
	@printf "==> pub docs...\n"
	@mkdocs gh-deploy

docs: docs_gen docs_pub
	@printf "==> docs...\n"

run: lint tag pub
	@printf "\nPublished at %s\n\n" "`date`"

.DEFAULT_GOAL := run
.PHONY: lint tag pub docs run sphinx-build
