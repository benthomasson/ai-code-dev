
.PHONY: all


all: build


build:
	podman build -t quay.io/bthomass/ai-code-dev:latest .

shell:
	podman run -it --rm --name ai-code-dev -v $(PWD):/opt/app-root/src --entrypoint /bin/bash quay.io/bthomass/ai-code-dev:latest


push:
	podman push quay.io/bthomass/ai-code-dev:latest
