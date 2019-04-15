import numpy as np
import sys
import os
import fileinput as fi
#from BlueSky import main
# print(sys.argv)
#sys.argv.append("--headless")
#sys.arg,"--scenfile","\experimental\Trajectories.scn"])
#main()

# Scenario batch file
global scenario_manager, settings_config, dt
scenario_manager = "F:\Documents\Google Drive\Thesis 2018\BlueSky\scenario\Trajectories-batch.scn"
settings_config = "F:\Documents\Google Drive\Thesis 2018\BlueSky\settings.cfg"
dt = '0.10' # format '#.##'
set_of_dt = ['0.05', '0.10', '0.20', '0.50', '1.00']
list_ensemble = list(range(1,5))

# Switches the ensemble in the scenario manager and adapts the name using the ensemble # and global dt
def replace_ensemble(ensemble):
    f = open(scenario_manager, 'r')
    filedata = list(f.read())
    f.close()
    ensemble = str(ensemble)

    if len(ensemble) < 2:
        filedata[63]    = str(0)
        filedata[64]    = ensemble[0]
        filedata[4135]  = str(0)
        filedata[4136]  = ensemble[0]
    else:
        filedata[63]    = ensemble[0]
        filedata[64]    = ensemble[1]
        filedata[4135]  = ensemble[0]
        filedata[4136]  = ensemble[1]

    filedata[4141]  = dt[0]
    filedata[4142]  = dt[1]
    filedata[4143]  = dt[2]
    filedata[4144]  = dt[3]

    filedata2 = str("".join(filedata))
    f = open(scenario_manager, 'w')
    f.write(filedata2)
    f.close()
    pass


# Changes the timestep in the settings config of BlueSky using the provided timestep
# Keep in mind that the savefile doesn't change its name, unless the timestep is set into the global variable dt
def set_dt(timestep):
    f = open(settings_config, 'r')
    filedata = list(f.read())
    f.close()

    filedata[1030] = timestep[0]
    filedata[1031] = timestep[1]
    filedata[1032] = timestep[2]
    filedata[1033] = timestep[3]

    filedata2 = str("".join(filedata))
    f = open(settings_config, 'w')
    f.write(filedata2)
    f.close()
    pass

# This functions replaces the dt in the settings.cfg with the globally defined dt
def replace_dt():
    f = open(settings_config, 'r')
    filedata = list(f.read())
    f.close()

    filedata[1030] = dt[0]
    filedata[1031] = dt[1]
    filedata[1032] = dt[2]
    filedata[1033] = dt[3]

    filedata2 = str("".join(filedata))
    f = open(settings_config, 'w')
    f.write(filedata2)
    f.close()
    pass

# Run a simulation of BlueSky using the desktop path
def run_bluesky_desktop():
    os.system("call C:\Programs\Tools\Anaconda\Program\Scripts\\activate.bat && \
                    cd C:\Documents\BlueSky && conda activate py36 && python BlueSky.py")

# Run a simulation of BlueSky using the laptop path
def run_bluesky_laptop():
    os.system("call I:\Programs\Anaconda\Program\Scripts\\activate.bat && \
                    cd I:\Documents\Google Drive\Thesis 2018\BlueSky Git2 && python BlueSky.py")

# Cut the number to 3 digits
def cut3(one):
    return round(one, 3)

# Cut the number to 7 digits
def cut7(one):
    return round(one, 7)

# Add a random delay to the time provided
def addSecs(tm, secs, secs2):
    secs = secs*60
    fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    if secs2 == 0:
        fulldate = fulldate + datetime.timedelta(seconds=(secs))
        delay = secs
    else:
        fulldate = fulldate - datetime.timedelta(seconds=(secs))
        delay = -secs
    return str(fulldate.time()), delay

