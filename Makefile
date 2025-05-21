VERSION := $(shell git rev-parse --short HEAD)
IMAGE := xxnuo/mypypi
UV := ~/.local/bin/uv

update:
	git submodule update --init --recursive

install: update
	$(UV) sync --all-groups

build:
	$(UV) pip compile --no-deps pyproject.toml -o requirements.txt
	docker build -t $(IMAGE):$(VERSION) -t $(IMAGE):latest .

test:
	docker run -p 10608:10608 -p 10609:10609 --rm --name mypypi $(IMAGE):$(VERSION) 

push:
	docker push $(IMAGE):$(VERSION)
	docker push $(IMAGE):latest