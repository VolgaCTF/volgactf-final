# VolgaCTF Final: Infrastructure guide

VolgaCTF Final infrastructure is based on [Vagrant Chef Zero Boilerplate](https://github.com/aspyatkin/vagrant-chef-zero-boilerplate).

This guide provides an example of the setup process and requires a **DevOps** set (see [Prerequisites](prerequisites.md)) to be installed.

## Expected result

- 4 virtual machine instances, which are configured to host an A/D CTF
- 2 virtual machine instances, which are configured to act as teams' vulnboxes

## Step 0: network

As a rule, an A/D CTF often requires a class B network (`/16`). In this guide, `172.20.0.0/16` is used.

## Step 1: DNS

It is required that virtual machine instances (VMI) have their own unique FQDN within a common domain. In this guide, the common domain is `final.volgactf.test` and VMI have the following FQDNs:

| VMI | FQDN | IP address |
| --- | ---- | ---------- |
| **master** | `master.final.volgactf.test` | `172.20.0.2` |
| **postgres** | `postgres.final.volgactf.test` | `172.20.0.3` |
| **redis** | `redis.final.volgactf.test` | `172.20.0.4` |
| **checker1** | `checker1.final.volgactf.test` | `172.20.0.11` |
| **team1** | `team1.final.volgactf.test` | `172.20.1.3` |
| **team2** | `team2.final.volgactf.test` | `172.20.2.3` |

FQDNs must resolve within the host computer, on which VMI are run. That implies one of the following:
1. FQDNs are written in `/etc/hosts` file
2. FQDNs are resolved by means of a host computer's local DNS server, e.g. [BIND](https://www.isc.org/downloads/bind/) or [Unbound](https://nlnetlabs.nl/projects/unbound/about/)
3. FQDNs are resolved by means of the global DNS network, which requires a real domain e.g. `final.volgactf.com`

## Step 2: Infrastructure repository

1. Clone a sample infrastructure repository and init a new git repository

```sh
$ cd ~/Projects
$ git clone https://github.com/VolgaCTF/volgactf-final-infrastructure ctf-infrastructure
$ cd ctf-infrastructure
$ rm -rf .git
$ git init
```

2. Install dependencies

```sh
$ cd ~/Projects/ctf-infrastructure
$ bundle install
$ bundle exec berks install
$ vagrant plugin install --plugin-version 1.5.1 vagrant-helpers
```

3. Copy the so-called [Vagrant insecure keypair](https://github.com/hashicorp/vagrant/tree/master/keys)

```sh
$ cd ~/.well-known
$ wget -O ~/.well-known/vagrant_private_key https://raw.githubusercontent.com/hashicorp/vagrant/master/keys/vagrant
$ chmod 600 ~/.well-known/vagrant_private_key
```

4. Create a secret key to encrypt certain configuration options (e.g. passwords). It is recommended (although not required) that it is stored in an encrypted container (for instance, [VeraCrypt](https://www.veracrypt.fr/en/Home.html) container). In this guide it is presupposed that a secure storage is available at `/Volumes/encrypted-container`.

```
$ mkdir /Volumes/encrypted-container/development
$ openssl rand -base64 512 | tr -d '\r\n' > /Volumes/encrypted-container/development/data_bag_secret
```

5. Copy configuration files from samples

```sh
$ cd ~/Projects/ctf-infrastructure
$ cp sample/opts.yaml .
$ cp sample/.env .
$ cp sample/environments/development.json environments
```

# Step 3: launch VMI and setup SSH connection

## License
MIT @ [VolgaCTF](https://github.com/VolgaCTF)
