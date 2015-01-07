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
    hosts = utils.get_config('hosts', 'hosts')
    for host in hosts:
        if host_meet_threshold(host, rule):
            LOG.info('Host %s running in normal status' % host)
            continue
        else:
            LOG.info('Host %s is goning to energy saving mode' % host)
            energy_saving(host)
            LOG.info('Host %s have been successfully live-migrated and shutdown')

def host_meet_threshold(host, rule):
    metrics = ['mem', 'cpu']
    result = True

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
        else # cpu
            factor = 2

        load = instances_num * factor

        if load < rule[metric_threshold]:
            result = True
        else
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


