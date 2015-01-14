#!/usr/bin/env python

import time
import log

import utils
import dbUtils
import private_cloud
import public_cloud

LOG = log.get_logger()

DONNOT_DOWN_HOSTS = ["compute1","compute2"]
CAN_MIGRATE_HOSTS = ["compute1","compute2","compute3","compute4","compute5"]

def execute(rule):
    hosts = ["compute1","compute2","compute3","compute4","compute5","compute6"] # compute4
    # hosts = ["compute9","compute8","compute7","compute6","compute5","compute4","compute3","compute2","compute1"]

    if rule.action == 'off':
        hosts = hosts[::-1]

    for host in hosts:
        LOG.info('Now checking Host %s ...' % host)
        if host_meet_threshold(host, rule):
		energy_action(host,rule.action)
    dbUtils.logfile_add('Checked! All hosts are in CORRECT status based on RULE %d!' % int(rule.id),'INFO')


def host_meet_threshold(host, rule):

    threshold = rule.threshold
    action = rule.action

    host_info = dbUtils.get_host_data_by_host_name(host)
    host_state = host_info['state']
    host_updatedTime = str(host_info['updated_at'])
    result = False

    #host_num
    host_num = len(dbUtils.get_all_up_hosts())
    

    if action == 'off' and host_state == 'down':
	LOG.info('Host %s off and in normal status!' % host)
        #dbUtils.logfile_add('Host %s off and in normal status!' % host,'INFO')
        return False

    if action == 'off' and host_num <= 2:#int(utils.get_config('hosts', 'MIN_NUM')):
        LOG.info('Has exceeded the minimal number of hosts!')
	LOG.info('Host %s failed to be turn down!' % host)
	dbUtils.logfile_add('Has exceeded the minimal number of hosts!','WARNING')
	return False

    if action == 'on' and host_num >= 6:
	LOG.info('Has exceeded the maximal number of hosts!')
	dbUtils.logfile_add('Has exceeded the maximal number of hosts!','WARNING')
        return False
    if action == 'on':
	if dbUtils.get_host_data_by_host_name(host)['state']=='up':
		return False
	elif int(time.time()-time.mktime(time.strptime(host_updatedTime,'%Y-%m-%d %H:%M:%S')))<=600:  #don't turn on the node which has just been turned down in 10 minutes
		LOG.info('Host %s has just been OFF and remained in protection period!' % host)
		dbUtils.logfile_add('Host %s has just been OFF and remained in protection period!' % host,'WARNING')
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
    LOG.info('Is updated at %s' % host_updatedTime)
    if int(time.time()-time.mktime(time.strptime(host_updatedTime,'%Y-%m-%d %H:%M:%S')))>1800:   #more than half an hour
	if real_load < threshold:
		LOG.info('Result is True, execute action for Host %s' % host)
		return True
	else:
		LOG.info('Host %s running in normal status!' % host)
		#dbUtils.logfile_add('Host %s running and in normal status!' % host,'INFO')
		return False
    else:
	LOG.info('Host %s has just been ON and remained in protection period!' % host)
        dbUtils.logfile_add('Host %s has just been ON and remained in protection period!' % host,'WARNING')
	return False

def on_status_check(host, rule):
    hosts = ["compute1","compute2","compute3","compute4","compute5","compute6"]
    host_info = dbUtils.get_host_data_by_host_name(host)
    host_state = host_info['state']
    
    if host_state == 'up':
        LOG.info('Host %s on and in normal status!' % host)
	#dbUtils.logfile_add('Host %s on and in normal status!' % host,'INFO')
	return False

    min_host = "null"
    min_load = 100

    for ho in hosts:
        load = get_host_real_load(ho, rule.type)
        if load < min_load and dbUtils.get_host_data_by_host_name(ho)['state']=='up':
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
	dbUtils.logfile_add('Host %s has been successfully live-migrated and shutdown' % host,'SUCCESS')
	dbUtils.logfile_add('Host %s was updated at %s' % (host,str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()+28800)))),'NOTICE')
    elif 'on' == action:
        LOG.info('Host %s is goning to up' % host)
       	dbUtils.logfile_add('Host %s was updated at %s' % (host,str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()+28800)))),'NOTICE')
        energy_adding(host)
        LOG.info('Host %s has been successfully up' % host)
	dbUtils.logfile_add('Host %s has been successfully up' % host,'SUCCESS')
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
	dbUtils.logfile_add('All instances have been live-migrated from Host %s' % host,'SUCCESS')
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
