#!/usr/bin/env python

import MySQLdb, MySQLdb.cursors

DBHOST = '10.10.82.112'
DBUSER = 'root'
DBPASSWORD = '123456'
DB = 'Auto_Test'

#add db connection decorator
def db_connect_control(sql_execute_func):
	def wrapper(*args):
		#get db connect
		con = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DB, cursorclass=MySQLdb.cursors.DictCursor)
		cursor = con.cursor()

		#perform the exact db action
		sql_execute_func(cursor, *args)

		#close db connect
		cursor.close()
		con.close()
		return cursor
		# UNdecide
	return wrapper

@db_connect_control
def get_all_rules(cursor):
	sql = "select * from autoscale_rules"
	cursor.execute(sql)
	rules = cursor.fetchall()
	return rules


'''
def get_all_rules():
	"""
	get all autoscale rules
	"""
	con = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DB, cursorclass=MySQLdb.cursors.DictCursor)
	# TODO db may need to change
	cursor = con.cursor()
	sql = "select * from autoscale_rules"
	cursor.execute(sql)
	rules = cursor.fetchall()
	cursor.close()
	con.close()
	#return a tuple consists of dict
	return rules
'''

def get_instances_id_by_group(group_id):
	con = MySQLdb.connect(host=DBHOST,user=DBUSER,passwd=DBPASSWORD,db=DB)
	# TODO db need to change

	cursor = con.cursor()
	sql="select uuid from instances where group_id="+str(group_id)+" and vm_state='active'"
	cursor.execute(sql)
	instances_id = cursor.fetchall()
	#type is a tuple, like
	#(('f6dbc8a2-fcae-4eab-aeb1-b797be57b07b',), ('05e195ae-a64f-4c4a-a7d9-1ef8617b0de4',), ('c72fc98c-d034-4174-85a3-3a040ed4e7e3',))
	cursor.close()
	con.close()
	return instances_id


def get_monitor_data(instance_id):
	instance_id = instance_id[0]
	# TODO need to remove this ugly usage
	con = MySQLdb.connect(host=DBHOST,user=DBUSER,passwd=DBPASSWORD,db=DB, cursorclass=MySQLdb.cursors.DictCursor)

	# TODO db need to change
	cursor = con.cursor()
	sql = "select * from vm_instance where instance_id ='"+ instance_id +"' order by timeStamp desc limit 1"
	cursor.execute(sql)
	instance_data = cursor.fetchall()[0]
	cursor.close()
	con.close()
	return instance_data


def get_monitor_data_by_group(group_id):
	#get all instances in the group, a tuple
	instances = get_instances_id_by_group(group_id)

	#get all monitor data, a list made by dict
	monitor_data = map(get_monitor_data,instances)

	inst_nums = len(instances)# instance numbers in group
	group_data = {'mem':0, 'cpu':0, 'disk':0, 'net_in':0, 'net_out':0}

	# TODO change style
	for inst_data in monitor_data:
		group_data['mem'] = group_data['mem'] + inst_data['memUsage']
		group_data['cpu'] = group_data['cpu'] + inst_data['cpuUsage']
		group_data['disk'] = group_data['disk'] + inst_data['diskUsed']
		group_data['net_in'] = group_data['net_in'] + inst_data['networkIncoming']
		group_data['net_out'] = group_data['net_out'] + inst_data['networkOutgoing']
	try:
		group_data = dict(map(lambda (key,val):(key,val/inst_nums), group_data.iteritems()))
	except ZeroDivisionError:
		pass
		#process zero

	return group_data

def update_flag_in_db(rule_id, flag_name, flag):
	con = MySQLdb.connect(host=DBHOST,user=DBUSER,passwd=DBPASSWORD,db=DB)
	cursor = con.cursor()
	sql="update autoscale_rules set %s = %s where id = %s" % (flag_name, flag, rule_id)
	cursor.execute(sql)
	con.commit()
	cursor.close()
	con.close()
	return flag

def update_cooldown_time(rule_id, flag):
	flag_name = 'cooldown_time'
	return update_flag_in_db(rule_id, flag_name, flag)

def update_auto_revert(rule_id,flag):
	flag_name = 'auto_revert'
	return update_flag_in_db(rule_id, flag_name, flag)

def update_ec2_action(rule_id, flag):
	flag_name = 'ec2_action'
	return update_flag_in_db(rule_id, flag_name, flag)

def read_ec2_action(rule_id):
	con = MySQLdb.connect(host=DBHOST,user=DBUSER,passwd=DBPASSWORD,db=DB)
	cursor = con.cursor()
	sql="select ec2_action from autoscale_rules	 where id ="+str(rule_id)
	cursor.execute(sql)
	ec2_action = cursor.fetchall()
	#type is a tuple, like
	#(('f6dbc8a2-fcae-4eab-aeb1-b797be57b07b',), ('05e195ae-a64f-4c4a-a7d9-1ef8617b0de4',), ('c72fc98c-d034-4174-85a3-3a040ed4e7e3',))
	cursor.close()
	con.close()
	return ec2_action

def get_last_instance_id(group_id):
	con = MySQLdb.connect(host=DBHOST,user=DBUSER,passwd=DBPASSWORD,db=DB)
	cursor = con.cursor()
	sql = "select uuid from instances where group_id ='"+ str(group_id) +"' order by created_at desc limit 1"
	cursor.execute(sql)
	instance_id = cursor.fetchall()
	cursor.close()
	con.close()
	return instance_id[0][0]