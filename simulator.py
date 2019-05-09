

#import importlib

#from configLoader import cfgFile
#config = importlib.import_module(cfgFile)


def simulate_household(value):

    hnum=value[0]
    household=value[1]

    household.simulate()
    household.scaleProfile()
    household.reactivePowerProfile()
    household.thermalGainProfile()

    print("Simulated household "+str(hnum))
    return (hnum, household)
	

    