#!/usr/bin/env python
import os,time

import novaclient.v1_1.client as nvclient


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
    return ds

def create_server():
    creds = get_nova_creds()
    nova = nvclient.Client(**creds)

    image = nova.images.find(name = "cirros-0.3.2-x86_64")
    flavor = nova.flavors.find(name = "m1.tiny")

    instance = nova.servers.create(name = "bryant", image = image, flavor = flavor)