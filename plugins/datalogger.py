""" BlueSky AC deletion and logger plugin. This plugin deletes AC on the ground
    with very low speeds. Make sure the numbers are tweaked in such a way
    (# of updates, FL, speed) that AC who are spawned aren't deleted.
    When the AC is deleted, the data has to be logged.
    The Area plugin is used as a framework. """
import numpy as np
import pandas as pd
import os
from datetime import datetime
# Import the global bluesky objects. Uncomment the ones you need
from bluesky import traf, sim, settings, scr  #, settings, navdb, traf, sim, scr, tools
from bluesky.tools import datalog, areafilter, \
    TrafficArrays, RegisterElementParameters
from bluesky import settings

# Global data
datalogger = None

### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():

    # Addtional initilisation code
    global datalogger, ensemble
    scenario_manager = "scenario\Trajectories-batch.scn"

    with open(scenario_manager, 'r') as f:
        filedata = f.read()

    banana = filedata.find(',Tigge_')

    ensemble = filedata[banana-2:banana]
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
            'Start logging the data [~doesn\'t work yet].'
        ],
        'WRITER': [
            'WRITER <FILENAME>',
            '[txt]',
            datalogger.write,
            'Write the results of traf.resultstosave into a file.'
        ],
        'PRINTER': [
            'PRINTER',
            '[string]',
            datalogger.printer,
            'Print some text in BlueSky and the console of python.'
        ],
    }

    # init_plugin() should always return these two dicts.
    return config, stackfunctions

