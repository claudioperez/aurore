
install:
	pip install -e .

docs:
	help2man aurore | pandoc -f man -t html > README.html
