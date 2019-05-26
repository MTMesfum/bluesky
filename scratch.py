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
# dt = 0.5
# replace_dt()
traj_folder1 = 'scenario\\remon'
traj_folder2 = 'scenario\\remon scen'

# print(traj[1])
# print(traj[2])

# bs_laptop()
# set_dt()
# set_dt(5.0)
# set_dt(1.5)
# exit()
# print(range(200, 273, 10))
# exit()
# for i in range(257, 264, 1):
#     replace_speed(i)
#     print('\nThe AC is flying at {0} [kts].\n'.format(i))
#     bs_desktop()
#
CreateSCN_Cruise(False, 280)
# exit()
traj_folder = traj_folder2

    # 'ADH931_LICC_LIRP_20140912072000'
# run a trajectory for every ensemble
for l in os.listdir(traj_folder):
    k = 0
    traj = os.listdir(traj_folder + "\\" + l)
    for j in traj:
    # j = traj[0]
        if k < len(traj):
            scen_next = traj_folder[9:] + '\\' + l + '\\' + j
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
                print(bcolors.UWARNING  + '\n\nRunning Trajectory'        +
                      bcolors.FAIL      + ' [{1}] {2}\{0} '.format(j, k+1, l)  +
                      bcolors.UWARNING + 'with Ensemble'  +
                      bcolors.FAIL + ' [{0}]'.format(i) +
                      bcolors.ENDC)
            else:
                print(bcolors.UWARNING  + '\n\nRunning Trajectory'        +
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
            # Move the input and output log files into their log folders
            movelog(i, j, l)
            # exit()
        writerfix(j, l, k)
        # exit()
        k += 1

        # if l == traj_folder[0]:
        #     exit()
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
