import logging

from example_samplers import *
from samplers.inventory_sampler import (
    InventoryRoleSampler,
    InventoryCountSampler,
    InventoryUnhealthyCountSampler,
)


logger = logging.getLogger(__name__)


def run(app, events_manager):
    samplers = [
        InventoryCountSampler(events_manager, 60),
        InventoryRoleSampler(events_manager, 30),
        InventoryUnhealthyCountSampler(events_manager, 30),
    ]

    try:
        app.run(debug=True,
                port=5000,
                threaded=True,
                use_reloader=False,
                use_debugger=True
                )
    finally:
        logger.info("Disconnecting clients")
        events_manager.stopped = True

        logger.info("Stopping %d timers" % len(samplers))
        for (i, sampler) in enumerate(samplers):
            sampler.stop()

    logger.info("Done")

if __name__ == '__main__':
    run()
