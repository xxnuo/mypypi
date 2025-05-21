VERSION := $(shell git rev-parse --short HEAD)
IMAGE := xxnuo/mypypi
IMAGE2 := ghcr.io/xxnuo/mypypi
UV := ~/.local/bin/uv
NAME := mypypi
ENV_PROXY := http://192.168.1.200:7890

update:
	git submodule update --init --recursive

install: update
	$(UV) sync --all-groups

build:
	$(UV) pip compile --no-deps pyproject.toml -o requirements.txt
	docker buildx build \
		--platform linux/386,linux/amd64,linux/arm64,linux/ppc64le,linux/s390x \
		--build-arg HTTP_PROXY=$(ENV_PROXY) \
		--build-arg HTTPS_PROXY=$(ENV_PROXY) \
		--build-arg ALL_PROXY=$(ENV_PROXY) \
		--build-arg NO_PROXY=localhost,127.0.0.1 \
		-t $(IMAGE):$(VERSION) \
		-t $(IMAGE):latest \
		--load .

test:
	docker run -p 10608:10608 -p 10609:10609 --rm --name $(NAME) $(IMAGE):$(VERSION) 

push:
	docker buildx build \
		--platform linux/386,linux/amd64,linux/arm64,linux/ppc64le,linux/s390x \
		--build-arg HTTP_PROXY=$(ENV_PROXY) \
		--build-arg HTTPS_PROXY=$(ENV_PROXY) \
		--build-arg ALL_PROXY=$(ENV_PROXY) \
		--build-arg NO_PROXY=localhost,127.0.0.1 \
		-t $(IMAGE):$(VERSION) \
		-t $(IMAGE):latest \
		-t $(IMAGE2):$(VERSION) \
		-t $(IMAGE2):latest \
		--push .
