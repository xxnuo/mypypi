install:
	git submodule update --init --recursive
	uv sync
	uv pip install -e ./thirdparty/pypi-browser

