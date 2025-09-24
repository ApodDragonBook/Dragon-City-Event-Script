'''

Author: Apod
Version: 1.0.0
Updated: Sept 24, 2025

'''

import sys, subprocess

def Module_Verification():
    Required_Mods = {
        'requests':'requests',
        'numpy':'numpy',
        'PIL':'pillow',
        'urllib3':'urllib3',
        'threading':'thread6',
        'xlsxwriter':'xlsxwriter',
        'cv2':'opencv-python',
        }

    Mods_Found = 0
    Mods_Missing = []
    
    for mod in Required_Mods:
        print(f'Checking for module: {mod}')
        try:
            __import__(mod)
        except:
            print(f'    Attempting to install module: {mod}')
            try:
                subprocess.check_call([sys.executable,'-m', 'pip', 'install', Required_Mods[mod]])
            except:
                print(f'    Failed to install module: {mod}')
            else:
                try:
                    __import__(mod)
                except:
                    print(f'    {mod} did not install correctly')
                else:
                    print(f'    Successfully installed module: {mod}')
                    Mods_Found +=1
        else:
            print(f'{mod} is already installed')
            Mods_Found +=1
     
    if Mods_Found == len(Required_Mods):
        print(f'All {Mods_Found} were successfully imported, you are ready to use the main script!')
        return 0
    else:
        print(f'The following {len(Mods_Missing)} mods were not succesfully imported:')
        for mod_missing in Mods_Missing:
            print(f'    {mod_missing}')
    
            return Mods_Missing
