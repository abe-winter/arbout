kustomize:
	kubectl apply -k kube/

# this creates a migration job. update the migrate newTag in kustomization.yml or this will probably be a no-op
migrate:
	kubectl create job mig-$(shell whoami)-$(shell date -u +%Y%m%d-%H%M) --from=cronjob/arbout-migrate
