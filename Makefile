TAG=`python setup.py --version`

lint:
	@printf "==> linting...\n"
	@python3 -m ruff check "$(CURDIR)"
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

docs: docs_pub

run: lint tag pub
	@printf "\nPublished at %s\n\n" "`date`"

.DEFAULT_GOAL := run
.PHONY: lint tag pub docs run
