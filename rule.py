#!/usr/bin/env python

import dbUtils

import private_cloud



class Rule(object):
	"""
	consist of condition and action
	"""
	def __init__(self, rule):
		#in case that policies will become more complicated , i devided condition and action into seperate class
		#self.id = rule['id']
		self.rule = rule

	#condition functions
	def check_if_monitor_meet_condition(self):
		#cooldown time
		if self.rule['cooldown_time'] != 0:
			return False
		#get monitor data as a dict
		monitor_data = dbUtils.get_monitor_data_by_group(self.rule['group_id'])

		#compare with condition
		result = self.compare_threshold(monitor_data)
		
		fd = open('/tmp/my_daemon_log.dat', 'a')
		fd.write(str(result) +'\n')
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

			#metric not in [-1,0,1] means wrong rule
			elif self.rule[metric_type] not in [-1,0,1]:
				result = False
				break

		if zero_flag == True:
			#all type are zero
			result = False

		return result

	#action functions

	def execute(self):
		if self.rule['action'] == "add":
			self.add_servers()
		elif self.rule['action'] == "reduce":
			self.reduce_servers()

	def add_servers(self):
		if self.rule['destination'] == "OpenStack":
			private_cloud.create_server()
			# TODO add parameters
			
		elif self.rule['destination'] == "ec2":
			public_cloud.create_server()

		rule_act_complete = dbUtils.update_cooldown_time(self.rule['id'], 1)
		# TODO implement the real cooldown function

	def reduce_servers(self):
		private_cloud.terminate_server()
		rule_act_complete = dbUtils.update_cooldown_time(self.rule['id'], 1)

	def execute_action(self):
		self.execute()

	def get_monitor_data_by_group(self):
		return dbUtils.get_monitor_data_by_group(self.rule['group_id'])



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
		else:
			continue
