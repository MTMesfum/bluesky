""" This plugin is going to regulate the time-window and RTA constraint.
    The way it works is by dividing the remaining distance by the leftover time.
    This will create a minimum and maximum speed required to match the RTA.
    The speed of the aircraft has to stay within the window. If the window
    is breached, then the speed has to be set to either the minimum or maximum speed
    depending on the breach. The initial version will not take wind into account,
    but this can be implemented very easily if the initial concept works.

    The following properties have to be changed or adapted;
    1) Store time constraints for waypoints
    2) Find the active waypoint and extract the lat/lon and RTA
    3) Use the aircraft's lat/lon, simtime, active wpt lat/lon and RTA to calculate the min/max speed
    4) Check whether the current speed lies within this window;
        - if it does    : do nothing
        - if it doesn't : set the speed to either min/max
    5) If no RTA is submitted, then this plugin should be passed

    *** The waypoints of this plugin should work interchangeably with the standard waypoints """

# Import the global bluesky objects. Uncomment the ones you need
from bluesky import stack, settings, navdb #, traf, sim, scr, tools
from bluesky.navdatabase import * # Navdatabase #navdb #.navdatabase import navdatabase
from bluesky.traffic import route
from bluesky.tools import geo
from bluesky.tools import TrafficArrays, RegisterElementParameters
from bluesky.tools.misc import latlon2txt
# from bluesky.Navdatabase import defwpt
# from bluesky import navdatabase
import numpy as np
from bluesky.traffic import Traffic
import bluesky as bs

# Global data
timewindow = None

### Initialization function of your plugin. Do not change the name of this
### function, as it is the way BlueSky recognises this file as a plugin.
def init_plugin():

    # Addtional initilisation code
    global timewindow, timewindow2
    timewindow      = TimeWindow()
    timewindow2     = TimeWindow2()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name'   :   'TIMEWINDOW',
        'plugin_type'   :   'sim',
        'update'        :   timewindow2.update,
        'preupdate'     :   preupdate,
        'reset'         :   timewindow.reset
        }

    stackfunctions = {
        'TIMEWINDOW': [
            'TIMEWINDOW ON/OFF',
            '[onoff]',
            timewindow_talk,
            'Activate or deactivate timewindow based waypoints [doesnt work yet].'
        ],
        'DEFWPT2': [
            "DEFWPT2 wpname, lat, lon, RTA HH:MM:SS, TW",
            "txt,latlon,[txt,int]",
            timewindow.defwpt2,
            "Define a waypoint only for this scenario/run with a RTA and TW"
        ],
        "POS2": [
            "POS2 waypoint",
            "wpt",
            timewindow.poscommand2,
            "Get info on a waypoint including its RTA and TW"
        ]
    }

    # init_plugin() should always return these two dicts.
    return config,  stackfunctions

class TimeWindow(Navdatabase):
    def __init__(self):
        super(TimeWindow, self).__init__()
        # from bs.navdatabase import Navdatabase
        # from bs.loadnavdata import load_aptsurface, load_coastlines
        # self.wpRTA =

    def defwpt(self,name=None,lat=None,lon=None,wptype=None):
        print('Im in TimeWindow.')
        stack.stack("DEFWPT %s, %s, %s, %s " % (name, lat, lon, wptype))
        # stack.stack("ECHO I'm testing!!!")
        super(TimeWindow, self).defwpt(name, lat, lon, 'RTA')
        self.wpRTA.append(None)
        self.wpTW.append(None)

    def defwpt2(self, name=None, lat=None, lon=None, RTA=None, TW=None):
        # stack.stack("DEFWPT %s, %s, %s " % (name, lat, lon) )
        # Navdatabase.defwpt(name, lat, lon)
        print('The additional values are ', RTA, ' and ', TW)
        super(TimeWindow, self).defwpt(name, lat, lon, 'RTA')
        stack.stack("DEFWPT %s, %s, %s, %s " % (name, lat, lon, 'RTA'))
        self.wpRTA.append(RTA)
        self.wpTW.append(TW)
        # self.wpid.index[-1] #(name) #[len(self.wpRTA)+1] = name
        # print(len(self.wpid))
        # print(len(self.wplat))
        # print(len(self.wplon))
        # print(len(self.wpRTA))
        # print((self.wpid[-150:]))
        # print((self.wplat[-150:]))
        # print((self.wplon[-150:]))
        # print((self.wpRTA[-150:]))
        # print((self.wpTW[-150:]))

    def poscommand2(self, idxorwp):
        # stack.stack("POS %s " % idxorwp )
        # super(TimeWindow, self).poscommand(idxorwp)
        wp = idxorwp.upper()
        reflat, reflon = bs.scr.getviewctr()
        wp2 = bs.navdb.getwpindices(wp,reflat,reflon)

        # try:
        i = self.wpid.index(wp) #int(wp2[0])
        # except:
        #     return -1
        # print('i is: ', i)
        # print(len((self.wpRTA)))
        # print(len((self.wpTW)))

        # Position report
        lines = "Info on " + wp + ":\n" \
                + latlon2txt(bs.navdb.wplat[wp2[0]], \
                        bs.navdb.wplon[wp2[0]]) + "\n" \
                + "RTA: %s; TW: %s [s]" % (str(self.wpRTA[i]), str(self.wpTW[i]))
        print(lines)
        return True, lines

    def reset(self):
        super(TimeWindow, self).reset()
        self.wpRTA = len(self.wpid) * [None]
        self.wpTW = len(self.wpid) * [None]
        # print(len(self.wpRTA))
        # print(type(self.wpRTA))
        pass

