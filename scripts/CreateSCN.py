# This script creates SCN files for BlueSky from queries
# 00:00:00.00>DEFWPT WPTZ0,2.91470132478, -2.91470132478

import pandas as pd
import os
from tkinter import Tk
from geo import qdrdist as dist
from geo import latlondist as dist2
from tkinter.filedialog import askopenfilename

# Constants
nm  = 1852.  # m       1 nautical mile

Tk().withdraw()
print("Choose the csv file:")
# FileName = askopenfilename()
FileName = 'C:\Documents\BlueSky\scenario\experimental\\Flight_1.csv'

scenario = pd.read_csv(FileName)
banana = list()
aircraftid = 'KLM1705'
actype  =  ', A320, '
[heading, distance] = dist(scenario['st_x(gpt.coords)'][0], scenario['st_y(gpt.coords)'][0],
                            scenario['st_x(gpt.coords)'][1], scenario['st_y(gpt.coords)'][1])
speed = '250'

# banana.append('>SPD KLM1705 250')
# banana.append('>ALT KLM1705 300')
# banana.append('>KLM1705 ORIG EHAM 00:00:00.00')
j = 0

for i in range(scenario.shape[0]):
    if i != 0:
        j = -1
    apple = scenario.time_over[i+j]
    apple = apple[-8:]
    FlightLevel = str(scenario['fl'][i])
    if FlightLevel.count('') < 3:
        FlightLevel = '0' + FlightLevel
    FlightLevel = 'FL' + FlightLevel

    if i == 0:
        banana.append('00:00:00.00> SWRAD VOR')
        banana.append(apple + '.00> CRE ' + aircraftid + actype + str(scenario['st_x(gpt.coords)'][i]) + ', '
                      + str(scenario['st_y(gpt.coords)'][i]) + ', ' + str(heading) + ', ' + FlightLevel + ', ' + '0')
        banana.append(apple + '.00> ORIG ' + aircraftid + ', ' +
                      str(scenario['st_x(gpt.coords)'][i]) + ' ' + str(scenario['st_y(gpt.coords)'][i]))
        banana.append(apple + '.00> DEST ' + aircraftid + ', ' + str(scenario['st_x(gpt.coords)'][scenario.shape[0]-1])
                                             + ' ' + str(scenario['st_y(gpt.coords)'][scenario.shape[0]-1]))
        # +str(scenario['fl'][i]) +
    else:
        #banana.append('> ALT ' + aircraftid + ', ' + FlightLevel)
        #banana.append('> SPD ' + aircraftid + ', ' + speed)
        banana.append(apple +'.00> ADDWPT ' + aircraftid + ', '+ str(scenario['st_x(gpt.coords)'][i]) + ', '
                      + str(scenario['st_y(gpt.coords)'][i]) + ', ' + FlightLevel + ', ' + speed )
        # banana.append(apple + ".00>DEFWPT WPTZ" + str(i) + ',' + str(scenario['st_x(gpt.coords)'][i]) + ', ' + str(scenario['st_y(gpt.coords)'][i]))

        #acid AFTER afterwp ADDWPT (wpname/lat,lon),[alt,spd]

#save = pd.DataFrame(banana)
with open("C:\Documents\BlueSky\scenario\experimental\\test2.scn", "w") as fin:
    fin.write('\n'.join(banana))

# save.to_csv('test1.scn', sep=',', index=False, header=False, quoting=0)
# banana.to_csv('test2.scn', sep=',')
# writer = pd. Writer('{0}/{1}.xlsx'.format(name, i))
# save.to_excel(writer)
# writer.save()

# os.startfile("F:\Documents\Python Scripts\ThesisScript")