# VolgaCTF Final: Service checker guide

A service checker is a REST service. It must conform to [VolgaCTF Final Checker Protocol](https://github.com/VolgaCTF/volgactf-final-checker-protocol).

One implementation (from the [Infrastructure guide](infrastructure-guide.md)) is the following: a VM instance, on which a number of Docker containers is run and Nginx acting as a load-balancer.

Containers are identical and based on an image created with the help of [VolgaCTF Final devenv](https://github.com/VolgaCTF/volgactf-final-devenv).

A so-called fleet is managed by `systemctl`:

```sh
$ ssh checker1.final.volgactf.test
$ sudo systemctl start/stop volgactf_final_checker1.target
```

The target comprises several systemd services. To get their statuses, run

```sh
$ ssh checker1.final.volgactf.test
$ sudo systemctl status 'volgactf_final_checker1*'
```

## License
MIT @ [VolgaCTF](https://github.com/VolgaCTF)
