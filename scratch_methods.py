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
from bluesky.tools import aero
import timeit
#from BlueSky import main
# print(sys.argv)
#sys.argv.append("--headless")
#sys.arg,"--scenfile","\experimental\Trajectories.scn"])
#main()

settings_config = "settings.cfg"
scenario_manager = "scenario\Trajectories-batch.scn"
exp = "scenario\Trajectories-batch2.scn"
save_ic = "scenario\\trajectories_saveic.scn"
dest_dir_input_logs = "output\\runs\\xlogs input"
dest_dir_output_logs = "output\\runs\\xlogs output"
dt = 0.5
TW_inf = 3600  # [s]
TW_min = 60  # [s]
set_of_delays = [0, 90, 720, 1050]  # [s]

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

def find_index(to_search, target):
    for number, i in enumerate(to_search):
        if target == i:
            return number
    return

# Scenario batch file
# Find the timestep which is defined in the settings config

def find_dt():
    #   Replace the dt in the settings.cfg
    # f = open(settings_config, 'r')
    # filedata = f.read()
    # f.close()

    with open(settings_config, 'r') as f:
        filedata = f.read()

    apple = filedata.find('simdt =')
    banana = filedata.find('# Snaplog dt')
    dt_settings = filedata[apple+8:banana-3]

    return dt_settings

# Switches the ensemble in the scenario manager and adapts the name using the ensemble # and global dt
def replace_ensemble(ensemble):
    if ensemble < 10:
        ensemble = str(0) + str(ensemble)

    # f = open(scenario_manager, 'r')
    # filedata = f.read()
    # f.close()

    with open(scenario_manager, 'r') as f:
        filedata = f.read()

    ensemble = str(ensemble)
    apple = filedata.find('LOAD_WIND')
    banana = filedata.find(',Tigge_')
    citrus = filedata.find('WRITER')
    date = filedata.find('_dt_')
    filedata = str("".join(filedata[0:apple+10] + str(ensemble) + filedata[banana:citrus+8]
                           + str(ensemble) + filedata[date:]))

    with open(scenario_manager, 'w') as f:
        f.write(filedata)

    # f = open(scenario_manager, 'w')
    # f.write(filedata)
    # f.close()

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

# Changes the timestep in the settings config of BlueSky using the provided timestep
# Keep in mind that the savefile doesn't change its name, unless the timestep is set into the global variable dt
def set_dt(timestep=dt):
    global dt
    dt = timestep

    with open(settings_config, 'r') as f:
        filedata = f.read()

    apple = filedata.find('simdt =')
    banana = filedata.find('# Snaplog dt')
    filedata = str("".join(filedata[0:apple+8] + str(timestep) + '\n \n' + filedata[banana:]))

    with open(settings_config, 'w') as f:
        f.write(filedata)

    with open(scenario_manager, 'r') as f:
        filedata = f.read()

    apple = filedata.find('_dt_')
    filedata = str("".join(filedata[0:apple+4] + str(timestep) + filedata[apple+7:]))

    with open(scenario_manager, 'w') as f:
        f.write(filedata)

    print('The timestep has been changed to {0} seconds.'.format(dt))
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
    os.system("call C:\Programs\Tools\Anaconda\Program\Scripts\\activate.bat && \
                    cd C:\Documents\Git 2 && conda activate py36 && python BlueSky.py")

