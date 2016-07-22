from example_samplers import *
from samplers.inventory_sampler import InventoryRoleSampler, InventoryCountSampler

def run(app, xyzzy):
    samplers = [
        InventoryCountSampler(xyzzy, 5),
        InventoryRoleSampler(xyzzy, 4),
        SynergySampler(xyzzy, 3),
        ConvergenceSampler(xyzzy, 1),
    ]

    try:
        app.run(debug=True,
                port=5000,
                threaded=True,
                use_reloader=False,
                use_debugger=True
                )
    finally:
        print("Disconnecting clients")
        xyzzy.stopped = True
        
        print("Stopping %d timers" % len(samplers))
        for (i, sampler) in enumerate(samplers):
            sampler.stop()

    print("Done")

if __name__ == '__main__':
    run()
