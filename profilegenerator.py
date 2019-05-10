#!/usr/bin/python3

	#Artifical load profile generator v1.2, generation of artificial load profiles to benchmark demand side management approaches
    #Copyright (C) 2018 Gerwin Hoogsteen

    #This program is free software: you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation, either version 3 of the License, or
    #(at your option) any later version.

    #This program is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with this program.  If not, see <http://www.gnu.org/licenses/>.



if __name__ == "__main__":
		
	import os
	import sys
	import getopt

	print("Profilegenerator 1.3.1\n")
	print("Copyright (C) 2019 Gerwin Hoogsteen")
	print("This program comes with ABSOLUTELY NO WARRANTY.")
	print("This is free software, and you are welcome to redistribute it under certain conditions.")
	print("See the acompanying license for more information.\n")

	if(len(sys.argv) > 1):
		#Get arguments:
		try:
			opts, args = getopt.getopt(sys.argv[1:],"c:o:f",["config=","output=", "force"])
		except getopt.GetoptError:
			print("Usage:")
			print('profilegenerator.py -c <config> [-o <output subfolder> -f]')
			sys.exit(2)

		# Default write into a new folder
		cfgOutputDir = 'output/output/'
		forceDeletion = False

		#Parse arguments
		for opt, arg in opts:
			if opt in ("-c", "--config"):
				cfgFile = arg
			elif opt in ("-o", "--output"):
				cfgOutputDir = 'output/'+arg+'/'
			elif opt in ("-f", "--force"):
				forceDeletion = True



		#Check if the output dir exists, otherwise make it
		os.makedirs(os.path.dirname(cfgOutputDir), exist_ok=True)

		if os.listdir(cfgOutputDir):
			# Empty the directory
			if forceDeletion:
				for tf in os.listdir(cfgOutputDir):
					fp = os.path.join(cfgOutputDir, tf)
					try:
						if os.path.isfile(fp):
							os.unlink(fp)
					except Exception as e:
						print(e)
			else:
				print("Config directory is not empty! Provide the --force flag to delete the contents")
				exit()

	else:
		print("Usage:")
		print('profilegenerator.py -c <config> [-o <output subfolder> -f]')
		exit()


	import random
	import importlib
	import profilegentools
	import neighbourhood
	import worker as worker
	from multiprocessing import Pool, cpu_count
	from configLoader import cfgFile
	
	config = importlib.import_module(cfgFile)

	# Randomize using the seed
	random.seed(config.seed)

	# Generate the households
	householdList = config.get_households()

	print('Loading config: '+cfgFile)
	print("The current config will create and simulate "+str(len(householdList))+" households")
	print("Results will be written into: "+cfgOutputDir+"\n")
	print("NOTE: Simulation may take a (long) while...\n")

	# Check the config:
	if config.penetrationEV + config.penetrationPHEV > 100:
		print("Error, the combined penetration of EV and PHEV exceed 100!")
		exit()
	if config.penetrationPV < config.penetrationBattery:
		print("Error, the penetration of PV must be equal or higher than PV!")
		exit()
	if config.penetrationHeatPump + config.penetrationCHP > 100:
		print("Error, the combined penetration of heatpumps and CHPs exceed 100!")
		exit()

	# Create empty files
	config.writer.init_writer()

	# Create neighbourhood
	neighbourhood.neighbourhood(householdList)

	print("Starting household simulation...")

	# Create pool of workers
	number_of_workers = cpu_count() if config.processes is None else config.processes
	p = Pool(number_of_workers, worker.init_worker)

	try:
		for (hnum, household) in p.imap(worker.simulate_household, enumerate(householdList)):
			config.writer.write_household(household, hnum)
			config.writer.write_neighbourhood(hnum)
		
		p.terminate()

	except KeyboardInterrupt:
		p.terminate()
		print("Simulation terminated!")
		sys.exit(1)


	print("Flushing writer.")
	config.writer.flush_writer()

	print("Simulation done.")
