# AV2PA
### Palo Alto External Dynamic List Generator

#### This script can be run at the command line to generate a list of IP addresses.  Use on a SEIM to dynamically block threats that IDS/IPS rules.  Data stored as JSON and IP list is outputted to a text file.  JSON stores information regarding current, history and exclude IPs. 

## Usage

#### Arguments

 -a, --action			Define the action [add,remove,exclude,clear]
 -v, --verbose			Output to terminal
 -i, --ip				IP address (required when action = add,remove,exclude)
 -p, --penalty			Penalty for IP address
 
#### Actions

#####add
Add an IP address to the block list.  If no penalty is defined the penalty is incremented each time the IP address is added until it reaches 16(indefinate).

#####remove
Remove an IP address from the block list.  Removes the IP from the current, history and exclude dictionaries.

#####exclude
Add an IP to the exclude list.  Excluded IPs will not be processed.

#####clear 
Removes all IPs from the current, history and exclude dictionaries.

#####cycle
Cycles the blocklist and checks IPs and Penalty times.  If penalty has been reached, IPs are removed from the blocklist.  IPs with a penalty of 16 are not removed.  

#### Penalties
1 = 1 minute
2 = 5 minutes
3 = 10 minutes
4 = 15 minutes
5 = 30 minutes
6 = 60 minutes (1 hour)
7 = 180 minutes (3 hours)
8 = 360 minutes (6 hours)
9 = 720 minutes (12 hours)
10 = 1440 minutes (1 day)
11 = 4320 minutes (3 days)
12 = 10080 minutes (7 days)
13 = 20160 minutes (14 days)
14 = 43200 minutes (30 days)
15 = 525600 minutes (1 year)
16 = indefinite


### Run at command line



./av2pa.py 