#!/usr/bin/env python

import time
import log

import utils
import dbUtils
import private_cloud
import public_cloud

LOG = log.get_logger()

DONNOT_DOWN_HOSTS = ["compute1","compute2","compute3"]
CAN_MIGRATE_HOSTS = ["compute1","compute2","compute3","compute5"]

def execute(rule):
    hosts = ["compute1","compute2","compute3","compute5"] # compute4
    # hosts = ["compute9","compute8","compute7","compute6","compute5","compute4","compute3","compute2","compute1"]
    if rule.action == 'off':
        hosts = hosts[::-1]

    for host in hosts:
        if host_meet_threshold(host, rule):
            LOG.info('Result is True, execute action for Host %s' % host)
            energy_action(host,rule.action)
        else:
            LOG.info('Host %s running in normal status' % host)
            continue


def host_meet_threshold(host, rule):

    metric = rule.type
    threshold = rule.threshold
    action = rule.action

    result = False

    #host_num
    host_num = len(dbUtils.get_all_up_hosts())
    host_info = dbUtils.get_host_data_by_host_name(host)
    host_state = host_info['state']
    host_mem = host_info['memorySize']
    host_cpu = host_info['CPU']
    host_disk = host_info['diskSize']

    if action == 'off' and host_num <= int(utils.get_config('hosts', 'MIN_NUM')):
        return False

    if action == 'on' and host_state == 'down' and host_num < int(utils.get_config('hosts', 'MAX_NUM')):
        return True # then up this host

    # in case of error
    if action == 'on':
        return False

    # following is to process the 'off' logic
    instances_num = len(dbUtils.get_instance_id_by_host_from_nova_db(host))

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
    LOG.info('Host %s real_load is %s' % (host, str(real_load)))
    LOG.info('Threshold is %s' % threshold)
    return real_load < threshold

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
        LOG.info('All instances have been live-migrated from Host %s' % host)
        while len(dbUtils.get_instance_id_by_host_from_nova_db(host)) != 0:
            time.sleep(5)
    else:
        LOG.info('Host cannot do live-migration, go directly shutdown %s' % host)

    # shutdown node
    if 'True' == utils.get_config('mode', 'testing'):
        LOG.info('Now begin to shutdown node')
    else:
        import node_manager
        demo=node_manager.computeNode(host)
        demo.stop()
        LOG.info('Host %s has been successfully shutdown' % host)

def energy_adding(host):
    if 'True' == utils.get_config('mode', 'testing'):
        LOG.info('Now begin to start node')
    else:
        import node_manager
        demo=node_manager.computeNode(host)
        demo.start()