# Run a simulation of BlueSky using the laptop path
def bs_laptop():
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

            FlightLevel = str(scenario['fl'][i])
            if FlightLevel.count('') < 3:
                FlightLevel = '0' + FlightLevel
            FlightLevel = 'FL' + FlightLevel

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
def CreateSCN_Cruise(alpha, fl_ref):
    folder = "scenario\\remon_raw_scenario\\"
    type_file = "AC Type 2.xlsx"
    FileName = os.listdir(folder)

    for k in FileName:
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
                banana.append(apple + '.00> PRINTER A delay of {0} seconds has been added.'.format(str(delay)))
                m += 1
                for i in range(scenario.shape[0]):
                    FlightLevel = 'FL' + str(scenario['fl'][i])

                    if i == 0:
                        banana.append(apple + '.00> CRE ' + aircraftid + ', ' + actype + str(cut7(scenario['st_x(gpt.coords)'][i]))
                                      + ', ' + str(cut7(scenario['st_y(gpt.coords)'][i])) + ', '
                                      + str(cut3(heading)) + ', ' + FlightLevel + ', 190')
                        banana.append(apple + '.00> DEFWPT ' + aircraftid + '-ORIG, '
                                      + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                                      + str(cut7(scenario['st_y(gpt.coords)'][i])))
                        banana.append(apple + '.00> ORIG ' + aircraftid + ', ' + aircraftid + '-ORIG')
                        banana.append(apple + '.00> DEFWPT ' + aircraftid + '-DEST, '
                                      + str(cut7(scenario['st_x(gpt.coords)'][scenario.shape[0]-1]))
                                      + ', ' + str(cut7(scenario['st_y(gpt.coords)'][scenario.shape[0]-1])))
                        banana.append(apple + '.00> DEST ' + aircraftid + ', ' + aircraftid + '-DEST' )
                        banana.append(apple + '.00> ' + aircraftid + ' AT ' + aircraftid
                                                        + '-DEST, ' + 'FL' + str(scenario['fl'][-1:].reset_index(drop=True)[0]))
                    else:
                        if i == scenario.shape[0]-1:
                            follow = aircraftid + '-' + str(i-1)
                            follow2 = aircraftid + '-' + str(i)
                            banana.append(apple + '.00> DEFWPT ' + follow2 + ', '
                                          + str(cut7(scenario['st_x(gpt.coords)'][scenario.shape[0] - 1]))
                                          + ', ' + str(cut7(scenario['st_y(gpt.coords)'][scenario.shape[0] - 1])))
                            banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                          + follow2 + ', ' + FlightLevel)
                            banana.append(apple + '.00> ' + aircraftid + ' AT ' + follow +
                                                ' ' + FL_OLD)
                            banana.append(apple + '.00> ' + aircraftid + ' after ' + follow2 + ' ADDWPT '
                                          + aircraftid + "-DEST" + ', ' + FlightLevel)
                            banana.append(apple + '.00> ' + aircraftid + ' AT ' + follow2 +
                                                ' ' + FL_OLD)
                            o = list(range(0, scenario.shape[0], 5))
                            o.append(scenario.shape[0])
                            o.pop(0)
                            citrus1, citrus2, citrus3 = ([], [], [])

                            for n in o:
                                if n == o[0]:
                                    wp_0 = aircraftid + '-' + str(1) + ' '
                                wp_1 = aircraftid + '-' + str(n-1) + ' '
                                time = scenario.time_over[n-1]
                                time = datetime.datetime(100, 1, 1, int(time[-8:-6]), int(time[-5:-3]), int(time[-2:]))

                                if l == 'min':      secs = TW_min/2
                                elif l == 'det':    secs = TW_det/2 * 60
                                elif l == 'prob':   secs = TW_stoch/2 * 60
                                elif l == 'inf':    secs = TW_inf/2

                                time = (time + datetime.timedelta(seconds=(secs))).time()
                                banana.append(apple + '.00> ' + aircraftid + ' RTA_AT ' + wp_1 + str(time))
                                citrus1.append(apple + '.00> ' + aircraftid + ' TW_SIZE_AT ' + wp_1 + str(int(secs*2)))
                                citrus2.append(apple + '.00> ' + aircraftid + ' OWN_SPD_FROM ' + wp_0)
                                citrus3.append(apple + '.00> ' + aircraftid + ' AFMS_FROM ' + wp_0 + 'tw')
                                wp_0 = wp_1
                                del secs
                            banana = banana + citrus1 + citrus2 + citrus3
                            banana.append(apple + '.00> ' + aircraftid + ' AFMS_FROM ' + wp_1 + 'off')
                            banana.append(apple + '.00> VNAV ' + aircraftid + ' ON')
                            banana.append(apple + '.00> LNAV ' + aircraftid + ' ON')
                            # banana.append(apple + '.00> dt 0.5')
                            banana.append(apple + '.00> FF')

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
                                banana.append(apple + '.00> ' + aircraftid + ' AT ' + aircraftid + '-' + str(i-1) +
                                                ' ' + FL_OLD)
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

