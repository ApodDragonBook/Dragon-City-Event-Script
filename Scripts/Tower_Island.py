'''
Version 1.0.1
Author: Apod
'''

import time
import numpy as np
import PIL.Image,PIL.ImageDraw,PIL.ImageFont

def Tower_Event_(Parent):
    Tower_Template = np.array(PIL.Image.open(Parent.Initial_fP+'/Tower_Island/'+'Tower_Template_DO_NOT_DELETE.jpg'))
    
    Tower_Event = Parent.data_view['tower_island']['islands'][-1]
    Event_Start_Date = time.ctime(Tower_Event['start_ts'])
    Zip_fileName = Tower_Event['zip_file'].split('.')[0].split('/')[-1]
    Asset_Zip = Parent.asset_zip_fP[0]+'tower_island'+Parent.asset_zip_fP[1]+Zip_fileName+'.zip'
    Parent.Assets_Output.write(f"tid name: {Tower_Event['tid_name']}\nanalytic id: {Tower_Event['analytics_id']}\nzip filepath:{Asset_Zip}\ncanvas url: {Tower_Event['canvas_assets_url']}")
    Parent.Assets_Output.close()
    
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
    
    Chests_of_Interest_Dict = {}
    for chest_count,chest in enumerate(Chests_of_Interest):
        Chests_of_Interest_Dict[chest] = Chests_of_Interest_Names[chest_count]
            
    
    print(f"Chests of interest: {Chests_of_Interest}\n\nChests of interest names: {Chests_of_Interest_Names}\n\nChests Desired: {Parent.Chests_Desired}\n\nChests Desired Name: {Parent.Chests_Desired_Names}")

    for x in Parent.data_view['tower_island']['squares']:
        Draw = False
        Catapult = False
        if x['type'] == 'CATAPULT':
            Color_Value = 150
            Draw = True
            Catapult = True
            for landing_spot in Parent.data_view['tower_island']['squares']:
                if landing_spot['id'] == x['catapult_destination_square_id']:
                    Landing_x,Landing_y = landing_spot['y'],landing_spot['x']
        if x['type'] == 'SINGLE_REWARD':
            if 'b' in x['rewards_array'][0]:
                Color_Value = 100
                Draw = True
            if 'chest' in x['rewards_array'][0]:
                if x['rewards_array'][0]['chest'] in Parent.Chests_Desired:
                    Color_Value = 100
                    Draw = True
        if x['type'] == 'SINGLE_DRAGON_PIECE':
            Color_Value = 175
            Draw = True
        if x['type'] == 'FINAL_DRAGON_SQUARE':
            Color_Value = 0
            Draw = True
        if Draw:
            x1 = Tower_Template.shape[0]-(100*(x['y']-1)+x['y']+5*int((x['y']-1)/5))
            x2 = Tower_Template.shape[0]-(100*(x['y']-1)+x['y']+100+5*int((x['y']-1)/5))
            y1 = 100*(x['x']-1)+x['x']
            y2 = 101*x['x']
            Tower_Template[x2:x1,y1:y2] = Color_Value
            
            if Catapult:
                x1 = Tower_Template.shape[0]-(100*(Landing_x-1)+Landing_x+5*int((Landing_x-1)/5))
                x2 = Tower_Template.shape[0]-(100*(Landing_x-1)+Landing_x+100+5*int((Landing_x-1)/5))
                y1 = 100*(Landing_y-1)+Landing_y
                y2 = 101*Landing_y
                Tower_Template[x2:x1,y1:y2] = Color_Value+50


    Tower_Image = PIL.Image.fromarray(Tower_Template)
    Tower_Draw = PIL.ImageDraw.Draw(Tower_Image)

    Catapult_Counter = 1
    Chest_Counter = 1
    Chest_Name_List = []
    Chest_Number_Dict = {}
    Dragon_Piece_Counter = 1
    
    Key_filePath = open(Parent.Event_fP+'Tower_Island_Key_Starting_'+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.txt','w')
    Key_filePath.write('Key: C# - Chest, D# - Dragon, F# - Final Dragon\n')

    for x in Parent.data_view['tower_island']['squares']:
        Horizontal_Offset = 0
        Vertical_Offset = 20
        if x['type'] == 'CATAPULT':
            Tower_Draw.text((100*(x['x']-1)+x['x']+Horizontal_Offset,Tower_Template.shape[0]-(100*(x['y']-1)+x['y']+100+5*int((x['y']-1)/5))+Vertical_Offset),str(Catapult_Counter)+'a',fill=0,font=PIL.ImageFont.truetype("arial.ttf", 60))
            for landing_spot in Parent.data_view['tower_island']['squares']:
                if landing_spot['id'] == x['catapult_destination_square_id']:
                    Landing_x,Landing_y = landing_spot['y'],landing_spot['x']
                    Tower_Draw.text((100*(Landing_y-1)+Landing_y+Horizontal_Offset,Tower_Template.shape[0]-(100*(Landing_x-1)+Landing_x+100+5*int((Landing_x-1)/5))+Vertical_Offset),str(Catapult_Counter)+'b',fill=0,font=PIL.ImageFont.truetype("arial.ttf", 60))
            Catapult_Counter+=1
        if x['type'] == 'SINGLE_REWARD':
            include_check = 0
            if 'chest' in x['rewards_array'][0]:
                if x['rewards_array'][0]['chest'] in Chests_of_Interest_Dict:
                    include_check = 1
                    Chest_Name = Chests_of_Interest_Dict[x['rewards_array'][0]['chest']]
            if 'b' in x['rewards_array'][0]:
                include_check = 1
                Chest_Name = Parent.Local_Dict['_'.join(['tid','building',str(x['rewards_array'][0]['b']),'name'])]
            if include_check == 1:
                Chest_Name_List.append(Chest_Name)
                Chest_Number_Dict[Chest_Name] = Chest_Counter
                Key_filePath.write(f'C{str(Chest_Counter)} - {Chest_Name}\n')
                Chest_Counter+=1
                Tower_Draw.text((100*(x['x']-1)+x['x']+Horizontal_Offset,Tower_Template.shape[0]-(100*(x['y']-1)+x['y']+100+5*int((x['y']-1)/5))+Vertical_Offset),'C'+str(Chest_Number_Dict[Chest_Name]),fill=255,font=PIL.ImageFont.truetype("arial.ttf", 60))
        if x['type'] == 'SINGLE_DRAGON_PIECE':
            Tower_Draw.text((100*(x['x']-1)+x['x']+Horizontal_Offset,Tower_Template.shape[0]-(100*(x['y']-1)+x['y']+100+5*int((x['y']-1)/5))+Vertical_Offset),'D'+str(x['piece_reward_id']),fill=0,font=PIL.ImageFont.truetype("arial.ttf", 60))
        if x['type'] == 'FINAL_DRAGON_SQUARE':
            Tower_Draw.text((100*(x['x']-1)+x['x']+Horizontal_Offset,Tower_Template.shape[0]-(100*(x['y']-1)+x['y']+100+5*int((x['y']-1)/5))+Vertical_Offset),'F1',fill=255,font=PIL.ImageFont.truetype("arial.ttf", 60))
            Final_Dragon_ID = x['rewards_array'][0]['egg']
    Key_filePath.write('\n')
    for x in Parent.data_view['tower_island']['rewards']:
        if x['island_id'] == Parent.data_view['tower_island']['islands'][Parent.Event_Date_Dict[Parent.Events_Available_String.get()]]['id']:
            Key_filePath.write(f"D{str(x['id'])} - {Parent.Local_Dict['tid_unit_'+str(x['dragon_reward_id'])+'_name']}\n")
    Key_filePath.write(f"\nF1 - {Parent.Local_Dict['tid_unit_'+str(Final_Dragon_ID)+'_name']}")
    Tower_Image_fP = Parent.Event_fP+'Tower_Map_'+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.jpg'
    Tower_Image.save(Tower_Image_fP)
