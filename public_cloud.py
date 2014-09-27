#!/usr/bin/env python

import dbUtils

def create_server(rule_id):
	#loop
	ec2_action = dbUtils.read_ec2_action(rule_id)[0][0]
	while ec2_action != 0:
		ec2_action = dbUtils.read_ec2_action(rule_id)[0][0]

	#execute
	dbUtils.update_ec2_action(rule_id, 1)

def delete_server(rule_id):

	#loop
	ec2_action = dbUtils.read_ec2_action(rule_id)[0][0]
	while ec2_action != 0:
		ec2_action = dbUtils.read_ec2_action(rule_id)[0][0]

	#execute
	dbUtils.update_ec2_action(rule_id, 1)