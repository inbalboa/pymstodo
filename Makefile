TAG=`python setup.py --version`

lint:
	@printf "==> linting...\n"
	@python -m flake8 --select=DUO pymstodo
	@python -m mypy --ignore-missing-imports --strict pymstodo

tag:
	@printf "==> tagging...\n"
	@git tag -a "v$(TAG)" -m "Release $(TAG)"

pub:
	@printf "==> git push...\n"
	@git push origin "v$(TAG)"

run: lint tag pub
	@printf "\nPublished at %s\n\n" "`date`"

.DEFAULT_GOAL := run
.PHONY: lint tag pub run