class DataLogger(TrafficArrays):
    def __init__(self):
        super(DataLogger, self).__init__()
        self.dataframe_holder = \
            ['Ensemble', 'Delay', 'AC ID', 'Date', 'Departure', 'Arrival', 'Fuel Consumed']
        traf.resultstosave = pd.DataFrame(columns=self.dataframe_holder)

        with RegisterElementParameters(self):
            self.counter  = np.array([])
            self.initmass = np.array([])
            self.fuelused = np.array([])
            self.inittime = ([])
            self.deltime  = ([])
            self.wpcounter = -2
            self.delay = np.array([])

    def preupdate(self):
        print(self.initmass-traf.perf.mass)

    def update(self):
        # print(self.initmass)
        # print(traf.perf.mass)
        print("Fuel used up till now: ", self.initmass-traf.perf.mass)

    def create(self, n=1):
        super(DataLogger, self).create(n)
        if len(traf.id) > 1:
            self.initmass[-1] = traf.perf.mass[-1]
            self.inittime[-1] = str(sim.utc.strftime("%H:%M:%S"))
            self.counter[-1] = 0
        else:
            self.initmass[0] = traf.perf.mass[0]
            self.inittime[0] = str(sim.utc.strftime("%H:%M:%S"))
            self.counter[0] = 0
        print("AC {0} [{1}] has been created at {2}.".format(traf.id[-1], traf.type[-1],
                                                             sim.utc.strftime("%d-%b-%Y %H:%M:%S")))

    def talko(self, delcounter):
        # if len(delcounter) == 1:
        #     print("Aircraft {0} has been deleted at {1}.".format(traf.id[int(delcounter)], sim.utc))
        #     print("Fuel used by {0} is {1} [kg].".format(traf.id[int(delcounter)],
        #                                             np.array2string(self.fuelused[int(delcounter)], precision=2)))
        # else:
        for i in range(0, len(delcounter)):
            print("Aircraft {0} has been deleted at {1}.".format(traf.id[int(delcounter[i])], sim.utc))
            print("Fuel used by {0} is {1} kg.".format(traf.id[int(delcounter[i])],
                                            np.array2string(self.fuelused[int(delcounter[i])], precision=2)))

    def save(self, results, delcounter):
        for i in delcounter:
            holder = [[ensemble, str(self.delay[int(i)]), str(traf.id[int(i)]),
                       str(sim.utc.strftime("%d-%b-%Y")), str(self.inittime[int(i)]),
                       str(self.deltime[int(i)]), np.array2string(self.fuelused[int(i)], precision=3)]]
            df = pd.DataFrame(holder, columns=self.dataframe_holder)
            results = results.append(df, ignore_index=True)
        return results

    # def save2(self):
    #     if self.wpcounter == -2:
    #         traf.resultstosave2 = pd.DataFrame()
    #         # number_of_waypoints = traf.ap.route[bs.traf.id2idx(traf.id[-1])].nwp
    #         for i in range(1, traf.ap.route[traf.id2idx(traf.id[-1])].nwp+1):
    #             if i < 10:
    #                 holder = pd.DataFrame(["[ 0{0} ]".format(i)], columns=['Waypoint {0}'.format(i)])
    #             else:
    #                 holder = pd.DataFrame(["[ {0} ]".format(i)], columns=['Waypoint {0}'.format(i)])
    #             traf.resultstosave2 = pd.concat([traf.resultstosave2, holder], axis=1)
    #         self.wpcounter = 0
    #         print(traf.resultstosave2)
    #     pass

    def write(self, *args):
        curtime = []
        if traf.resultstosave.empty:
            curtime = str(sim.utc.strftime("%H:%M:%S"))
            for i in range(0, len(traf.id)):
                holder = [[ensemble, str(self.delay[int(i)]), str(traf.id[int(i)]),
                           str(sim.utc.strftime("%d-%b-%Y")), str(self.inittime[int(i)]),
                           str(curtime), np.array2string(self.initmass[int(i)]-traf.perf.mass[int(i)], precision=3)]]
                df = pd.DataFrame(holder, columns=self.dataframe_holder)
                traf.resultstosave = traf.resultstosave.append(df, ignore_index=True)
                print("\nAircraft {0} has been deleted at {1}.".format(traf.id[i], sim.utc.strftime("%d-%b-%Y %H:%M:%S")))
                print("Fuel used by {0} is {1} [kg].\n".format(traf.id[i],
                                         np.array2string(self.initmass[int(i)]-traf.perf.mass[int(i)], precision=2)))
        traf.resultstosave = pd.concat([traf.resultstosave, traf.resultstosave2], axis=1)

        if not args:
            print('\033[94m' + '\033[4m' + '\nSaving the results in a standard file!!!\n\n' + '\033[0m')
            # traf.resultstosave.to_csv('output\WRITER Standard File.csv')
            # check whether the file exist, if it does append it, otherwise create it
            exists = os.path.isfile('output\WRITER Standard File.csv')
            if exists:
                with open('output\WRITER Standard File.csv', 'a') as f:
                    traf.resultstosave.to_csv(f, header=False)
            else:
                traf.resultstosave.to_csv('output\WRITER Standard File.csv')
            # os.startfile('output\WRITER Standard File.csv')
        else:
            filename = str(args[0])
            print('\033[94m' + '\033[4m' + '\nSaving the results in {0}!!!\n\n'.format(filename) + '\033[0m')
            # check whether the file exist, if it does append it, otherwise create it
            exists = os.path.isfile('\output\WRITER {0}.csv'.format(filename))
            if exists:
                df = pd.read_csv('\output\WRITER {0}.csv'.format(filename), index_col=0)
                with open('\output\WRITER {0}.csv'.format(filename), 'a') as f:
                    df.to_csv(f, header=False)
            else:
                traf.resultstosave.to_csv('output\WRITER {0}.csv'.format(filename))
            # os.startfile('output\WRITER {0}.csv'.format(filename))

        if curtime:
            traf.resultstosave = pd.DataFrame(columns=self.dataframe_holder)

    def printer(self, delay):
        # print('The delay is {} seconds.'.format(delay[7:]))
        self.delay = np.array(delay.split()[3])
        # print('Echo starting now!')
        print('\n' + delay + '\n')
        # print(self.delay)
        scr.echo(delay)
        pass

    def log(self):
        apple = len(traf.id)
        limit = 5
        # datalogger.update()

        if apple > 0:
            self.counter += np.ones(apple) * np.logical_and(traf.alt<1, True)  # _and , traf.M<0.007

            # datalogger.save2()
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
        pass