# class TimeWindow2(Route):
#     def __init__(self):
#         super(TimeWindow2, self).__init__()
#
#     def _del_wpt_data(self, idx):
#         del self.wpRTA[idx]
#         del self.wpTW[idx]

# class TimeWindow2(Traffic):
#     def poscommand(self, idxorwp):
#         print(' TEST TEST')
#         super(TimeWindow2, self).poscommand(idxorwp)
#         print(' TEST TEST')
#         wp = idxorwp.upper()
#         reflat, reflon = bs.scr.getviewctr()
#         iwps = bs.navdb.getwpindices(wp, reflat, reflon)
#         iwp = iwps[0]
#         print(bs.navdb.wplon[iwp])
#         print(' TEST TEST')

# class TimeWindow(Traffic):
#     def __init__(self):
#         super(TimeWindow, self).__init__()

# def load_navdata_txt():
#     wptdata, aptdata, awydata, firdata, codata = .load_navdata_text()
#     wptdata['wpRTA']    = []
#     wptdata['wpTW']     = []
    # wptdata['wpRTA'][10] = 10



def timewindow_talk(apple):
    print('This is timewindow!')

class TimeWindow2(Traffic):
    def __init__(self):
        super(TimeWindow2, self).__init__()

    def update(self):
        #   1) Find the flying aircraft along with its position
        # print('This is update in TimeWindow PLugin!')
        if self.ntraf == 0:
            return

        #   2) Find their active waypoints
        #   3) Find the corresponding RTA and TW
        #   4) Calculate the min/max speed of the aircraft to reach the waypoint
        #   5) If the speed exceeds the range of these speeds,
        #           then set the speed to either the minimum or maximum.
        pass

def preupdate():
    pass


#
#         defwpt(name, lat, lon, )
#         # Prevent polluting the database: check arguments
#         if name == None or name == "":
#             return False, "Insufficient arguments"
#         elif name.isdigit():
#             return False, "Name needs to start with an alphabetical character"
#
#         # No data: give info on waypoint
#         elif lat == None or lon == None:
#             reflat, reflon = bs.scr.getviewctr()
#             if self.wpid.count(name.upper()) > 0:
#                 i = self.getwpidx(name.upper(), reflat, reflon)
#                 txt = self.wpid[i] + " : " + str(self.wplat[i]) + "," + str(self.wplon[i])
#                 if len(self.wptype[i] + self.wpco[i]) > 0:
#                     txt = txt + "  " + self.wptype[i] + " in " + self.wpco[i]
#                 return True, txt
#
#             # Waypoint name is free
#             else:
#                 return True, "Waypoint " + name.upper() + " does not yet exist."
#
#         # Still here? So there is data, then we add this waypoint
#         self.wpid.append(name.upper())
#         self.wplat = np.append(self.wplat, lat)
#         self.wplon = np.append(self.wplon, lon)
#
#         if wptype == None:
#             self.wptype.append("")
#         else:
#             self.wptype.append(wptype)
#
#         self.wpelev.append(0.0)  # elevation [m]
#         self.wpvar.append(0.0)  # magn variation [deg]
#         self.wpfreq.append(0.0)  # frequency [kHz/MHz]
#         self.wpdesc.append("Custom waypoint")  # description
#
#         # Update screen info
#         bs.scr.addnavwpt(name.upper(), lat, lon)
#
#         return True  # ,name.upper()+" added to navdb."
#
#
#
# def update():
#     stack.stack('ECHO MY_PLUGIN update: creating a random aircraft')
#     stack.stack('MCRE 1')
#
# def preupdate():
#     pass
#
# def reset():
#     pass
#
# ### Other functions of your plugin
# def myfun(flag=True):
#     return True, 'My plugin received an o%s flag.' % ('n' if flag else 'ff')
