# NYU DevOps Project- Wishlists Service
[![Build Status](https://github.com/CSCI-GA-2820-FA23-001/wishlists/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA23-001/wishlists/actions)
[![Build Status](https://github.com/CSCI-GA-2820-FA23-001/wishlists/actions/workflows/bdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA23-001/wishlists/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA23-001/wishlists/branch/master/graph/badge.svg?token=U9QCD0SANQ)](https://codecov.io/gh/CSCI-GA-2820-FA23-001/wishlists)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)



## Overview

This repository contains code for Wishlists for an e-commerce web site. This shows how to create a REST API with subordinate resources like wishlists that have products:



## Running the service locally

Before Run, make sure you have install [Docker Desktop](https://www.docker.com/products/docker-desktop), [Visual Studio Code](https://code.visualstudio.com), [Remote Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) first. Then you could clone the repository and then run the following commands:

- ```cd wishlist```
- ```code .```
- Reopen the folder in Dev Container
- Run ```flask run``` command on the terminal
- The service is available at localhost: ```http://localhost:8000```
- Or uses *honcho* which gets it's commands from the `Procfile`. To start the service simply use:
            
```shell
$ honcho start
```

To run the all the test cases locally, please run the command ```make test```. The test cases have 98% code coverage currently.



## Deploy to Kubernetes locally

Use the command to create a cluster:

- ```make cluster```

Then use the commands to build, tag and push the image:

- ```docker build -t wishlist:1.0 .```
- ```docker tag wishlist:1.0 cluster-registry:32000/wishlist:1.0```
- ```docker push cluster-registry:32000/wishlist:1.0```

Finally, use the command to deploy the service to Kubernetes:

- ```kubectl apply -f k8s```

## Deploy to OpenShift
Our service is now available at [Wishlist Service](https://wishlists-chrisxhhh-dev.apps.sandbox-m2.ll9k.p1.openshiftapps.com/)

Check the status of microservice using ```/health``` endpoint. Run the following command:
```
curl https://wishlists-chrisxhhh-dev.apps.sandbox-m2.ll9k.p1.openshiftapps.com/health
```

## Wishlist Model
```
wishlist = {
            "id": Int,
            "name": String,
            "date_joined": DateTime,
            "products": [],
            "owner": String
        }
```
## Product Model
```
product = {
            "id": Int,
            "wishlist_id": Int,
            "name": String,
            "quantity": Int
        }
```

## Wishlist Service APIs


These are the RESTful routes for `wishlists` and `products`
```
Endpoint          Methods  Rule
----------------  -------  -----------------------------------------------------
index              GET      /
list_wishlists     GET      /wishlists
create_wishlists   POST     /wishlists
get_wishlists      GET      /wishlists/<int: wishlist_id>
update_wishlists   PUT      /wishlists/<int: wishlist_id>
copy_wishlists     POST   /wishlists/<int: wishlist_id>

list_products      GET      /wishlists/<int: wishlist_id>/products
create_products    POST     /wishlists/<int: wishlist_id>/products
get_products       GET      /wishlists/<int: wishlist_id>/products/<int: product_id>
update_products    PUT      /wishlists/<int: wishlist_id>/products/<int: product_id>
delete_products    DELETE   /wishlists/<int: wishlist_id>/products/<int: product_id>
```
<!-- 
The test cases have 95% test coverage and can be run with `make test` -->



## Contents

The project contains the following:

```text
.gitignore                            - this will ignore vagrant and other metadata files
.flaskenv                             - Environment variables to configure Flask
.gitattributes                        - File to gix Windows CRLF issues
.devcontainers/                       - Folder with support for VSCode Remote Containers
dot-env-example                       - copy to .env to use environment variables
requirements.txt                      - list if Python libraries required by your code
config.py                             - configuration parameters

features/
├── steps.py                          - define file for the BDD tests
│   ├── web_steps.py                  - define specific to web interactions
│   └── wishlists_steps.py            - define specifically for the 'wishlists' feature
├── enviroments.py                    - setup and teardown methods that are executed before and after each scenario or suite of tests
└── wishlists.feature                 - feature file for the 'wishlists' functionality

.tekton/
├── events/                           - holds Tekton Triggers resources for handling external events.
│   ├── event_listener.yaml           - defines an EventListener
│   ├── trigger.yaml                  - specifies a Trigger
│   ├── trigger_binding.yaml          - contains TriggerBindings
│   └── trigger_template.yaml         - holds a TriggerTemplate
├── pipeline.yaml                     - main pipeline definition that specifies tasks to be executed
├── tasks.yaml                        - defines the individual tasks that the pipeline will run
└── workspace.yaml                    - specifies workspace definitions for sharing data between tasks in a pipeline

k8s/
├── deployment.yaml                   - defines application's deployment
├── ingress.yaml                      - ingress rules
├── postgres.yaml                     - deploy a PostgreSQL database within the cluster
├── pv.yaml                           - sefines Persistent Volume (PV) resources
└── service.yaml                      - specifies the service objects, pods, network traffic

service/                              - service python package
├── __init__.py                       - package initializer
├── models.py                         - module with business models
├── routes.py                         - module with service routes
└── common                            - common code package
    ├── error_handlers.py             - HTTP error handling code
    ├── log_handlers.py               - logging setup code
    └── status.py                     - HTTP status constants

tests/                                - test cases package
├── __init__.py                       - package initializer
├── test_models.py                    - test suite for business models
└── test_routes.py                    - test suite for service routes
```

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
