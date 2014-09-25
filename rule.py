#!/usr/bin/env python

import dbUtils

import private_cloud

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
		# TODO refine this usage
		self.rule = rule

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

			else:
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

		if zero_flag == True:
			#all type are zero
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
		self.rule = rule

	def execute(self):
		if self.action == "add":
			self.add_servers()
		elif self.action == "reduce":
			self.reduce_servers()

	def add_servers(self):
		if self.destination == "OpenStack":
			private_cloud.create_server()
			# TODO add parameters
			
		elif self.destination == "ec2":
			public_cloud.create_server()

		rule_act_complete = dbUtils.update_cooldown_time(self.rule['id'], 1)
		# TODO implement the real cooldown function

	def reduce_servers(self):
		private_cloud.terminate_server()
		rule_act_complete = dbUtils.update_cooldown_time(self.rule['id'], 1)

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
		monitor_data = dbUtils.get_monitor_data_by_group(self.group_id)

		#compare with condition
		result = self.condition.compare_threshold(monitor_data)
		
		fd = open('/tmp/my_daemon_log.dat', 'a')
		fd.write(str(result) +'\n')
		fd.close()

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
