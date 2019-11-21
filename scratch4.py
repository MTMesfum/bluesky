from scratch_methods import *

# flights = ['DLH87P', 'DLH48H']  # file 0
# flights = ['BAW4TM', 'BEL724']  # file 1
flights = ['ADH931', 'AEE929']
path = 'F:\Documents\BlueSky Backup\Final Runs\Oct 31 Remon TW_bot Wx1'
path2 = 'C:\Documents\Git 2\output\\runs-save'
flights1 = 'EXS79G'
flights2 = [flights1]
set_TW_place(False)
# TAP1015, AZA1572, BEL7PC, EXS79G
# overall_aggregate2()
# result_analysis2(None, ['min', 'det'])

# 1
# print(' ')
# getLog(path, flights1, [0, 900, 1800]) #, False, 10)
# 2
# speedchanges(flights2, path)
# speedchanges(None, path)
flights2 = [flights1]
# 4
limits = [3600, 4000, 1.005]
# tw = fuelvsdelay(flights1, path, limits)
# 3 - distance as well
TWscore(None, path, None, 250)
# TWscore(flights2, path, tw)
# TWperformance(flights2, path, [3, 7])




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







