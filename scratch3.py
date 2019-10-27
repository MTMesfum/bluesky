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

# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 500)
# pd.set_option('display.width', 1000)

# class bcolors:
#     HEADER = '\033[95m'
#     OKBLUE = '\033[94m'
#     OKGREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'
#     UWARNING = '\033[4m' + '\033[93m'
#     UBLUE = '\033[4m' + '\033[94m'

# dt = find_dt() # format '#.##'
set_of_dt = ['0.05', '0.10', '0.20', '0.50', '1.00']
list_ensemble = np.arange(44, 51) #np.flip(np.arange(1, 51))
list_ensemble = np.arange(10, 11) #np.flip(np.arange(1, 51))
# list_ensemble = list([4, 13, 17, 21, 22, 23, 31, 33, 39, 41, 45, 47, 50])
skip_entire_dir = ['1 min', '3 inf', '3 prob'] # ['1 min', '2 det', '3 prob', '4 inf']
set_of_delays = [0, 180, 300, 600, 900, 1200, 1500, 1800]
# set_of_delays = [0, 60, 90, 180, 300, 450, 600, 900, 1200] #, 180, 300, 600, 720, 900]  # [s]
              # [0, 1, 2,  3,  4,  5,   6,   7,   8,   9,  10,   11]
              #                       [ 0,   1,   2,   3,   4,    5]

traj_folder1 = 'scenario\\remon'
traj_folder2 = 'scenario\\remon scen'
set_dt(0.1)
traj_folder = traj_folder2

analysis = True

runs = 0
del_runs = False
run = False

FE = False
create_scenarios = False
create_scenarios_custom = False
selection_made = False

# position of the TW. True is in middle, False is on the bottom
set_TW_place(True)

clear_mylog()
timeit.default_timer()
set_delays(set_of_delays)

if analysis:
    analysis_path = 'C:\Documents\Git 2\output\\runs\\xlogs input\\3 inf'
    # analysis_path = None
    # flights = ['TAP1015', 'AZA1572', 'BEL7PC', 'EXS79G']
    # flights = ['DLH2557', 'IBE31DD', 'SAS4759', 'AFL2326']
    flights = ['IBE31DD', 'SAS4759']

    # flights = ['DLH48H', 'JEI252']
    selection = [0, 600, 1200, 1800]

    # for flight in flights:
    #     getLog(analysis_path, flight, selection, False)

    path = 'F:\Documents\BlueSky Backup\Final Runs'
    Dir = os.listdir(path)
    Dir.pop(0)
    for dir in Dir:
        result_analysis2(os.path.join(path, dir))


# This section is used to find the most FE speed
if FE:
    zeta = [0.83, 0.03, 0.001]
    # zzeta = [0.78]
    # CreateSCN_FE('B737', 'FL360', zeta[0], zeta[1], zeta[2])
    CreateSCN_FE('B763', 'FL380', zeta[0], zeta[1], zeta[2])
    set_dt(0.1)
    try:
        os.remove("output\\WRITER Standard File.xlsx")
        os.remove("output\\WRITER Standard File2.xlsx")
    except:     pass
    bs_desktop()
    apple = pd.read_excel("output\\WRITER Standard File.xlsx")
    apple['index2'] = pd.Series((np.arange(zeta[0]-zeta[1], zeta[0]+zeta[1], zeta[2])), index=apple.index)
    apple.to_excel("output\\WRITER Standard File2.xlsx")
    banana = min(apple['Fuel Consumed'])
    apple = apple[apple['Fuel Consumed'] <= banana]
    print('\nmach speed is: ', apple['index2'].values[0])
    os.startfile("C:\Documents\Git 2\\output\WRITER Standard File2.xlsx")
    # compare_ff()
    exit()

if create_scenarios:
    selected = ['TAP1015', 'AZA1572', 'BEL7PC', 'EXS79G']
    CreateSCN_Cruise2(True)
    CreateSCNM3('Trajectories-batch3')
    orig = "1 min" #+ '\\min ADH931.scn'

