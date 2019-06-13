# import numpy as np
# import sys
# from math import *
import pandas as pd, os, datetime, random
# import pdb
# import fileinput as fi
# import geo
# from bluesky.tools import geo
from bluesky.tools.geo import qdrdist as dist
from bluesky.tools.geo import latlondist as dist2
# from plugins.fms_mode import _eta2tw_cas_wfl as time_required2
# from bluesky.tools.geo import vmach2cas as M2C
from bluesky.tools import aero
import numpy as np
import timeit
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from xml.etree import ElementTree
#from BlueSky import main
# print(sys.argv)
#sys.argv.append("--headless")
#sys.arg,"--scenfile","\experimental\Trajectories.scn"])
#main()

settings_config = "settings.cfg"
scenario_manager = "scenario\Trajectories-batch3.scn"
scenario_manager2 = "scenario\Trajectories-batch4.scn"
exp = "scenario\Trajectories-batch2.scn"
save_ic = "scenario\\trajectories_saveic.scn"
dest_dir_input_logs = "output\\runs\\xlogs input"
dest_dir_output_logs = "output\\runs\\xlogs output"
writer_file = 'output\WRITER Standard File.xlsx'
wind_ensemble = "Tigge_2014-09-08_00_243036.nc"
flight_date = "9,9,2014"
dt = 0.5
TW_inf = 3600  # [s]
TW_min = 60  # [s]
set_of_delays = [0, 90, 720, 1050]  # [s]

# drive_folder = '/BlueSky Simulation/Run [ X ]/'
# # drive_folder_inf = '0'
# # drive_folder_prob = '0'
# # drive_folder_det = '0'
# # drive_folder_min = '0'
# # drive_folder_output = '0'
# # drive_folder_input = '0'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    UWARNING = '\033[4m' + '\033[93m'
    UBLUE = '\033[4m' + '\033[94m'

def set_delays(input= [0, 90, 720, 1050]):
    global set_of_delays
    set_of_delays = input
    pass


def find_index(to_search, target):
    for number, i in enumerate(to_search):
        if target == i:
            return number
    return

# Replace the dt in the settings.cfg
def find_dt():

    with open(settings_config, 'r') as f:
        filedata = f.read()

    apple = filedata.find('simdt =')
    banana = filedata.find('# Snaplog dt')
    dt_settings = filedata[apple+8:banana-3]

    return dt_settings

# Switches the ensemble in the scenario manager and adapts the name using the ensemble # and global dt
def replace_ensemble(ensemble, file=None):
    if file == None:
        file = scenario_manager
    else:
        file = 'scenario\\' + file

    with open(file, 'r') as f:
        filedata = f.read()

    ensemble = str(ensemble)
    apple = filedata.find('LOAD_WIND')
    banana = filedata.find(', Tigge_')
    # citrus = filedata.find('WRITER')
    # date = filedata.find('_dt_')
    filedata = str("".join(filedata[0:apple+11] + str(ensemble).zfill(2) +
                           filedata[banana:]))
                           # filedata[banana:citrus+8] + str(ensemble) + filedata[date:]))

    with open(file, 'w') as f:
        f.write(filedata)

    # os.startfile(scenario_manager)
    pass

def replace_batch(scen_new):
    with open(scenario_manager, 'r') as f:
        filedata = f.read()

    apple = filedata.find('PCALL "')
    banana = filedata.find('.scn')
    filedata = str("".join(filedata[0:apple+7] + str(scen_new) +
                           filedata[banana+4:]))

    with open(scenario_manager, 'w') as f:
        f.write(filedata)

    # os.startfile(scenario_manager)

def replace_batch_set(scen_new, source, save_file):
    dir = os.getcwd()
    dest_dir = dir + "\\scenario\\" + save_file + '.scn'
    with open("scenario\\" + source + '.scn', 'r') as f:
        filedata = f.read()
    for i, j in enumerate(set_of_delays):
        apple = filedata.find('"Trajectories.scn"')
        banana = apple + len('"Trajectories.scn" ')
        filedata = str("".join(filedata[:apple+1] + str(scen_new)[:-4-len(str(set_of_delays[0]))]
                            + str(set_of_delays[i]) + '.scn" ' + str(i).zfill(2)
                               + filedata[banana+2:]))
        with open(dest_dir, 'w') as f:
            f.write(filedata)
        with open("scenario\\" + save_file + '.scn', 'r') as f:
            filedata = f.read()
    # os.startfile(dest_dir)

def replace_batch_set2(scen_new, source, save_file):
    dir = os.getcwd()
    folder = "\\scenario\\remon scen\\" + scen_new
    FileName = os.listdir(dir + folder)
    dest_dir = dir + "\\scenario\\" + save_file + '.scn'
    with open("scenario\\" + source + '.scn', 'r') as f:
        filedata = f.read()
    for i, j in enumerate(FileName):
        apple = filedata.find('"Trajectories.scn"')
        banana = apple + len('"Trajectories.scn" 00')
        filedata = str("".join(filedata[:apple+1] + "remon scen\\"
                               + str(scen_new) + "\\" + j + filedata[banana:]))
        with open(dest_dir, 'w') as f:
            f.write(filedata)
        with open("scenario\\" + save_file + '.scn', 'r') as f:
            filedata = f.read()

# Changes the timestep in the settings config of BlueSky using the provided timestep
# Keep in mind that the savefile doesn't change its name, unless the timestep is set into the global variable dt
def set_dt(timestep=dt):
    global dt
    dt = timestep

    with open(settings_config, 'r') as f:
        filedata = f.read()

    apple = filedata.find('simdt =')
    banana = filedata.find('# Performance')
    filedata = str("".join(filedata[0:apple+8] + str(timestep) + '\n \n' + filedata[banana:]))

    with open(settings_config, 'w') as f:
        f.write(filedata)

    print('\nThe timestep has been changed to {0} seconds.\n'.format(dt))
    # print('The dt is {0} seconds.\n'.format(dt))
    # os.startfile(settings_config)
    pass

# Switches the speed in run_experiment
def replace_speed(speed):
    with open(exp, 'r') as f:
        filedata = f.read()

    apple = filedata.find('run_experiment') #+16
    banana = filedata.find('00:00:00.00> FF')
    filedata = str("".join(filedata[0:apple+16] + str(speed) + filedata[banana-1:]))

    with open(exp, 'w') as f:
        f.write(filedata)

    # os.startfile(exp)
    pass

# Run a simulation of BlueSky using the desktop path
def bs_desktop():
    global drive_folder, drive_folder_inf, drive_folder_prob, \
        drive_folder_det, drive_folder_min, drive_folder_output, drive_folder_input
    drive_folder = '/BlueSky Simulation/Run Desktop Home/'
    drive_folder_inf = '12LqgB2NtdHGU2EspFY5tgmO88fc53XEj'
    drive_folder_prob = '1N-V2AQzv2SnaUt_sGb6sxns3PZ3sEwmz'
    drive_folder_det = '1GzpfVUNmcCiM69mfvf0c-2eqCKIDqlYB'
    drive_folder_min = '1mE8bK9LmptxXHQbzKkSwSaNZsFw-HGGE'
    drive_folder_output = '1W_v0EuNL6WxpT18aHsf_PO6oHYXDDSNi'
    drive_folder_input = '1N7p25hQTLqmRUR_YAOPsdHvLHBeiRWF3'
    os.system("call C:\Programs\Tools\Anaconda\Program\Scripts\\activate.bat && \
                    cd C:\Documents\Git 2 && conda activate py36 && python BlueSky.py")

