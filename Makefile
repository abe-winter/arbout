DBNAME=arbout-db

start-db:
	docker run --name $(DBNAME) -d postgres:11

db-host:
	@docker inspect -f '{{.NetworkSettings.IPAddress}}' $(DBNAME)

psql:
	docker exec -it $(DBNAME) psql -U postgres
