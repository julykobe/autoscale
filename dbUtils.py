#!/usr/bin/env python
import log
import MySQLdb
import MySQLdb.cursors

import utils

DBHOST = utils.get_config('database', 'DBHOST')
DBUSER = utils.get_config('database', 'DBUSER')
DBPASSWORD = utils.get_config('database', 'DBPASSWORD')
DB = utils.get_config('database', 'DB')

LOG = log.get_logger()

# TODO need to move the cursor execute to decorator, and the func provides sql only
def db_connect_control(cursorclass, *args, **kwargs):
    def real_decorator(sql_execute_func):
        def wrapper(*args, **kwargs):
            # get db connect
            con = MySQLdb.connect(
                host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DB)
            if 'dict' == cursorclass:
                cursor = con.cursor(cursorclass=MySQLdb.cursors.DictCursor)
            elif 'tuple' == cursorclass:
                cursor = con.cursor()
            else:
                LOG.error('Undefined cursorclass')
                raise ValueError

            # perform the exact db action
            result = sql_execute_func(cursor, *args, **kwargs)

            # close db connect
            cursor.close()
            con.close()
            return result
        return wrapper
    return real_decorator


@db_connect_control(cursorclass="dict")
def get_all_rules(cursor):
    sql = "select * from autoscale_rules"
    try:
        cursor.execute(sql)
    except:
        LOG.error('Unable to execute sql action: %s' % sql)
    rules = cursor.fetchall()
    return rules

@db_connect_control(cursorclass="dict")
def get_energy_rules(cursor):
    sql = "select * from energy_test"
    try:
        cursor.execute(sql)
    except:
        LOG.error('Unable to execute sql action: %s' % sql)
    rules = cursor.fetchall()
    return rules

@db_connect_control(cursorclass="dict")
def get_all_up_hosts(cursor):
    sql = "select * from hardware where type = 'compute_Node' and state = 'up'"
    try:
        cursor.execute(sql)
    except:
        LOG.error('Unable to execute sql action: %s' % sql)
    hosts = cursor.fetchall()
    return hosts

@db_connect_control(cursorclass="dict")
def get_host_data_by_host_name(cursor, host_name):
    sql = "select * from hardware where hardwareName ='" + host_name + "'"
    try:
        cursor.execute(sql)
    except:
        LOG.error('Unable to execute sql action: %s' % sql)
    host_data = cursor.fetchall()
    return host_data[0]


@db_connect_control(cursorclass="tuple")
def get_instances_id_by_group(cursor, group_id):
    sql = "select uuid from instances where group_id=" + \
        str(group_id) + " and vm_state='active'"
    try:
        cursor.execute(sql)
    except:
        LOG.error('Unable to execute sql action: %s' % sql)
    instances_id = cursor.fetchall()
    # type is a tuple, like
    #(('f6dbc8a2-fcae-4eab-aeb1-b797be57b07b',), ('05e195ae-a64f-4c4a-a7d9-1ef8617b0de4',), ('c72fc98c-d034-4174-85a3-3a040ed4e7e3',))
    return instances_id

@db_connect_control(cursorclass="tuple")
def get_instances_id_by_host(cursor, host_name):
    sql = "select uuid from instances where hostname='" + \
        host_name + "' and vm_state='active'"
    try:
        cursor.execute(sql)
    except:
        LOG.error('Unable to execute sql action: %s' % sql)
    instances_id = cursor.fetchall()
    # type is a tuple, like
    #(('f6dbc8a2-fcae-4eab-aeb1-b797be57b07b',), ('05e195ae-a64f-4c4a-a7d9-1ef8617b0de4',), ('c72fc98c-d034-4174-85a3-3a040ed4e7e3',))
    return instances_id

def get_instance_id_by_host_from_nova_db(host_name):
    con = MySQLdb.connect(
                host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db="nova")
    cursor = con.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    sql = "select uuid from instances where host='" + \
            host_name + "' and vm_state='active'"
    cursor.execute(sql)
    instances_id = cursor.fetchall()
    
    cursor.close()
    con.close()

    return instances_id

@db_connect_control(cursorclass="dict")
def get_monitor_data(cursor, instance_id):
    instance_id = instance_id[0]
    # TODO need to remove this ugly usage

    sql = "select * from vm_instance where instance_id ='" + \
        instance_id + "' order by timeStamp desc limit 1"
    try:
        cursor.execute(sql)
    except:
        LOG.error('Unable to execute sql action: %s' % sql)
    instance_data = cursor.fetchall()[0]
    return instance_data


