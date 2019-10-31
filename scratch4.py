from scratch_methods import *

# flights = ['DLH87P', 'DLH48H']  # file 0
# flights = ['BAW4TM', 'BEL724']  # file 1
flights = ['ADH931', 'AEE929']
# overall_aggregate2()
# result_analysis2(None, ['min', 'det'])

# fuelvsdelay('BEL7PC')
# TWscore()
# TWperformance(['ADH931'])



exit()
set_delays([0, 180, 300, 600, 900, 1200, 1500, 1800])
# path = 'F:\Documents\BlueSky Backup\Final Runs\Run Oct 24 TW_mid Munich Wx3'
# overall_aggregate2(path)

path = 'F:\Documents\BlueSky Backup\Final Runs\Run Oct 14 TW_bot Remon Wx3'
set_delays([0, 180, 300, 600, 900, 1200, 1500, 1800])
result_analysis2(path)
exit()
overall_aggregate2(path)

Dir = os.listdir(path)
print(Dir)
for i, dir in enumerate(Dir):
    if 'mid' in dir:
        print(f'TW is placed in the middle!')
        set_TW_place(True)
    if 'bot' in dir:
        print(f'TW is placed at the bottom!')
        set_TW_place(False)
    if i > 3:
        continue
    print(f'Starting analysis for folder {dir}')
    overall_aggregate2(os.path.join(path, dir))