# Create a scenario file from the provided trajectories and save it in the provided name
def CreateSCN(alpha, save_file):
    # Constants
    nm  = 1852.  # m       1 nautical mile
    ft  = .3048  # m        1 foot

    folder = "\queries\\"
    FileName = os.listdir(folder)

    # Tk().withdraw()
    # print("Choose the csv file:")
    # FileName = askopenfilename()
    #FileName = 'C:\Documents\BlueSky\scenario\experimental\\Flight_1.csv'
    traj = 0
    banana = list()
    #banana.append('00:00:00.00> SWRAD VOR')
    #banana.append('00:00:00.00> FF 79495')

    for k in FileName:
        scenario = pd.read_csv(folder +"\\" + k)
        traj += 1
        traj2 = str(traj)
        if traj2.count('') < 3:
            id = '0' + str(traj)
        else:
            id = str(traj)
        aircraftid = 'KLM' + id + '-%0'
        actype  =  ', A320, '
        [heading, distance] = dist(scenario['st_x(gpt.coords)'][0], scenario['st_y(gpt.coords)'][0],
                                    scenario['st_x(gpt.coords)'][1], scenario['st_y(gpt.coords)'][1])
        if heading < 0:
            heading += 360

        #speed = '250'
        apple = scenario.time_over[0]

        if alpha:
            apple = datetime.datetime(100, 1, 1, int(apple[-8:-6]), int(apple[-5:-3]), int(apple[-2:]))
            apple, delay = addSecs(apple, random.randrange(16), random.randrange(1))
        else:
            apple = apple[-8:]
        # banana.append('>SPD KLM1705 250')
        # banana.append('>ALT KLM1705 300')
        # banana.append('>KLM1705 ORIG EHAM 00:00:00.00')
        j = 0

        for i in range(scenario.shape[0]):
            if i != 0:
                j = -1

            FlightLevel = str(scenario['fl'][i])
            if FlightLevel.count('') < 3:
                FlightLevel = '0' + FlightLevel
            FlightLevel = 'FL' + FlightLevel

            if i == 0:
                banana.append(apple + '.00> CRE ' + aircraftid + actype + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                              + str(cut7(scenario['st_y(gpt.coords)'][i])) + ', ' + str(cut3(heading)) + ', ' + FlightLevel + ', ' + '0')
                banana.append(apple + '.00> DEFWPT ' + aircraftid + '-ORIG,' + str(cut7(scenario['st_x(gpt.coords)'][i])) + ', '
                              + str(cut7(scenario['st_y(gpt.coords)'][i])))
                banana.append(apple + '.00> ORIG ' + aircraftid + ', ' + aircraftid + '-ORIG')
                              #str(scenario['st_x(gpt.coords)'][i]) + ' ' + str(scenario['st_y(gpt.coords)'][i]))
                banana.append(apple + '.00> DEFWPT ' + aircraftid + '-DEST, ' + str(cut7(scenario['st_x(gpt.coords)'][scenario.shape[0]-1]))
                                + ', ' + str(cut7(scenario['st_y(gpt.coords)'][scenario.shape[0]-1])))
                banana.append(apple + '.00> DEST ' + aircraftid + ', ' + aircraftid + '-DEST' )
                #+ str(scenario['st_x(gpt.coords)'][scenario.shape[0] - 1]) + ' ' + str(scenario['st_y(gpt.coords)'][scenario.shape[0] - 1])
                # +str(scenario['fl'][i]) +
            else:
                #banana.append('> ALT ' + aircraftid + ', ' + FlightLevel)
                #banana.append('> SPD ' + aircraftid + ', ' + speed)
                if i == scenario.shape[0]-1:
                    follow = aircraftid + '-' + str(i-1)
                    banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                  + aircraftid + "-DEST" + ', ' + FlightLevel + ', ' + '0')
                else:
                    deltatime   = datetime.datetime.strptime(scenario.time_over[i], '%Y-%m-%d %H:%M:%S') -\
                                    datetime.datetime.strptime(scenario.time_over[i+j], '%Y-%m-%d %H:%M:%S')

                    distance    = abs(dist2(scenario['st_x(gpt.coords)'][i+j], scenario['st_y(gpt.coords)'][i+j],
                                     scenario['st_x(gpt.coords)'][i], scenario['st_y(gpt.coords)'][i]))

                    height      = abs((scenario['fl'][i] - scenario['fl'][i+j]) * 100 * ft)
                    distance    = (height**2 + distance**2)**(1/2)

                    speed = distance / deltatime.total_seconds() * 3600 / nm

                    if i == 1:
                        follow = aircraftid + '-ORIG'
                    else:
                        follow = aircraftid + '-' + str(i-1)

                    banana.append(apple + '.00> DEFWPT ' + aircraftid + '-' + str(i) + ', '+ str(cut7(scenario['st_x(gpt.coords)'][i]))
                                        + ', ' + str(cut7(scenario['st_y(gpt.coords)'][i])))
                    banana.append(apple + '.00> ' + aircraftid + ' after ' + follow + ' ADDWPT '
                                        + aircraftid + '-' + str(i) + ', ' + FlightLevel + ', ' + str(cut3(speed)))
                    #+ ', ' + FlightLevel + ', ' + speed
                    # banana.append(apple + ".00>DEFWPT WPTZ" + str(i) + ',' + str(scenario['st_x(gpt.coords)'][i]) + ', ' + str(scenario['st_y(gpt.coords)'][i]))

                    #acid AFTER afterwp ADDWPT (wpname/lat,lon),[alt,spd]

    #save = pd.DataFrame(banana)
    with open("C:\Documents\Git\\trunk\scenario\\"+ save_file + '.scn', "w") as fin:
        fin.write('\n'.join(banana))
    os.startfile("C:\Documents\Git\\trunk\scenario\\" + save_file + '.scn')

    # save.to_csv('test1.scn', sep=',', index=False, header=False, quoting=0)
    # banana.to_csv('test2.scn', sep=',')
    # writer = pd. Writer('{0}/{1}.xlsx'.format(name, i))
    # save.to_excel(writer)
    # writer.save()

    # os.startfile("F:\Documents\Python Scripts\ThesisScript")

CreateSCN(False, 'Test4')

# assign the timestep and run the simulations X times
for i in set_of_dt:
    dt = i
    replace_dt()
    for j in list_ensemble:
        replace_ensemble(i)
        run_bluesky_desktop()
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

