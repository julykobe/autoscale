#!/usr/bin/env python

import time

import utils
import dbUtils
import private_cloud
import public_cloud
import energy

import log

LOG = log.get_logger()


class Rule(object):

    """
    consist of condition and action
    """

    def __init__(self, rule):
        self.id = rule['id']
        self.type = rule['type']
        self.threshold = rule['threshold']
        self.action = rule['action']
        self.rule = rule

    # condition functions
    def check_if_monitor_meet_condition(self):
        # get monitor data as a dict
        monitor_data = dbUtils.get_monitor_data_by_group(self.group_id)

        # compare with condition
        result = self.compare_threshold(monitor_data)
        LOG.info('The result of comparation with threshold is %s' % result)

        # return
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

            # else metric_type != 0
            zero_flag = False

            #data > threshold
            if (self.rule[metric_type] == 1) and (monitor_data[metric] <= self.rule[metric_threshold]):
                result = False
                break

            #data < threshold
            elif (self.rule[metric_type] == -1) and (monitor_data[metric] >= self.rule[metric_threshold]):
                result = False
                break

            # metric_type not in [-1,0,1] means wrong rule
            elif self.rule[metric_type] not in [-1, 0, 1]:
                result = False
                break

        # all type are zero
        if zero_flag == True:
            result = False

        return result

    # action functions

    def execute_action(self):
        if self.action == 'add':
            # TODO need to refine
            if self.instance_add_num >= self.max_num:
                self.destination = 'ec2'

            self.add_servers()

        elif self.action == 'reduce':
            if self.instance_add_num > self.max_num:
                self.destination = 'ec2'

            self.reduce_servers()

    def execute_revert_action(self):
        if self.action == 'add':
            self.action = 'reduce'

        elif self.action == 'reduce':
            self.action = 'add'

        self.execute_action()

    def add_servers(self):
        if self.destination == "OpenStack":
            private_cloud.create_server()
            # TODO add parameters
            LOG.info('A private instance has been launched')

        elif self.destination == "ec2":
            # public_cloud.create_server()
            # use for fake
            public_cloud.create_server(self.rule['id'])
            LOG.info('A public instance has been launched')

        # so ugly! use cooldown_time as instance numbers
        # TODO implement the real cooldown function
        self.instance_add_num += 1

        total_add_num = dbUtils.update_instance_add_num(
            self.id, self.instance_add_num)

    def reduce_servers(self):
        if self.destination == "OpenStack":
            private_cloud.delete_server(self.group_id)
            # TODO add parameters

            LOG.info('A private instance has been terminated')

        elif self.destination == "ec2":
            public_cloud.delete_server(self.id)

            LOG.info('A public instance has been launched')

        self.instance_add_num -= 1

        total_add_num = dbUtils.update_instance_add_num(
            self.id, self.instance_add_num)


def check_all_rules():
    # get all rules
    db_rules = dbUtils.get_all_rules()

    # loop and check every rule
    for db_rule in db_rules:
        try:
            # init a rule
            rule = Rule(db_rule)
        except:
            LOG.error('Connot initialize the rule: %s' % db_rule['id'])
        LOG.info('Checking the rule: %s' % rule.id)

        # get condition of a rule and analyse it
        if rule.check_if_monitor_meet_condition():

            LOG.info('Going to execute the %s action of the rule' %
                     rule.action)
            rule.execute_action()
            LOG.info('The rule %s has been executed' % rule.id)

        elif (rule.instance_add_num != 0) and (rule.auto_revert == 1):
            # an experiment func:auto revert
            rule.execute_revert_action()
        else:
            continue

def check_energy_rules():
    db_rules = dbUtils.get_energy_rules()

    for db_rule in db_rules:
        try:
            rule = Rule(db_rule)
        except:
            LOG.error('Connot initialize the rule: %s' % db_rule['id'])

        LOG.info('Checking the rule: %s' % rule.id)
        energy.execute(rule)
        LOG.info('The rule %s has been checked' % rule.id)