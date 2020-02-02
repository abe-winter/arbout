DBNAME=arbout-db

start-db:
	docker run --name $(DBNAME) -d postgres:11

db-host:
	@docker inspect -f '{{.NetworkSettings.IPAddress}}' $(DBNAME)

psql:
	docker exec -it $(DBNAME) psql -U postgres

BOOTSTRAP_VERSION := 4.4.1
BOOTSTRAP_ZIP := bootstrap-$(BOOTSTRAP_VERSION)-dist.zip
$(BOOTSTRAP_ZIP):
	wget -q https://github.com/twbs/bootstrap/releases/download/v$(BOOTSTRAP_VERSION)/$(BOOTSTRAP_ZIP)

static/bootstrap.min.css: $(BOOTSTRAP_ZIP)
	unzip -j $(BOOTSTRAP_ZIP) bootstrap-$(BOOTSTRAP_VERSION)-dist/css/bootstrap.min.css -d static

lint:
	pylint lib
