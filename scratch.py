import numpy as np
import sys
# from math import *
import pandas as pd, os, datetime, random
import pdb
import fileinput as fi
# import geo
# from bluesky.tools import geo
from bluesky.tools.geo import qdrdist as dist
from bluesky.tools.geo import latlondist as dist2
from bluesky.tools import aero
#from BlueSky import main
# print(sys.argv)
#sys.argv.append("--headless")
#sys.arg,"--scenfile","\experimental\Trajectories.scn"])
#main()

# Scenario batch file
# Find the timestep which is defined in the settings config
def find_dt():
    #   Replace the dt in the settings.cfg
    f = open(settings_config, 'r')
    filedata = f.read()
    apple = filedata.find('simdt =')
    banana = filedata.find('# Snaplog dt')
    dt_settings = filedata[apple+8:banana-3]
    f.close()
    return dt_settings

# Switches the ensemble in the scenario manager and adapts the name using the ensemble # and global dt
def replace_ensemble(ensemble):
    if ensemble < 10:
        ensemble = str(0) + str(ensemble)

    f = open(scenario_manager, 'r')
    filedata = f.read()
    f.close()

    ensemble = str(ensemble)
    apple = filedata.find('LOAD_WIND')
    banana = filedata.find(',Tigge_')
    citrus = filedata.find('WRITER')
    date = filedata.find('_dt_')
    filedata = str("".join(filedata[0:apple+10] + str(ensemble) + filedata[banana:citrus+8]
                           + str(ensemble) + filedata[date:]))

    f = open(scenario_manager, 'w')
    f.write(filedata)
    f.close()
    # os.startfile(scenario_manager)
    pass

def replace_batch(scen_new):
    f = open(scenario_manager, 'r')
    filedata = f.read()
    f.close()

    apple = filedata.find('remon')
    banana = filedata.find('.scn')
    filedata = str("".join(filedata[0:apple] + str(scen_new) +
                           filedata[banana+4:]))

    f = open(scenario_manager, 'w')
    f.write(filedata)
    f.close()
    # os.startfile(scenario_manager)

# Changes the timestep in the settings config of BlueSky using the provided timestep
# Keep in mind that the savefile doesn't change its name, unless the timestep is set into the global variable dt
def set_dt(timestep):

    #   Replace the dt in the settings.cfg
    f = open(settings_config, 'r')
    filedata = f.read()
    f.close()

    apple = filedata.find('simdt =')
    banana = filedata.find('# Snaplog dt')
    filedata = str("".join(filedata[0:apple+8] + str(timestep) + '\n \n' + filedata[banana:]))

    f = open(settings_config, 'w')
    f.write(filedata)
    f.close()
    # os.startfile("C:\Documents\Git\\" + settings_config)

    #   Replace the dt in the save file
    f = open(scenario_manager, 'r')
    filedata = f.read()
    f.close()

    apple = filedata.find('_dt_')
    banana = filedata.find('> EXIT')
    filedata = str("".join(filedata[0:apple+4] + str(timestep) + filedata[apple+7:]))

    f = open(scenario_manager, 'w')
    f.write(filedata)
    f.close()
    dt = timestep
    print('The timestep has been changed to {0} seconds.'.format(timestep))
    # os.startfile("C:\Documents\Git\\" + scenario_manager)

    pass

# This functions replaces the dt in the settings.cfg with the globally defined dt
def replace_dt():
    set_dt(dt)
    pass

# Run a simulation of BlueSky using the desktop path
def bs_desktop():
    os.system("call C:\Programs\Tools\Anaconda\Program\Scripts\\activate.bat && \
                    cd C:\Documents\Git && conda activate py36 && python BlueSky.py")

# Run a simulation of BlueSky using the laptop path
def bs_laptop():
    os.system("call I:\Programs\Anaconda\Program\Scripts\\activate.bat && \
                    cd I:\Documents\Google Drive\Thesis 2018\BlueSky Git3 && python BlueSky.py")