if create_scenarios_custom:
    file1 = "scenario\\custom scen raw\\"
    file2 = "Trajectories_adapted.csv"
    file3 = "scenario\\remon scen"
    file4 = "scenario\\custom scen"
    save_file = 'scenario\\selected_trajectories.txt'
    save_file = os.path.join(os.getcwd(), save_file)

    apple = pd.read_csv(file1 + file2)
    apple = apple[apple.columns[1:-9]]
    banana = set(apple['callsign_geo'])

    path_traj = os.path.join(os.getcwd(), file4)
    if os.path.isdir(path_traj):
        shutil.rmtree(path_traj)
    os.makedirs(path_traj)

    if not selection_made:
        # Create a selection list for ac type
        counter = 0
        ac_types = ['A320', 'B737', 'B752', 'B734',
                    'A319', 'A321', 'B77L', 'B738',
                    'B736', 'B738', 'B733']
        # ac_types = ['A320', 'A321', 'A319']
        selection = list()
        for i, j in enumerate(banana):
            # Filter trajectories by Flight Time and Flight Level
            limit_up    = 600   # [minutes]
            limit_down  = 80   # [minutes]
            limit_FL = 334      # [FL]
            citrus = apple[apple['callsign_geo'] == j].reset_index(drop=True)
            citrus['fl'] = pd.to_numeric(citrus['fl'])
            durian = citrus.fl.max()
            date_1 = datetime.datetime.strptime(citrus['time_over'][0], '%d/%m/%Y %H:%M')
            date_2 = datetime.datetime.strptime(citrus['time_over'][citrus.shape[0] - 1], '%d/%m/%Y %H:%M')
            actype = citrus['AAC-type'][0]
            timedelta = (date_2 - date_1).total_seconds() / 60
            if timedelta > limit_down \
                    and timedelta < limit_up and durian <= limit_FL:
                counter += 1
                print("Selecting trajectory #{} : {}   | FL{}    | {}".format(str(counter).zfill(2), actype, durian, j))
                selection.append(j)

        selection = ['DLH35N', 'DLH37F', 'EZY81NL', 'GMI2209',
                     'IBE31DP', 'SBI795', 'SBI797', 'SDM6657', 'VOE27SR',
                     'AEE8', 'DLH48H', 'DLH62K',
                     'AFL2326', 'DLH1781', 'DLH1835', 'DLH2557', 'DLH2EJ',
                     'DLH2JW', 'DLH587', 'DLH681', 'DLH9CF', 'NLY1GG',
                     'NLY6WW', 'SBI897', 'TRA908V', 'TRA9352', 'NAX56MG',
                     'SAS4759', 'ICE532', 'IBE31DD']

        # selection = ['DLH48H', 'TRA9352', 'TRA908V',
        #              'DLH2WT', 'JEI252', 'DLH87P']

        # selection = ['DLH2557', 'IBE31DD', 'SAS4759', 'AFL2326']

        with open(save_file, 'wb') as fp:
            pickle.dump(selection, fp)

    with open(save_file, 'rb') as fp:
        selection = pickle.load(fp)

    print('\nThe selected trajectories are:\n')
    for counter, word in enumerate(selection):
        if ((counter+1) % 3) == 0:  print(word)
        else:                   print(word, end=' ')
    print(' ')
    counter = 0
    for i, j in enumerate(banana):
        citrus = apple[apple['callsign_geo'] == j].reset_index(drop=True)
        if j in selection:
            counter += 1
            print("Saving trajectory #{} : {}".format(str(counter).zfill(2), j))
            name = j
            citrus.to_excel(path_traj + "\\" + name + ".xlsx", j)

    print(' ')
    CreateSCN_Cruise3(True, selection)
    CreateSCNM3('Trajectories-batch3', file4)
    orig = os.listdir(os.path.join(os.getcwd(), file3))[0]

if del_runs:
    if os.path.isdir("output\\runs"):
        shutil.rmtree("output\\runs")
    try:
        os.remove("output\\WRITER Standard File.xlsx")
    except:
        pass

# run a trajectory for every ensemble
if run:
    traj_folder_list = os.listdir(traj_folder)
    # traj_folder_list.reverse()
    for dir in traj_folder_list:
        if dir in skip_entire_dir:
            continue
        traj_counter = 0
        traj = os.listdir(traj_folder + "\\" + dir)
        traj.append('dummy')
        replace_batch_set2(dir, "Trajectories-batch3", "Trajectories-batch4")
        talk_traj2(dir, traj_counter)
        if dir in '4 inf':
            list_ensemble = np.arange(29, 30)  # np.flip(np.arange(1, 51))
        for ensemble in list_ensemble:
            replace_ensemble(ensemble, "Trajectories-batch4.scn")
            runs += 1
            talk_time(runs)
            talk_run3(ensemble, dir, runs)
            try:
                bs_desktop()
                # Move the input and output log files into their log folders
                movelog2(ensemble, dir, False)
                writerfix2(dir, traj_counter, False)
            except:
                print(f'The run for Ensemble {ensemble} failed for w/e reason :( !!')
                print('The simulation will try to continue with the next iteration!')
                continue
        traj_counter += 1

# Open the folder with all the results
talk_time(runs)
# os.startfile('output\\runs')

# overall_aggregate() #os.getcwd() + '\\output\\runs_save')
# skip = [#'ADH931', 'AEE929', 'AUI34L', 'TFL219',
#         'SWR779', 'AZA1572', 'DLH156', 'FPO551',
#         'PRI5403', 'EZY471', 'RYR5008',
#         'DLH1HU', 'SHT2J', 'BAW4TM', 'AFR234H',
#         'PGT4629',
#         'SAS1842', 'DLH08W', 'SAS1042',
#         'TAP803L', 'NJE2FD', 'LBT7362',
#         'KLM1395', 'BLX328', 'BER717E',
#         'TAP1015', 'PGT424', 'EZY92FN',
#         'AFL2352', 'QTR022',
#         'BEL7PC', 'DTH3057', 'EXS79G',
#         'CCA931', 'ROT608D', 'VLG2473',
#         'BAW66Q', 'EIN111', 'DLH8PK',
#         'SAS618', 'DLH8PK', 'BEL724',
#         'TAY011', 'EZY471', 'OHY2160',
#         'WZZ114', 'MON752A'
#         ]

try:
    overall_aggregate2()
    result_analysis2()
except:
    pass

talk_time(runs)
# exit()
os.system("shutdown /s /t 180")

# import pickle
# df = pickle.load( open(
#   "I:\Documents\Google Drive\Thesis 2018\BlueSky Git3\queries\pickle\\results_3600_1-50.p", "rb" ) )
# print(df.to_string())
# df.to_csv('Results_1-50')
