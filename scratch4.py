from scratch_methods import *

# flights = ['DLH87P', 'DLH48H']  # file 0
# flights = ['BAW4TM', 'BEL724']  # file 1
flights = ['ADH931', 'AEE929']
# path = 'F:\Documents\BlueSky Backup\Final Runs\Oct 31 Remon TW_bot Wx1'
path = 'F:\Documents\BlueSky Backup\Final Runs\\Nov 15 Munich TW_mid Wx1'
path2 = 'C:\Documents\Git 2\output\\runs-save'
flights1 = 'SAS4759'
flights2 = [flights1]
set_TW_place(True)
# Set II: DLH2557, IBE31DD, SAS4759, -- AFL2326
# Set  I: TAP1015, AZA1572, BEL7PC, EXS79G
# BER717E CCA931 DLH08W AFR234H
# overall_aggregate2()
# result_analysis2(None, ['min', 'det'])

overall_scoring = True

if not overall_scoring:
    # 1
    # print(' ')
    # getLog(path, flights1, [0, 900, 1800]) #, False, 10)
    # 2
    # speedchanges(flights2, path, 6)
    # speedchanges(None, path)
    flights2 = [flights1]
    # 4
    limits = [71000, 74000, 1.005]
    limits = [750, 1150]
    limits = [2200, 2600, 1.01]
    # tw = fuelvsdelay(flights1, path, limits)
    # tw = fuelvsdelay(flights1, path)
    # 3 - distance as well
    # TWscore(None, path, None, 200)
    # TWscore(flights2, path, tw)
    TWperformance(flights2, path, [3, 21])
    # TWperformance(flights2, path)
else:
    # Overall scoring
    speedchanges(None, path)
    TWscore(None, path, None, 200)


#
# path = 'F:\Documents\BlueSky Backup\Final Runs\Run Oct 14 TW_bot Remon Wx3'
# set_delays([0, 180, 300, 600, 900, 1200, 1500, 1800])
# Dir = os.listdir(path)
# for i, dir in enumerate(Dir):
#     if 'mid' in dir:
#         print(f'TW is placed in the middle!')
#         set_TW_place(True)
#     if 'bot' in dir:
#         print(f'TW is placed at the bottom!')
#         set_TW_place(False)
#     if i > 3:
#         continue
#     print(f'Starting analysis for folder {dir}')
#     overall_aggregate2(os.path.join(path, dir))
#     result_analysis2(os.path.join(path, dir))







