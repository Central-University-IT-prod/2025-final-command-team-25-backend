cd app

poetry run python -m coverage erase
poetry run python -m coverage run -m pytest test -v -s
poetry run python -m coverage report