@db_connect_control(cursorclass="tuple")
def get_last_instance_id(cursor, group_id):
    sql = "select uuid from instances where group_id ='" + \
        str(group_id) + "' order by created_at desc limit 1"
    try:
        cursor.execute(sql)
    except:
        LOG.error('Unable to execute sql action: %s' % sql)
    instance_id = cursor.fetchall()
    return instance_id[0][0]


def get_monitor_data_by_group(group_id):
    # get all instances in the group, a tuple
    instances = get_instances_id_by_group(group_id)

    # get all monitor data, a list made by dict
    monitor_data = map(get_monitor_data, instances)

    # instance numbers in group
    inst_nums = len(instances)
    group_data = {'mem': 0, 'cpu': 0, 'disk': 0, 'net_in': 0, 'net_out': 0}

    # TODO change style
    # because the db of instance monitor is bad
    for inst_data in monitor_data:
        group_data['mem'] = group_data['mem'] + inst_data['memUsage']
        group_data['cpu'] = group_data['cpu'] + inst_data['cpuUsage']
        group_data['disk'] = group_data['disk'] + inst_data['diskUsed']
        group_data['net_in'] = group_data[
            'net_in'] + inst_data['networkIncoming']
        group_data['net_out'] = group_data[
            'net_out'] + inst_data['networkOutgoing']
    try:
        group_data = dict(map(lambda (key, val): (key, val / inst_nums),
                              group_data.iteritems()))

    except ZeroDivisionError:
        LOG.error('There are no instances in group: %s' % group_id)

    return group_data

def update_instance_state_to_migrating(instance_id):
    con = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DB)
    cursor = con.cursor()

    sql = "update instances set vm_state = 'MIGRATING' where uuid = %s" % instance_id
    cursor.execute(sql)
    con.commit()

    cursor.close()
    con.close()
    return instance_id

def get_vm_state_by_instance_id_from_nova_db(instance_id):
    con = MySQLdb.connect(
                host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db="nova")
    cursor = con.cursor()

    sql = "select vm_state from instances where uuid='" + str(instance_id) + "'" 
    cursor.execute(sql)
    vm_state = cursor.fetchall()
    
    cursor.close()
    con.close()

    return vm_state[0][0]

def update_instance_state_to_active(instance_id):
    con = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DB)
    cursor = con.cursor()

    sql = "update instances set vm_state = 'active' where uuid = %s" % instance_id
    cursor.execute(sql)
    con.commit()

    cursor.close()
    con.close()
    return instance_id

def update_flag_in_db(rule_id, flag_name, flag):
    con = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DB)
    cursor = con.cursor()
    sql = "update autoscale_rules set %s = %s where id = %s" % (
        flag_name, flag, rule_id)

    try:
        cursor.execute(sql)
        con.commit()
    except:
        # rollback when commit failed
        con.rollback()
        LOG.error('update autoscale_rules error, rollback')

    cursor.close()
    con.close()
    return flag


def update_instance_add_num(rule_id, flag):
    flag_name = 'instance_add_num'
    return update_flag_in_db(rule_id, flag_name, flag)


def update_auto_revert(rule_id, flag):
    flag_name = 'auto_revert'
    return update_flag_in_db(rule_id, flag_name, flag)

# TODO remove these ugly ec2 db action
def update_ec2_action(rule_id, flag):
    flag_name = 'ec2_action'
    return update_flag_in_db(rule_id, flag_name, flag)


def read_ec2_action(rule_id):
    con = MySQLdb.connect(host=DBHOST, user=DBUSER, passwd=DBPASSWORD, db=DB)
    cursor = con.cursor()
    sql = "select ec2_action from autoscale_rules	 where id =" + str(rule_id)

    try:
        cursor.execute(sql)
        ec2_action = cursor.fetchall()
        # type is a tuple, like
        #(('f6dbc8a2-fcae-4eab-aeb1-b797be57b07b',), ('05e195ae-a64f-4c4a-a7d9-1ef8617b0de4',), ('c72fc98c-d034-4174-85a3-3a040ed4e7e3',))
    except:
        LOG.error('Unable to fetch data')

    cursor.close()
    con.close()
    return ec2_action
