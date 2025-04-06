'''

Author: Apod
Version: 1.0.2
Updated: January 25, 2025

'''

import time
import os
import numpy as np
import PIL.Image,PIL.ImageDraw,PIL.ImageFont
import xlsxwriter
import cv2
import urllib.request
import string

def Fog_Event_(Parent):
    starting_time = time.perf_counter()
    Fog = Parent.data_view['fog_island']
    Board_Array = np.array(PIL.Image.open(Parent.Initial_fP+'/Fog_Island/'+'Fog_Board_DO_NOT_DELETE.jpg'))
    Board_Template = np.copy(Board_Array)
    Chests_Only,Dragons_Only,Chest_and_Dragons = np.copy(Board_Array),np.copy(Board_Array),np.copy(Board_Array)

    Fog_Event = Fog['islands'][Parent.event_number]
    Zip_fileName = Fog_Event['zip_file'].split('.')[0].split('/')[-1]
    Asset_Zip = Parent.asset_zip_fP[0]+'fog_island'+Parent.asset_zip_fP[1]+Zip_fileName+'.zip'
    Parent.Assets_Output.write(f"tid name: {Fog_Event['tid_name']}\nanalytic id: {Fog_Event['analytics_id']}\nzip filepath:{Asset_Zip}\ncanvas url: {Fog_Event['canvas_assets_url']}\nbackground: {Fog_Event['background_plist']}\nforegound: {Fog_Event['foregrounds_plists']}")
    Parent.Assets_Output.close()
    Missing_Images_filePath = Parent.Event_fP+"Missing_Images.txt"
    
    Temp_fP = Parent.Event_fP+'Temp.png'
    Temp_Default_fP = '/'.join(Parent.Event_fP.split('/')[:-2])+'/Temp_Default.png'
    Default_Icon = np.copy(np.asarray(PIL.Image.open(Temp_Default_fP)))
    Icon_Sizing = (60,60)
    Fog_Rewards = {'CHEST':{},'DRAGON_PIECE':{}}
    Images_Downloaded = {}
    Chests_of_Interest = []
    for chest in Parent.Chests_Desired:
        if isinstance(chest,list):
            for chest_entry in chest:
                Chests_of_Interest.append(chest_entry)
        else:
            Chests_of_Interest.append(chest)
    Chests_of_Interest_Names = []
    for chest_count,chest_name in enumerate(Parent.Chests_Desired_Names):
        if isinstance(Parent.Chests_Desired[chest_count],list):
            for chest_entry in Parent.Chests_Desired[chest_count]:
                Chests_of_Interest_Names.append(chest_name)
        else:
            Chests_of_Interest_Names.append(chest_name)

    # print(1,time.perf_counter()-starting_time)
    # 1, pull data from asset_versioning
    # 2, in there you will find a chests section
    # 3, which has the following entry chest_guard_bp_x5    spine    1
    # 4, if you don't find an entry for the chest, you can assume that it conforms to the old method for URL construction
    # 5, "spine" means you need to insert basic_ at the front of the name before concatenating the rest of the URL
    # So it's (url) + "basic_" + chest name from config
    # Spine value other than 1 appends corresponding letter "_b" for 2, etc.
    for grid in Fog['squares']:
        
        if grid['type'] == 'CHEST':
            if not grid['type_id'] in Fog_Rewards['CHEST']:
                Chest_Name_Spine_Conditional_Front = ""
                Chest_Name_Spine_Conditional_Back = ""
                Chest_Name = Parent.Chest_Ids[grid['type_id']]['img_name']
                if Chest_Name in Parent.Asset_Versioning['Chests']:
                    if Parent.Asset_Versioning['Chests'][Chest_Name]['Format'] == 'spine':
                        Chest_Name_Spine_Conditional_Front = "basic_"
                    if Parent.Asset_Versioning['Chests'][Chest_Name]['Version'] != 1:
                        Chest_Name_Spine_Conditional_Back = "_"+string.ascii_lowercase[Parent.Asset_Versioning['Chests'][Chest_Name]['Version']]
                Chest_Image_Link = Parent.Image_Formats[grid['type']]+Chest_Name_Spine_Conditional_Front+Chest_Name+Chest_Name_Spine_Conditional_Back+".png"
                try:
                    urllib.request.urlretrieve(Chest_Image_Link,Temp_fP)
                except urllib.request.HTTPError:
                    if not os.path.exists(Parent.Event_fP+"Missing_Images.txt"):
                        with open(Missing_Images_filePath,'w') as missing_images_file:
                            missing_images_file.write(f"{grid['type']} #{grid['type_id']}\n")
                    else:
                        with open(Missing_Images_filePath,'a') as missing_images_file:
                            missing_images_file.write(f"{grid['type']} #{grid['type_id']}\n")
                        
                array_temp = np.copy(np.asarray(PIL.Image.open(Temp_fP)))
                PIL.Image.fromarray(Default_Icon).save(Temp_fP)
                for x in range(array_temp.shape[0]):
                    for y in range(array_temp.shape[1]):
                        if array_temp[y,x,3] != 255:
                            array_temp[y,x,:] = [255,255,255,255]
                out_array_temp = np.copy(array_temp)
                array_temp_transparency = np.argwhere(array_temp[:,:,3]==0)
                for z in array_temp_transparency:
                    out_array_temp[z[0],z[1]] = (255,255,255,255)
                Fog_Rewards['CHEST'][grid['type_id']] = PIL.Image.fromarray(cv2.resize(out_array_temp[:,:,:-1],dsize=Icon_Sizing,interpolation=cv2.INTER_CUBIC))
        if grid['type'] == 'DRAGON_PIECE':
            if not grid['reward_id'] in Fog_Rewards['DRAGON_PIECE']:
                urllib.request.urlretrieve("https://dca-static-s1.socialpointgames.com/static/dragoncity/mobile/ui/dragons/HD/thumb_"+Parent.Dragon_Info[Fog['rewards'][grid['reward_id']-1]['reward_id']]['img_name_mobile']+'_3.png',Temp_fP)
                array_temp = np.asarray(PIL.Image.open(Temp_fP))
                Fog_Rewards['DRAGON_PIECE'][grid['reward_id']] = PIL.Image.fromarray(cv2.resize(array_temp,dsize=Icon_Sizing,interpolation=cv2.INTER_CUBIC))
    
    # print(2,time.perf_counter()-starting_time)
    # print(Parent.Chests_Desired)
    for x in Fog['squares']:
        x1 = 1515-(100*(x['y']+1)+x['y'])
        x2 = 1515-(100*x['y']+x['y'])
        y1 = (100*x['x']+x['x']+1)
        y2 = (100*(x['x']+1)+x['x']+1)
        if 'type_id' in x:
            # for chest_listing in Parent.Chests_Desired:
            if x['type_id'] in Chests_of_Interest:
                # print(x)
                Board_Array[x1:x2,y1:y2] = 25
                Chests_Only[x1:x2,y1:y2] = 25
                Chest_and_Dragons[x1:x2,y1:y2] = 25
        if x['type'] == 'DRAGON_PIECE':
            Board_Array[x1:x2,y1:y2] = 75
            # if x['reward_id'] == len(Fog['rewards']):
            Dragons_Only[x1:x2,y1:y2] = 75
            Chest_and_Dragons[x1:x2,y1:y2] = 75

    # print(3,time.perf_counter()-starting_time)
    Event_Start_Date = time.ctime(Fog['islands'][Parent.event_number]['start_ts'])
    PIL.Image.fromarray(Chests_Only).save(Parent.Event_fP+'Chests Only.jpg')
    PIL.Image.fromarray(Dragons_Only).save(Parent.Event_fP+'Dragons Only.jpg')
    PIL.Image.fromarray(Chest_and_Dragons).save(Parent.Event_fP+'Chests and Dragons.jpg')
    PIL.Image.fromarray(Board_Array).save(Parent.Event_fP+'Fog Board Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.jpg')
    Fog_Board = PIL.Image.open(Parent.Event_fP+'Fog Board Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.jpg')
    Temp_Array = np.zeros((Board_Array.shape[0],Board_Array.shape[1],3),'uint8')
    if len(Board_Template.shape) == 3:
        for x in range(3):
            Temp_Array[:,:,x] = Board_Template[:,:,x]
    if len(Board_Template.shape) == 2:
        for x in range(3):
            Temp_Array[:,:,x] = Board_Template
        
    Fog_Board_Visual = PIL.Image.fromarray(Temp_Array)
    Fog_Board_Chests_Visual = PIL.Image.fromarray(Temp_Array)
    Fog_Board_Dragons_Visual = PIL.Image.fromarray(Temp_Array)
    Fog_Board_Dragons_and_Chests_Visual = PIL.Image.fromarray(Temp_Array)
    workbook = xlsxwriter.Workbook(Parent.Event_fP+'Fog Board Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.xlsx')
    
    # print(4,time.perf_counter()-starting_time)
    def Draw_On_Fog(Image_Drawn_On,Fill_Color,Output_Text,Cost_Text,Font_Used,x_placement,y_placement,Cost_Text_Offset):
        if Output_Text!="":
            Image_Drawn_On.text((x_placement,y_placement),Output_Text,fill=Fill_Color,font=Font_Used)
        Image_Drawn_On.text((x_placement,y_placement+Cost_Text_Offset),Cost_Text,fill=Fill_Color,font=Font_Used)
     
    worksheet = workbook.add_worksheet()
    Fog_Image = PIL.ImageDraw.Draw(Fog_Board)
    Fog_Image_Visual = PIL.ImageDraw.Draw(Fog_Board_Visual)
    Fog_Image_Chests_Visual = PIL.ImageDraw.Draw(Fog_Board_Chests_Visual)
    Fog_Image_Dragons_Visual = PIL.ImageDraw.Draw(Fog_Board_Dragons_Visual)
    Fog_Image_Dragons_and_Chests_Visual = PIL.ImageDraw.Draw(Fog_Board_Dragons_and_Chests_Visual)
    
    for Square in Fog['squares']:
        x_placement = (100*(Square['x'])+Square['x']+5)
        y_placement = 1515-(100*(Square['y']+1)+Square['y']+5)
        Color = 255
        Font_Used = PIL.ImageFont.truetype("arial.ttf", 20)
        #Font_Used = PIL.ImageFont.truetype(20)
        Cost_Text_Offset = 40
        Chest_Dragon_Identifier = ""
        if 'type_id' in Square:
            Chest_Dragon_Identifier = Square['type_id']
            if Square['type_id'] in Chests_of_Interest:
                Chest_Numbered = np.argwhere(np.array(Chests_of_Interest)==Square['type_id'])[0][0]+1
                Output_Text = 'Chest #' + str(Chest_Numbered)
                Cost_Text = 'cost:'+str(Square['claim_cost'])
                Fill_Color = Color
            if Square['type_id'] not in Chests_of_Interest:
                Output_Text = ""
                Cost_Text = 'cost:'+str(Square['claim_cost'])
                Fill_Color = 0
        if Square['type'] == 'NONE':
            Output_Text = 'Start'
            Cost_Text = 'cost:'+str(Square['claim_cost'])
            Fill_Color = 0
        if Square['type'] == 'STEP':
            Output_Text = 'Tutorial'
            Cost_Text = 'cost:'+str(Square['claim_cost'])
            Fill_Color = 0
        if Square['type'] == 'DRAGON_PIECE':
            Chest_Dragon_Identifier = Square['reward_id']
            Output_Text = 'Dragon #'+str(Square['reward_id'])
            Cost_Text = 'cost:'+str(Square['claim_cost'])
            Fill_Color = Color
        Draw_On_Fog(Fog_Image,Fill_Color,Output_Text,Cost_Text,Font_Used,x_placement,y_placement,Cost_Text_Offset)
        Fog_Image_Visual.text((x_placement+10,y_placement+75),Cost_Text,fill=Fill_Color,font=Font_Used)
        Fog_Image_Dragons_Visual.text((x_placement+10,y_placement+75),Cost_Text,fill=Fill_Color,font=Font_Used)
        Fog_Image_Chests_Visual.text((x_placement+10,y_placement+75),Cost_Text,fill=Fill_Color,font=Font_Used)
        Fog_Image_Dragons_and_Chests_Visual.text((x_placement+10,y_placement+75),Cost_Text,fill=Fill_Color,font=Font_Used)
        if Chest_Dragon_Identifier != "":
            #print(f"{Square}\n  {Square['type']}\n  {Chest_Dragon_Identifier}\n\n")
            Fog_Board_Visual.paste(Fog_Rewards[Square['type']][Chest_Dragon_Identifier],(x_placement+15,y_placement+15))
        
        if Square['type'] == 'CHEST':
            if Square['type_id'] in Chests_of_Interest:
                if Chest_Dragon_Identifier != "":
                    Fog_Board_Chests_Visual.paste(Fog_Rewards[Square['type']][Chest_Dragon_Identifier],(x_placement+15,y_placement+15))
                    Fog_Board_Dragons_and_Chests_Visual.paste(Fog_Rewards[Square['type']][Chest_Dragon_Identifier],(x_placement+15,y_placement+15))
        
        if Square['type'] == 'DRAGON_PIECE':
            if Chest_Dragon_Identifier != "":
                Fog_Board_Dragons_Visual.paste(Fog_Rewards[Square['type']][Chest_Dragon_Identifier],(x_placement+15,y_placement+15))
                Fog_Board_Dragons_and_Chests_Visual.paste(Fog_Rewards[Square['type']][Chest_Dragon_Identifier],(x_placement+15,y_placement+15))
        
        worksheet.write(14-Square['y'],Square['x'],Square['claim_cost'])
    
    # print(5,time.perf_counter()-starting_time)
    Dragon_Key_File = open(Parent.Event_fP+'Dragon_and_Chest_Board_Number_Key.txt','w')
    Dragon_Key_File.write('Dragon Piece Key\n')
    for x in Parent.data_view['fog_island']['rewards']:
        Dragon_Key_File.write(f"#{x['id']}: {Parent.Local_Dict['tid_unit_'+str(x['reward_id'])+'_name']}\n")
     
    # print(6,time.perf_counter()-starting_time)
    Dragon_Key_File.write('\nChest Key\n')
    for chest_count,chest in enumerate(Chests_of_Interest_Names):
        Dragon_Key_File.write(f"#{chest_count+1}: {chest}\n")
    Dragon_Key_File.close()

    # print(7,time.perf_counter()-starting_time)
    workbook.close()
    Fog_Board.save(Parent.Event_fP+'Edited Fog Board Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.jpg')
    Fog_Board_Visual.save(Parent.Event_fP+'Image Added Fog Board Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.png')
    Fog_Board_Chests_Visual.save(Parent.Event_fP+'Image Added Fog Board [Chests] Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.png')
    Fog_Board_Dragons_Visual.save(Parent.Event_fP+'Image Added Fog Board [Dragons] Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.png')
    Fog_Board_Dragons_and_Chests_Visual.save(Parent.Event_fP+'Image Added Fog Board [Chests and Dragons] Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.png')
    