#!/usr/bin/env python

import time
import log

import utils
import dbUtils
import private_cloud
import public_cloud

LOG = log.get_logger()

def execute(min_num):
    check_all_nodes(min_num)

def check_all_nodes(min_num):
    hosts = utils.get_config('hosts', 'hosts')
    for host in hosts:
        if private_cloud.count_instances_num_on_host(host) >= min_num:
            LOG.info('Host %s running in normal status' % host)
            continue
        else:
            LOG.info('Host %s is goning to energy saving mode' % host)
            energy_saving(host)
            LOG.info('Host %s have been successfully live-migrated and shutdown')

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


