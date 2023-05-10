TAG=`python setup.py --version`

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

docs:
	@printf "==> gen docs...\n"
	@pdoc --docformat google --no-search --no-show-source --output-directory docs ./pymstodo/client.py

run: lint tag pub
	@printf "\nPublished at %s\n\n" "`date`"

.DEFAULT_GOAL := run
.PHONY: lint tag pub docs run
