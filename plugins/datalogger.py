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
        # The name of your plugin
        'plugin_name':     'datalogger',

        # The type of this plugin. For now, only simulation plugins are possible.
        'plugin_type':     'sim',

        # # Update interval in seconds.
        # 'update_interval': update,

        # The update function is called after traffic is updated.
        'update': datalogger.log,
        # 'preupdate': datalogger.preupdate,
        'reset': datalogger.reset
        }

    stackfunctions = {
        "DATALOGGER": [
            # A short usage string. This will be printed if you type HELP <name> in the BlueSky console
            "DATALOGGER <ON/OFF>",

            # A list of the argument types your function accepts. For a description of this, see ...
            '[]',

            # The name of your function in this plugin
            datalogger.log,

            # a longer help text of your function.
            "Start logging the data."
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
        # global resultstosave
        # global counter
        traf.resultstosave = pd.DataFrame(columns=['AC ID', 'Actual Departure Time', 'Arrival Time', 'Fuel Consumed'])
        # traf.counter = np.array([])


        with RegisterElementParameters(self):
            self.counter  = np.array([])
            self.initmass = np.array([])
            self.fuelused = np.array([])
            self.inittime = ([])
            self.deltime  = ([])
            #data = np.array(data, dtype=np.float32)
        pass

    def preupdate(self):
        # if len(traf.perf.mass) > 0:
        #     print('mass in preupdate is:', traf.perf.mass)
        # print(self.fuelused)
        print(self.initmass-traf.perf.mass)

    def update(self):
        #stack.stack('ECHO MY_PLUGIN update: creating a random aircraft')
        #stack.stack('MCRE 1')
        # print(self.fuelused)
        # if len(traf.perf.mass) > 0:
        #     print('mass in update is:', traf.perf.mass)
        #
        # if len(traf.id) > 0:
        #     print(np.array2string((traf.perf.mass), precision=2))
        # print(self.initmass)
        # print(traf.perf.mass)
        print(self.initmass-traf.perf.mass)
        pass

    def create(self, n=1):
        # global resultstosave, counter
        super(DataLogger, self).create(n)
        # print('before assignment')
        # print(self.initmass)
        # print(self.inittime)

        if len(traf.id) > 1:
            self.initmass[-1] = traf.perf.mass[-1]
            self.inittime[-1] = str(sim.utc.strftime("%d-%b-%Y %H:%M:%S"))
            self.counter[-1] = 0
        # Try to print/use simt
        else:
            self.initmass[0] = traf.perf.mass[0]
            self.inittime[0] = str(sim.utc.strftime("%d-%b-%Y %H:%M:%S"))
            self.counter[0] = 0
        # print('after assignment')
        # print(self.initmass)
        # print(self.inittime)
        # if len(traf.counter) > 0:
        #     # print(traf.counter)
        #     # print(len(traf.counter))
        #     traf.counter = np.append(traf.counter, [0.])
        #     # print(traf.counter)
        #     print(self.initmass, traf.perf.mass, self.initmass-traf.perf.mass)
        # else:
        #     traf.counter = np.array([0.])
        #     print(self.initmass, traf.perf.mass, self.initmass-traf.perf.mass)
        #     # print(traf.counter)
        #print(self.inittime)
        print("AC {0} has been created at {1}.".format(traf.id[-1], self.inittime[-1]))
        # print(self.initmass)
        # print(traf.perf.mass)

        # print('mass in create is:', traf.perf.mass)
        # print(sim.utc)
        pass

    def talko(self, delcounter):
        # super(DataLogger, self).delete(delcounter)

        if len(delcounter) == 1:
            print("Aircraft {0} has been deleted at {1}.".format(traf.id[int(delcounter)], sim.utc))
            print("Fuel used by {0} is {1} [kg].".format(traf.id[int(delcounter)],
                                                    np.array2string(self.fuelused[int(delcounter)], precision=2)))
        else:
            for i in range(0, len(delcounter)):
                print("Aircraft {0} has been deleted at {1}.".format(traf.id[int(delcounter[i])], sim.utc))
                print("Fuel used by {0} is {1} kg.".format(traf.id[int(delcounter[i])],
                                                np.array2string(self.fuelused[int(delcounter[i])], precision=2)))
        # print(self.counter)
        pass

    def save(self, results, delcounter):
        # holder = []
        for i in delcounter:
            # print('We are in the save function!')
            # print(traf.id)
            # print(traf.counter)
            # print(self.initmass)
            # print(traf.perf.mass)
            # print(self.inittime)
            # print(self.deltime)
            # print(self.fuelused)
            holder = [[str(traf.id[int(i)]), str(self.inittime[int(i)]),
                            str(self.deltime[int(i)]), np.array2string(self.fuelused[int(i)], precision=3)]]

            # print(delcounter)
            # print(results)
            # print(holder)
            df = pd.DataFrame(holder, columns=['AC ID', 'Actual Departure Time', 'Arrival Time', 'Fuel Consumed'])
            # print(df)
            results = results.append(df, ignore_index=True)
            # df = pd.DataFrame([traf.id[int(delcounter)], self.inittime[int(delcounter)],
        #                         self.deltime[int(delcounter)], self.fuelused[int(delcounter)]],
        #                             columns=['AC ID', 'Actual Departure Time', 'Arrival Time', 'Fuel Consumed'])


        #results = results.append(df, ignore_index=True)
        #print(results)
        del df, holder
        return results

    def write(self, *args):
        if not args:
            print('Now i will save a standard file!!!')
            # r‘C:\Users\doron\Desktop\export_dataframe.csv‘
            traf.resultstosave.to_csv(
                r'\output\WRITER Standard File.csv') # Desktop
            # traf.resultstosave.to_csv(
            #     r'I:\Documents\Google Drive\Thesis 2018\BlueSky\output\WRITER Standard File.csv') # Laptop
            #, index=None,
                      #header=True)  # Don't forget to add '.csv' at the end of the path
            os.startfile("\output\WRITER Standard File.csv")
        else:
            filename = str(args[0])
            print('Now i will save a file in {0}!!!'.format(filename))
            #print(traf.resultstosave)
            traf.resultstosave.to_csv(
                'output\WRITER {0}.csv'.format(filename)) # Desktop
            # traf.resultstosave.to_csv(
            #     'I:\Documents\Google Drive\Thesis 2018\BlueSky\\output\\WRITER {0}.csv'.format(filename)) # Laptop
            os.startfile('output\WRITER {0}.csv'.format(filename))
        print(traf.resultstosave)

        pass

    def log(self):
        apple = len(traf.id)
        limit = 5
        # datalogger.update()

        if apple > 0:
            # print(traf.id)
            # print(self.counter)
            # print('apple is', apple)
            # print(traf.alt)
            # print(traf.M)
            # print(traf.perf.mass)
            # print(self.initmass)
            # print(np.logical_and(traf.alt<1, traf.M<0.002))
            self.counter += np.ones(apple) * np.logical_and(traf.alt<1, True)  # _and , traf.M<0.007

            if np.size((np.nonzero(self.counter > limit))) > 0:
                delcounter = np.delete(traf.id2idx(traf.id), np.nonzero(self.counter < limit))
                #print(delcounter)
                # print(self.deltime)

                if len(range(0, len(delcounter))) > 0:
                    for i in range(0, len(delcounter)):
                        delcounter[i] = int(delcounter[i])
                        self.deltime[delcounter[i]] = str(sim.utc.strftime("%d-%b-%Y %H:%M:%S"))
                else:
                    delcounter[0] = int(delcounter[0])
                    self.deltime[0] = str(sim.utc.strftime("%d-%b-%Y %H:%M:%S"))
                # print(delcounter)

                # print(traf.id)
                # print(traf.counter)
                # print(self.initmass)
                # print(self.inittime)
                # print(self.deltime)
                # print(self.fuelused)

                # Print some stuff
                self.fuelused = self.initmass - traf.perf.mass

                # print('after assignment')
                # print(self.deltime)
                datalogger.talko(delcounter)

                # Save some stuff
                try:
                    results2 = traf.resultstosave
                    # print('delcounter according to save fnc!')
                    # print(delcounter)
                    traf.resultstosave = datalogger.save(results2, delcounter)
                except:
                    test = pd.DataFrame(columns=['AC ID', 'Actual Departure Time', 'Arrival Time', 'Fuel Consumed'])
                    traf.resultstosave = datalogger.save(test, delcounter)
                    del test

                # Clear the to-be-deleted AC
                #self.counter = np.delete(self.counter, delcounter)
                # self.fuelused = np.delete(self.fuelused, delcounter)
                # self.initmass = np.delete(self.initmass, delcounter)
                # for i in delcounter:
                #     self.deltime.pop(delcounter[i])
                #     self.inittime.pop(delcounter[i])
                    #     = np.delete(self.deltime, delcounter)
                    # self.inittime = np.delete(self.inittime, delcounter)

                #print(traf.resultstosave)
                #print('deleting aircrafts now :)')
                traf.delete(delcounter)
                # self.counter = np.delete(self.counter, delcounter)
                del delcounter
        pass

"""
        # def quit(self):
        #     #this doesnt work properly. it doesn't get called when the program quits
        #     #super(DataLogger, self).quit()
        #     print('A savelog should have been created now... (?)    QUIT')
        #     print(traf.resultstosave)
        # p.dump(results, open("output/data.p", "wb"))

        # def reset(self):
        #     #   this does get called if the program is resetted
        #     print('A savelog should have been created now... (?)       RESET')
        #     print(traf.resultstosave)

        # def stop(self):
        #     #this doesnt work properly. it doesn't get called when the program stops
        #
        #     print('A savelog should have been created now... (?)    stop')
        #     print(traf.resultstosave)
        #     super(DataLogger, self).stop()
        # p.dump(results, open("output/data.p", "wb"))

        # def delete(self, idx):
        #     super(DataLogger, self).delete(idx)
        #
        #
        #
        #     pass

        # save_list = save_list.append(self.fuelused)
        # print(save_list)

                # initialize list of lists
                # data = list([])
                # data.append([traf.id[delcounter], self.inittime[delcounter],
                #                 self.deltime[delcounter], self.fuelused[delcounter]])
                # df = pd.DataFrame(data, columns=['AC Number', 'Actual Departure Time',
                #                                           'Arrival Time', 'Fuel Consumed'])
                # p.dump(df, open("output/data.p", "wb"))
                # try:
                #     save_list
                # except NameError:
                #     save_list = []
                # save_list.append(self.fuelused[delcounter])
                # print(data)



            #print(self.counter.shape)
            #print(traf.M)
            #counter2 = np.vstack(np.ones(len(self.counter))
            #print(((np.ones(len(traf.id)) * [traf.alt<1]) * \
            #                (np.ones(len(traf.id)) * [traf.M<0.001])).shape)
            #print( len(self.counter))
            #print(traf.alt.size)
            #print(traf.M.shape)



                            # (np.ones(apple) * )
            # print(self.counter)
            # print(self.fuelcons.initmass)
            #print(traf.id2idx(traf.id))
            #print(sim.utc)


                # delcounter = traf.id2idx(traf.id)
            #self.counter = self.counter *
            #np.vstack((np.ones(len(lat_i))
            #holder = np.ones(self.counter.shape) * 5
            #if self.counter > holder:
            #print("Update")
            #print(self.counter)
            #if self.counter.any > 0:
            #    print(self.counter)
            # if traf.alt == 0:
            #     #apple = traf.alt[traf.alt==0]
            #     if traf.M < 0.001:
            #         #apple =
            #         self.counter = (self.counter < 3).astype(int)
            #         self.counter += 1
            #         print(self.counter)
            # if apple = (self.counter[] > 5):
            #     # print(id)
            #     traf.delete(traf.id2idx(traf.id))
        # return

    # def update(self):
    #
    #         DataLogger.log(self)

    #def reset(self):
     #   self.counter = []

    #     resultantspd = np.sqrt(traf.gs * traf.gs + traf.vs * traf.vs)
    #     self.distance2D += self.dt * traf.gs
    #     self.distance3D += self.dt * resultantspd
    #
    #     if settings.performance_model == 'openap':
    #         self.work += (traf.perf.thrust * self.dt * resultantspd)
    #     else:
    #         self.work += (traf.perf.Thr * self.dt * resultantspd)
    #
     # ToDo: Add autodelete for descending with swTaxi:
    #     if self.swtaxi:
    #         pass # To be added!!!
    #
    #     # Find out which aircraft are currently inside the experiment area, and
    #     # determine which aircraft need to be deleted.
    #     inside = areafilter.checkInside(self.name, traf.lat, traf.lon, traf.alt)
    #     delidx = np.intersect1d(np.where(np.array(self.inside)==True), np.where(np.array(inside)==False))
    #     self.inside = inside
    #
    #     # Log flight statistics when for deleted aircraft
    #     if len(delidx) > 0:
    #         self.logger.log(
    #             np.array(traf.id)[delidx],
    #             self.create_time[delidx],
    #             sim.simt - self.create_time[delidx],
    #             self.distance2D[delidx],
    #             self.distance3D[delidx],
    #             self.work[delidx],
    #             traf.lat[delidx],
    #             traf.lon[delidx],
    #             traf.alt[delidx],
    #             traf.tas[delidx],
    #             traf.vs[delidx],
    #             traf.hdg[delidx],
    #             # traf.ap.origlat[delidx],
    #             # traf.ap.origlon[delidx],
    #             # traf.ap.destlat[delidx],
    #             # traf.ap.destlon[delidx],
    #             traf.asas.active[delidx],
    #             traf.pilot.alt[delidx],
    #             traf.pilot.tas[delidx],
    #             traf.pilot.vs[delidx],
    #             traf.pilot.hdg[delidx]
    #         )
    #
    #         # delete all aicraft in self.delidx
    #         traf.delete(delidx)
    #
    # def set_area(self, *args):
    #     ''' Set Experiment Area. Aicraft leaving the experiment area are deleted.
    #     Input can be exisiting shape name, or a box with optional altitude constrainsts.'''
    #
    #     # if all args are empty, then print out the current area status
    #     if not args:
    #         return True, "Area is currently " + ("ON" if self.active else "OFF") + \
    #                      "\nCurrent Area name is: " + str(self.name)
    #
    #     # start by checking if the first argument is a string -> then it is an area name
    #     if isinstance(args[0], str) and len(args)==1:
    #         if areafilter.hasArea(args[0]):
    #             # switch on Area, set it to the shape name
    #             self.name = args[0]
    #             self.active = True
    #             self.logger.start()
    #             return True, "Area is set to " + str(self.name)
    #         if args[0]=='OFF' or args[0]=='OF':
    #             # switch off the area
    #             areafilter.deleteArea(self.name)
    #             self.logger.reset()
    #             self.active = False
    #             self.name = None
    #             return True, "Area is switched OFF"
    #
    #         # shape name is unknown
    #         return False, "Shapename unknown. " + \
    #             "Please create shapename first or shapename is misspelled!"
    #     # if first argument is a float -> then make a box with the arguments
    #     if isinstance(args[0],(float, int)) and 4<=len(args)<=6:
    #         self.active = True
    #         self.name = 'DELAREA'
    #         areafilter.defineArea(self.name, 'BOX', args[:4], *args[4:])
    #         self.logger.start()
    #         return True, "Area is ON. Area name is: " + str(self.name)
    #
    #     return False,  "Incorrect arguments" + \
    #                    "\nAREA Shapename/OFF or\n Area lat,lon,lat,lon,[top,bottom]"
    #
    # def set_taxi(self, flag):
    #     If you want to delete below 1500ft,
    #         make an box with the bottom at 1500ft and set it to Area.
    #         This is because taxi does nothing. 
    #     self.swtaxi = flag
                                    """