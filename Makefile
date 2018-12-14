image:
	docker build -t idb-convert .

run:
	docker run -it --rm -v $(PWD):/data idb-convert /data/IntenseDebate_clean.xml > ./output.txt

print-empty-urls:
	docker run -it --rm -v $(PWD):/data idb-convert --print-empty-urls /data/IntenseDebate_clean.xml

shell:
	docker run -it --rm -v $(PWD):/data --entrypoint /bin/sh idb-convert

