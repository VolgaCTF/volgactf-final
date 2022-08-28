# VolgaCTF Final: Technical information sample

[Network](#network)  
[Virtual machine image](#virtual-machine-image)  
[Flag​ ​signatures](#flag-signatures)  
​[Submitting​ ​flags](#submitting-flags)  
[An​ ​insight​ ​into​ ​ACS](#an-insight-into-acs)  

## Network

Each team's network segment has the following address: `172.20.N.0/24`, where `N` stands for a team's number.

Vulnbox instance **MUST** be assigned the following address: `172.20.N.3`.

Scoreboard URL (intranet): [final.volgactf.test/scoreboard](http://final.volgactf.test/scoreboard)

Scoreboard URL (public): [live.volgactf.ru](https://live.volgactf.ru)

## Virtual machine image

[Vulnbox]()

**before launching the vulnbox, do not forget to regenerate your virtual machine instance mac address!**

A vulnbox is based on Ubuntu xx.yy x64 Server, all services are isolated from each other by the means of LXD. Containers start at boot.

### LXC

All​ ​commands​ ​below​ ​should​ ​be​ ​performed​ ​on​ ​behalf​ ​of​ ​root​ ​user.

List​ ​containers

```sh
$​ ​lxc list
```

By​ ​default​ ​all​ ​containers​ ​will​ ​be​ ​"running".​ ​To​ ​stop​ ​a​ ​container,​ ​run

```sh
$​ ​lxc stop​ ​​<CONTAINER_NAME>
```

Starting​ ​a​ ​container

```sh
$​ ​lxc start​ ​​<CONTAINER-NAME>
```

Access​ ​a​ ​container's​ ​console

```sh
$​ ​lxc exec <CONTAINER_NAME> -- /bin/bash
```

Exit​ ​a​ ​container's​ ​console: `Ctrl​ ​+​ ​D`.

### Services

Each service is located in a home directory of a container's default user account. Managing a service is simple:

```sh
$ systemctl start <SERVICE_NAME>
$ systemctl stop <SERVICE_NAME>
```

## Flag​ ​signatures

Flags are stored and transported into so-called ​capsules​. A capsule looks​ ​like​ ​this:

```
VolgaCTF{eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJmbGFnIjoiYzA4ODI0NjI2MjNkNjFmM2VlYzgwYjcyY2ZlNDQ3NjkifQ.YqcT52o3_S9XhjE6txPayJ-iylCHhpQs4SzfnCwKKsP3_XGol30GQVWf9QZ85RaO4l5uXVOgrkF335UIDn7x4A}
```

Data between ​`VolgaCTF{` and `​}` is a [JSON Web Token](https://jwt.io) signed using ES256 algorithm. You will need ​an ACS [public key](http://final.volgactf.test/api/capsule/v1/public_key) to decode a capsule and​ ​obtain​ ​a​ ​flag​ ​from​ ​it.​ ​Flag​ ​format​ ​is​ ​​`^[\da-f]{32}=$`.

### Public key (for the sample capsule)

```
-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE5aiazVMn0K9M0PyP4/iGZpKKqYez\n+6rCzO8iUjfkVvH87KcccPfNzv2olMtrFvF1bTLBAchFfDiNqewauTe/GA==
-----END PUBLIC KEY-----
```

## Submitting​ ​flags

You must submit **flags** (not capsules!) to `final.volgactf.test`. Each flag lives for 6 minutes.

### API

- [VolgaCTF Final API](https://github.com/VolgaCTF/volgactf-final-api) - public APIs description
- [volgactf.final](https://github.com/VolgaCTF/volgactf-final-py) - CLI & public API library for Python 2/3

### Rate limits

- Flag info 10r/s
- Flag submit 5r/s
- Service status 10r/s

## An​ ​insight​ ​into​ ​ACS

A​ ​game​ ​is​ ​divided​ ​in​ ​2-minute​ ​rounds.

When a new round is triggered, ACS tries to push flags (transported in capsules) to every service of every team. If a push attempt of a flag is successful, this particular flag is marked as ​**active**​. ACS immediately tries to pull **active** flags.

Every flag expires 6 minutes​ ​after​ ​it​ ​has​ ​been​ ​marked​ ​as​ **a​ctive**​.

Additionally, ​in each round ACS​ launches 3 **polls**: it ​pulls​ ​one ​randomly​ ​chosen​ ​​**active** ​​flag from each service from each team.

Scores are updated when all **active** flags issued in a particular round become **expired**.

### Availability

1 point for ​**availability** ​(AP<sub​>flag</sub​>)​ is given if all attempts to pull a flag were successful (**UP** state). Otherwise, a fraction of a point is given according to​ ​the​ ​equation:

<code>
AP<sub>​flag</sub>​​ ​=​ ​SPA<sub>​flag</sub>​​ ​/​ ​TPA<sub>​flag</sub>
</code>

where SPA stands for the number of successful pull attempts and TPA stands​ ​for​ ​the​ ​total​ ​number​ ​of​ ​pull​ ​attempts.

### Defence

By default, no defence points for flags from a service are given.

Points are to be awarded starting from the next round a service is attacked by any team. 1 point for ​**defence** ​(DP<sub>f​lag</sub>)​ is given if ​**all** attempts to pull a flag were successful and no-one has stolen and submitted this particular flag into ACS.

### Attack

1​ ​point​ ​for​ ​​attack​ ​​is​ ​given​ ​for​ ​each​ ​stolen​ ​flag.

A team ​cannot ​submit a flag stolen from a service **X** if a state of a service​ **​X**​ ​in​ ​their​ ​vulnbox​ ​is​ ​not​ ​​**UP**.

### Total

Total​ ​team​ ​score​ ​(TtS)​ ​is​ ​calculated​ ​as a sum of total scores (tS) in each category:

<code>
TtS​ ​=​ ​tS<sub>​attack</sub>​​ ​+​ ​tS<sub>​defence</sub>​​ ​+​ tS<sub>​availability</sub>​
</code>

In case of equal TtS a team who performed the last attack before the other​ ​team​ ​is​ ​placed​ ​higher​ ​in​ ​the​ ​scoreboard.

## License
MIT @ [VolgaCTF](https://github.com/VolgaCTF)
