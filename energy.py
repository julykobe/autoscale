#!/usr/bin/env python

import time
import log

import utils
import dbUtils
import private_cloud
import public_cloud

LOG = log.get_logger()

DONNOT_DOWN_HOSTS = ["compute1","compute2"]
CAN_MIGRATE_HOSTS = ["compute1","compute2","compute3","compute5"]

def execute(rule):
    hosts = ["compute1","compute2","compute3","compute5","compute6"] # compute4
    # hosts = ["compute9","compute8","compute7","compute6","compute5","compute4","compute3","compute2","compute1"]

    if rule.action == 'off':
        hosts = hosts[::-1]

    for host in hosts:
        LOG.info('Checking Host %s' % host)
        if host_meet_threshold(host, rule):
            LOG.info('Result is True, execute action for Host %s' % host)
            energy_action(host,rule.action)
        else:
            LOG.info('Host %s running in normal status' % host)


def host_meet_threshold(host, rule):

    threshold = rule.threshold
    action = rule.action

    host_info = dbUtils.get_host_data_by_host_name(host)
    host_state = host_info['state']
    result = False

    #host_num
    host_num = len(dbUtils.get_all_up_hosts())
    

    if action == 'off' and host_state == 'down':
        return False

    if action == 'off' and host_num <= 3:#int(utils.get_config('hosts', 'MIN_NUM')):
        return False

    if action == 'on' and host_num >= 6:
        return False

    if action == 'on':
        return on_status_check(host, rule)

    #if action == 'on' and host_state == 'down' and host_num < 6:#int(utils.get_config('hosts', 'MAX_NUM')):
    #    return True # then up this host

    # in case of error
    if action == 'on':
        return False

    # following is to process the 'off' logic
    real_load = get_host_real_load(host, rule.type)

    LOG.info('Host %s real_load is %s' % (host, str(real_load)))
    LOG.info('Threshold is %s' % threshold)

    return real_load < threshold

def on_status_check(host, rule):
    hosts = ["compute1","compute2","compute3","compute5"] # compute4
    host_info = dbUtils.get_host_data_by_host_name(host)
    host_state = host_info['state']
    
    if host_state == 'up':
        return False

    min_host = "null"
    min_load = 100

    for ho in hosts:
        load = get_host_real_load(ho, rule.type)
        if load < min_load and load > 0:
            min_load = load
            min_host = ho

    if min_load > rule.threshold:
        return True
    return False


def get_host_real_load(host, metric):
    instances_num = len(dbUtils.get_instance_id_by_host_from_nova_db(host))

    host_info = dbUtils.get_host_data_by_host_name(host)
    host_state = host_info['state']
    host_mem = host_info['memorySize']
    host_cpu = host_info['CPU']
    host_disk = host_info['diskSize']

    factor = 1
    if metric == "mem":
        factor = 2
        host_total = host_mem
    elif metric == "cpu":
        factor = 1
        host_total = host_cpu
    else:#disk
        factor = 20
        host_total = host_disk

    real_load = instances_num * factor / host_total * 100
    return real_load

def energy_action(host, action):
    if 'off' == action:
        LOG.info('Host %s is goning to switch energy saving mode' % host)
        energy_saving(host)
        LOG.info('Host %s has been successfully live-migrated and shutdown' % host)
    elif 'on' == action:
        LOG.info('Host %s is goning to up' % host)
        energy_adding(host)
        LOG.info('Host %s has been successfully up' % host)
    else:
        return

def energy_saving(host):
    if host in DONNOT_DOWN_HOSTS:
        LOG.info('Host %s cannot shutdown' % host)
        return

    # live migrate
    if host in CAN_MIGRATE_HOSTS:
        private_cloud.live_migrate_for_host(host)
        while len(dbUtils.get_instance_id_by_host_from_nova_db(host)) != 0:
            time.sleep(5)
            LOG.info('Check whether all of the instances have been migrated')
        LOG.info('All instances have been live-migrated from Host %s' % host)
    else:
        LOG.info('Host cannot do live-migration, go directly shutdown %s' % host)

    # shutdown node
    import node_manage
    demo=node_manage.computeNode(host)
    demo.stop()
    LOG.info('Host %s has been successfully shutdown' % host)

def energy_adding(host):
    import node_manage
    demo=node_manage.computeNode(host)
    demo.start()