# Run a simulation of BlueSky using the laptop path
def bs_laptop():
    global drive_folder, drive_folder_inf, drive_folder_prob, \
        drive_folder_det, drive_folder_min, drive_folder_output, drive_folder_input
    drive_folder = '/BlueSky Simulation/Run Laptop/'
    drive_folder_inf = '12LqgB2NtdHGU2EspFY5tgmO88fc53XEj'
    drive_folder_prob = '1N-V2AQzv2SnaUt_sGb6sxns3PZ3sEwmz'
    drive_folder_det = '1GzpfVUNmcCiM69mfvf0c-2eqCKIDqlYB'
    drive_folder_min = '1mE8bK9LmptxXHQbzKkSwSaNZsFw-HGGE'
    drive_folder_output = '1W_v0EuNL6WxpT18aHsf_PO6oHYXDDSNi'
    drive_folder_input = '1N7p25hQTLqmRUR_YAOPsdHvLHBeiRWF3'
    os.system("call I:\Programs\Anaconda\Program\Scripts\\activate.bat && \
                    cd I:\Documents\Google Drive\Thesis 2018\BlueSky Git4 && python BlueSky.py")

# Cut the number to 3 digits
def cut3(one):
    return round(one, 3)

# Cut the number to 7 digits
def cut7(one):
    return round(one, 7)

# Add a random delay to the time provided
# def addSecs(tm, secs, secs2):
def addSecs(time, set_of_delays2):
    if set_of_delays2 == []:
        set_of_delays2 = [0]
    list_of_times = [time + datetime.timedelta(seconds=x) for x in set_of_delays2]
    return list_of_times, set_of_delays2

# Create a scenario file from the provided trajectories and save it in the provided name
# The first entry in the method decides whether a random delay is added
def CreateSCN(alpha, save_file, folder = "queries\\"):
    FileName = os.listdir(folder)
    # FileName.remove('hide')
    traj = 0
    banana = list()
    scenario2 = pd.DataFrame()

    for k in FileName:
        _, ext = os.path.splitext(k)
        if ext != '.csv':
            continue
        if not scenario2.empty:
            scenario2 = scenario2.append(pd.read_csv(folder + "\\" + k))
        else:
            scenario2 = pd.read_csv(folder + "\\" + k)

    scenario2 = scenario2.sort_values(by=['time_over']).reset_index(drop=True)

    for l in set(scenario2['trajectory_id']):
        scenario    = scenario2[scenario2['trajectory_id'][:] == scenario2['trajectory_id'][0]].reset_index(drop=True)
        scenario2   = scenario2[scenario2['trajectory_id'][:] != scenario2['trajectory_id'][0]].reset_index(drop=True)

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

        if alpha:
            apple = datetime.datetime(100, 1, 1, int(apple[-8:-6]), int(apple[-5:-3]), int(apple[-2:]))
            apple, delay = addSecs(apple, random.randrange(16), random.randrange(1))
        else:
            apple = apple[-8:]
        j = 0

        for i in range(scenario.shape[0]):
            if i != 0:
                j = -1

            # FlightLevel = str(scenario['fl'][i])
            # if FlightLevel.count('') < 3:
            #     FlightLevel = '0' + FlightLevel
            FlightLevel = 'FL' + str(scenario['fl'][i]).zfill(3)

            if i == 0:
                deltatime = datetime.datetime.strptime(scenario.time_over[i + 1], '%Y-%m-%d %H:%M:%S') - \
                            datetime.datetime.strptime(scenario.time_over[i ], '%Y-%m-%d %H:%M:%S')

                distance = abs(dist2(scenario['st_x(gpt.coords)'][i + 1], scenario['st_y(gpt.coords)'][i + 1],
                                     scenario['st_x(gpt.coords)'][i], scenario['st_y(gpt.coords)'][i]))

                height = abs((scenario['fl'][i + 1] - scenario['fl'][i]) * 100 * aero.ft)
                distance = (height ** 2 + distance ** 2) ** (1 / 2)

                speed = distance / deltatime.total_seconds()
                speed = aero.tas2cas(speed, int(FlightLevel[2:]) * 100 * aero.ft) * 3600 / aero.nm

                banana.append(apple + '.00> CRE ' + aircraftid + actype + str(cut7(scenario['st_x(gpt.coords)'][i]))
                              + ', ' + str(cut7(scenario['st_y(gpt.coords)'][i])) + ', '
                              + str(cut3(heading)) + ', 10, ' + str(cut3(speed))) #+ FlightLevel
                banana.append(apple + '.00> DEFWPT ' + aircraftid + '-ORIG,'
                              + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                              + str(cut7(scenario['st_y(gpt.coords)'][i])))
                banana.append(apple + '.00> ORIG ' + aircraftid + ', ' + aircraftid + '-ORIG')
                banana.append(apple + '.00> DEFWPT ' + aircraftid + '-DEST, '
                              + str(cut7(scenario['st_x(gpt.coords)'][scenario.shape[0]-1]))
                              + ', ' + str(cut7(scenario['st_y(gpt.coords)'][scenario.shape[0]-1])))
                banana.append(apple + '.00> DEST ' + aircraftid + ', ' + aircraftid + '-DEST' )
                banana.append(apple + '.00> ' + aircraftid + ' AT ' + aircraftid + '-DEST' + ' FL00/0.0')
                # banana.append(apple + '.00> DEST ' + aircraftid + ', '
                #                                + str(cut7(scenario['st_x(gpt.coords)'][scenario.shape[0]-1]))
                #                                + ' ' + str(cut7(scenario['st_y(gpt.coords)'][scenario.shape[0]-1])) )
            else:
                if i == scenario.shape[0]-1:
                    follow = aircraftid + '-' + str(i-1)
                    banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                  + aircraftid + "-DEST" + ', ' + FlightLevel + ', ' + '0')
                    banana.append(apple + '.00> ' + aircraftid + ' AT ' + aircraftid + '-' + str(i-1) +
                                        ' ' + FL_OLD + '/0')
                else:
                    deltatime   = datetime.datetime.strptime(scenario.time_over[i], '%Y-%m-%d %H:%M:%S') -\
                                    datetime.datetime.strptime(scenario.time_over[i+j], '%Y-%m-%d %H:%M:%S')

                    distance    = abs(dist2(scenario['st_x(gpt.coords)'][i+j], scenario['st_y(gpt.coords)'][i+j],
                                     scenario['st_x(gpt.coords)'][i], scenario['st_y(gpt.coords)'][i]))

                    height      = abs((scenario['fl'][i] - scenario['fl'][i+j]) * 100 * aero.ft)
                    distance    = (height**2 + distance**2)**(1/2)

                    speed = distance / deltatime.total_seconds()
                    speed = aero.tas2cas(speed, int(FlightLevel[2:]) * 100 * aero.ft) * 3600 / aero.nm

                    if i == 1:
                        follow = aircraftid + '-ORIG'
                    else:
                        follow = aircraftid + '-' + str(i-1)

                    banana.append(apple + '.00> DEFWPT ' + aircraftid + '-' + str(i) + ', '
                                  + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                                  + str(cut7(scenario['st_y(gpt.coords)'][i])))
                    banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                        + aircraftid + '-' + str(i) + ', ' + FlightLevel + ', ' + str(cut3(speed)))
                    if i >= 2:
                        banana.append(apple + '.00> ' + aircraftid + ' AT ' + aircraftid + '-' + str(i-1) +
                                        ' ' + FL_OLD + '/' + str(cut3(speed)))
            FL_OLD = FlightLevel

    #save = pd.DataFrame(banana)
    dir = os.getcwd()
    with open(dir + '/scenario/' + save_file + '.scn', "w") as fin:
        fin.write('\n'.join(banana))
    os.startfile(dir + '/scenario/' + save_file + '.scn')

    # os.startfile("F:\Documents\Python Scripts\ThesisScript")