# Cut the number to 3 digits
def cut3(one):
    return round(one, 3)

# Cut the number to 7 digits
def cut7(one):
    return round(one, 7)

# Add a random delay to the time provided
def addSecs(tm, secs, secs2):
    secs = secs*60
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    if secs2 == 0:
        fulldate = fulldate + datetime.timedelta(seconds=(secs))
        delay = secs
    else:
        fulldate = fulldate - datetime.timedelta(seconds=(secs))
        delay = -secs
    return str(fulldate.time()), delay

# Create a scenario file from the provided trajectories and save it in the provided name
# The first entry in the method decides whether a random delay is added
def CreateSCN(alpha, save_file):
    # Constants
    # nm  = 1852.  # m       1 nautical mile
    # ft  = .3048  # m        1 foot

    folder = "queries\\"
    FileName = os.listdir(folder)
    FileName.remove('hide')
    traj = 0
    banana = list()
    scenario2 = pd.DataFrame()

    for k in FileName:
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

    # save.to_csv('test1.scn', sep=',', index=False, header=False, quoting=0)
    # banana.to_csv('test2.scn', sep=',')
    # writer = pd. Writer('{0}/{1}.xlsx'.format(name, i))
    # save.to_excel(writer)
    # writer.save()

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
    df = pd.read_csv('output\WRITER Standard File.csv')
    # df = pd.read_csv('output\\runs\WRITER {0}.csv'.format(traj))
    df = df.drop('Unnamed: 0', axis=1)
    df.reset_index(inplace=True)
    df.index = df.index + 1
    df = df.drop('index', axis=1)
    if not os.path.isdir('output\\runs\{0}'.format(dir)):
        os.mkdir('output\\runs\{0}'.format(dir))
    df.to_excel('output\\runs\{1}\{0}.xlsx'.format(traj[0:-4], dir))
    os.remove('output\WRITER Standard File.csv')
    print(bcolors.UBLUE     + 'Saved'   +
          bcolors.FAIL      + ' [{1}] {0} '.format(traj, counter)   +
          bcolors.UBLUE     + 'in'      +
          bcolors.FAIL      + ' {0}'.format(
                            'output\\runs\{1}\{0}.xlsx'.format(traj[0:-4], dir)) +
          bcolors.ENDC)
    # os.startfile('output\\runs\WRITER {0}.xlsx'.format(traj))
#############################       Methods are described above this line ##############################################

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

global scenario_manager, settings_config, dt
scenario_manager = "scenario\Trajectories-batch.scn"
# scenario_manager = "scenario\Test10.scn"
settings_config = "settings.cfg"
dt = find_dt() # format '#.##'
set_of_dt = ['0.05', '0.10', '0.20', '0.50', '1.00']
list_ensemble = list(range(1,51))
dt = 2.0
replace_dt()
traj_folder = os.listdir('scenario\\remon')

# print(traj[1])
# print(traj[2])

# bs_desktop()

    # 'ADH931_LICC_LIRP_20140912072000'
