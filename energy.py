#!/usr/bin/env python

import time
import log

import utils
import dbUtils
import private_cloud
import public_cloud

LOG = log.get_logger()

def execute(rule):
    check_all_nodes(rule)

def check_all_nodes(rule):
    #hosts = utils.get_config('hosts', 'hosts')
    hosts = ["compute1","compute3","compute5"]
    for host in hosts:
        if host_meet_threshold(host, rule):
            LOG.info('Host %s running in normal status' % host)
            continue
        else:
            LOG.info('Host %s is goning to energy saving mode' % host)
            energy_saving(host)
            LOG.info('Host %s have been successfully live-migrated and shutdown')

def host_meet_threshold(host, rule):
    metrics = ['mem', 'cpu', 'disk']
    zero_flag = True
    result = False

    #host_num
    host_num = len(dbUtils.get_all_hosts())
    host_info = dbUtils.get_host_data_by_host_name(host)
    host_mem = host_info['memorySize']
    host_cpu = host_info['CPU']
    host_disk = host_info['diskSize']

    # if hosts number <= MIN_NUM, return false, do nothing
    if host_num <= int(utils.get_config('hosts', 'MIN_NUM')):
        return False

    for metric in metrics:
        metric_type = metric + '_type'
        metric_threshold = metric + '_threshold'

        if self.rule[metric_type] == 0:
            continue

        zero_flag == False

        instances_num = private_cloud.count_instances_num_on_host(host)

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

        real_load = instances_num * factor / host_total

        if real_load < rule[metric_threshold]:
            return True
        else:
            continue

    # all type are zero
    if zero_flag == True:
        result = False

    return result

def energy_saving(host):
    private_cloud.live_migrate_for_host(host)
    import node_manager
    demo=node_manage.computeNode(host)
    try:
        if sys.argv[1]=='start':
            demo.start()
        elif sys.argv[1]=='stop':
            demo.stop()
        else:
            raise StopIteration
    except:
        print 'Undefined Operation!'


