
import signal
import random

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def simulate_household(value):

    hnum = value[0]
    household = value[1]

    random.seed(household.seed)

    household.simulate()
    household.scaleProfile()
    household.reactivePowerProfile()
    household.thermalGainProfile()

    print(f"Simulated household {str(hnum)}")
    return (hnum, household)
