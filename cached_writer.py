
	#Artifical load profile generator v1.3, generation of artificial load profiles to benchmark demand side management approaches
    #Copyright (C) 2019 Martin Schmidt

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



import os
import profilegentools
import pandas as pd

from configLoader import OUTPUTFOLDER



class CachedWriter:

	def __init__(self):
		self.dataframes = {}
		pass

	def _add_list_to_dataframe(self, dataframe, num, data_list):
		if dataframe in self.dataframes:
			df = self.dataframes[dataframe]
			df[str(num)] = data_list
		else:
			df = pd.DataFrame(data_list, columns=[str(num)])
			self.dataframes[dataframe] = df
			

	def _append_line_to_file(self, fname, hnum, line):
		if not os.path.exists(OUTPUTFOLDER+'/'+fname): 
			#overwrite
			f = open(OUTPUTFOLDER+'/'+fname, 'w')
		else:
			#append
			f = open(OUTPUTFOLDER+'/'+fname, 'a')
		f.write(line + '\n')
		f.close()

	def init_writer(self):
		os.makedirs(OUTPUTFOLDER, exist_ok=True)

	def flush_writer(self):
		for fname, df in self.dataframes.items():
			df.to_csv(OUTPUTFOLDER+'/'+fname, index=False)
		

	def write_neighbourhood(self, num):
		pass

	def write_household(self, house, num):

		self._add_list_to_dataframe('Electricity_Profile.csv', num, house.Consumption['Total'])
		self._add_list_to_dataframe('Electricity_Profile_GroupOther.csv', num, house.Consumption['Other'])
		self._add_list_to_dataframe('Electricity_Profile_GroupInductive.csv', num, house.Consumption['Inductive'])
		self._add_list_to_dataframe('Electricity_Profile_GroupFridges.csv', num, house.Consumption['Fridges'])
		self._add_list_to_dataframe('Electricity_Profile_GroupElectronics.csv', num, house.Consumption['Electronics'])
		self._add_list_to_dataframe('Electricity_Profile_GroupLighting.csv', num, house.Consumption['Lighting'])
		self._add_list_to_dataframe('Electricity_Profile_GroupStandby.csv', num, house.Consumption['Standby'])
		
		self._add_list_to_dataframe('Reactive_Electricity_Profile.csv', num, house.ReactiveConsumption['Total'])
		self._add_list_to_dataframe('Reactive_Electricity_Profile_GroupOther.csv', num, house.ReactiveConsumption['Other'])
		self._add_list_to_dataframe('Reactive_Electricity_Profile_GroupInductive.csv', num, house.ReactiveConsumption['Inductive'])
		self._add_list_to_dataframe('Reactive_Electricity_Profile_GroupFridges.csv', num, house.ReactiveConsumption['Fridges'])
		self._add_list_to_dataframe('Reactive_Electricity_Profile_GroupElectronics.csv', num, house.ReactiveConsumption['Electronics'])
		self._add_list_to_dataframe('Reactive_Electricity_Profile_GroupLighting.csv', num, house.ReactiveConsumption['Lighting'])
		self._add_list_to_dataframe('Reactive_Electricity_Profile_GroupStandby.csv', num, house.ReactiveConsumption['Standby'])

		# Save HeatGain profiles
		self._add_list_to_dataframe('Heatgain_Profile.csv', num, house.HeatGain['Total'])
		self._add_list_to_dataframe('Heatgain_Profile_Persons.csv', num, house.HeatGain['PersonGain'])
		self._add_list_to_dataframe('Heatgain_Profile_Devices.csv', num, house.HeatGain['DeviceGain'])

		# Safe TapWater profiles
		self._add_list_to_dataframe('Heatdemand_Profile.csv', num, house.HeatDemand['Total'])
		self._add_list_to_dataframe('Heatdemand_Profile_DHWTap.csv', num, house.HeatDemand['DHWDemand'])

		# Airflow, kind of hacky
		self._add_list_to_dataframe('Airflow_Profile_Ventilation.csv', num, house.HeatGain['VentFlow'])

		# self.add_list_to_dataframe('Heatgain_Profile_Solar.csv', num, house.HeatGain['SolarGain'])

		# FIXME Add DHW Profile

		#Write all devices:
		for k, v, in house.Devices.items():
			house.Devices[k].writeDevice(num)

		#Write all heatdevices:
		for k, v, in house.HeatingDevices.items():
			house.HeatingDevices[k].writeDevice(num)
		
		#House specific devices	
		if house.House.hasPV:
			text = str(num)+':'
			text += str(house.House.pvElevation)+','+str(house.House.pvAzimuth)+','+str(house.House.pvEfficiency)+','+str(house.House.pvArea)
			self._append_line_to_file('PhotovoltaicSettings.txt', num, text)
			
		self._add_list_to_dataframe('Electricity_Profile_PVProduction.csv', num, house.PVProfile)
			
		if house.House.hasBattery:
			text = str(num)+':'
			text += str(house.House.batteryPower)+','+str(house.House.batteryCapacity)+','+str(round(house.House.batteryCapacity/2))
			self._append_line_to_file('BatterySettings.txt', num, text)

		# Write what type of heating device is used
		if house.hasHP:
			text = str(num)+':HP'			# Heat pump
			self._append_line_to_file('HeatingSettings.txt', num, text)
		elif house.hasCHP:
			text = str(num)+':CHP'			# Combined Heat Power
			self._append_line_to_file('HeatingSettings.txt', num, text)
		else:
			text = str(num)+':CONVENTIONAL'	# Conventional heating device, e.g. natural gas boiler
			self._append_line_to_file('HeatingSettings.txt', num, text)
		
	def write_device_buffer_timeshiftable(self, machine, hnum):
		if machine.BufferCapacity > 0 and len(machine.StartTimes) > 0:
			text = str(hnum)+':'
			text += profilegentools.createStringList(machine.StartTimes, None, 60)
			self._append_line_to_file('ElectricVehicle_Starttimes.txt', hnum, text)
			
			text = str(hnum)+':'
			text += profilegentools.createStringList(machine.EndTimes, None, 60)
			self._append_line_to_file('ElectricVehicle_Endtimes.txt', hnum, text)
				
			text = str(hnum)+':'
			text += profilegentools.createStringList(machine.EnergyLoss, None, 1, False)
			self._append_line_to_file('ElectricVehicle_RequiredCharge.txt', hnum, text)	
				
			text = str(hnum)+':'
			text += str(machine.BufferCapacity)+','+str(machine.Consumption)
			self._append_line_to_file('ElectricVehicle_Specs.txt', hnum, text)
			

	def write_device_timeshiftable(self, machine, hnum):
		if len(machine.StartTimes) > 0:
			text = str(hnum)+':'
			text += profilegentools.createStringList(machine.StartTimes, None, 60)
			self._append_line_to_file(f'{machine.name}_Starttimes.txt', hnum, text)
			
			text = str(hnum)+':'
			text += profilegentools.createStringList(machine.EndTimes, None, 60)
			self._append_line_to_file(f'{machine.name}_Endtimes.txt', hnum, text)
			
			text = str(hnum)+':'
			text += machine.LongProfile
			self._append_line_to_file(f'{machine.name}_Profile.txt', hnum, text)

	def write_device_thermostat(self, machine, hnum):
		text = str(hnum)+':'
		text += profilegentools.createStringList(machine.StartTimes, None, 60)
		self._append_line_to_file('Thermostat_Starttimes.txt', hnum, text)

		text = str(hnum)+':'
		text += profilegentools.createStringList(machine.Setpoints)
		self._append_line_to_file('Thermostat_Setpoints.txt', hnum, text)