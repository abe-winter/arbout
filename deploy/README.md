# Arbout deployment

Example terraform & kube configs. This is used to host the live arbout at https://arbout.org.

## Setup steps

### Cloud basics

* deps: kubectl and terraform binaries
* set up a google cloud account
* look at the terraform variables at the top of gcloud.tf and populate them in an .envrc or something
* run the terraform

### Kube basics

* when the terraform is clean (may initially error because resources take a while to create), use something like `gcloud container clusters get-credentials $CLUSTERNAME` to get kubeconfig credentials, set KUBECONFIG=kubeconfig.yml or something
* you'll need to build the kube images and push them to a docker registry somewhere. Check out ../.gitlab-ci.yml for an example of how to do this
* in kustomization.yml, set `newName` to your hosted location and set `newTag` to an up-to-date tag
* create kube/secrets.env with vars `db_url`, `global_salt`, `global_crypt` (todo: instructions on key sizes)
* create kube/.dockerconfigjson with creds to your repo
* update `image` everywhere to point to your docker image (todo: build and host this publicly)
* override the host in the Ingress in service.yml
* run `make kustomize` to apply the kube
* it takes a really long time (10+ minutes) for the the certs and ingress to be correct, expect a bunch of 502s in the meantime. you can `kube describe managedcertificate` to watch provisioning status
* (todo: describe how to run the initial migration by modifying migrate.yml and running `make migrate`)

## Deploying a new version

* update `newTag` and run `make kustomize`
* (todo: migration instructions)