# run a trajectory for every ensemble
for l in traj_folder:
    k = 0
    traj = os.listdir('scenario\\remon\\' + l)
    for j in traj:
        if k < len(traj):
            scen_next = 'remon\\' + l + '\\' + traj[k]
            replace_batch(scen_next)
            print(bcolors.UWARNING  + '\nReplaced Trajectory to'  +
                  bcolors.FAIL      + ' [{1}] {0}'.format(scen_next, k+1) +
                  bcolors.ENDC)
            # print(bcolors.UNDERLINE + bcolors.WARNING +
            #       '\nReplaced Trajectory [{2}] {0} with [{3}] {1}\n'.format(
            #           traj[k], traj[k+1], k, k+1) + bcolors.ENDC)
        for i in list_ensemble:
            replace_ensemble(i)
            if i > 9:
                print(bcolors.UWARNING  + '\nRunning Trajectory'        +
                      bcolors.FAIL      + ' [{1}] {2}\{0} '.format(j, k+1, l)  +
                      bcolors.UWARNING + 'with Ensemble'  +
                      bcolors.FAIL + ' [{0}]\n'.format(i) +
                      bcolors.ENDC)
            else:
                print(bcolors.UWARNING  + '\nRunning Trajectory'        +
                      bcolors.FAIL      + ' [{1}] {2}\{0} '.format(j, k+1, l)  +
                      bcolors.UWARNING  + 'with Ensemble'       +
                      bcolors.FAIL      + ' [0{0}]\n'.format(i) +
                      bcolors.ENDC)
            # if i > 9:
            #     print(bcolors.UWARNING  + '\nRunning Ensemble'  +
            #           bcolors.FAIL      + ' [{0}]\n'.format(i)  +
            #           bcolors.ENDC)
            # else:
            #     print(bcolors.UWARNING  + '\nRunning Ensemble'  +
            #           bcolors.FAIL      + ' [0{0}]\n'.format(i) +
            #           bcolors.ENDC)
            bs_desktop()
        writerfix(j, l, k)
        k += 1
        # if k == len(traj):
        #     scen_reset = 'remon\\' + traj_folder[0] + '\\' + traj[0]
        #     replace_batch(scen_reset)
        #     print(bcolors.UWARNING  + '\nReplaced Trajectory'   +
        #           bcolors.FAIL      + ' [{2}] {0}'              +
        #           bcolors.UWARNING  + 'with'                    +
        #           bcolors.FAIL      + ' [{3}] {1}\n'.format(
        #                                     traj[k], traj[0], k, 0) +
        #           bcolors.ENDC)

# Open the folder with all the results
os.startfile('output\\runs')
# os.system("shutdown /s /t 60")

# os.rename('output\WRITER Standard File.csv', 'output\\runs\WRITER {0}.csv'.format(traj))
# print(dt)
# scenario_manager = "scenario\Test10.scn"
# CreateSCN(False, 'testtest')
# set_dt(1.0)
# CreateSCN(False, 'Trajectories')
# CreateSCNM(5, 1, "Trajectories-batch")
# set_dt(1.0)
# bs_desktop()

# CreateSCNM(20, 5, 'Test10')
# replace_ensemble(50)
# CreateSCNM(5, 3, 'Trajectories-batch')

# replace_ensemble(1)
# set_dt(10.0)
# bs_desktop()

# assign the timestep and run the simulations X times
# for i in set_of_dt:
    # dt = i
    # replace_dt()
    # for j in list_ensemble:
        # replace_ensemble(i)
        # run_bluesky_desktop()
        # run_bluesky_laptop()

# os.system("call C:\Programs\Tools\Anaconda\Program\Scripts\\activate.bat && \
#             cd C:\Documents\BlueSky && conda activate py36 && python BlueSky.py")

#
# os.system("call C:\Programs\Tools\Anaconda\Program\Scripts\\activate.bat && \
#               cd C:\Documents\BlueSky && conda activate py36 && python BlueSky.py")

# os.system("call C:\Programs\Tools\Anaconda\Program\Scripts\\activate.bat && \
#            cd C:\Documents\BlueSky && conda activate py36 && \
#              python BlueSky.py --headless --scenfile \experimental\Trajectories.scn")
# #sys.argv.append('--headless')
#\BlueSky.py
#'--config-file'
#\experimental\Trajectories.scn

#"IC C:\Documents\BlueSky\scenario\experimental\Trajectories.scn"

# import pickle
# df = pickle.load( open(
#   "I:\Documents\Google Drive\Thesis 2018\BlueSky Git3\queries\pickle\\results_3600_1-50.p", "rb" ) )
# print(df.to_string())
# df.to_csv('Results_1-50')
