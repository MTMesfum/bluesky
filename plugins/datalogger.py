""" BlueSky AC deletion and logger plugin. This plugin deletes AC on the ground
    with very low speeds. Make sure the numbers are tweaked in such a way
    (# of updates, FL, speed) that AC who are spawned aren't deleted.
    When the AC is deleted, the data has to be logged.
    The Area plugin is used as a framework. """
import numpy as np
import pandas as pd
import os
from datetime import datetime as dt
# Import the global bluesky objects. Uncomment the ones you need
from bluesky import traf, sim, settings  #, settings, navdb, traf, sim, scr, tools
from bluesky.tools import datalog, areafilter, \
    TrafficArrays, RegisterElementParameters
from bluesky import settings

# Log parameters for the flight statistics log
header = \
    "#######################################################\n" + \
    "FLST LOG\n" + \
    "Flight Statistics\n" + \
    "#######################################################\n\n" + \
    "Parameters [Units]:\n" + \
    "Deletion Time [s], " + \
    "Call sign [-], " + \
    "Spawn Time [s], " + \
    "Flight time [s], " + \
    "Actual Distance 2D [m], " + \
    "Actual Distance 3D [m], " + \
    "Work Done [J], " + \
    "Latitude [deg], " + \
    "Longitude [deg], " + \
    "Altitude [m], " + \
    "TAS [m/s], " + \
    "Vertical Speed [m/s], " + \
    "Heading [deg], " + \
    "Origin Lat [deg], " + \
    "Origin Lon [deg], " + \
    "Destination Lat [deg], " + \
    "Destination Lon [deg], " + \
    "ASAS Active [bool], " + \
    "Pilot ALT [m], " + \
    "Pilot SPD (TAS) [m/s], " + \
    "Pilot HDG [deg], " + \
    "Pilot VS [m/s]"  + "\n"

# Global data
datalogger = None

### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():

    # Addtional initilisation code
    global datalogger
    datalogger = DataLogger()

    # Configuration parameters
    config = {
        'plugin_name'   :   'datalogger',
        'plugin_type'   :   'sim',
        'update'        :   datalogger.log,
        # 'preupdate'   :   datalogger.preupdate,
        'reset'         :   datalogger.reset
        }

    stackfunctions = {
        "DATALOGGER": [
            "DATALOGGER <ON/OFF>",
            '[]',
            datalogger.log,
            'Start logging the data [doesn\'t work yet].'
        ],
        'WRITER': [
            'WRITER <FILENAME>',
            '[txt]',
            datalogger.write,
            'Write the results of traf.resultstosave into a file.']
    }

    # init_plugin() should always return these two dicts.
    return config, stackfunctions

class DataLogger(TrafficArrays):
    def __init__(self):
        super(DataLogger, self).__init__()
        traf.resultstosave = pd.DataFrame(columns=['AC ID', 'Actual Departure Time', 'Arrival Time', 'Fuel Consumed'])

        with RegisterElementParameters(self):
            self.counter  = np.array([])
            self.initmass = np.array([])
            self.fuelused = np.array([])
            self.inittime = ([])
            self.deltime  = ([])

    def preupdate(self):
        print(self.initmass-traf.perf.mass)

    def update(self):
        print(self.initmass)
        print(traf.perf.mass)
        print(self.initmass-traf.perf.mass)

    def create(self, n=1):
        super(DataLogger, self).create(n)
        if len(traf.id) > 1:
            self.initmass[-1] = traf.perf.mass[-1]
            self.inittime[-1] = str(sim.utc.strftime("%d-%b-%Y %H:%M:%S"))
            self.counter[-1] = 0
        else:
            self.initmass[0] = traf.perf.mass[0]
            self.inittime[0] = str(sim.utc.strftime("%d-%b-%Y %H:%M:%S"))
            self.counter[0] = 0
        print("AC {0} [{1}] has been created at {2}.".format(traf.id[-1], traf.type[-1], self.inittime[-1]))

    def talko(self, delcounter):
        if len(delcounter) == 1:
            print("Aircraft {0} has been deleted at {1}.".format(traf.id[int(delcounter)], sim.utc))
            print("Fuel used by {0} is {1} [kg].".format(traf.id[int(delcounter)],
                                                    np.array2string(self.fuelused[int(delcounter)], precision=2)))
        else:
            for i in range(0, len(delcounter)):
                print("Aircraft {0} has been deleted at {1}.".format(traf.id[int(delcounter[i])], sim.utc))
                print("Fuel used by {0} is {1} kg.".format(traf.id[int(delcounter[i])],
                                                np.array2string(self.fuelused[int(delcounter[i])], precision=2)))

    def save(self, results, delcounter):
        for i in delcounter:
            holder = [[str(traf.id[int(i)]), str(self.inittime[int(i)]),
                            str(self.deltime[int(i)]), np.array2string(self.fuelused[int(i)], precision=3)]]
            df = pd.DataFrame(holder, columns=['AC ID', 'Actual Departure Time', 'Arrival Time', 'Fuel Consumed'])
            results = results.append(df, ignore_index=True)
        return results

    def write(self, *args):
        curtime = []
        if traf.resultstosave.empty:
            curtime = str(sim.utc.strftime("%d-%b-%Y %H:%M:%S"))
            for i in range(0,len(traf.id)):
                holder = [[str(traf.id[int(i)]), str(self.inittime[int(i)]),
                           str(curtime), np.array2string(self.initmass[int(i)]-traf.perf.mass[int(i)], precision=3)]]
                df = pd.DataFrame(holder, columns=['AC ID', 'Actual Departure Time', 'Arrival Time', 'Fuel Consumed'])
                traf.resultstosave = traf.resultstosave.append(df, ignore_index=True)

        if not args:
            print('Now i will save a standard file!!!')
            traf.resultstosave.to_csv('output\WRITER Standard File.csv')
            os.startfile('output\WRITER Standard File.csv')
        else:
            filename = str(args[0])
            print('Now i will save a file in {0}!!!'.format(filename))
            traf.resultstosave.to_csv('output\WRITER {0}.csv'.format(filename))
            os.startfile('output\WRITER {0}.csv'.format(filename))
        print(traf.resultstosave)
        
        if curtime:
            traf.resultstosave = pd.DataFrame(
                columns=['AC ID', 'Actual Departure Time', 'Arrival Time', 'Fuel Consumed'])

    def log(self):
        apple = len(traf.id)
        limit = 5
        # datalogger.update()

        if apple > 0:
            self.counter += np.ones(apple) * np.logical_and(traf.alt<1, True)  # _and , traf.M<0.007

            if np.size((np.nonzero(self.counter > limit))) > 0:
                delcounter = np.delete(traf.id2idx(traf.id), np.nonzero(self.counter < limit))
                if len(range(0, len(delcounter))) > 0:
                    for i in range(0, len(delcounter)):
                        delcounter[i] = int(delcounter[i])
                        self.deltime[delcounter[i]] = str(sim.utc.strftime("%d-%b-%Y %H:%M:%S"))
                else:
                    delcounter[0] = int(delcounter[0])
                    self.deltime[0] = str(sim.utc.strftime("%d-%b-%Y %H:%M:%S"))
                # Print some stuff
                self.fuelused = self.initmass - traf.perf.mass
                datalogger.talko(delcounter)

                # Save some stuff
                traf.resultstosave = datalogger.save(traf.resultstosave, delcounter)
                traf.delete(delcounter)