# AV2PA
### Palo Alto External Dynamic List Generator

#### This script can be run at the command line to generate a list of IP addresses.  Use on a SIEM to dynamically block threats that match IDS/IPS rules.  Data stored as JSON and IP list is outputted to a text file.  JSON stores information regarding current, history and exclude IPs.  Script logs to a syslog file and to the terminal if verbose is enabled. 

## Usage

#### Arguments

 -a, --action &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Define the action [add,remove,exclude,clear]
 
 -v, --verbose &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Output to terminal
 
 -i, --ip &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; IP address (required when action = add,remove,exclude)
 
 -p, --penalty &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Penalty for IP address
 
 
#### Actions

##### add
Add an IP address to the block list.  If no penalty is defined the penalty is incremented each time the IP address is added until it reaches 16(indefinate).

##### remove
Remove an IP address from the block list.  Removes the IP from the current, history and exclude dictionaries.

##### exclude
Add an IP to the exclude list.  Excluded IPs will not be processed.

##### clear 
Removes all IPs from the current, history and exclude dictionaries.

##### cycle
Cycles the blocklist and checks IPs and Penalty times.  If penalty has been reached, IPs are removed from the blocklist.  IPs with a penalty of 16 are not removed.  Suggest running this on a cron job to periodically cycle through the IP list.

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
[Block 1.2.3.4 temporarily, penalty is incremented]
./av2pa.py -a add -i 1.2.3.4 

[Block 1.2.3.4 for 1 day]
./av2pa.py -a add -i 1.2.3.4 -p '10'

[Block 1.2.3.4 indefinately]
./av2pa.py -a add -i 1.2.3.4 -p '~'

[Remove 1.2.3.4]
./av2pa.py -a remove -i 1.2.3.4

[Exclude 1.2.3.4]
./av2pa.py -a exclude -i 1.2.3.4

### Run Cron

<span>* * * * *</span> python path/to/your/av2pa.py


## Script Settings

##### blocklist 
Set location of the blocklist (e.g '/var/www/block_inbound.txt').  This file should be https accessible if you intend to setup a Palo Alto External Dynamic List
##### log 
Set a log file location (e.g '/var/log/block_inbound')
##### timezone 
Set the local timezone(e.g 'America/Denver')


 
