from scratch_methods import *

set_TW_place(True)
path = 'F:\\Documents\\BlueSky Backup\\Final Runs\\Nov 15 Munich TW_mid Wx3'
set_delays([0, 180, 300, 600, 900, 1200, 1500, 1800])
result_analysis2(path, ['1 min'])
# exit()
overall_aggregate2(path)
os.system("shutdown /s /t 600")