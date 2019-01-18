#!/usr/bin/env python

import os
import os.path
import argparse
import json
import time
import syslog
import logging
import logging.handlers
import calendar
from pprint import pprint
from datetime import datetime, timedelta



'''
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
'''

'''
Settings
'''

blocklist = '/var/www/block_inbound.txt'
log = '/var/log/block_inbound'
timezone = 'America/Denver'


class AV2PA:
	verbose = False
	action = ""
	ip = ""
	penalty = ""
	blocklist = ""
	log = ""
	path = ""
	d = {"current":{}, "history":{}, "exclude":{}}
	penalty_d = { '1' : 1, '2' : 5, '3' : 10, '4' : 15, '5' : 30, '6' : 60, '7' : 180, '8' : 360, '9' : 720, '10' : 1440, '11' : 4320, '12' : 10080, '13' : 20160, '14' : 43200, '15' : 525600, '16' : '~'}
	
	def __init__(self, blocklist, log):
		self.blocklist = blocklist
		self.log = log
		self.path = os.path.dirname(os.path.realpath(__file__))
		self.logger = logging.getLogger(__name__)
		self.logger.propagate = False
		self.handler = logging.FileHandler(self.log)
		self.init()

	def init(self):
		self.get_opts()
		if os.path.exists(self.path+'/data.json') == False:
			data = {}
			data["current"] = {}
			data["history"] = {}
			data["exclude"] = {}
			with open(self.path+"data.json", "w") as f:
				self.syslog("info",self.path+"/data.json not found.  Creating file")
				json.dump(data,f,indent=4,sort_keys=True)
		self.process_action()
		self.generate_files()
				
	def pretty(self, d, indent=0):
		for key, value in d.items():
			print('\t' * indent + str(key))
			if isinstance(value, dict):
				if self.verbose:
					self.pretty(value, indent+1)
			else:
				if self.verbose:
					print('\t' * (indent+1) + str(value))
		
	def get_opts(self):
		parser = argparse.ArgumentParser()
		parser.add_argument("-v", "--verbose", help="Show verbose output", action="store_true")
		parser.add_argument("-a", "--action", help="Select the action [add,remove,exclude,clear,cycle] (Defaults to cycle)")
		parser.add_argument("-i", "--ip", help="IP you want to add to block list")
		parser.add_argument("-p", "--penalty", help="Define a time penalty [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,~] for the IP ")
		
		args = parser.parse_args()
		if args.verbose:
			self.verbose = True
		if args.action:
			self.action = args.action
		if args.ip:
			self.ip = args.ip
		if args.penalty:
			self.penalty = args.penalty
				
	def process_action(self):
		try:
			self.action
		except NameError:
			self.syslog("error","Action not defined")
		else:
			if self.action == "add":
				if self.ip:
					self.syslog("info","Calling add_ip("+self.ip+")")
					self.add_ip()
				else:
					self.syslog("error","Cannot call add_ip("+self.ip+"), missing IP")
			elif self.action == "remove":
				if self.ip:
					self.syslog("info","Calling remove_ip("+self.ip+")")
					self.remove_ip()
				else:
					self.syslog("error","Cannot call remove_ip("+self.ip+"), missing IP")
			elif self.action == "exclude":
				if self.ip:
					self.syslog("info","Calling exclude_ip("+self.ip+")")
					self.exclude_ip()
				else:
					self.syslog("error","Cannot call exclude_ip("+self.ip+"), missing IP")
			elif self.action == "clear":
				self.syslog("info","Calling clear()")
				self.clear()
			elif self.action == "cycle":
				self.syslog("info","Calling cycle()")
				self.cycle()
			else:
				self.syslog("info","Calling cycle()")
				self.cycle()
				
	def add_ip(self):
		with open(self.path+'/data.json') as f:
			data = json.load(f)
		
		current = data.get("current", "")
		history = data.get("history", "")
		exclude = data.get("exclude", "")
		
		ts = time.time()
		
		for key in list(exclude):
			if self.ip == key:
				self.syslog("info", self.ip +" found in exclude dictionary, exiting")
				self.d["current"] = current
				self.d["history"] = history
				self.d["exclude"] = exclude
				return
		
		if self.ip in history:
			self.syslog("info", self.ip +" found in history dictionary, incrementing penalty")
			if self.penalty:
				history_penalty = self.penalty
			else:
				if history[self.ip]['penalty'] == 15 or history[self.ip]['penalty'] == '~':
					history_penalty = '~'
				else:
					history[self.ip]['penalty'] += 1
					history_penalty = history[self.ip]['penalty']
			
			history[self.ip]['penalty'] = history_penalty
			history[self.ip]['last_seen'] = ts
		else:
			self.syslog("info", self.ip +" not found in history dictionary, creating entry")
			history_penalty = 1
			data = {'penalty':1,'last_seen':ts}
			history.update({self.ip:data})
		
		if self.ip in current:
			self.syslog("info", self.ip +" found in current dictionary, incrementing penalty")
			current[self.ip]['penalty'] = history_penalty
			current[self.ip]['last_seen'] = ts
		else:
			self.syslog("info", self.ip +" not found in current dictionary, creating entry based off history")
			data = {'penalty':history_penalty,'last_seen':ts}
			current.update({self.ip:data})
			
		self.d["current"] = current
		self.d["history"] = history
		self.d["exclude"] = exclude
		
	
	def remove_ip(self):
		with open(self.path+'/data.json') as f:
			self.d = json.load(f)
			
		for key in list(self.d["current"]):
			if key == self.ip:
				del self.d["current"][key]
				
		for key in list(self.d["history"]):
			if key == self.ip:
				del self.d["history"][key]
				
	
	def exclude_ip(self):
		with open(self.path+'/data.json') as f:
			data = json.load(f)

		exclude = data.get("exclude", "")
		
		if self.ip in exclude:
			self.syslog("info", self.ip +" found in exclude dictionary, exiting")
		else:
			self.syslog("info", self.ip +" not found in exclude dictionary, creating entry")
			data = {}
			exclude.update({self.ip:data})
			self.remove_ip()
		
		self.d["exclude"] = exclude

	
	def cycle(self):
		ts = time.time()
		with open(self.path+'/data.json') as f:
			self.d = json.load(f)
			
		if "current" in self.d:
			for key in list(self.d["current"]):
				if self.d["current"][key]["penalty"] == "~":
					continue
				self.syslog("info", "Cycling " + key)
				cur_penalty = str(self.d["current"][key]["penalty"])
				cur_penalty_mins = self.penalty_d[cur_penalty]
				
				self.syslog("info", "Current Penalty = "+str(cur_penalty))
				self.syslog("info", "Current Penalty Mins = "+str(cur_penalty_mins))
				
				date = self.aslocaltimestr(datetime.utcfromtimestamp(self.d["current"][key]["last_seen"]))
				self.syslog("info", key + " last seen at " + date + " and has a penalty of " + str(cur_penalty_mins) + " minutes")
				
				elapsed = (ts - self.d["current"][key]["last_seen"]) / 60
				self.syslog("info", "Elapsed = "+str(elapsed))

				if elapsed >= cur_penalty_mins:
					self.syslog("info", "Removing " + key + " due to " + str(elapsed) + " elapsed minutes")
					del self.d["current"][key]
				else:
					remaining = cur_penalty_mins - elapsed
					self.syslog("info", key + " has " + str(remaining) + " minutes remaining")
		print "Current"
		pprint(self.d["current"])
		print "History"
		pprint(self.d["history"])
		print "Exclude"
		pprint(self.d["exclude"])
		
	def clear(self):
		with open(self.path+'/data.json') as f:
			self.d = json.load(f)
			
		self.d["current"] = {}	
		self.d["history"] = {}
		self.d["exclude"] = {}
		
		
	def generate_files(self):
		self.syslog("info", "Writing dictionary to "+self.path+"/data.json")
		with open(self.path+'/data.json', 'w') as fp:
			json.dump(self.d, fp)
		self.syslog("info", "Writing current dictionary to '"+self.blocklist+"'")
		with open(self.blocklist, "w") as f:
			for key in self.d['current']:
				print >>f, key
	
	def syslog(self, type, msg):	
		if type == 'info':
			self.logger.setLevel(logging.INFO)
			self.handler.setLevel(logging.INFO)
		elif type == 'error':
			self.logger.setLevel(logging.ERROR)
			self.handler.setLevel(logging.ERROR)
		else:
			self.logger.setLevel(logging.INFO)
			self.handler.setLevel(logging.INFO)
		
		if self.verbose:
			print "Verbose: " + msg
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		self.handler.setFormatter(formatter)
		self.logger.addHandler(self.handler)
		self.logger.info(msg)
	
	
	def utc_to_local(self, utc_dt):
		# get integer timestamp to avoid precision lost
		timestamp = calendar.timegm(utc_dt.timetuple())
		local_dt = datetime.fromtimestamp(timestamp)
		assert utc_dt.resolution >= timedelta(microseconds=1)
		return local_dt.replace(microsecond=utc_dt.microsecond)
		
	
	def aslocaltimestr(self, utc_dt):
		return self.utc_to_local(utc_dt).strftime('%Y-%m-%d %H:%M:%S.%f %Z%z')
	
if __name__ == '__main__':
	AV2PA(blocklist, log)