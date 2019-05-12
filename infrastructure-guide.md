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

# Step 3: prepare VM instances

1. Start VM instances

    ```sh
    $ cd ~/Projects/ctf-infrastructure
    $ vagrant up redis postgres master checker1
    ```

2. Check SSH connection

    ```sh
    $ cd ~/Projects/ctf-infrastructure
    $ ssh redis.final.volgactf.test
      ...
    $ ssh postgres.final.volgactf.test
      ...
    $ ssh master.final.volgactf.test
      ...
    $ ssh checker1.final.volgactf.test
      ...
    ```

3. Setup Chef agent on VM instances

    ```sh
    $ cd ~/Projects/ctf-infrastructure
    $ script/bootstrap redis
      ...
    $ script/bootstrap postgres
      ...
    $ script/bootstrap master
      ...
    $ script/bootstrap checker1
      ...
    ```

    Several files will be created in `nodes` directory, namely `redis.json`, `postgres.json`, `master.json`, `checker1.json`. They **must** be modified so that they are in accord with the files in `sample/nodes` directory.

# Step 4: examine configuration options

1. Examine settings in `environments/development.json`

    Environment settings are shared for every VM instance (or a `node`, in [Chef terms](https://docs.chef.io/nodes.html)).

    The settings below are copied from `sample/environments/development.json` but may well be adjusted to contest organiser's liking.

    ```json
    {
      "name": "development", // environment name
      "default_attributes": {
        "firewall": { // firewall
          "ubuntu_iptables": true,
          "allow_loopback": true,
          "allow_ssh": true,
          "allow_icmp": true,
          "ipv6_enabled": false
        },
        "latest-nodejs": { // node.js
          "install": "lts",
          "binary": true
        },
        "ntp": { // ntp
          "servers": [
            "0.pool.ntp.org",
            "1.pool.ntp.org",
            "2.pool.ntp.org",
            "3.pool.ntp.org"
          ]
        },
        "volgactf": {
          "final": {
            "dns": { // internal DNS
              "records": [
                {
                  "type": "A",
                  "name": "master.final.volgactf",
                  "ipv4_address": "172.20.0.2"
                },
                {
                  "type": "A",
                  "name": "postgres.final.volgactf",
                  "ipv4_address": "172.20.0.3"
                },
                {
                  "type": "A",
                  "name": "redis.final.volgactf",
                  "ipv4_address": "172.20.0.4"
                },
                {
                  "type": "A",
                  "name": "checker1.final.volgactf",
                  "ipv4_address": "172.20.0.11"
                }
              ]
            },
            "postgres": {
              "host": "postgres.final.volgactf"
            },
            "redis": {
              "host": "redis.final.volgactf"
            },
            "master": {
              "fqdn": "master.final.volgactf"
            },
            "checker": {
              "allow_access_from": [ // checkers must be accessible only from master node
                "172.20.0.2/32"
              ]
            },
            "config": {
              "internal_networks": [ // admin network (contest organisers)
                "172.20.0.0/24"
              ],
              "api_req_limits": { // Flag API limits (based on Nginx rate limiting)
                "flag_info": {
                  "rate": "10r/s",
                  "burst": 5,
                  "nodelay": true
                },
                "flag_submit": {
                  "rate": "5r/s",
                  "burst": 5,
                  "nodelay": true
                }
              },
              "competition": {
                "title": "VolgaCTF Final"
              },
              "settings": {
                "flag_lifetime": 360, // Number of seconds a flag is "live"
                "round_timespan": 120, // Start a new round each N seconds
                "poll_timespan": 35, // Poll "live" flags (from current and several previous rounds) each N seconds
                "poll_delay": 40 // Make a delay of N seconds before the first poll in a round
              },
              "teams": { // list of teams
                "team1": { // team alias
                  "name": "team #1", // team displayed name
                  "network": "172.20.1.0/24" // team network
                },
                "team2": {
                  "name": "team #2",
                  "network": "172.20.2.0/24"
                },
                "team3": {
                  "name": "team #3",
                  "network": "172.20.3.0/24"
                },
                "team4": {
                  "name": "team #4",
                  "network": "172.20.4.0/24",
                  "guest": true // a flag indicating a "guest" team
                }
              },
              "domain_files": [ // service and checker configuration files
                {
                  "name": "init-10",
                  "type": "competition_init",
                  "services": {
                    "service1": { // service alias
                      "name": "service #1", // service displayed name
                      "hostmask": "0.0.0.3", // network | hostmask = vulnbox IP address, e.g. 172.20.1.0 | 0.0.0.3 = 172.20.1.3
                      "checker_endpoint": "http://checker1.final.volgactf", // checker REST API endpoint
                      "attack_priority": true // No defence points until a first attack is made
                    }
                  }
                }
              ]
            }
          }
        }
      }
    }
    ```

2. Examine settings in `nodes/*.json` files

    Node settings are applied to a specific VM instance.

    The settings below are copied from `sample/nodes/*.json` but may well be adjusted to contest organiser's liking.

    **redis.json**

    ```json
    {
      "name": "redis",
      "chef_environment": "development",
      "normal": {
        "knife_zero": {
          "host": "redis.final.volgactf.test"
        },
        "volgactf": {
          "final": {
            "redis": {
              "allow_access_from": [ // Redis server must be accessible only from master server
                "172.20.0.2/32"
              ]
            }
          }
        }
      },
      "automatic": {
        "fqdn": "redis.final.volgactf.test"
      },
      "run_list": [
        "recipe[main::redis_server]"
      ]
    }
    ```

    **postgres.json**

    ```json
    {
      "name": "postgres",
      "chef_environment": "development",
      "normal": {
        "knife_zero": {
          "host": "postgres.final.volgactf.test"
        },
        "volgactf": {
          "final": {
            "postgres": {
              "allow_access_from": [ // PostgreSQL server must be accessible only from master server
                "172.20.0.2/32"
              ]
            }
          }
        }
      },
      "automatic": {
        "fqdn": "postgres.final.volgactf.test"
      },
      "run_list": [
        "recipe[main::postgres_server]"
      ]
    }
    ```

    **master.json**

    ```json
    {
      "name": "master",
      "chef_environment": "development",
      "normal": {
        "knife_zero": {
          "host": "master.final.volgactf.test"
        },
        "volgactf": {
          "final": {
            "master": {
              "extra_fqdn": [ // extra FQDN (e.g. public) for scoreboard
                "final.volgactf.test"
              ]
            }
          }
        }
      },
      "automatic": {
        "fqdn": "master.final.volgactf.test"
      },
      "run_list": [
        "recipe[main::master_server]"
      ]
    }
    ```

    **checker1.json**

    ```json
    {
      "name": "checker1",
      "chef_environment": "development",
      "normal": {
        "knife_zero": {
          "host": "checker1.final.volgactf.test"
        },
        "volgactf": {
          "final": {
            "checker": {
              "fqdn": "checker1.final.volgactf",
              "environment": {
                "THEMIS_FINALS_PING_ENABLED": "yes"
              },
              "network": {
                "name": "checker1-network" // Docker network name
              },
              "image": {
                "name": "checker1", // Docker image name
                "repo": "volgactf/volgactf-final-devenv-checker", // Docker image repository
                "tag": "1.0.0" // Docker image tag/version
              }
            }
          }
        }
      },
      "automatic": {
        "fqdn": "checker1.final.volgactf.test"
      },
      "run_list": [
        "recipe[main::checker_server]"
      ]
    }
    ```

3. Generate secrets

    **redis**
    ```sh
    $ cd ~/Projects/ctf-infrastructure
    $ python3 gen_data_bag.py redis
    {
      "id": "development",
      "password": "XfOsHkby0gtKw48KtrtfbiRJ"
    }
    $ script/databag create redis
      ...
      copy the output above and save
      ...
      use "script/databag show redis" to view settings
      or "script/databag edit redis" to edit them
      ...
    ```

    **postgres**
    ```sh
    $ cd ~/Projects/ctf-infrastructure
    $ python3 gen_data_bag.py postgres
    {
      "id": "development",
      "password": {
        "postgres": "j8lvij6UopQl4f8BC1YM9Zxe",
        "volgactf_final": "f6usTIJ4hTDBztA1dzPtOXth"
      }
    }
    $ script/databag create postgres
      ...
      copy the output above and save
      ...
      use "script/databag show postgres" to view settings
      or "script/databag edit postgres" to edit them
      ...
    ```

    **volgactf-final**
    ```sh
    $ cd ~/Projects/ctf-infrastructure
    $ python3 gen_data_bag.py volgactf-final
    {
      "id": "development",
      "auth": {
        "checker": {
          "username": "checker",
          "password": "raoN6IezStMvIqSg1pxKDs2nQUMAlV7i"
        },
        "master": {
          "username": "master",
          "password": "b8ggHDJ7vVL7xV9Rq9NaQJpWJ88BBq7l"
        }
      },
      "flag": {
        "generator_secret": "T-GRH4InaxmI7-gg0ukqWZWrSYLy3wyYEhQpJ7E2jGA=",
        "sign_key": {
          "public": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEdCvE7oMFMsfGWDnhvHU0yefW5jqw\nJp6t1RWV+OB8k2ulIx9ParDMfKb+3kxZVVwOz9cEwEGkLsrotm5KbXuKsw==\n-----END PUBLIC KEY-----",
          "private": "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEIEtkGFbohqnfkVOGIKY+JlaNzH3i5Tf5s0FuR4bdrl9EoAoGCCqGSM49\nAwEHoUQDQgAEdCvE7oMFMsfGWDnhvHU0yefW5jqwJp6t1RWV+OB8k2ulIx9ParDM\nfKb+3kxZVVwOz9cEwEGkLsrotm5KbXuKsw==\n-----END EC PRIVATE KEY-----"
        }
      }
    }
    $ script/databag create volgactf-final
      ...
      copy the output above and save
      ...
      use "script/databag show volgactf-final" to view settings
      or "script/databag edit volgactf-final" to edit them
      ...
    ```

# Step 5: install and configure software on VM instances

```sh
$ cd ~/Projects/ctf-infrastructure
$ script/converge redis
  ...
$ script/converge postgres
  ...
$ script/converge master
  ...
$ script/converge checker1
  ...
```

# Step 6: start team vulnboxes

```sh
$ cd ~/Projects/ctf-infrastructure
$ vagrant up team1 team2
```

Two desktop VM are started. They may be used so as to test the contest network as well as launch attacks. Here are some tips:

- in a team vulnbox, run `python -m SimpleHTTPServer 8080` so that `checker1` considers a service state as `UP`
- in a team vulnbox, install `volgactf.final` Python package so at to obtain information about flags and submit them

## License
MIT @ [VolgaCTF](https://github.com/VolgaCTF)
