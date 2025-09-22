VERSION := $(shell git rev-parse --short HEAD)
IMAGE := xxnuo/mypypi
IMAGE2 := ghcr.io/xxnuo/mypypi
UV := ~/.local/bin/uv
NAME := mypypi
UV := ~/.local/bin/uv
CURL := $(shell if command -v axel >/dev/null 2>&1; then echo "axel"; else echo "curl"; fi)
REMOTE := nvidia@gpu
REMOTE_PATH := ~/compose/mypypi
ENV_PROXY := http://wa.lan:7890

sync-from-gpu:
	rsync -arvzlt --delete --exclude-from=.rsyncignore $(REMOTE):$(REMOTE_PATH)/packages ./packages

sync-to-gpu:
	ssh -t $(REMOTE) "mkdir -p $(REMOTE_PATH)"
	rsync -arvzlt --delete --exclude-from=.rsyncignore ./packages $(REMOTE):$(REMOTE_PATH)/packages

sync-clean:
	ssh -t $(REMOTE) "rm -rf $(REMOTE_PATH)"

update:
	git submodule update --init --recursive

install:
	$(UV) sync --all-groups

build:
	$(UV) pip compile --no-deps pyproject.toml -o requirements.txt
	docker build \
		--progress=plain \
		--no-cache \
		--platform linux/amd64,linux/arm64/v8 \
		--build-arg HTTP_PROXY=$(ENV_PROXY) \
		--build-arg HTTPS_PROXY=$(ENV_PROXY) \
		--build-arg ALL_PROXY=$(ENV_PROXY) \
		--build-arg NO_PROXY=localhost,127.0.0.1 \
		-t $(IMAGE):$(VERSION) \
		-t $(IMAGE):latest \
		.

test:
	docker run -p 10608:10608 -p 10609:10609 -v ./packages:/app/packages --rm --name $(NAME) $(IMAGE):$(VERSION)

push:
	$(UV) pip compile --no-deps pyproject.toml -o requirements.txt
	docker build \
		--progress=plain \
		--no-cache \
		--platform linux/amd64,linux/arm64/v8 \
		--build-arg HTTP_PROXY=$(ENV_PROXY) \
		--build-arg HTTPS_PROXY=$(ENV_PROXY) \
		--build-arg ALL_PROXY=$(ENV_PROXY) \
		--build-arg NO_PROXY=localhost,127.0.0.1 \
		-t $(IMAGE):$(VERSION) \
		-t $(IMAGE):latest \
		-t $(IMAGE2):$(VERSION) \
		-t $(IMAGE2):latest \
		--push .
