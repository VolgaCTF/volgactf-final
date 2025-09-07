# VolgaCTF Final generator

The generator scaffolds a docker compose project with a fully functional VolgaCTF Final checking system.

## Prerequisites

- Python 3
- Docker Compose
- [mkcert](https://github.com/FiloSottile/mkcert)
- (optional) any browser extension to conect to HTTP proxy e. g. [FoxyProxy](https://chromewebstore.google.com/detail/foxyproxy/gcknhkkoolaabfmlnjonogaaifnjlfnp)

## Setup

Install Python packages:

```shell
$ cd generator
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ deactivate
```

Copy sample settings:

```shell
$ cp generator/vars.example.yml generator/vars.yml
```

and adjust the copied file if necessary (network settings, teams, services et al.)

### Configuration

Depending on settings (in `vars.yml`), the generator will create a docker compose project for multiple containers. The most important setting here is the network CIDR (`volgactf.final.network.cidr`):
- must be a local network with a `/16` prefix
- must not collide with any other networks in use (Docker, VirtualBox, VPN, Wi-Fi or Ethernet)

The next important group of options is the range of exposed ports (`volgactf.final.expose_ports.start` and `volgactf.final.expose_ports.end`). These ports are used by proxy containers:
- the first is used by a proxy container that is connected to "admin network"
- the next N ports are used by proxy containers that are connected to "team N network"
- the last port is used by a proxy container that exposes a database client

In essence all the traffic coming into the system is routed through those proxies - neither a system backend servers or service checkers are exposed publicly. This allows quick switching between different actors in the system.

## Generate

Choose an empty directory, in the example below `generated` will be used

```shell
$ cd generator
$ source .venv/bin/activate
$ python main.py templates ../generated vars.yml
$ deactivate
```

## Use

To start the system:
1. Navigate to the `generated` directory.
2. Read through post-generator steps and apply changes if necessary (add the system hostname to the local resolver, configure proxies in a browser)
3. Launch the system with `docker compose up -d`. This will take some time.
4. Connect to a proxy (of an admin or of a specific team).
5. Navigate to the system hostname e. g. `https://final.volgactf.test` (specificed in `volgactf.final.hostname`).

To shut down: either `docker compose down` or `docker compose down -v` to do cleanup.

## Regenerate

For now, it is advised to destroy the project that was created previously, and generate it anew.

## Control tools

The commands described below must be launched with at least `postges` and `redis` containers up and running.

Competition tools:

```shell
$ cd generated
$ script/cli.sh competition start
$ script/cli.sh competition pause
$ script/cli.sh competition resume
$ script/cli.sh competition finish
```

Reset the competition:
```shell
$ cd generated
$ script/db-reset.sh
$ script/cli.sh competition init /opt/volgactf/final/domain/competition_init.rb
```