# alpha = random delay
target_speed = 272.8 #A320
sub_FL = 0
def CreateSCN_Cruise(alpha, fl_ref, cap=999):
    if os.path.exists("scenario\\remon scen"):
        shutil.rmtree("scenario\\remon scen")
    folder = "scenario\\remon_raw_scenario\\"
    type_file = "AC Type 2.xlsx"
    FileName = os.listdir(folder)

    for index, k in enumerate(FileName):
        if cap == index:
            fl_ref = fl_ref - 20
        # print('FileName is: ', k)
        # print('FL_ref is: ', fl_ref)
        # print('cap is {} with index {}'.format(cap, index))
        if cap == index-1:
            return
        acid, ext = os.path.splitext(k)
        if ext != '.csv':
            continue
        scenario = pd.read_csv(folder + k)
        aircraftid = acid + '-%0'
        actype_file = pd.read_excel(folder + type_file)
        actype = actype_file[actype_file['id'].str.contains(k[0:7])]['AC type'].reset_index(drop=True)[0] + ', '
        TW_det = actype_file[actype_file['id'].str.contains(k[0:7])]['TW Det'].reset_index(drop=True)[0]
        TW_stoch = actype_file[actype_file['id'].str.contains(k[0:7])]['TW Stoch'].reset_index(drop=True)[0]

        scenario = scenario[scenario['fl']>fl_ref].reset_index(drop=True)
        apple = scenario.time_over[0]
        [heading, _] = dist(scenario['st_x(gpt.coords)'][0], scenario['st_y(gpt.coords)'][0],
                                    scenario['st_x(gpt.coords)'][1], scenario['st_y(gpt.coords)'][1])
        if heading < 0:
            heading += 360

        apple = datetime.datetime(100, 1, 1, int(apple[-8:-6]), int(apple[-5:-3]), int(apple[-2:]))
        basket_of_apples, set_of_delays2 = addSecs(apple, set_of_delays*alpha)

        replacement = zip(basket_of_apples, set_of_delays2)

        for apple, delay in replacement:
            apple = str(apple.time())
            m = 0
            for l in ['min', 'det', 'prob', 'inf']:
                banana = list()
                m += 1
                for i in range(scenario.shape[0]):
                    FlightLevel = 'FL' + str(scenario['fl'][i]-sub_FL).zfill(3)

                    if i == 0:
                        banana.append('00:00:00.00> FF')
                        banana.append(apple + '.00> CRE ' + aircraftid + ', ' + actype + str(cut7(scenario['st_x(gpt.coords)'][i]))
                                      + ', ' + str(cut7(scenario['st_y(gpt.coords)'][i])) + ', '
                                      + str(cut3(heading)) + ', ' + FlightLevel + ', ' + str(target_speed))
                        banana.append(apple + '.00> ASAS OFF')
                        banana.append(apple + '.00> PRINTER A delay of {0} seconds has been added.'.format(str(delay)))
                        banana.append(apple + '.00> DEFWPT ' + aircraftid + '-ORIG, '
                                      + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                                      + str(cut7(scenario['st_y(gpt.coords)'][i])))
                        banana.append(apple + '.00> ORIG ' + aircraftid + ', ' + aircraftid + '-ORIG')
                        banana.append(apple + '.00> DEFWPT ' + aircraftid + '-DEST '
                                      + str(cut7(scenario['st_x(gpt.coords)'][scenario.shape[0]-1]))
                                      + ', ' + str(cut7(scenario['st_y(gpt.coords)'][scenario.shape[0]-1]))
                                      + ', FLYOVER')
                        banana.append(apple + '.00> DEST ' + aircraftid + ', ' + aircraftid + '-DEST')
                        banana.append(apple + '.00> ' + aircraftid + ' AT ' + aircraftid
                                                        + '-DEST ' + 'FL' + str(scenario['fl'][-1:].reset_index(drop=True)[0]))
                    else:
                        if i == scenario.shape[0]-1:
                            follow = aircraftid + '-' + str(i-1)
                            follow2 = aircraftid + '-' + str(i)
                            banana.append(apple + '.00> DEFWPT ' + follow2 + ', '
                                          + str(cut7(scenario['st_x(gpt.coords)'][scenario.shape[0] - 1]))
                                          + ', ' + str(cut7(scenario['st_y(gpt.coords)'][scenario.shape[0] - 1]))
                                          + ', FLYOVER')
                            banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                          + follow2 + ', ' + FlightLevel)
                            banana.append(apple + '.00> ' + aircraftid + ' AT ' + follow +
                                                ' ' + FL_OLD)
                            banana.append(apple + '.00> ' + aircraftid + ' after ' + follow2 + ' ADDWPT '
                                          + aircraftid + "-DEST, " + FlightLevel)
                            banana.append(apple + '.00> ' + aircraftid + ' AT ' + follow2 +
                                                ' ' + FL_OLD)
                            o = list(range(0, scenario.shape[0], 5))
                            o.append(scenario.shape[0])
                            o.pop(0)
                            citrus1, citrus2, citrus3 = ([], [], [])
                            q = 1
                            time_to_add = 0
                            time = scenario.time_over[0]
                            time = datetime.datetime(1, 1, 1, int(time[-8:-6]), int(time[-5:-3]), int(time[-2:]))

                            for n in o:
                                if n == o[0]:
                                    wp_0 = aircraftid + '-ORIG ' #+ str(1) + ' '

                                wp_1 = aircraftid + '-' + str(n-1) + ' '

                                for p in range(q-1, n-1):
                                    [_, distance_local] = dist(scenario['st_x(gpt.coords)'][q-1],
                                                                scenario['st_y(gpt.coords)'][q-1],
                                                                scenario['st_x(gpt.coords)'][q],
                                                                scenario['st_y(gpt.coords)'][q])
                                    time_to_add += time_required2(distance_local, scenario['fl'][q]-sub_FL, target_speed)
                                    # time_to_add += time_required(distance_local, scenario['fl'][q]-sub_FL, target_speed)
                                    # print('Q is {} and time_to_add is {}'.format(q-1, time_to_add))
                                    q += 1

                                if l == 'min':      secs = TW_min/2
                                elif l == 'det':    secs = TW_det/2 * 60
                                elif l == 'prob':   secs = TW_stoch/2 * 60
                                elif l == 'inf':    secs = TW_inf/2

                                # now = dt.datetime.now()
                                delta = datetime.timedelta(seconds=(secs+round(time_to_add)))
                                # time_to_add = 0
                                t = time.time()
                                # print(t)
                                # 12:39:11.039864

                                # print(()
                                # print((dt.datetime.combine(dt.date(1, 1, 1), t) + delta).time())

                                # time = (datetime.datetime.combine(datetime.date(1, 1, 1), t) + delta)
                                time2 = (datetime.datetime.combine(datetime.date(1, 1, 1), t) + delta).time()
                                # print(time2)
                                banana.append(apple + '.00> ' + aircraftid + ' RTA_AT ' + wp_1 + str(time2))
                                citrus1.append(apple + '.00> ' + aircraftid + ' TW_SIZE_AT ' + wp_1 + str(int(secs*2)))
                                citrus2.append(apple + '.00> ' + aircraftid + ' OWN_SPD_FROM ' + wp_0 + ' ' + str(target_speed))
                                citrus3.append(apple + '.00> ' + aircraftid + ' AFMS_FROM ' + wp_0 + 'tw')
                                wp_0 = wp_1
                                del secs
                            banana = banana + citrus1 + citrus2 + citrus3
                            banana.append(apple + '.00> ' + aircraftid + ' AFMS_FROM ' + wp_1 + 'off')
                            banana.append(apple + '.00> VNAV ' + aircraftid + ' ON')
                            banana.append(apple + '.00> LNAV ' + aircraftid + ' ON')
                            # banana.append(apple + '.00> dt 0.5')

                        else:
                            if i == 1:
                                follow = aircraftid + '-ORIG'
                            else:
                                follow = aircraftid + '-' + str(i-1)

                            banana.append(apple + '.00> DEFWPT ' + aircraftid + '-' + str(i) + ', '
                                          + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                                          + str(cut7(scenario['st_y(gpt.coords)'][i])))
                            banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                                + aircraftid + '-' + str(i) + ', ' + FlightLevel)
                            if i >= 2:
                                banana.append(apple + '.00> ' + aircraftid + ' AT ' + aircraftid + '-' + str(i-1)
                                              + ' ' + FL_OLD)
                            [_, distance] = dist(scenario['st_x(gpt.coords)'][i], scenario['st_y(gpt.coords)'][i],
                                                    scenario['st_x(gpt.coords)'][i+1], scenario['st_y(gpt.coords)'][i+1])

                            # Time error calculation between database and bada
                            # time1 = scenario.time_over[i-1]
                            # time2 = scenario.time_over[i]
                            # time1 = datetime.datetime(100, 1, 1, int(time1[-8:-6]), int(time1[-5:-3]), int(time1[-2:]))
                            # time2 = datetime.datetime(100, 1, 1, int(time2[-8:-6]), int(time2[-5:-3]), int(time2[-2:]))
                            # time3 = time2 - time1
                            # print('\nWaypoint #', i)
                            # print('time required according to database: ', time3.total_seconds())
                            # print('time required according to bada: ',
                            #       time_required(distance, int(FlightLevel[2:]), 0.782))

                    FL_OLD = FlightLevel

                    dir = os.getcwd()
                    dest_dir = dir + '/scenario/remon scen/' + str(m) + ' ' + l + '/'

                    if not os.path.isdir(dest_dir):
                        os.makedirs(dest_dir)
                    with open(dest_dir + l + ' ' + acid + " D" + str(delay).strip() + '.scn', "w") as fin:
                        fin.write('\n'.join(banana))

            if not alpha:
                break


    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(scenario)

    # os.startfile("F:\Documents\Python Scripts\ThesisScript")
    return

