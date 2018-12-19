image:
	docker build -t idb-convert .

run:
	docker run -it --rm -v $(PWD):/data idb-convert --filter /data/IntenseDebate_clean.xml > ./output.txt

print-urls-mapping:
	@docker run -it --rm -v $(PWD):/data --entrypoint /app/gen_new_urls.py idb-convert titles.json

shell:
	docker run -it --rm -v $(PWD):/data --entrypoint /bin/sh idb-convert

doctest:
	python3 -m doctest convert.py
