"""Generate fake set of host data."""
import random
import socket
import struct

from hippo.config import config
from hippo.lib.host_types import EC2Host
from hippo.lib.inventory import HostInventory

def random_ip():
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

def make_fake_host():
    rand_host_id = random.randint(0,1000000)
    """
{"private_ip": "10.0.171.62", "public_ip": "54.85.70.14", "launch_time": 1466684269, "tags": [{"Value": "app", "Key": "Role"}, {"Value": "prod", "Key": "Environment"}, {"Value": "loggedout-pool", "Key": "aws:autoscaling:groupName"}, {"Value": "app-257", "Key": "Name"}, {"Value": "r2", "Key": "Component"}, {"Value": "reddit", "Key": "Product"}]},
    """
    role = random.choice(['app', 'cache', 'lb'])
    name = "%s-%d" % (role, random.randint(0,1000))
    rand_host_properties = {
        'private_ip': random_ip(),
        'public_ip': random_ip(),
        'tags': [
            { 'Value': role,
              'Key': 'Role'
            },
            { 'Value': random.choice(['loggedout-pool', 'test-pool', 'main-pool']),
              'Key': 'aws:autoscaling:groupName'
            },
            { 'Value': name,
              'Key': 'Name'
            }
        ]
    }
    host = EC2Host(rand_host_id, rand_host_properties)
    return host

host_inventory = HostInventory(config)

def destroy_host(inventory):
    try:
        host_id = inventory.get_host_ids()[0]
        inventory.remove_host(host_id)
    except:
        pass

def random_health_sweep(inventory):
    for host in inventory.get_all_hosts():
        if random.randint(0,1) == 0:
            print("Marking unhealthy: %s" % host)
            inventory.mark_unhealthy(host.host_id)
        else:
            inventory.reset_unhealthy_count(host.host_id)

choice = random.randint(0,1)
if choice == 0:
    print("Creating")
    for i in range(0,random.randint(1,100)):
        host = make_fake_host()
        host_inventory.add_host(host)
else:
    print("Destroying")
    for i in range(0, random.randint(1,100)):
        destroy_host(host_inventory)

random_health_sweep(host_inventory)