# This function is meant to create a set of scenarios which runs every traj
# of 1 ensemble of a case out of [min, det, stoch, inf]
def CreateSCN_Cruise2(alpha, cap=999):
    if os.path.exists("scenario\\remon scen"):
        shutil.rmtree("scenario\\remon scen")
    folder = "scenario\\remon_raw_scenario\\"
    type_file = "AC Type 2.xlsx"
    FileName = os.listdir(folder)
    cruise_speed = pd.read_excel('C:\Documents\Git 2\queries\AC Cruise Speed.xlsx')
    sub_FL = 0
    # print(FileName)

    # How to build new scenarios:
    # -> get flight
    # -> run through min / det / stoch / inf
    # 	-> get TW size for respective min etc
    # 		-> run through set of delays
    # 		-> add to file
    # 	-> save respective min etc

    for index, k in enumerate(FileName):
        # if cap == index:
        #     fl_ref = fl_ref - 20
        # print('FileName is: ', k)
        # print('FL_ref is: ', fl_ref)
        # print('cap is {} with index {}'.format(cap, index))
        if cap == index-1:
            return
        acid, ext = os.path.splitext(k)
        if ext != '.csv':
            continue
        scenario = pd.read_csv(folder + k)
        actype_file = pd.read_excel(folder + type_file)
        actype = actype_file[actype_file['id'].str.contains(k[0:7])]['AC type'].reset_index(drop=True)[0] + ', '
        TW_det = actype_file[actype_file['id'].str.contains(k[0:7])]['TW Det'].reset_index(drop=True)[0]
        TW_stoch = actype_file[actype_file['id'].str.contains(k[0:7])]['TW Stoch'].reset_index(drop=True)[0]

        fl_ref = max(scenario['fl']) - 1
        scenario = scenario[scenario['fl'] > fl_ref].reset_index(drop=True)
        apple = scenario.time_over[0]
        [heading, _] = dist(scenario['st_x(gpt.coords)'][0], scenario['st_y(gpt.coords)'][0],
                                    scenario['st_x(gpt.coords)'][1], scenario['st_y(gpt.coords)'][1])
        if heading < 0:
            heading += 360

        target_speed = cruise_speed[cruise_speed['AC Type'] == actype[:-2]].Speed.item()
        apple = datetime.datetime(100, 1, 1, int(apple[-8:-6]), int(apple[-5:-3]), int(apple[-2:]))
        basket_of_apples, set_of_delays2 = addSecs(apple, set_of_delays*alpha)
        m = 0

        for l in ['min', 'det', 'prob', 'inf']:
            banana = list()
            banana.append('00:00:00.00> FF')
            m += 1
            replacement = zip(basket_of_apples, set_of_delays2)
            for apple, delay in replacement:
                # print(l)
                # print(apple, delay)
                apple = str(apple.time())
                aircraftid = acid + '-' + l + '-' + str(delay)
                for i in range(scenario.shape[0]):
                    FlightLevel = 'FL' + str(scenario['fl'][i]-sub_FL).zfill(3)

                    if i == 0:
                        banana.append(apple + '.00> CRE ' + aircraftid + ', ' + actype + str(cut7(scenario['st_x(gpt.coords)'][i]))
                                      + ', ' + str(cut7(scenario['st_y(gpt.coords)'][i])) + ', '
                                      + str(cut3(heading)) + ', ' + FlightLevel + ', ' + str(target_speed))
                        banana.append(apple + '.00> ASAS OFF')
                        banana.append(apple + '.00> PRINTER A delay of {0} seconds has been added.'.format(str(delay)))
                        banana.append(apple + '.00> DEFWPT ' + aircraftid + '-ORIG, '
                                      + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                                      + str(cut7(scenario['st_y(gpt.coords)'][i])))
                        banana.append(apple + '.00> ORIG ' + aircraftid + ', ' + aircraftid + '-ORIG')
                        banana.append(apple + '.00> DEFWPT ' + aircraftid + '-DEST '
                                      + str(cut7(scenario['st_x(gpt.coords)'][scenario.shape[0]-1]))
                                      + ', ' + str(cut7(scenario['st_y(gpt.coords)'][scenario.shape[0]-1]))
                                      + ', FLYOVER')
                        banana.append(apple + '.00> DEST ' + aircraftid + ', ' + aircraftid + '-DEST')
                        banana.append(apple + '.00> ' + aircraftid + ' AT ' + aircraftid
                                                        + '-DEST ' + 'FL' + str(scenario['fl'][-1:].reset_index(drop=True)[0]))
                    else:
                        if i == scenario.shape[0]-1:
                            follow = aircraftid + '-' + str(i-1)
                            follow2 = aircraftid + '-' + str(i)
                            banana.append(apple + '.00> DEFWPT ' + follow2 + ', '
                                          + str(cut7(scenario['st_x(gpt.coords)'][scenario.shape[0] - 1]))
                                          + ', ' + str(cut7(scenario['st_y(gpt.coords)'][scenario.shape[0] - 1]))
                                          + ', FLYOVER')
                            banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                          + follow2 + ', ' + FlightLevel)
                            banana.append(apple + '.00> ' + aircraftid + ' AT ' + follow +
                                                ' ' + FL_OLD)
                            banana.append(apple + '.00> ' + aircraftid + ' after ' + follow2 + ' ADDWPT '
                                          + aircraftid + "-DEST, " + FlightLevel)
                            banana.append(apple + '.00> ' + aircraftid + ' AT ' + follow2 +
                                                ' ' + FL_OLD)
                            o = list(range(0, scenario.shape[0], 5))
                            o.append(scenario.shape[0])
                            o.pop(0)
                            citrus1, citrus2, citrus3 = ([], [], [])
                            q = 1
                            time_to_add = 0
                            time = scenario.time_over[0]
                            time = datetime.datetime(1, 1, 1, int(time[-8:-6]), int(time[-5:-3]), int(time[-2:]))

                            for n in o:
                                if n == o[0]:
                                    wp_0 = aircraftid + '-ORIG ' #+ str(1) + ' '

                                wp_1 = aircraftid + '-' + str(n-1) + ' '

                                for p in range(q-1, n-1):
                                    [_, distance_local] = dist(scenario['st_x(gpt.coords)'][q-1],
                                                                scenario['st_y(gpt.coords)'][q-1],
                                                                scenario['st_x(gpt.coords)'][q],
                                                                scenario['st_y(gpt.coords)'][q])
                                    time_to_add += time_required2(distance_local, scenario['fl'][q]-sub_FL, target_speed)
                                    # time_to_add += time_required(distance_local, scenario['fl'][q]-sub_FL, target_speed)
                                    # print('Q is {} and time_to_add is {}'.format(q-1, time_to_add))
                                    q += 1

                                if l == 'min':      secs = TW_min/2
                                elif l == 'det':    secs = TW_det/2 * 60
                                elif l == 'prob':   secs = TW_stoch/2 * 60
                                elif l == 'inf':    secs = TW_inf/2

                                # now = dt.datetime.now()
                                delta = datetime.timedelta(seconds=(secs+round(time_to_add)))
                                # time_to_add = 0
                                t = time.time()
                                # print(t)
                                # 12:39:11.039864

                                # print(()
                                # print((dt.datetime.combine(dt.date(1, 1, 1), t) + delta).time())

                                # time = (datetime.datetime.combine(datetime.date(1, 1, 1), t) + delta)
                                time2 = (datetime.datetime.combine(datetime.date(1, 1, 1), t) + delta).time()
                                # print(time2)
                                banana.append(apple + '.00> ' + aircraftid + ' RTA_AT ' + wp_1 + str(time2))
                                citrus1.append(apple + '.00> ' + aircraftid + ' TW_SIZE_AT ' + wp_1 + str(int(secs*2)))
                                citrus2.append(apple + '.00> ' + aircraftid + ' OWN_SPD_FROM ' + wp_0 + ' ' + str(target_speed))
                                citrus3.append(apple + '.00> ' + aircraftid + ' AFMS_FROM ' + wp_0 + 'tw')
                                wp_0 = wp_1
                                del secs
                            banana = banana + citrus1 + citrus2 + citrus3
                            banana.append(apple + '.00> ' + aircraftid + ' AFMS_FROM ' + wp_1 + 'off')
                            banana.append(apple + '.00> VNAV ' + aircraftid + ' ON')
                            banana.append(apple + '.00> LNAV ' + aircraftid + ' ON')
                            # banana.append(apple + '.00> dt 0.5')

                        else:
                            if i == 1:
                                follow = aircraftid + '-ORIG'
                            else:
                                follow = aircraftid + '-' + str(i-1)

                            banana.append(apple + '.00> DEFWPT ' + aircraftid + '-' + str(i) + ', '
                                          + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                                          + str(cut7(scenario['st_y(gpt.coords)'][i])))
                            banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                                + aircraftid + '-' + str(i) + ', ' + FlightLevel)
                            if i >= 2:
                                banana.append(apple + '.00> ' + aircraftid + ' AT ' + aircraftid + '-' + str(i-1)
                                              + ' ' + FL_OLD)
                            [_, distance] = dist(scenario['st_x(gpt.coords)'][i], scenario['st_y(gpt.coords)'][i],
                                                    scenario['st_x(gpt.coords)'][i+1], scenario['st_y(gpt.coords)'][i+1])

                            # Time error calculation between database and bada
                            # time1 = scenario.time_over[i-1]
                            # time2 = scenario.time_over[i]
                            # time1 = datetime.datetime(100, 1, 1, int(time1[-8:-6]), int(time1[-5:-3]), int(time1[-2:]))
                            # time2 = datetime.datetime(100, 1, 1, int(time2[-8:-6]), int(time2[-5:-3]), int(time2[-2:]))
                            # time3 = time2 - time1
                            # print('\nWaypoint #', i)
                            # print('time required according to database: ', time3.total_seconds())
                            # print('time required according to bada: ',
                            #       time_required(distance, int(FlightLevel[2:]), 0.782))

                    FL_OLD = FlightLevel

            dest_dir = os.getcwd() + '/scenario/remon scen/' + str(m) + ' ' + l + '/'
            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)
            with open(dest_dir + l + ' ' + acid + '.scn', "w") as fin:
                fin.write('\n'.join(banana))

            # if not alpha:
            #     break


    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(scenario)

    # os.startfile("F:\Documents\Python Scripts\ThesisScript")
    with open(os.getcwd() + '/scenario/number_of_ac.txt', "w+") as fin:
        number = (len(FileName)-1) * len(set_of_delays)
        fin.write(str(number))

    return

