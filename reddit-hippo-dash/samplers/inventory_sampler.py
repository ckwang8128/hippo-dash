import collections
import logging
import random

from hippo.config import config, get_host_health_thresholds
from hippo.lib.inventory import HostInventory

from dashie_sampler import DashieSampler

logging.basicConfig()
logger = logging.getLogger(__name__)

class InventoryRoleSampler(DashieSampler):
    def __init__(self, *args, **kwargs):
        DashieSampler.__init__(self, *args, **kwargs)
        self.inventory = HostInventory(config)

    def name(self):
        return 'inventoryrole'

    def sample(self):
        hosts = self.inventory.get_hosts(self.inventory.get_host_ids())
        role_dict = collections.defaultdict(int)
        for host in hosts:
            role_dict[host.role()] += 1
        items = [{'label': role_name, 'value': role_count} for role_name, role_count in role_dict.items()]
        return {'items': items}

class InventoryClusterCountSampler(DashieSampler):
    def name(self):
        return 'inventoryclustercount'

    def __init__(self, *args, **kwargs):
        pass

    def sample(self):
        hosts = self.inventory.get_hosts(self.inventory.get_host_ids())
        role_dict = collections.defaultdict(int)
        for host in hosts:
            role_dict[host.cluster()] += 1
        items = [{'label': cluster_name, 'value': cluster_count}
                 for cluster_name, cluster_count in role_dict.items()]
        return {'items': items}


class InventoryCountSampler(DashieSampler):
    def name(self):
        return 'inventorycount'

    def __init__(self, *args, **kwargs):
        self.seedX = 0
        self.items = collections.deque()
        self.inventory = HostInventory(config)
        DashieSampler.__init__(self, *args, **kwargs)

    def sample(self):
        self.items.append({'x': self.seedX,
                           'y': len(self.inventory.get_host_ids())})
        self.seedX += 1
        if len(self.items) > 20:
            self.items.popleft()
        return {'points': list(self.items)}

class InventoryUnhealthyCountSampler(DashieSampler):
    def name(self):
        return 'inventoryhealth'

    def __init__(self, *args, **kwargs):
        DashieSampler.__init__(self, *args, **kwargs)
        self.inventory = HostInventory(config)

    def sample(self):
        hosts = self.inventory.get_unhealthy_hosts(get_host_health_thresholds())
        items = []
        count = 0
        for host in hosts:
            count += 1
            if len(items) < 5:
                items.append({
                    'label': host.host_id,
                    'value': self.inventory.get_health_counts(host.host_id)['unhealthy']
                })
        return {
            'items': items,
            'moreinfo': "Total Count=%d" % count,
        }
