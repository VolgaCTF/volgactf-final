# VolgaCTF Final: Contest management guide

Instrumental actions (e.g. start/stop a competition) require an SSH connection to the **master** server.

Less important actions (e.g. post a piece of news, view logs) require a connection to the **admin** subnet and a web browser.

## systemd target

```sh
$ ssh master.final.volgactf.test
$ sudo systemctl start/stop volgactf_final.target
```

The target comprises several systemd services. To get their statuses, run

```sh
$ ssh master.final.volgactf.test
$ sudo systemctl status 'volgactf_final*'
```

## CLI program

CLI program is installed on the **master** server.

### database management

Reset the database (remove all tables and recreate them). Use at the start of every contest.

```
$ volgactf-final-cli db reset
```

### competition state management

Init a competition (write information about teams, services etc. into the database) from a so-called **domain** file.

```sh
$ volgactf-final-cli competition init /opt/volgactf/final/domain/init-10.rb
```

Start a competition. *This command runs asyncronously (a new round will not be started immediately, watch the status in the scoreboard).*

```sh
$ volgactf-final-cli competition start
```

Pause a competition. *This command runs asyncronously (all "live" flags must expire, watch the status in the scoreboard).*

```sh
$ volgactf-final-cli competition pause
```

Resume a competition. *This command runs asyncronously (a new round will not be started immediately, watch the status in the scoreboard).*

```sh
$ volgactf-final-cli competition resume
```

Finish a competition. *This command runs asyncronously (all "live" flags must expire, watch the status in the scoreboard).*

```sh
$ volgactf-final-cli competition finish
```

### scoreboard visibility management

Disable scoreboard update (for teams' subnets during a last hour of a competition)

```sh
$ volgactf-final-cli scoreboard disable
```

## scoreboard

Users connected to **admin** network (organisers) have access to competition logs, news editing and teams' performance stats, not to mention visualisation system available at `/visualization`.

## use case

1. stop the systemd target
2. reset database
3. start the systemd target
4. init a competition
5. start the competition
6. (optional) pause the competition, then resume
7. disable scoreboard update for teams one hour before the end
8. stop the competition

## License
MIT @ [VolgaCTF](https://github.com/VolgaCTF)
