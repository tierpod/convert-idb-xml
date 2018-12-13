image:
	docker build -t idb-convert .

run:
	docker run -it --rm -v $(PWD):/data idb-convert /data/IntenseDebate_clean.xml > ./output.json

select-empty-url:
	cat output.json | jq '.[] | select(.locator.url == "") | { id: .id, pid: .pid, url: .locator.url }' -c
	@# cat output.json | jq '.[] | select(.locator.url == "") | { title: .title, url: .locator.url }' -c | uniq
