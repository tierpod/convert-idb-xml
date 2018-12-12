image:
	docker build -t idb-convert .

run:
	docker run -it --rm -v $(PWD):/data idb-convert /data/input.xml

shell:
	docker run -it --rm -v $(PWD):/data --entrypoint /bin/sh idb-convert
