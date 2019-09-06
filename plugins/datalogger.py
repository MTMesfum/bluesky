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
from bluesky import traf, sim, stack, settings, scr  #, settings, navdb, traf, sim, scr, tools
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
    # scenario_manager = "scenario\Trajectories-batch.scn"
    scenario_manager = "scenario\Trajectories-batch4.scn"
    with open(scenario_manager, 'r') as f:
        filedata = f.read()

    banana = filedata.find(', Tigge_')

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
        'WRITER2': [
            'WRITER <FILENAME>',
            '[txt, txt, int]',
            datalogger.write2,
            'Save the fuel consumption into traf.resultstosave.'
            'If one AC remains, write the results of traf.resultstosave into a file.'
        ],
        'PRINTER': [
            'PRINTER',
            '[string]',
            datalogger.printer,
            'Print some text in BlueSky and the console of python.'
        ],
        'LOAD_WIND2': [
            'LOAD_WIND2',
            '[int, string]',
            datalogger.load,
            'Load wind and print some text.'
        ],
        'SPD2': [
            'SPD2 acid, spd',
            'acid, spd',
            datalogger.speed,
            'Speed command (autopilot) with a Vmax cap.'
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
            with open(os.getcwd() + '\\scenario\\number_of_ac.txt', "r") as fin:
                self.aclimit = int(fin.read())
                self.aclimit2 = 0

    def preupdate(self):
        # print(sim.utc.strftime("%S"))
        if len(traf.id) > 0 and sim.utc.strftime("%S") == '00':
            stack.stack('GETWIND {}, {}, {}'.format(traf.lat[0], traf.lon[0], traf.alt[0]))
            print('\nFuelflow is: ', traf.perf.fuelflow)
            print('Fuel used is: ', self.initmass-traf.perf.mass)
            print('Thrust is: ', traf.perf.Thr)
            print('pilot tas is {} \n tas is {} \n delspd becomes {}'.format(
                  traf.pilot.tas, traf.tas, traf.pilot.tas-traf.tas))
            print('The groundspeed is: ', traf.gs)
        # print('eta is {} \n Thrust is {} \n '
        #       'cf_cruise jet is {} \n jt is {}'.format(
        #         eta, self.Thr, self.cf_cruise, jt))

    def update(self):
        # print(self.initmass)
        # print(traf.perf.mass)
        print("Fuel used up till now: ", self.initmass-traf.perf.mass)

    def load(self, ensemble, file):
        print('\033[91m' +
              "\nFile '{}' with ensemble [{}] will be loaded!\n".format(file, ensemble)
              + '\033[0m')
        stack.stack('LOAD_WIND {}, {}'.format(ensemble, file))


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
        print("\nAC {0} [{1}] has been created at {2}.".format(traf.id[-1], traf.type[-1],
                                                             sim.utc.strftime("%d-%b-%Y %H:%M:%S")))


    def speed(self, ac_id, ac_target_speed):
        # Check whether Vmax is exceeded, if so replace it with Vmax
        # print(ac_id)
        # print(traf.id[ac_id])
        # index = self.idx2id(ac_id)
        # print(index)
        # This is the target altitude of the next waypoint
        # print(traf.ap.route[ac_id].wpalt[traf.ap.route[ac_id].iactwp])
        # This is the ac type
        # print(traf.type[ac_id])
        # Now find the maximum velocity of the ac type corresponding at that altitude
        # print(traf.perf.vmo)
        # print('The maximum operating mach number is: ', traf.perf.mmo)
        # print(traf.tas)
        # print('Vmax is: ', traf.perf.asas.vmax)
        # Either pick the speed which is put in or the max operating speed
        ac_speed = min(traf.perf.mmo[ac_id] - 0.001, ac_target_speed)
        # print('\nThe target speed is: ', ac_target_speed)
        # print('The max speed is: ', traf.perf.mmo[ac_id])
        # print('The selected speed is: ', ac_speed)
        stack.stack(f'SPD {traf.id[ac_id]} {ac_speed}')

        # "SPD": [
        #         #     "SPD acid,spd (CAS-kts/Mach)",
        #         #     "acid,spd",
        #         #     bs.traf.ap.selspdcmd,
        #         #     "Speed command (autopilot)"

    def idx2id(self, ac_id):
        # Fast way of finding indices of all ACID's in a given list
        tmp = dict((v, i) for i, v in enumerate(traf.id))
        return [tmp.get(acidi, -1) for acidi in ac_id]


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

    def write2(self, acid, traf_id, index, *args):
        curtime = []
        i = int(acid)
        print('\nacid {} is saved on {}'.format(traf_id, acid))
        # print('What is saved in i?? : ', i)
        # print('i is supposed to be: ', traf.id[index])
        # print('i as index is: ', traf.id[i])
        self.aclimit2 += 1
        curtime = str(sim.utc.strftime("%H:%M:%S"))
        traf.resultstosave = pd.DataFrame([[ensemble, str(self.delay[int(i)]), str(traf_id),
                   str(sim.utc.strftime("%d-%b-%Y")), str(self.inittime[int(i)]),
                   str(curtime), np.array2string(self.initmass[int(i)]-traf.perf.mass[int(i)], precision=3)]],
                              columns=self.dataframe_holder)
        traf.resultstosave3 = traf.resultstosave3.append(traf.resultstosave, ignore_index=True)
        stack.stack('DEL {}'.format(traf_id))
        print("\nAircraft {0} has been deleted at {1}.".format(traf.id[i], sim.utc.strftime("%d-%b-%Y %H:%M:%S")))
        print("Fuel used by {0} is {1} [kg].".format(traf.id[i],
                                 np.array2string(self.initmass[int(i)]-traf.perf.mass[int(i)], precision=2)))
        # print('traf.id length is: ', len(traf.id))
        print('ac_limit is1: ', self.aclimit)
        print('ac_limit is2: ', self.aclimit2)
        if traf.resultstosave2.iloc[-1, -1] is not None and \
                (len(traf.id) == 1 or self.aclimit2 == self.aclimit):
            traf.resultstosave3 = traf.resultstosave3.sort_values('AC ID').reset_index(drop=True)
            traf.resultstosave2 = traf.resultstosave2.sort_values('AC ID').reset_index(drop=True)
            traf.resultstosave = pd.concat([traf.resultstosave3,
                                            traf.resultstosave2], axis=1)
            # traf.resultstosave.to_csv('output\WRITER Standard File.csv')
            # check whether the file exist, if it does append it, otherwise create it
            exists = os.path.isfile('output\WRITER Standard File.xlsx')
            if exists:
                with open('output\WRITER Standard File.xlsx', 'wb') as f:
                    traf.resultstosave.to_excel(f, header=False)
            else:
                traf.resultstosave.to_excel('output\WRITER Standard File.xlsx')
            print('\033[94m' + '\033[4m' +
                  '\nSaving the results in a standard file with N = {}!!!\n'.format(self.aclimit2) +
                  '\033[0m')
            # os.startfile('output\WRITER Standard File.xlsx')
        elif args:
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
            os.startfile('output\WRITER {0}.csv'.format(filename))

        if curtime:
            traf.resultstosave = pd.DataFrame(columns=self.dataframe_holder)
        # print(self.aclimit2)
        if self.aclimit2 == self.aclimit:
            print('Final aircraft has landed!')
            stack.stack('EXIT')
        pass

    # This method prints something to the cmd window (useful for feedback)
    def printer(self, delay):
        # if len(traf.id) > 1:
        self.delay[-1] = delay.split()[3]
        # else:
        #     self.delay[0] = delay.split()[3]
        # print('Echo starting now!')
        print(delay)
        # print(self.delay)
        # scr.echo(delay)
        pass

    def log(self):
        apple = len(traf.id)
        limit = 5
        # datalogger.update()

        if apple > 0:
            # print('Fuelflows are: {} at {}'.format(traf.perf.fuelflow, str(sim.utc.strftime("%H:%M:%S"))))
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