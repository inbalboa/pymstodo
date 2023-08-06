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
	@git tag -a "v$(TAG)" -m "Release $(TAG)"
	@git push --atomic origin master "v$(TAG)"

docs_gen:
	@printf "==> gen docs...\n"
	@mkdocs build

docs_pub:
	@printf "==> pub docs...\n"
	@mkdocs gh-deploy

docs: docs_pub

win_tz:
	@printf "==> getting windows time zones...\n"
	@python3 update_windows_zones_data.py

run: lint tag pub
	@printf "\nPublished at %s\n\n" "`date`"

.DEFAULT_GOAL := run
.PHONY: lint tag pub docs win_tz run