def CreateSCN_FE(actype, FlightLevel, v_bada, delta, steps=0.001):
    # Setup for the SCN Manager and scenarios
    to_save = actype + ' ' + FlightLevel + '.scn'
    dir = 'data/performance/BS/aircraft'
    to_run = 'Flight Test/' + to_save
    actype_doc = actype + '.xml'
    path = os.path.join(dir, actype_doc)
    # start 50 3.5, [1] 51 3.5, [2] 52 3.5, [3] 53 3.5, [4] 54 3.5, [5] 55 3.5
    lat_start = 50
    lon_start = 3.5
    heading_start = 33
    # 51.75 2.17 35
    # lat_start = 51.75
    # lon_start = 2.17
    # heading_start = 19
    # WPT1: 54 3.5
    # Dest: 55 3.6

    # Create a SCN Manager
    files = os.listdir(dir)
    if actype_doc not in files:
        print('AC Type not found!')
        # os.startfile('C:\Documents\Git 2\\' + dir)
        # exit()
    # ac_doc = ElementTree.parse(path)
    # v_bada = float(ac_doc.find('speeds/cr_MA').text)

    gamma = list()
    gamma.append('# This is the scenario manager to find the speed corresponding to the lowest fuel consumption')
    gamma.append('00:00:00.00> SWRAD VOR')
    gamma.append('00:00:00.00> SAVEIC trajectories_saveic')
    gamma.append('00:00:00.00> CRELOG MYLOG 0.1 "MYLOG"')
    # gamma.append('00:00:00.00> MYLOG ADD traf.id, traf.lat, traf.lon, traf.perf.mass,')
    gamma.append('00:00:00.00> MYLOG ADD traf.id, traf.ax, traf.gs, pilot.tas, traf.lat, '
                 'traf.lon, traf.perf.fuelflow')
    gamma.append('00:00:00.00> MYLOG ON')
    gamma.append('00:00:00.00> FF')
    # gamma.append('00:00:00.00> PLUGIN REMOVE AFMS')
    # banana = list()
    # banana.append(apple + '.00> PLUGIN REMOVE AFMS')
    # dest_dir = os.getcwd() + '/scenario/Flight Test/'
    # to_save = actype + ' SPD=' + str(j) + ' ' + FlightLevel + '.scn'
    for i, j in enumerate(np.arange(v_bada - delta, v_bada + delta, steps)):
        # print("%.2f" % a)
        gamma.append('')
        gamma.append('# Load trajectories for a run')
        gamma.append('00:00:00.00> SCEN Test_' + str(i).zfill(2))
        j2 = str("%.4f" % j)[2:] #str(round(j, 3))[2:]
        # print(j2)
        # gamma.append('00:00:00.00> PCALL "{}" {}'.format(to_run, str(i).zfill(2)))
        gamma.append('00:00:00.00> PCALL "{}" {}, {}'.format(to_run, str(i).zfill(2), str(j2)))
                     # + "%.4f" % j)
        gamma.append('23:59:00.00> HOLD')

    # Create set of scenarios
    aircraftid = actype + '-%0'
    banana = list()
    apple = '00:00:00'
    banana.append(apple + '.00> CRE ' + aircraftid + ', ' + actype + ', ' + str(lat_start) + ', '
                  + str(lon_start) + ', ' + str(heading_start) + ', ' + FlightLevel + ', 0.%1')
    # banana.append(apple + '.00> SPD ' + aircraftid + ', 0.%1')
    banana.append(apple + '.00> ASAS OFF')
    banana.append(apple + '.00> DEFWPT ' + aircraftid + '-ORIG '
                  + str(lat_start) + ', ' + str(lon_start) + ', FLYOVER')
    banana.append(apple + '.00> ORIG ' + aircraftid + ', ' + aircraftid + '-ORIG')
    banana.append(apple + '.00> DEFWPT ' + aircraftid + '-DEST '
                  + str(lat_start+5) + ', ' + str(lon_start+5) + ', FLYOVER')
    banana.append(apple + '.00> DEST ' + aircraftid + ', ' + aircraftid + '-DEST')
    banana.append(apple + '.00> ' + aircraftid + ' AT ' + aircraftid + '-DEST ' + FlightLevel)
    follow = aircraftid + '-ORIG'

    for k in range(1, 5):
        follow2 = aircraftid + '-' + str(k)
        banana.append(apple + '.00> DEFWPT ' + follow2 + ', ' + str(lat_start+k)
                      + ', ' + str(lon_start+k) + ', FLYOVER')
        banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                      + follow2 + ', ' + FlightLevel)
        follow = follow2
    banana.append('00:00:15.00> FF')
    banana.append('23:00:00.00> EXIT')

    # Save the scenarios
    dest_dir = os.getcwd() + '\scenario\Flight Test\\'
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    with open(dest_dir + to_save, "w") as fin:
        fin.write('\n'.join(banana))

    # Save the SCNM after adding the distances between the waypoints
    for k in range(1, 4):
        _, distance = dist(lat_start+k, lon_start+k, lat_start+k+1, lon_start+k+1)
        gamma.append('# Distance between Waypoint {} and {} is {}.'.format(k-1, k, round(distance, 2)))
    with open(dest_dir + 'SCNM {} {}.scn'.format(actype, FlightLevel), "w") as fin:
        fin.write('\n'.join(gamma))
    # print(V_bada)
    # print(FlightLevel)
    pass

