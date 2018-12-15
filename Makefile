image:
	docker build -t idb-convert .

run:
	docker run -it --rm -v $(PWD):/data idb-convert /data/IntenseDebate_clean.xml > ./output.txt

print-empty-urls:
	@docker run -it --rm -v $(PWD):/data idb-convert --print-empty-urls /data/IntenseDebate_clean.xml

print-urls-mapping:
	@docker run -it --rm -v $(PWD):/data --entrypoint /app/gen_new_urls.py idb-convert titles.json

shell:
	docker run -it --rm -v $(PWD):/data --entrypoint /bin/sh idb-convert

