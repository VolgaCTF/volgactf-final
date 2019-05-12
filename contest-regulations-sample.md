# VolgaCTF Final: Contest regulations sample

[General provisions](#general-provisions)  
[Common terms and definitions](#common-terms-and-definitions)  
[Teams' rights and responsibilities](#teams-rights-and-responsibilities)  
[Calculating scores](#calculating-scores)  

## General provisions

As the competition starts, all teams are provided with identical virtual machine images (called **vulnboxes**), each of which contains a set of vulnerable services. The contestants' target is to detect vulnerabilities in these services, patch their vulnbox so as to defend their services and to exploit those vulnerabilities, stealing confidential information (flags) from rival teams' services. The game is managed by the automatic checking system (**ACS** for short) which places new flags into services on a regular basis. ACS also accepts flags captured by teams, checks availability of all services and recalculates teams' scores. A team gaining the maximum score becomes the winner.

## Common terms and definitions

A **team** is a group made of 3-7 persons, who are **physically present** at the venue. Other people are not treated as participants of a team and thus are not allowed to take part in a game on behalf of that particular team.

A team's ultimate **aim** is to detect vulnerabilities in the services, patch services in their vulnbox and to obtain flags by exploiting those vulnerabilities in other teams' services.

A **service** is a program or a set of programs which implements some functions and interacts with ACS by the means of some protocol.

A service **state** is considered **UP** when a service fully implements its basic functions and correctly interacts with ACS.

A service state is considered **DOWN** when a service is not reachable within the game network.

A service state is considered **MUMBLE** when a service does not fully implement its functions and/or does not comply with the communication protocol (ACS ⟷ service).

A service state is considered **CORRUPT** when a service returns unexpected data (e.g. a wrong flag) **although** fully implementing its functions and being in compliance with the communication protocol (ACS ⟷ service).

The **performance** of each service is evaluated by three parameters: defence, availability and attack.

A **vulnerability** in a service is a design flaw which enables inadvertent and/or potentially malicious behaviour in a service.

A **flag** is the string which stands for some valuable and confidential information and thus is in need of protection.

ACS is a set of programs which manages the game. ACS has the following functions:

- creating and signing flags;
- placing flags into teams' services by the means of some protocol;
- checking placed flags by the means of some protocol;
- checking whether each service of each team implements an
original set of functions;
- accepting captured flags.

## Teams' rights and responsibilities

A team is **obliged**:

- to use their own computer as a virtual machine instance host;
- to install a virtualization tool and to configure virtual machine instance parameters, such as instance location on a hard disk, amount of RAM, MAC-address of a network card etc.;
- to launch a vulnbox instance and configure its operating system & network, including resetting of instance user account password, setting static IP address etc.;
- to investigate into services and to perform other actions exclusively from their network segment.

A team is **prohibited**:
- to perform attacks against competition infrastructure;
- to filter network traffic with an intention to block other teams' actions against them (e.g. by IP addresses);
- to generate an inexplicably immense amount of traffic (flood, DOS, DDOS);
- to perform destructive attacks against vulnboxes & infrastructure units belonging to other teams;
- to perform all aforementioned actions on behalf of other teams
- to address individuals not belonging to their team for help (e.g. by means of VPN and/or by other means of communication).

A team has the right:

- to change the network topology of their network segment at
their own risk.

## Calculating scores

A team gets scores for:

1. maintaining their services so as they are in **UP** state;
2. patching their services so that other teams are not able to obtain
flags from them;
3. handling successful attacks against other teams's services and
submitting stolen flags to ACS.

## License
MIT @ [VolgaCTF](https://github.com/VolgaCTF)