# Create a scenario manager to run a file alpha times, load wind ensemble beta and save the file in save_file
def CreateSCNM(alpha, beta, save_file):
    gamma = list()
    gamma.append('# Load wind data')
    gamma.append('00:00:00.00> LOAD_WIND ' + str(beta).zfill(2) + ', Tigge_01_09_2017.nc')
    gamma.append('00:00:00.00> DATE 1,9,2017')
    gamma.append('00:00:00.00> FF')

    for i in range(1, alpha):
        gamma.append('')
        gamma.append('# Load trajectories for a run')
        gamma.append('00:00:00.00> SWRAD VOR')
        gamma.append('00:00:00.00> SCEN Test_' + str(i).zfill(2))
        gamma.append('00:00:00.00> PCALL "Trajectories.scn" ' + str(i).zfill(2))
        gamma.append('00:00:00.00> FF')
        gamma.append('23:59:00.00> HOLD')

    gamma.append('')
    gamma.append('# Load trajectories for a run')
    gamma.append('00:00:00.00> SCEN Test_' + str(alpha).zfill(2))
    gamma.append('00:00:00.00> PCALL "Trajectories.scn" ' + str(alpha).zfill(2))
    gamma.append('00:00:00.00> SWRAD VOR')
    gamma.append('00:00:00.00> FF')
    gamma.append('23:58:59.00> WRITER W' + str(beta).zfill(2) + '_dt_' + str(dt))
    gamma.append('23:58:59.00> EXIT')

    dir = os.getcwd()
    with open(dir + '/scenario/' + save_file + '.scn', "w") as fin:
        fin.write('\n'.join(gamma))
    os.startfile(dir + '/scenario/' + save_file + '.scn')

# Create a different scenario manager to run a file [alpha times], load wind ensemble beta and save the file in save_file
def CreateSCNM2(save_file):
    alpha = len(set_of_delays)
    beta = 1
    gamma = list()
    gamma.append('# Load wind data')
    gamma.append('00:00:00.00> SAVEIC trajectories_saveic')
    gamma.append('00:00:00.00> CRELOG MYLOG 0.1 "MYLOG"')
    # gamma.append('00:00:00.00> MYLOG ADD traf.id, traf.lat, traf.lon, traf.perf.mass,')
    gamma.append('00:00:00.00> MYLOG ADD traf.id, traf.ax, traf.gs, pilot.tas, traf.lat, traf.lon, traf.perf.fuelflow')
    gamma.append('00:00:00.00> MYLOG ON')
    gamma.append('00:00:00.00> ASAS OFF')
    gamma.append('00:00:00.00> DATE ' + flight_date)
    gamma.append('00:00:00.00> LOAD_WIND2 ' + str(beta).zfill(2) +', ' + wind_ensemble)

    for i in range(1, alpha):
        gamma.append('')
        gamma.append('# Load trajectories for a run')
        gamma.append('00:00:00.00> SCEN Test_' + str(i).zfill(2))
        gamma.append('00:00:00.00> PCALL "Trajectories.scn" ' + str(i).zfill(2))
        gamma.append('00:00:00.00> FF')
        gamma.append('23:59:00.00> HOLD')

    gamma.append('')
    gamma.append('# Load trajectories for a run')
    gamma.append('00:00:00.00> SWRAD VOR')
    gamma.append('00:00:00.00> SCEN Test_' + str(alpha).zfill(2))
    gamma.append('00:00:00.00> PCALL "Trajectories.scn" ' + str(alpha).zfill(2))
    gamma.append('00:00:00.00> FF')
    # gamma.append('23:58:59.00> WRITER W' + str(beta).zfill(2) +'_dt_' +str(dt))
    gamma.append('23:58:59.00> EXIT')

    with open('scenario\\' + save_file + '.scn', "w") as fin:
        fin.write('\n'.join(gamma))
    # os.startfile('scenario\\' + save_file + '.scn')

# Create a different scenario manager to run a every traj of one ensemble
def CreateSCNM3(save_file):
    alpha = len(os.listdir(os.getcwd() + "\\scenario\\remon scen\\1 min\\"))
    beta = 1
    gamma = list()
    gamma.append('# Load wind data')
    gamma.append('00:00:00.00> SAVEIC trajectories_saveic')
    gamma.append('00:00:00.00> CRELOG MYLOG 10 "MYLOG"')
    # gamma.append('00:00:00.00> MYLOG ADD traf.id, traf.lat, traf.lon, traf.perf.mass,')
    gamma.append('00:00:00.00> MYLOG ADD traf.id, traf.ax, traf.gs, pilot.tas, traf.lat, traf.lon, traf.perf.fuelflow')
    gamma.append('00:00:00.00> MYLOG ON')
    gamma.append('00:00:00.00> SWRAD VOR')
    gamma.append('00:00:00.00> ASAS OFF')
    gamma.append('00:00:00.00> DATE ' + flight_date)
    gamma.append('00:00:00.00> LOAD_WIND2 ' + str(beta).zfill(2) +', ' + wind_ensemble)

    for i in range(1, alpha+1):
        gamma.append('')
        gamma.append('# Load trajectories for a run')
        gamma.append('00:00:00.00> SCEN Test_' + str(i).zfill(2))
        gamma.append('00:00:00.00> PCALL "Trajectories.scn" ' + str(i).zfill(2))
        gamma.append('00:00:00.00> FF')
        gamma.append('23:59:00.00> HOLD')

    # gamma.pop(-1)
    # gamma.append('23:58:59.00> WRITER W' + str(beta).zfill(2) +'_dt_' +str(dt))
    # gamma.append('23:58:59.00> EXIT')

    with open('scenario\\' + save_file + '.scn', "w") as fin:
        fin.write('\n'.join(gamma))
    # os.startfile('scenario\\' + save_file + '.scn')

