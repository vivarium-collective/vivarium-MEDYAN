# vivarium-MEDYAN

A Vivarium wrapper for [MEDYAN](http://medyan.org/index.html)

---

# Installation

First, we recommend you create an environment (with pyenv, conda, or similar).

Then, to install:
**Stable Release:** `pip install vivarium_medyan` (coming soon)<br>
**Development Head:** `pip install git+https://github.com/vivarium-collective/vivarium-MEDYAN.git`<br>
**Local Editable Install** `pip install -e .[dev]` (or `pip install -e .\[dev\]` on mac) from repo root directory

Or use Conda with the `env.yml` file to create the environment: 
```
conda env create -f env.yml
conda activate vivarium-models
```

The `MedyanProcess` will download the latest MEDYAN image from Simularium Docker Hub the first time it runs, and use that to simulate in MEDYAN.

# Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

## useful docker commands

### create a new docker network

> docker network create vivarium-test

### build a docker container from scratch

> docker build --no-cache -t vivarium-medyan:latest ./

### start a long-running container (inside a network)

> docker run --network vivarium-test --network-alias medyan -t -d vivarium-medyan

### execute a command inside a running container

> docker exec sweet_feistel ./medyan

### kill a running container

> docker container kill sweet_feistel

### kill all containers

> docker system prune

## Commands You Need To Know

1. `black vivarium_medyan`

    This will fix lint issues.

2. `make build`

    This will run `tox` which will run all your tests as well as lint your code.

3. `make clean`

    This will clean up various Python and build generated files so that you can ensure that you are working in a clean environment.
