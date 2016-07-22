from dashie_sampler import DashieSampler

import random
import collections

from hippo.config import config
from hippo.lib.inventory import HostInventory

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

class InventoryPoolCountSampler(DashieSampler):
    def name(self):
        return 'inventorypoolcount'

    def __init__(self, *args, **kwargs):
        pass

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
        if len(self.items) > 100:
            self.items.popleft()
        return {'points': list(self.items)}
