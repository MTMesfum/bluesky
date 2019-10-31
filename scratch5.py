from scratch_methods import *


set_TW_place(False)
# path = 'F:\Documents\BlueSky Backup\Final Runs'
result_analysis2()
exit()


Dir = os.listdir(path)
print(Dir)
for i, dir in enumerate(Dir):
    if i < 3 or i > 3:
        continue
    print(f'Starting analysis for folder {dir}')
    result_analysis2(os.path.join(path, dir))