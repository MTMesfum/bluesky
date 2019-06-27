"""
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
"""
# Methods are described in scratch_methods ##############################################
from scratch_methods import *
import shutil

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

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


# scenario_manager = "scenario\Trajectories-batch.scn"
# scenario_manager = "scenario\Test10.scn"
# settings_config = "settings.cfg"
# dt = find_dt() # format '#.##'
set_of_dt = ['0.05', '0.10', '0.20', '0.50', '1.00']
list_ensemble = list(np.arange(1, 25))
# list_ensemble = list([4, 13, 17, 21, 22, 23, 31, 33, 39, 41, 45, 47, 50])
skip_entire_dir = ['1 min', '2 det'] # ['1 min', '2 det', '3 prob', '4 inf']
set_of_delays = [0, 90, 300, 600, 720, 900, 1020, 1200]
# set_of_delays = [0, 60, 90, 180, 300, 450, 600, 900, 1200] #, 180, 300, 600, 720, 900]  # [s]
              # [0, 1, 2,  3,  4,  5,   6,   7,   8,   9,  10,   11]
              #                       [ 0,   1,   2,   3,   4,    5]
# dt = 0.5
# set_dt(0.1)
traj_folder1 = 'scenario\\remon'
traj_folder2 = 'scenario\\remon scen'
set_dt(0.1)
traj_folder = traj_folder2
runs = 0
FE = False
create_scenarios = False
del_runs = False

clear_mylog()
timeit.default_timer()
set_delays(set_of_delays)

# This section is used to find the most FE speed
if FE:
    zeta = [0.95, 0.1, 0.001]
    # CreateSCN_FE('B737', 'FL360', zeta[0], zeta[1], zeta[2])
    CreateSCN_FE('A332', 'FL410', zeta[0], zeta[1], zeta[2])
    set_dt(0.1)
    try:
        os.remove("output\\WRITER Standard File.xlsx")
        os.remove("output\\WRITER Standard File2.xlsx")
    except:     pass
    bs_desktop()
    apple = pd.read_excel("output\\WRITER Standard File.xlsx")
    apple['index2'] = pd.Series(np.flip(np.arange(zeta[0]-zeta[1], zeta[0]+zeta[1], zeta[2])), index=apple.index)
    apple.to_excel("output\\WRITER Standard File2.xlsx")
    banana = min(apple['Fuel Consumed'])
    apple = apple[apple['Fuel Consumed'] <= banana]
    print('\nmach speed is: ', apple['index2'].values[0])
    os.startfile("C:\Documents\Git 2\\output\WRITER Standard File2.xlsx")
    # compare_ff()
    exit()

if create_scenarios:
    CreateSCN_Cruise2(True)
    # exit()
    CreateSCNM3('Trajectories-batch3')


    # orig = "remon scen\\1 min" + '\\min ADH931 D{}.scn'.format(str(set_of_delays[0]))
    orig = "1 min" #+ '\\min ADH931.scn'

    # replace_batch_set2(orig, "Trajectories-batch3", "Trajectories-batch4")
    # bs_desktop()
    # compare_ff()

    # exit()

# exit()
if del_runs:
    if os.path.isdir("output\\runs"):
        shutil.rmtree("output\\runs")
    try:
        os.remove("output\\WRITER Standard File.xlsx")
    except:
        pass

import warnings
warnings.filterwarnings("ignore")
# overall_aggregate() #os.getcwd() + '\\output\\runs_save')
skip = [#'ADH931', 'AEE929', 'AUI34L', 'TFL219',
        'SWR779', 'AZA1572', 'DLH156', 'FPO551',
        'PRI5403', 'EZY471', 'RYR5008',
        'DLH1HU', 'SHT2J', 'BAW4TM', 'AFR234H',
        'PGT4629',
        'SAS1842', 'DLH08W', 'SAS1042',
        'TAP803L', 'NJE2FD', 'LBT7362',
        'KLM1395', 'BLX328', 'BER717E',
        'TAP1015', 'PGT424', 'EZY92FN',
        'AFL2352', 'QTR022',
        'BEL7PC', 'DTH3057', 'EXS79G',
        'CCA931', 'ROT608D', 'VLG2473',
        'BAW66Q', 'EIN111', 'DLH8PK',
        'SAS618', 'DLH8PK', 'BEL724',
        'TAY011', 'EZY471', 'OHY2160',
        'WZZ114', 'MON752A'
        ]
result_analysis(None, None, skip)

# run a trajectory for every ensemble
for dir in os.listdir(traj_folder):
    if dir in skip_entire_dir:
        continue
    traj_counter = 0
    traj = os.listdir(traj_folder + "\\" + dir)
    # traj = [traj[traj.index(i)] for i in traj if ('D'+str(set_of_delays[0])) in i]
    traj.append('dummy')
    # print('traj holds: ', traj)

    # scen_next = traj_folder[9:] + '\\' + dir + '\\' + sgl_traj
    # print(scen_next)
    replace_batch_set2(dir, "Trajectories-batch3", "Trajectories-batch4")
    # replace_batch(scen_next)
    # exit()
    talk_traj2(dir, traj_counter)
    # if dir == '2 det':
    #     if sgl_traj in ['det ADH931 D0.scn',
    #                     'det ADH931 D720.scn', 'det ADH931 D1050.scn']:
    #         continue
    for ensemble in list_ensemble:
        replace_ensemble(ensemble, "Trajectories-batch4.scn")
        runs += 1
        talk_time(runs)
        talk_run3(ensemble, dir, runs)
        bs_desktop()
        # Move the input and output log files into their log folders
        movelog2(ensemble, dir, False)
        # exit()
    # exit()
        writerfix2(dir, traj_counter, False)
    # if traj_counter == 3:
    #     exit()
    traj_counter += 1

# Open the folder with all the results
# exit()
talk_time(runs)

os.startfile('output\\runs')
os.system("shutdown /s /t 300")

# import pickle
# df = pickle.load( open(
#   "I:\Documents\Google Drive\Thesis 2018\BlueSky Git3\queries\pickle\\results_3600_1-50.p", "rb" ) )
# print(df.to_string())
# df.to_csv('Results_1-50')
