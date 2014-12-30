#!/usr/bin/env python
import os
import time

import utils
import dbUtils
import log

LOG = log.get_logger()


def get_keystone_creds():
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['password'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['tenant_name'] = os.environ['OS_TENANT_NAME']
    return d


def get_nova_creds():
    d = {}
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = os.environ['OS_TENANT_NAME']
    return d


def create_server():
    # testing environment
    if 'True' == utils.get_config('mode', 'testing'):
        LOG.info('Now launching a private instance')

    # producting environment
    else:
        # TODO diy rest?
        import novaclient.v1_1.client as nvclient
        creds = get_nova_creds()
        nova = nvclient.Client(**creds)

        image = nova.images.find(name="cirros-0.3.2-x86_64")
        flavor = nova.flavors.find(name="m1.tiny")
        nics = [{'net-id': '80963cd2-0f29-433c-bb33-c4e25ad8719b'}]

        instance = nova.servers.create(
            name="bryant", image=image, flavor=flavor, nics=nics)
        LOG.info('Now launched a private instance')

        instance.add_floating_ip(get_floating_ip())
        LOG.info('Now adding floating ip to the private instance')


def delete_server(group_id):
    # testing environment
    if 'True' == utils.get_config('mode', 'testing'):
        LOG.info('Now deleting a private instance')

    # producting environment
    else:
        # get instance_id
        instance_id = dbUtils.get_last_instance_id(group_id)
        creds = get_nova_creds()
        nova = nvclient.Client(**creds)

        nova.servers.delete(instance_id)
        LOG.info('Now deleting the private instance [%s]' % instance_id)


def get_floating_ip():
    creds = get_nova_creds()
    nova = nvclient.Client(**creds)
    ip_lists = nova.floating_ips.list()
    for tmp in ip_lists:
        ip_str = str(tmp)[1:-1].split(',')
        if ip_str[0].find('None') != -1:
            return ip_str[3][4:]

def live_migrate_for_host(host_name):
    # testing environment
    if 'True' == utils.get_config('mode', 'testing'):
        LOG.info('Now begin live migrate')

    # producting environment
    else:
        creds = get_nova_creds()
        nova = nvclient.Client(**creds)
        instance_ids = dbUtils.get_instances_id_by_host(host_name)
        for instance_id in instance_ids:
            nova.servers.live_migrate(instance_id)#maybe don't need host Or add host for the second parameter