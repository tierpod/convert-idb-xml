image:
	docker build -t idb-convert .

run:
	docker run -it --rm -v $(PWD):/data idb-convert /data/IntenseDebate_clean.xml

