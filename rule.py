#!/usr/bin/env python

import time

import dbUtils
import private_cloud, public_cloud



class Rule(object):
	"""
	consist of condition and action
	"""
	def __init__(self, rule):
		#in case that policies will become more complicated , i devided condition and action into seperate class
		#self.id = rule['id']
		self.rule = rule
		# TODO need to remove this ugly usage
		self.instance_num = self.rule['cooldown_time']

	#condition functions
	def check_if_monitor_meet_condition(self):

		#get monitor data as a dict
		monitor_data = dbUtils.get_monitor_data_by_group(self.rule['group_id'])

		#compare with condition
		result = self.compare_threshold(monitor_data)
		
		fd = open('/tmp/my_daemon_log.dat', 'a')
		fd.write(str(result)+' [rusult] \n')
		fd.close()

		#return
		return result

	def compare_threshold(self, monitor_data):
		# TODO be sure that type don't be 0 for all
		metrics = ['mem', 'disk', 'cpu', 'net_in', 'net_out']
		zero_flag = True
		result = True

		for metric in metrics:
			metric_type = metric + '_type'
			metric_threshold = metric + '_threshold'

			if self.rule[metric_type] == 0:
				continue

			#else metric_type != 0
			zero_flag = False

			if (self.rule[metric_type] == 1) and (monitor_data[metric] <= self.rule[metric_threshold]) :
			#data > threshold
				result = False
				break

			elif (self.rule[metric_type] == -1) and (monitor_data[metric] >= self.rule[metric_threshold]) :
			#data < threshold
				result = False
				break

			#metric_type not in [-1,0,1] means wrong rule
			elif self.rule[metric_type] not in [-1,0,1]:
				result = False
				break

		if zero_flag == True:
			#all type are zero
			result = False

		return result

	#action functions

	def execute_action(self):
		if self.rule['action'] == 'add':
			# TODO need to refine 
			if self.instance_num >= self.rule['max_num'] :
				self.rule['destination'] = 'ec2'

			self.add_servers()

		elif self.rule['action'] == 'reduce':
			if self.instance_num > self.rule['max_num']:
				self.rule['destination'] = 'ec2'

			self.reduce_servers()

	def execute_revert_action(self):
		if self.rule['action'] == 'add':
			self.rule['action'] = 'reduce'
			
		elif self.rule['action'] == 'reduce':
			self.rule['action'] = 'add'
		self.execute_action()

	def add_servers(self):
		if self.rule['destination'] == "OpenStack":
			private_cloud.create_server()
			# TODO add parameters
			fd = open('/tmp/my_daemon_log.dat', 'a')
			now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
			fd.write(str(now)+' [launch] a private instance\n')
			fd.close()
			
		elif self.rule['destination'] == "ec2":
			
			#public_cloud.create_server()
			#use for fake
			public_cloud.create_server(self.rule['id'])

			fd = open('/tmp/my_daemon_log.dat', 'a')
			now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
			fd.write(str(now)+' [launch] a public instance\n')
			fd.close()

		#so ugly! use cooldown_time as instance numbers
		# TODO implement the real cooldown function
		self.instance_num += 1

		total_add_num = dbUtils.update_cooldown_time(self.rule['id'], self.instance_num)

	def reduce_servers(self):
		if self.rule['destination'] == "OpenStack":
			private_cloud.delete_server(self.rule['group_id'])
			# TODO add parameters

			fd = open('/tmp/my_daemon_log.dat', 'a')
			now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
			fd.write(str(now)+' [terminate] a private instance\n')
			fd.close()
			
		elif self.rule['destination'] == "ec2":
			public_cloud.delete_server(self.rule['id'])

			fd = open('/tmp/my_daemon_log.dat', 'a')
			now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
			fd.write(str(now)+' [launch] a public instance\n')
			fd.close()

		self.instance_num -= 1

		total_add_num = dbUtils.update_cooldown_time(self.rule['id'], self.instance_num)







def check_all_rules():
	#get all rules
	db_rules = dbUtils.get_all_rules()

	#loop and check every rule
	for db_rule in db_rules:
		#init a rule
		rule = Rule(db_rule)
		
		#get condition of a rule and analyse it
		if rule.check_if_monitor_meet_condition():
			rule.execute_action()
		elif ( rule.instance_num != 0 ) and ( rule.rule['auto_revert'] == 1 ):
			#an experiment func:auto revert
			rule.execute_revert_action()
		else:
			continue
