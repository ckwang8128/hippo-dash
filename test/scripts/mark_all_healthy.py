from hippo.config import config
from hippo.lib.host_types import EC2Host
from hippo.lib.inventory import HostInventory

host_inventory = HostInventory(config)
for host_id in host_inventory.get_host_ids():
    host_inventory.reset_unhealthy_count(host_id)
