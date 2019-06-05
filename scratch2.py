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
list_ensemble = list(range(1, 3))
skip_entire_dir = [] # ['1 min', '2 det', '3 prob', '4 inf']
set_of_delays = [0, 10, 30, 60, 90, 120, 150, 180, 300, 600, 900, 1200]
# set_of_delays = [0, 60, 90, 180, 300, 450, 600, 900, 1200] #, 180, 300, 600, 720, 900]  # [s]
              # [0, 1, 2,  3,  4,  5,   6,   7,   8,   9,  10,   11]
              #                       [ 0,   1,   2,   3,   4,    5]
# dt = 0.5
# set_dt(0.1)
traj_folder1 = 'scenario\\remon'
traj_folder2 = 'scenario\\remon scen'


# for i in range(257, 264, 1):
#     replace_speed(i)
#     print('\nThe AC is flying at {0} [kts].\n'.format(i))
clear_mylog()
# 0.782
# CreateSCN_FE('A320', 'FL360', 0.05, 0.001)
set_dt(0.1)
# bs_desktop()
# compare_ff()
# exit()
#
# 21746.00000000,ADH931-01,42.44795639,10.80771208
# 21749.00000000,ADH931-02,42.44817349,10.80741316
# 21752.00000000,ADH931-03,42.44755099,10.80827128
# 21769.00000000,ADH931-04,42.44791395,10.80777491
# 21783.00000000,ADH931-05,42.44764942,10.80814739
# 21805.00000000,ADH931-06,42.44792320,10.80776035
# 21985.00000000,ADH931-07,42.44802828,10.80761494
# 22163.00000000,ADH931-08,42.44768581,10.80809387
# 22244.00000000,ADH931-09,42.44719295,10.80880379
# 22521.00000000,ADH931-10,42.44800279,10.80759016
# 22821.00000000,ADH931-11,42.44800279,10.80759016

# compare_ff('C:\Documents\BlueSky_Joost\output\\runs\\xlogs output\\1 min\ADH931\\1 min ADH931 D0 OE01 D450.log')


timeit.default_timer()
# compare_ff('C:\Documents\BlueSky Rene Unchanged\output\MYLOG__20190531_07-23-38.log')
# compare_ff('C:\Documents\BlueSky_Joost\output\MYLOG__20190531_07-15-53.log')
# exit()
set_dt(0.1)
set_delays(set_of_delays)
CreateSCN_Cruise(True, 350, 3)
# exit()
CreateSCNM2('Trajectories-batch3')

orig = "remon scen\\1 min" + '\\min ADH931 D{}.scn'.format(str(set_of_delays[0]))
replace_batch_set(orig, "Trajectories-batch3", "Trajectories-batch4")
# bs_desktop()
# compare_ff()

# exit()
# exit()

traj_folder = traj_folder2
runs = 0

if os.path.isdir("output\\runs"):
    shutil.rmtree("output\\runs")
try:
    os.remove("output\\WRITER Standard File.xlsx")
except:
    pass

import warnings
warnings.filterwarnings("ignore")

# run a trajectory for every ensemble
for dir in os.listdir(traj_folder):
    if dir in skip_entire_dir:
        continue
    traj_counter = 0
    traj = os.listdir(traj_folder + "\\" + dir)
    traj = [traj[traj.index(i)] for i in traj if ('D'+str(set_of_delays[0])) in i]
    traj.append('dummy')
    print('traj holds: ', traj)
    for sgl_traj in traj:
        if sgl_traj == 'dummy':
            continue
        if traj_counter < len(traj):
            scen_next = traj_folder[9:] + '\\' + dir + '\\' + sgl_traj
            # print(scen_next)
            replace_batch_set(scen_next, "Trajectories-batch3", "Trajectories-batch4")
            # replace_batch(scen_next)
            talk_traj(scen_next, traj_counter)
        # if dir == '2 det':
        #     if sgl_traj in ['det ADH931 D0.scn',
        #                     'det ADH931 D720.scn', 'det ADH931 D1050.scn']:
        #         continue
        for ensemble in list_ensemble:
            replace_ensemble(ensemble)
            runs += 1
            talk_time(runs)
            talk_run(ensemble, sgl_traj, traj_counter, dir)
            bs_desktop()
            # Move the input and output log files into their log folders
            movelog(ensemble, sgl_traj, dir)
            # exit()
        # exit()
            writerfix2(sgl_traj, dir, traj_counter)
        # if traj_counter == 3:
        exit()
        traj_counter += 1

# Open the folder with all the results
talk_time(runs)
os.startfile('output\\runs')
# os.system("shutdown /s /t 60")

# import pickle
# df = pickle.load( open(
#   "I:\Documents\Google Drive\Thesis 2018\BlueSky Git3\queries\pickle\\results_3600_1-50.p", "rb" ) )
# print(df.to_string())
# df.to_csv('Results_1-50')