# Create a scenario manager to run a file alpha times, load wind ensemble beta and save the file in save_file
def CreateSCNM(alpha, beta, save_file):
    gamma = list()
    gamma.append('# Load wind data')
    if beta < 10:
        gamma.append('00:00:00.00> LOAD_WIND 0' + str(beta) +',Tigge_01_09_2017.nc')
    else:
        gamma.append('00:00:00.00> LOAD_WIND ' + str(beta) + ',Tigge_01_09_2017.nc')
    gamma.append('00:00:00.00> DATE 1,9,2017')
    gamma.append('00:00:00.00> FF')

    for i in range(1, alpha):
        gamma.append('')
        gamma.append('# Load trajectories for a run')
        gamma.append('00:00:00.00> SWRAD VOR')
        if i < 10:
            gamma.append('00:00:00.00> SCEN Test_0'+str(i))
            gamma.append('00:00:00.00> PCALL "Trajectories.scn" 0' + str(i))
        else:
            gamma.append('00:00:00.00> SCEN Test_' + str(i))
            gamma.append('00:00:00.00> PCALL "Trajectories.scn" ' + str(i))
        gamma.append('00:00:00.00> FF')
        gamma.append('23:59:00.00> HOLD')

    gamma.append('')
    gamma.append('# Load trajectories for a run')
    if alpha < 10:
        gamma.append('00:00:00.00> SCEN Test_0' + str(alpha))
        gamma.append('00:00:00.00> PCALL "Trajectories.scn" 0' + str(alpha))
    else:
        gamma.append('00:00:00.00> SCEN Test_' + str(alpha))
        gamma.append('00:00:00.00> PCALL "Trajectories.scn" ' + str(alpha))
    gamma.append('00:00:00.00> SWRAD VOR')
    gamma.append('00:00:00.00> FF')
    if beta < 10:
        gamma.append('23:58:59.00> WRITER W0' +str(beta) +'_dt_' +str(dt))
    else:
        gamma.append('23:58:59.00> WRITER W' + str(beta) +'_dt_' +str(dt))
    gamma.append('23:58:59.00> QUIT')

    dir = os.getcwd()
    with open(dir + '/scenario/' + save_file + '.scn', "w") as fin:
        fin.write('\n'.join(gamma))
    os.startfile(dir + '/scenario/' + save_file + '.scn')

# Clean up,  and open the output file
def writerfix(traj, dir, counter):
    dest_dir = 'output\\runs\{0}'.format(dir)
    df = pd.read_csv('output\WRITER Standard File.csv')
    # df = pd.read_csv('output\\runs\WRITER {0}.csv'.format(traj))
    df = df.drop('Unnamed: 0', axis=1)
    df.reset_index(inplace=True)
    df.index = df.index + 1
    df = df.drop('index', axis=1)
    name, _ = os.path.splitext(traj)

    with open(dest_dir_input_logs + "\\" + dir[0:7] + " " + traj[4:10] + " IE01 D0.scn", 'r') as f:
        filedata = f.read()
    apple = filedata.find('TW_SIZE_AT ')
    banana = filedata[apple+len('TW_SIZE_AT '):].find('TW_SIZE_AT ') + apple
    _, _, TW_size, *_ = filedata[apple:banana].split()

    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)
    df.to_excel(dest_dir + '\{0} TW={1}.xlsx'.format(name, TW_size))
    os.remove('output\WRITER Standard File.csv')
    print(bcolors.UBLUE     + '\n\nSaved'   +
          bcolors.FAIL      + ' [{1}] {0} '.format(traj, counter)   +
          bcolors.UBLUE     + 'in'      +
          bcolors.FAIL      + ' {0}'.format(
                              dest_dir + '\{0}.xlsx'.format(name)) +
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
    pass

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

def talk_run(ensemble, sgl_traj, traj_counter, dir):
    print(bcolors.UWARNING + '\nRunning Trajectory' +
          bcolors.FAIL + ' [{1}] {2}\{0} '.format(sgl_traj, traj_counter + 1, dir) +
          bcolors.UWARNING + 'with Ensemble' +
          bcolors.FAIL + ' [{0}]\n'.format(str(ensemble).zfill(2)) +
          bcolors.ENDC)