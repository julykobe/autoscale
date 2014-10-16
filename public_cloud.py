#!/usr/bin/env python

import utils
import dbUtils
import log

LOG = log.get_logger()

def create_server(rule_id):
    # testing environment
    if 'True' == utils.get_config('mode', 'testing'):
        LOG.info('Now launching a public instance')

    else:
        # loop
        ec2_action = dbUtils.read_ec2_action(rule_id)[0][0]
        while ec2_action != 0:
            ec2_action = dbUtils.read_ec2_action(rule_id)[0][0]

        # execute
        dbUtils.update_ec2_action(rule_id, 1)


def delete_server(rule_id):
    # testing environment
    if 'True' == utils.get_config('mode', 'testing'):
        LOG.info('Now deleting a public instance')

    else:
        # loop
        ec2_action = dbUtils.read_ec2_action(rule_id)[0][0]
        while ec2_action != 0:
            ec2_action = dbUtils.read_ec2_action(rule_id)[0][0]

        # execute
        dbUtils.update_ec2_action(rule_id, 1)