# Clean up,  and open the output file
def writerfix(traj, dir, counter):
    dest_dir = 'output\\runs\{0}'.format(dir)
    df = pd.read_excel('output\WRITER Standard File.xlsx')
    # df = pd.read_csv('output\\runs\WRITER {0}.csv'.format(traj))
    # print(df)
    # df = df.drop('Unnamed: 0', axis=1)
    df.reset_index(inplace=True)
    df.index = df.index + 1
    df = df.drop('index', axis=1)
    name, _ = os.path.splitext(traj)

    dest_dir_input_logs2 = dest_dir_input_logs + "\\" + dir[0:7] + "\\" + traj[4:10]
    with open(dest_dir_input_logs2 + "\\" + dir[0:7] + " " + traj[4:10] +
              " IE01 D{}.scn".format(str(set_of_delays[0])), 'r') as f:
        filedata = f.read()
    apple = filedata.find('TW_SIZE_AT ')
    banana = filedata[apple+len('TW_SIZE_AT '):].find('TW_SIZE_AT ') + apple
    _, _, TW_size, *_ = filedata[apple:banana].split()

    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)
    df.to_excel(dest_dir + '\{0} TW={1}.xlsx'.format(name, TW_size))
    os.remove('output\WRITER Standard File.xlsx')
    print(bcolors.UBLUE     + '\n\nSaved'   +
          bcolors.FAIL      + ' [{1}] {0} '.format(traj, counter)   +
          bcolors.UBLUE     + 'in'      +
          bcolors.FAIL      + ' {0}'.format(
                              dest_dir + '\{0}.xlsx'.format(name)) +
          bcolors.ENDC)
    # os.startfile('output\\runs\WRITER {0}.xlsx'.format(traj))

# Clean up,  and open the output file
def writerfix2(dir, counter, upload):
    dest_dir = 'output\\runs\{0}'.format(dir)
    with open(scenario_manager2, 'r') as f:
        filedata = f.read()
    apple = filedata.find('LOAD_WIND2')
    banana = filedata.find(', ' + wind_ensemble)
    # [apple+len('TW_SIZE_AT '):].find('TW_SIZE_AT ') + apple
    # _, _, TW_size, *_ = filedata[apple:banana].split()
    ensemble = str(filedata[apple+11:banana]).zfill(2)

    # df.to_excel(dest_dir + '\{0} TW={1}.xlsx'.format(name, TW_size))
    new_name0 = '{} Ensemble={}.xlsx'.format(dir, ensemble)
    new_name = dest_dir + '\\{} Ensemble={}.xlsx'.format(dir, ensemble)
    # print('new name is: ', new_name)
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)
    os.rename(writer_file, new_name)
    if upload:
        drive_folder2 = drive_folder + dir + '/'
        upload_file(new_name, new_name0, drive_folder2)

    print(bcolors.UBLUE     + '\n\nSaved'   +
          bcolors.FAIL      + ' [{1}] {0} '.format(dir, counter)   +
          bcolors.UBLUE     + 'in'      +
          bcolors.FAIL      + ' {0}'.format(new_name) +
          bcolors.ENDC)
    # os.startfile('output\\runs\WRITER {0}.xlsx'.format(traj))

def movelog(ensemble, traj, dir):
    #Move the input log file into the input log folder
    dest_dir_input_logs2 = dest_dir_input_logs + "\\" + dir[0:7] + "\\" + traj[4:10]
    if not os.path.isdir(dest_dir_input_logs2):
        os.makedirs(dest_dir_input_logs2)

    with open(save_ic, 'r') as f:
        filedata = f.read()

    apple = filedata.find('PRINTER A delay of') #+16
    banana = filedata.find('seconds has been added')
    delay = filedata[apple+len('PRINTER A delay of '):banana]

    new_name = "\\" + dir[0:7] + " " + traj[4:10] + \
               " IE" + str(ensemble).zfill(2) + " D" + str(delay).strip() + ".scn"
    os.rename(save_ic, dest_dir_input_logs2 + new_name)

    #Move the output log file into the output log folder if the file exists
    dest_dir_output_logs2 = dest_dir_output_logs + "\\" + dir[0:7] + "\\" + traj[4:10]
    if not os.path.isdir(dest_dir_output_logs2):
        os.makedirs(dest_dir_output_logs2)
    files = os.listdir('output\\')
    files = [files[files.index(i)] for i in files if 'MYLOG' in i]
    if files == []:
        pass
    else:
        files = str(files[-1])
        new_name = "\\" + dir[0:7] + " " + traj[4:-4] + \
                   " OE" + str(ensemble).zfill(2) + " D" + str(delay).strip() + ".log"
        os.rename("output\\" + files, dest_dir_output_logs2 + new_name)
        # Analyse the data and open the file
        # compare_ff(dest_dir_output_logs2 + new_name)
    pass

def movelog2(ensemble_int, dir, upload):
    #Move the input log file into the input log folder
    dest_dir_input_logs2 = dest_dir_input_logs + "\\" + dir[0:7]
    if not os.path.isdir(dest_dir_input_logs2):
        os.makedirs(dest_dir_input_logs2)

    with open(save_ic, 'r') as f:
        filedata = f.read()

    apple = filedata.find('LOAD_WIND2') #+16
    banana = filedata.find(', ' + wind_ensemble)
    ensemble = str(filedata[apple+11:banana]).zfill(2)

    if ensemble != str(ensemble_int).zfill(2):
        print("The ensembles don't match!")
        print("Ensemble should be {} but {} has been read in!".format(ensemble_int, ensemble))

    new_name = '{} IEnsemble={}.scn'.format(dir, ensemble)
    new_name2 = dest_dir_input_logs2 + "\\" + new_name
    os.rename(save_ic, new_name2)
    if upload:
        drive_folder2 = drive_folder + dest_dir_input_logs[-11:] + '/'
        upload_file(new_name2, new_name, drive_folder2)

    #Move the output log file into the output log folder if the file exists
    dest_dir_output_logs2 = dest_dir_output_logs + "\\" + dir[0:7]
    if not os.path.isdir(dest_dir_output_logs2):
        os.makedirs(dest_dir_output_logs2)
    files = os.listdir('output\\')
    files = [files[files.index(i)] for i in files if 'MYLOG' in i]
    if files == []:
        pass
    else:
        new_name = '{} OEnsemble={}.log'.format(dir, ensemble)
        new_name2 = dest_dir_output_logs2 + '\\' + new_name
        os.rename("output\\" + str(files[-1]), new_name2)
        if upload:
            drive_folder2 = drive_folder + dest_dir_output_logs[-12:] + '/'
            upload_file(new_name2, new_name, drive_folder2)
        # Analyse the data and open the file
        # compare_ff(dest_dir_output_logs2 + new_name)
    pass

def clear_mylog():
    files = os.listdir('output\\')
    files = [files[files.index(i)] for i in files if 'MYLOG' in i]
    for i in files:
        os.remove('output\\' + i)
        print('The file {} has been deleted!'.format(i))

