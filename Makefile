update:
	git submodule update --init --recursive

install: update
	uv sync --all-groups
