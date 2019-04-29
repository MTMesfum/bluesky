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
    global timewindow
    timewindow = TimeWindow()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'TIMEWINDOW',

        # The type of this plugin. For now, only simulation plugins are possible.
        'plugin_type':     'sim',

        # Update interval in seconds. By default, your plugin's update function(s)
        # are called every timestep of the simulation. If your plugin needs less
        # frequent updates provide an update interval.
        'update_interval': 1.0,

        # The update function is called after traffic is updated. Use this if you
        # want to do things as a result of what happens in traffic. If you need to
        # something before traffic is updated please use preupdate.
        'update':          update,

        # The preupdate function is called before traffic is updated. Use this
        # function to provide settings that need to be used by traffic in the current
        # timestep. Examples are ASAS, which can give autopilot commands to resolve
        # a conflict.
        'preupdate':       preupdate,

        # If your plugin has a state, you will probably need a reset function to
        # clear the state in between simulations.
        'reset':         timewindow.reset
        }

    stackfunctions = {
        # The command name for your function
        'TIMEWINDOW': [
            'TIMEWINDOW ON/OFF',
            '[onoff]',
            timewindow_talk,
            'Activate or deactivate timewindow based waypoints.'
        ],
        'DEFWPT2': [
            "DEFWPT2 wpname, lat, lon, RTA HH:MM:SS, TW",
            "txt, latlon, txt, int",
            timewindow.defwpt2,
            "Define a waypoint only for this scenario/run with a RTA and TW"
        ],
        "POS2": [
            "POS2 waypoint",
            "wpt",
            timewindow.poscommand2,
            "Get info on a waypoint including RTA and TW"
        ]
    }

    # init_plugin() should always return these two dicts.
    return config,  stackfunctions

class TimeWindow(Navdatabase):
    def __init__(self):
        super().__init__()
        # self.wpRTA =

    def defwpt(self,name=None,lat=None,lon=None,wptype=None):
        print('Im in TimeWindow.')
        # stack.stack("DEFWPT %s, %s, %s " % (name, lat, lon) )
        stack.stack("ECHO I'm testing!!!")
        super().defwpt(name, lat, lon, wptype)

        pass

    def defwpt2(self, name=None, lat=None, lon=None, RTA=None, TW=None):
        stack.stack("DEFWPT %s, %s, %s " % (name, lat, lon) )
        # Navdatabase.defwpt(name, lat, lon)
        print('The additional values are ', RTA, ' and ', TW)
        self.wpRTA.append(RTA)
        self.wpTW.append(TW)
        # print(self.wpRTA)

    def poscommand2(self, idxorwp):
        stack.stack("POS %s " % idxorwp )
        # super(TimeWindow, self).poscommand(idxorwp)
        print('I do pass here')
        if type(idxorwp) == int and idxorwp >= 0:
            print('Apparantly, Im a fckin airplane??')
        else:
            wp = idxorwp.upper()

            # Reference position for finding nearest
            reflat, reflon = bs.scr.getviewctr()
            iwps = bs.navdb.getwpindices(wp, reflat, reflon)
            lines = "Info on "+wp+":\n"
            #
            #
            # if iwps[0] >= 0:
            #     typetxt = ""
            #     desctxt = ""
            #     lastdesc = "XXXXXXXX"
            #     for i in iwps:
            #
            #         # One line type text
            #         if typetxt == "":
            #             typetxt = typetxt + bs.navdb.wptype[i]
            #         else:
            #             typetxt = typetxt + " and " + bs.navdb.wptype[i]
            #
            #         # Description: multi-line
            #         samedesc = bs.navdb.wpdesc[i] == lastdesc
            #         if desctxt == "":
            #             desctxt = desctxt + bs.navdb.wpdesc[i]
            #             lastdesc = bs.navdb.wpdesc[i]
            #         elif not samedesc:
            #             desctxt = desctxt + "\n" + bs.navdb.wpdesc[i]
            #             lastdesc = bs.navdb.wpdesc[i]
            #
            #         # Navaid: frequency
            #         if bs.navdb.wptype[i] in ["VOR", "DME", "TACAN"] and not samedesc:
            #             desctxt = desctxt + " " + str(bs.navdb.wpfreq[i]) + " MHz"
            #         elif bs.navdb.wptype[i] == "NDB" and not samedesc:
            #             desctxt = desctxt + " " + str(bs.navdb.wpfreq[i]) + " kHz"
            #
            #     iwp = iwps[0]
            #
            #     # Basic info
            #     lines = lines + wp + " is a " + typetxt \
            #             + " at\n" \
            #             + latlon2txt(bs.navdb.wplat[iwp], \
            #                          bs.navdb.wplon[iwp])
            #
            #     # How many others?
            #     nother = bs.navdb.wpid.count(wp) - len(iwps)
            #     if nother > 0:
            #         verb = ["is ", "are "][min(1, max(0, nother - 1))]
            #         lines = lines + "\nThere " + verb + str(nother) + \
            #                 " other waypoint(s) also named " + wp
            #
            #     # In which airways?
            #     connect = bs.navdb.listconnections(wp, \
            #                                        bs.navdb.wplat[iwp],
            #                                        bs.navdb.wplon[iwp])
            #     if len(connect) > 0:
            #         awset = set([])
            #         for c in connect:
            #             awset.add(c[0])
            #
            #         lines = lines + "\nAirways: " + "-".join(awset)

            # print(iwp)
            name = idxorwp.upper()
            try:
                i = self.wpid.index(name)
            except:
                return -1

            idx = []
            idx.append(i)
            found = True
            while i < len(self.wpid) - 1 and found:
                try:
                    i = self.wpid.index(name, i + 1)
                    idx.append(i)
                except:
                    found = False
            if len(idx) == 1:
                iwp = idx[0]
            else:
                imin = idx[0]
                dmin = geo.kwikdist(reflat, reflon, self.wplat[imin], self.wplon[imin])
                for i in idx[1:]:
                    d = geo.kwikdist(reflat, reflon, self.wplat[i], self.wplon[i])
                    if d < dmin:
                        imin = i
                        dmin = d
                iwp = imin
        print(iwp)
        RTA = self.wpRTA[iwp]
        print(self.wpRTA)
        TW = self.wpTW[iwp]
        # Position report

        lines = "RTA: %s. TW: %s" % (RTA, TW)

        print(lines)
        print('Why doesnt this work ??')
        return True, lines

    def reset(self):
        super().reset()
        self.wpRTA = list( -1 * np.ones(len(self.wpid)) )
        self.wpTW = list( -1 * np.ones(len(self.wpid)) )
        # print(type(self.wpRTA))
        pass

# class TimeWindow(Traffic):
#     def __init__(self):
#         super(TimeWindow, self).__init__()



def timewindow_talk(apple):
    print('This is timewindow!')

def update():
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
