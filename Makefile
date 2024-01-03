TAG=`python setup.py --version`

lint:
	@printf "==> linting...\n"
	@python3 -m ruff check --preview --unsafe-fixes "$(CURDIR)"
	@python3 -m mypy --ignore-missing-imports --strict pymstodo

check:
	@printf "==> checking the working tree... "
	@sh -c 'if [ -z "`git status --porcelain=v1`" ]; then printf "clean\n"; else printf "working tree is dirty, please, commit changes\n" && false; fi'

tag:
	@printf "==> tagging...\n"
	@git tag -a "v$(TAG)" -m "Release $(TAG)"

pub:
	@printf "==> pushing...\n"
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
	@python3 update_win_tz.py

run: lint check tag pub docs
	@printf "\nPublished at %s\n\n" "`date`"

.DEFAULT_GOAL := run
.PHONY: lint check tag pub docs win_tz run
