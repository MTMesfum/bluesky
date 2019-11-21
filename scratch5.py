from scratch_methods import *


set_TW_place(True)
path = 'F:\\Documents\\BlueSky Backup\\Final Runs\\Nov 15 Munich TW_mid Wx1'
set_delays([0, 180, 300, 600, 900, 1200, 1500, 1800])
result_analysis2(path, ['1 min'])
overall_aggregate2(path)

exit()
Dir = os.listdir(path)
print(Dir)
for i, dir in enumerate(Dir):
    if i < 3 or i > 3:
        continue
    print(f'Starting analysis for folder {dir}')
    result_analysis2(os.path.join(path, dir))