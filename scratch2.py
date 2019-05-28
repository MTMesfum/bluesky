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
list_ensemble = list(range(1, 2))
skip_entire_dir = [] # ['1 min', '2 det', '3 prob', '4 inf']
set_of_delays = [0, 90, 300,]  # [s]

# dt = 0.5
set_dt()
traj_folder1 = 'scenario\\remon'
traj_folder2 = 'scenario\\remon scen'

# for i in range(257, 264, 1):
#     replace_speed(i)
#     print('\nThe AC is flying at {0} [kts].\n'.format(i))
#     bs_desktop()
#
timeit.default_timer()
set_delays(set_of_delays)
CreateSCN_Cruise(True, 280, 3)
CreateSCNM2('Trajectories-batch3')

orig = "\"remon scen\\1 min" + '\\min ADH931'
replace_batch_set(orig, "Trajectories-batch3", "Trajectories-batch4")
bs_desktop()
exit()

traj_folder = traj_folder2
runs = 0
# run a trajectory for every ensemble
for dir in os.listdir(traj_folder):
    if dir in skip_entire_dir:
        continue
    traj_counter = 0
    traj = os.listdir(traj_folder + "\\" + dir)

    for sgl_traj in traj:
        if traj_counter < len(traj):
            scen_next = traj_folder[9:] + '\\' + dir + '\\' + sgl_traj
            replace_batch(scen_next)
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

        writerfix(sgl_traj, dir, traj_counter)
        if traj_counter == 3:
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
