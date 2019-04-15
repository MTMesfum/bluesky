# This script creates SCN files for BlueSky from queries
# 00:00:00.00>DEFWPT WPTZ0,2.91470132478, -2.91470132478

import pandas as pd
import os
import random
# from datetime import datetime
# from datetime import timedelta
from tkinter import Tk
from geo import qdrdist as dist
from geo import latlondist as dist2
import datetime
from tkinter.filedialog import askopenfilename

def cut3(one):
    return round(one, 3)

def cut7(one):
    return round(one, 7)

def addSecs(tm, secs, secs2):
    secs = secs*5
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    if secs2 == 0:
        fulldate = fulldate + datetime.timedelta(seconds=(secs))
        delay = secs
    else:
        fulldate = fulldate - datetime.timedelta(seconds=(secs))
        delay = -secs
    return str(fulldate.time()), delay

def CreateSCN(alpha):
    # Constants
    nm  = 1852.  # m       1 nautical mile
    ft  = .3048  # m        1 foot

    folder = "C:\\Users\Johannes\Desktop\Dropbox\# TU Delft Master\Thesis 2018\Main Phase\Queries\\trajectories"
    FileName = os.listdir(folder)

    # Tk().withdraw()
    # print("Choose the csv file:")
    # FileName = askopenfilename()
    #FileName = 'C:\Documents\BlueSky\scenario\experimental\\Flight_1.csv'
    traj = 0
    banana = list()
    #banana.append('00:00:00.00> SWRAD VOR')
    #banana.append('00:00:00.00> FF 79495')

    for k in FileName:
        scenario = pd.read_csv(folder +"\\" + k)
        traj += 1
        traj2 = str(traj)
        if traj2.count('') < 3:
            id = '0' + str(traj)
        else:
            id = str(traj)
        aircraftid = 'KLM' + id + '-%0'
        actype  =  ', A320, '
        [heading, distance] = dist(scenario['st_x(gpt.coords)'][0], scenario['st_y(gpt.coords)'][0],
                                    scenario['st_x(gpt.coords)'][1], scenario['st_y(gpt.coords)'][1])
        if heading < 0:
            heading += 360

        #speed = '250'
        apple = scenario.time_over[0]
        apple = apple[-8:]
        if alpha:
            apple = datetime.datetime(100, 1, 1, int(apple[-8:-6]), int(apple[-5:-3]), int(apple[-2:]))
            apple, delay = addSecs(apple, random.randrange(181), random.randrange(1))
        # banana.append('>SPD KLM1705 250')
        # banana.append('>ALT KLM1705 300')
        # banana.append('>KLM1705 ORIG EHAM 00:00:00.00')
        j = 0

        for i in range(scenario.shape[0]):
            if i != 0:
                j = -1

            FlightLevel = str(scenario['fl'][i])
            if FlightLevel.count('') < 3:
                FlightLevel = '0' + FlightLevel
            FlightLevel = 'FL' + FlightLevel

            if i == 0:
                banana.append(apple + '.00> CRE ' + aircraftid + actype + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                              + str(cut7(scenario['st_y(gpt.coords)'][i])) + ', ' + str(cut3(heading)) + ', ' + FlightLevel + ', ' + '0')
                banana.append(apple + '.00> DEFWPT ' + aircraftid + '-ORIG,' + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                              + str(cut7(scenario['st_y(gpt.coords)'][i])))
                banana.append(apple + '.00> ORIG ' + aircraftid + ', ' + aircraftid + '-ORIG')
                              #str(scenario['st_x(gpt.coords)'][i]) + ' ' + str(scenario['st_y(gpt.coords)'][i]))
                banana.append(apple + '.00> DEFWPT ' + aircraftid + '-DEST, ' + str(cut7(scenario['st_x(gpt.coords)'][scenario.shape[0]-1]))
                                + ', ' + str(cut7(scenario['st_y(gpt.coords)'][scenario.shape[0]-1])))
                banana.append(apple + '.00> DEST ' + aircraftid + ', ' + aircraftid + '-DEST' )
                #+ str(scenario['st_x(gpt.coords)'][scenario.shape[0] - 1]) + ' ' + str(scenario['st_y(gpt.coords)'][scenario.shape[0] - 1])
                # +str(scenario['fl'][i]) +
            else:
                #banana.append('> ALT ' + aircraftid + ', ' + FlightLevel)
                #banana.append('> SPD ' + aircraftid + ', ' + speed)
                if i == scenario.shape[0]-1:
                    follow = aircraftid + '-' + str(i-1)
                    banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                  + aircraftid + "-DEST" + ', ' + FlightLevel + ', ' + '0')
                else:
                    deltatime   = datetime.datetime.strptime(scenario.time_over[i], '%Y-%m-%d %H:%M:%S') -\
                                    datetime.datetime.strptime(scenario.time_over[i+j], '%Y-%m-%d %H:%M:%S')

                    distance    = abs(dist2(scenario['st_x(gpt.coords)'][i+j], scenario['st_y(gpt.coords)'][i+j],
                                     scenario['st_x(gpt.coords)'][i], scenario['st_y(gpt.coords)'][i]))

                    height      = abs((scenario['fl'][i] - scenario['fl'][i+j]) * 100 * ft)
                    distance    = (height**2 + distance**2)**(1/2)

                    speed = distance / deltatime.total_seconds() * 3600 / nm

                    if i == 1:
                        follow = aircraftid + '-ORIG'
                    else:
                        follow = aircraftid + '-' + str(i-1)

                    banana.append(apple + '.00> DEFWPT ' + aircraftid + '-' + str(i) + ', '+ str(cut7(scenario['st_x(gpt.coords)'][i]))
                                        + ', ' + str(cut7(scenario['st_y(gpt.coords)'][i])))
                    banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                        + aircraftid + '-' + str(i) + ', ' + FlightLevel + ', ' + str(cut3(speed)))
                    #+ ', ' + FlightLevel + ', ' + speed
                    # banana.append(apple + ".00>DEFWPT WPTZ" + str(i) + ',' + str(scenario['st_x(gpt.coords)'][i]) + ', ' + str(scenario['st_y(gpt.coords)'][i]))

                    #acid AFTER afterwp ADDWPT (wpname/lat,lon),[alt,spd]

    #save = pd.DataFrame(banana)
    with open("C:\Documents\Git\\trunk\scenario\Test3.scn", "w") as fin:
        fin.write('\n'.join(banana))
    os.startfile("C:\Documents\Git\\trunk\scenario\Test3.scn")

    # save.to_csv('test1.scn', sep=',', index=False, header=False, quoting=0)
    # banana.to_csv('test2.scn', sep=',')
    # writer = pd. Writer('{0}/{1}.xlsx'.format(name, i))
    # save.to_excel(writer)
    # writer.save()

    # os.startfile("F:\Documents\Python Scripts\ThesisScript")

CreateSCN(False)