def talk_time(runs):
    print(bcolors.UWARNING + "\nExecuting simulation {1} and {0} seconds have passed!".format(
        int(timeit.default_timer()), runs) + bcolors.ENDC)
    if runs > 1:
        print(bcolors.UWARNING +
              "This results in {0} seconds per run!".format(int(timeit.default_timer() / (runs - 1)))
              + bcolors.ENDC)

def talk_traj(scen_next, traj_counter):
    print(bcolors.UWARNING + '\nReplaced Trajectory to' +
          bcolors.FAIL + ' [{1}] {0}'.format(scen_next, traj_counter + 1) +
          bcolors.ENDC)

def talk_traj2(scen_next, traj_counter):
    print(bcolors.UWARNING + '\nReplaced Trajectories to' +
          bcolors.FAIL + ' [{1}] {0}'.format(scen_next[:-7], traj_counter + 1) +
          bcolors.ENDC)

def talk_run(ensemble, sgl_traj, traj_counter, dir):
    print(bcolors.UWARNING + '\nRunning Trajectory' +
          bcolors.FAIL + ' [{1}] {2}\{0} '.format(sgl_traj, traj_counter + 1, dir) +
          bcolors.UWARNING + 'with Ensemble' +
          bcolors.FAIL + ' [{0}]\n'.format(str(ensemble).zfill(2)) +
          bcolors.ENDC)

def talk_run2(ensemble, sgl_traj, traj_counter, dir):
    print(bcolors.UWARNING + '\nRunning Trajectory' +
          bcolors.FAIL + ' [{1}] {2}\{0} '.format(sgl_traj[:-7], traj_counter + 1, dir) +
          bcolors.UWARNING + 'with Ensemble' +
          bcolors.FAIL + ' [{0}]\n'.format(str(ensemble).zfill(2)) +
          bcolors.ENDC)

def talk_run3(ensemble, dir, runs):
    print(bcolors.UWARNING + '\nRunning Trajectory directory' +
          bcolors.FAIL + ' {} '.format(dir, runs) +
          bcolors.UWARNING + 'with Run / Ensemble:' +
          bcolors.FAIL + ' [{} / {}]\n'.format(runs, str(ensemble).zfill(2)) +
          bcolors.ENDC)

# This method reads in the mylog files and orders them on fuelflow for comparison
def compare_ff(file=None):
    if file is None:
        files = os.listdir('output\\')
        files = ['output\\' + files[files.index(i)] for i in files if 'MYLOG' in i]
    else:
        files = list([file])
        files.append('dummy')
    # print(files)
    for i in files:
        if i[-3:] != 'log':
            continue
        # set_of_ac = list()

        with open(i, 'r') as fin:
            data = fin.read().splitlines(True)
            # print(data[0])
        if 'MYLOG' in data[0]:
            with open(i, 'w') as fout:
                fout.writelines(data[1:])
        with open(i, 'r') as f:
            f = pd.read_csv(i)
        # print(f.columns)
        # f = f[2:]
        # print(f)
        f = f.sort_values([' id', '# simt']).reset_index(drop=True)
        # f.reset_index
        set_of_ac = set(f[' id'])
        print('Number of rows in the log: ', len(f))
        # print('The following aircrafts have been found: ', set_of_ac)
        partial_0 = 0
        to_save = i[:-4] + ' - formatted.xlsx'
        writer = pd.ExcelWriter(to_save, engine='xlsxwriter')
        for index, e in enumerate(set_of_ac):
             #int(len(f)/2) +20
            partial_1 = max(partial_0, f[f[' id'] == e].index[0])
            if partial_0 == partial_1:
                partial_1 = -1
            f1 = f[partial_0:partial_1]
            if partial_0 > 0:
                f1 = f1.drop(columns='# simt')
                partial_0 = partial_1
            # f3 = pd.concat([f1[-250:], f2[-250:]], axis=1, ignore_index=True)

            # f1.to_excel('output\\' + i[:-4] + '1.xlsx'.format(i))
            # f2.to_excel('output\\' + i[:-4] + '2.xlsx'.format(i))
            # f1[-100:].to_excel(writer)
            # l = bool(index > 0)
            # print(index)
            # print(len(f.columns))
            f1[-10:].to_excel(writer, startcol=((len(f.columns)+1)*index))
        writer.save()
        # os.startfile(to_save)
    # exit()

def time_required(distance, FL, speed):
    # distance in nm and speed in mach
    tas = aero.vcas2tas(speed * aero.nm / 3600, FL * 100 * aero.ft) / aero.nm # [Nm / s]
    # tas = aero.vmach2tas(speed, FL * 100 * aero.ft) / aero.nm # [Nm / s]
    return distance / tas
    # print('tas is: ', tas)
    # print('coefficient is: ', 0.12390501319261213720316622691293)
    # print('coefficient is: ', 0.12377203290246768507638072855464)
    # print('coefficient is: ', 0.12417203290246768507638072855464)
    # time_req = distance / 0.12400203290246768507638072855464
    # return time_req

def time_required2(distances_nm, FL, speed):
    # def _eta2tw_cas_wfl(self, distances_nm, flightlevels_m, cas_m_s):
    """
    Estimate for the given CAS the ETA to the next TW waypoint
    No wind is taken into account.
    :param distances: distances between waypoints
    :param flightlevels: flightlevels for sections
    :param cas_m_s: CAS in m/s
    :return: ETA in seconds
    """
    cas_m_s = speed * aero.nm / 3600
    distances_m = distances_nm * aero.nm
    # times_s = np.empty_like(distances_m)
    # previous_fl_m = flightlevels_m

    # Assumption is instantanuous climb to next flight level, and instantanuous speed change at new flight level
    # for i, distance_m in enumerate(distances_m):
    #     if flightlevels_m[i] < 0:
    #         next_fl_m = previous_fl_m
    #     else:
    #         next_fl_m = flightlevels_m[i]
    #         previous_fl_m = next_fl_m
    # print('FL is: ', FL)
    next_tas_m_s = aero.vcas2tas(cas_m_s, FL * aero.ft * 100)
    step_time_s = distances_m / (next_tas_m_s + 0.00001)
    # times_s[i] = step_time_s
    # print('step time is: ', step_time_s)
    # total_time_s = np.sum(times_s)
    return step_time_s

def upload_file(file_upload, name, dir):
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("mycreds.txt")
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()

    drive = GoogleDrive(gauth)
    if 'min' in dir:        fid = drive_folder_min
    elif 'det' in dir:      fid = drive_folder_det
    elif 'prob' in dir:     fid = drive_folder_prob
    elif 'inf' in dir:      fid = drive_folder_inf
    elif 'input' in dir:    fid = drive_folder_input
    elif 'output' in dir:   fid = drive_folder_output
    else:
        print('Upload directory not found!')
        return

    with open(file_upload, "r") as file:
        file_drive = drive.CreateFile({'parents': [{"kind": "drive#fileLink",
                                                     "id": fid}],
                                        'title': name})
        # os.path.basename(file.name)
        # file_drive.SetContentString(file.read())
        file_drive.SetContentFile(file_upload)
        file_drive.Upload()
        # f = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": fid}]})
        # f.SetContentFile(some_path)
        # f.Upload()

        # file1 = drive.CreateFile({'parent': '/home/pi'})
        # file1.SetContentFile('test.txt')
        # file1.Upload()

        #Get content from Google Drive
        # file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        # for file1 in file_list:
        #     print('title: %s, id: %s' % (file1['title'], file1['id']))

    print("File '{}' has been uploaded!".format(file_upload))

def overall_aggregate():
    pass

# df = pd.read_excel('queries\\remon raw scenarios\\AC type 2.xlsx')
# unique_types = set(df['AC type'])
# compare_ff('C:\Documents\BlueSky_Joost\output\\runs\\xlogs output\\1 min\ADH931\\1 min ADH931 D0 OE01 D0.log')