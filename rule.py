#!/usr/bin/env python

import dbUtils

class Condition(object):
	"""
	refers to the conditional data of a rule
	"""
	def __init__(self, rule):
		#threshold: 0 means doesn't exist
		#1 means >
		#-1 means <
		self.mem_type = rule['mem_type']
		self.mem_threshold = rule['mem_threshold']
		self.disk_type = rule['disk_type']
		self.disk_threshold = rule['disk_threshold']
		self.cpu_type = rule['cpu_type']
		self.cpu_threshold = rule['cpu_threshold']
		self.net_in_type = rule['net_in_type']
		self.net_in_threshold = rule['net_in_threshold']
		self.net_out_type = rule['net_out_type']
		self.net_out_threshold = rule['net_out_threshold']

	def compare_threshold(self, monitor_data):
		# TODO be sure that type don't be 0 for all
		metrics = ['mem', 'disk', 'cpu', 'net_in', 'net_out']
		zero_flag = True
		result = True

		for metric in metrics:
			metric_type = metric + '_type'
			metric_threshold = metric + '_threshold'

			if self.metric_type != 0:
				zero_flag = False

			if self.metric_type == 1:
				#data > threshold
				if monitor_data[metric] <= self.metric_threshold:
					result = False
					break

			elif self.metric_type == -1:
				#data < threshold
				if monitor_data[metric] >= self.metric_threshold:
					result = False
					break
			else:
				result = False

		if zero_flag == True:
			result = False

		return result






class Action(object):
	"""
	actions to be performed
	"""
	def __init__(self, rule):
		self.action = rule['action']
		self.destination = rule['destination']
		self.num = rule['num']

	def execute(self):
		if self.action == "add":
			self.add_servers()
		elif self.action == "reduce":
			self.reduce_servers()

	def add_servers(self):
		if self.destination == "OpenStack":
			private_cloud.create_servers()
			# TODO add parameters
			
		elif self.destination == "ec2":
			public_cloud.create_servers()

		dbUtils.update_cooldown_time(self.id, 1)
		# TODO implement the real cooldown function

	def reduce_servers(self):
		private_cloud.terminate_servers()
		dbUtils.update_cooldown_time(self.id, 1)

class Rule(object):
	"""
	consist of a condition and an action
	"""
	def __init__(self, rule):
		#in case that policies will become more complicated , i devided condition and action into seperate class
		self.id = rule['id']
		self.group_id = rule['group_id']
		self.cooldown_time = rule['cooldown_time']
		# TODO need to complete this function
		self.condition = Condition(rule)
		self.action = Action(rule)

	def check_if_monitor_meet_condition(self):
		#cooldown time
		if self.cooldown_time != 0:
			return False
		#get monitor data as a dict
		monitor_data = get_monitor_data_by_group(self.group_id)

		#compare with condition
		result = self.condition.compareThreshold(monitor_data)

		#return
		return result

	def execute_action(self):
		self.action.execute()

	def get_monitor_data_by_group(self):
		return dbUtils.get_monitor_data_by_group(self.group_id)



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