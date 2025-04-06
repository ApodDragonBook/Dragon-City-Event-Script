import time
import numpy as np
import xlsxwriter

def rgb_to_hex(r,g,b):
    return '#%02x%02x%02x' % (r, g, b)

def Light_v_Dark(r,g,b):
    if (.299*r**2+.587*g**2+.114*b**2)<(127**2):
        Text_Color = 255
    if (.299*r**2+.587*g**2+.114*b**2)>=(127**2):
        Text_Color = 0
    
    return Text_Color

def Maze_Event_(Parent):
    Maze = Parent.data_view['maze_island']
    Islands = Maze['islands']
    Paths = Maze['paths']
    Maze_Dictionary = {'Nodes':{},'Paths':{},'Rewards':{}}
    for node in Maze['nodes']:
        Maze_Dictionary['Nodes'][node['id']] = node
    for rewards in Maze['rewards']:
        Maze_Dictionary['Rewards'][rewards['id']] = rewards['reward'][0]
    for pathing in Paths:
        Maze_Dictionary['Paths'][pathing['id']] = pathing
    
    
    Maze_Event = Islands[Parent.event_number]
    
    colors_used = []
    for path_given in Maze_Event['paths']:
        for path in Paths:
            if path_given == path['id']:
                colors_used.append(path['color'])
    
    if not Parent.Maze_Color_Check_Status:
        return colors_used, Maze_Dictionary
    
    Zip_fileName = Maze_Event['zip_file'].split('.')[0].split('/')[-1]
    Asset_Zip = Parent.asset_zip_fP[0]+'maze_island'+Parent.asset_zip_fP[1]+Zip_fileName+'.zip'
    Parent.Assets_Output.write(f"tid name:{Maze_Event['tid_name']}\nzip filepath:{Asset_Zip}\n")
    Coins = 1800*(int((Maze_Event['availability']['to']-Maze_Event['availability']['from'])/(3600*24))+1)+Maze_Event['initial_points']

    #Name output file
    Event_Start_Date = time.ctime(Maze_Event['availability']['from'])
    Output_fP_Format = Parent.Event_fP+Parent.Event_fP.split('/')[-2].split(' ')[0]+' Maze Island Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]
    file = open(Output_fP_Format+'.txt','w')
    
    workbook = xlsxwriter.Workbook(Output_fP_Format+'.xlsx')
    ws1 = workbook.add_worksheet()
    ws1.write(1,0,'Dragons')
    ws1.write(2,0,'Book ID')
    ws1.write(3,0,'Path Type')
    Total_Path_Data = []
    Total_Path_Data_Double = []
    Longest_Path,Locked_Path_Count,Timed_Path_Count = [],0,0
    Path_Information = []
    
    path_numbers = []
    Path_Dragons = []
    Color_Formatting = []
    Track_Color = 0
    for path_given in Maze_Event['paths']:
        counting = 0
        for path in Paths:
            if path_given == path['id']:
                Color_Formatter = workbook.add_format()
                Color_Formatter.set_bg_color(rgb_to_hex(colors_used[Track_Color][0],colors_used[Track_Color][1],colors_used[Track_Color][2]))
                Text_Color = Light_v_Dark(colors_used[Track_Color][0],colors_used[Track_Color][1],colors_used[Track_Color][2])
                Color_Formatter.set_font_color(rgb_to_hex(Text_Color,Text_Color,Text_Color))
                Color_Formatting.append(Color_Formatter)
                Track_Color+=1
                path_numbers.append(counting)
                Path_Dragons.append(' '.join(Parent.Local_Dict['tid_unit_'+str(path['dragon_type'])+'_name'].split(" Dragon")))
            counting+=1
    
    del Path_Dragons[0] #Don't need the first entry, used for the naming the keys in the spreadsheet and the first dragon does not require a key

    Dragon_Output_Tracker = 0
    path_attributes = []
    prior_path_key = True
    key_path_cost = 0
    first_path = True
    Longest_Path = 0
    Path_Tracker = 1
    Align_Right = workbook.add_format()
    Align_Right.set_align('right')
    ws1.set_column('A:XFD', None, Align_Right)
    Red_Background = workbook.add_format()
    Red_Background.set_bg_color('#FF0000')
    Key_Path_Count = 0
    Prior_Key_Cost = 0
    for path_viewing in path_numbers:
        Width_Check = 8
        if not first_path and not prior_path_key and not 'availability' in Paths[path_viewing]:
            ws1.write(3,Path_Tracker,'Open')
        Color_Format = Color_Formatting[Path_Tracker-1]
        Node_Tracker = 0
        if (len(Paths[path_viewing]['nodes'])-1)>Longest_Path:
            Longest_Path = len(Paths[path_viewing]['nodes'])-1
        Key_Found = False
        timed_dragon = 0
        for timed in Paths[path_viewing]:
            if timed == 'availability':
                timed_dragon = 1
        dragons_id = Paths[path_viewing]['dragon_type']
        dragons_name = Parent.Local_Dict['tid_unit_'+str(dragons_id)+'_name']
        ws1.write(1,Path_Tracker,dragons_name,Color_Format)
        if len(dragons_name)>Width_Check:
            Width_Check = len(dragons_name)+1
            Rarity = Parent.Dragon_Info[dragons_id]['dragon_rarity']
            if Rarity == 'V':
                Rarity = 'VR'
            if not dragons_id in Parent.Dragon_Book_IDs:
                ws1.write(2,Path_Tracker,Rarity+'# Unknown',Color_Format)
                if len(Rarity+'# Unknown')+1>Width_Check:
                    Width_Check=len(Rarity+'# Unknown')+2
            if dragons_id in Parent.Dragon_Book_IDs:
                Dragons_ID = Parent.Dragon_Book_IDs[dragons_id]
                ws1.write(2,Path_Tracker,Rarity+'# '+str(Dragons_ID),Color_Format)
                if len(Rarity+'# '+str(Dragons_ID))+1>Width_Check:
                    Width_Check=len(Rarity+'# '+str(Dragons_ID))+2
             
        starting_node = 0
        total_cost = 0
        total_path_costs = [0 for _ in path_numbers]
        key_path_costs = [0 for _ in path_numbers]
        locked_by_key_check = [0 for _ in path_numbers]
        Total_Path_Data_Double_Temp = []
     
        if not first_path and prior_path_key:
            ws1.write(3,Path_Tracker,'Locked')
        Phrase = ''
        Reward_Double_List = []
        for reward_spot in Parent.data_view['maze_island']['rewards']:
            if 'double_with_video_ad' in reward_spot:
                Reward_Double_List.append(reward_spot['id'])
        for key in Paths[path_viewing]['nodes']:
            key2 = Maze_Dictionary['Nodes'][key]
            enemy_list = []
            if 'cost' in key2:
                Node_Cost = str(key2["cost"]["ep"])
                if prior_path_key and not Key_Found:
                    key_path_cost+=key2["cost"]["ep"]
            found = 0
            Video_Ad_Double = 0
            if 'reward_id' in key2:
                if key2['reward_id'] in Reward_Double_List:
                    Video_Ad_Double = 1
            if 'reward' in key2:
                if 'g' in key2['reward'][0]:
                    found=1
                    Phrase += Node_Cost+' gold: '+str(key2["reward"][0]["g"])
                if 'f' in key2['reward'][0]:
                    found=1
                    Phrase+=Node_Cost+' food: '+str(key2["reward"][0]["f"])
                if 'chest' in key2['reward'][0]:
                    found = 1
                    chest_name = Parent.Chest_Naming(Parent.Chest_Ids[key2['reward'][0]['chest']])
                    Phrase+=Node_Cost+' chest: '+chest_name
                if 'perks' in key2['reward'][0]:
                    found = 1
                    Phrase+=Node_Cost+' perk: '+str(key2['reward'][0]['perks'][0]['quantity'])+' of '+Parent.Perks[key2['reward'][0]['perks'][0]['id']]
                if 'b' in key2['reward'][0]:
                    found = 1
                    building_name = Parent.Local_Dict['_'.join(['tid','building',str(key2['reward'][0]['b']),'name'])]
                    Phrase+=Node_Cost+' item: '+building_name
                if bool(Video_Ad_Double):
                    Phrase += ' [Video Double: Yes]'
            if 'encounter' in key2:
                found = 1
                for encount in Parent.data_view['maze_island']['encounters']:
                    if encount['id'] == key2['encounter']:
                        for enemy in encount['enemies']:
                            for enemy_dragon in Parent.data_view['maze_island']['enemies']:
                                if enemy_dragon['id']==enemy:
                                    dragon_id = enemy_dragon['dragon_ids'][0]
                                    Name = Parent.Local_Dict['tid_unit_'+str(enemy_dragon['dragon_ids'][0])+'_name']
                                    enemy_list.append(Name)
                Phrase+=Node_Cost+' battle: '+str(enemy_list)+' ['+str(key2["encounter_skip_cost"]["ep"])+' skip cost]'
            if 'key' in key2:
                Key_Found = True
                prior_path_key = True
                Key_Path_Count += 1
                found = 1
                for key3 in Paths:
                    if key3['id'] == key2['key']:
                        Phrase+=Node_Cost+' key: '+Parent.Local_Dict['tid_unit_'+str(key3['dragon_type'])+'_name']+' key'
            Spreadsheet_Text = ""
            Spreadsheet_Text_Color_Check = False
            Spreadsheet_Text_Color = None
            Spreadsheet_Text_X = 0
            Spreadsheet_Text_Y = 0
            if found == 0 and starting_node == 1 and "cost" in key2:
                #print(key2)
                #total_cost+=key2["cost"]["ep"]
                total_cost+=key2["cost"]["ep"]
                if not 'key' in key2:
                    Spreadsheet_Text = key2['cost']['ep']
                    Spreadsheet_Text_Color_Check = False
                    Spreadsheet_Text_X = 4 + Node_Tracker
                    Spreadsheet_Text_Y = Path_Tracker
                if 'key' in key2:
                    Spreadsheet_Text = key2['cost']['ep']
                    Spreadsheet_Text_Color_Check = True
                    Spreadsheet_Text_Color = Color_Formatting[Path_Tracker]
                    Spreadsheet_Text_X = 4 + Node_Tracker
                    Spreadsheet_Text_Y = Path_Tracker
                if not (prior_path_key) or (prior_path_key and first_path):
                    Phrase+=Node_Cost+' Finish [Total: '+str(total_cost)+']'
                if prior_path_key and not first_path:
                    Costing = total_cost+Prior_Key_Cost
                    Prior_Key_Cost = key_path_cost
                    Phrase+=Node_Cost+' Finish [Total: '+str(total_cost)+'/'+str(Costing)+']'
            if found == 0 and starting_node == 0:
                starting_node = 1
                Phrase+='Starting node for '+dragons_name
                if timed_dragon == 1:
                    start_timed = Paths[path_viewing]['availability']['from']+3600*9
                    end_timed = Paths[path_viewing]['availability']['to']+3600*9
                    duration = np.ceil((end_timed-start_timed)/(3600*24))
                    start_date = time.ctime(Paths[path_viewing]['availability']['from'])
                    Start_Date_Text = start_date[4:7]+' '+str(int(start_date[8:10]))
                    end_date = time.ctime(Paths[path_viewing]['availability']['to'])
                    End_Date_Text = str(int(end_date[8:10]))
                    if end_date[4:7]!=start_date[4:7]:
                        End_Date_Text = end_date[4:7]+' '+end_date[8:10]
                    Date_Text = Start_Date_Text+' - '+End_Date_Text
                    Spreadsheet_Text = Date_Text
                    Spreadsheet_Text_Color_Check = True
                    Spreadsheet_Text_Color = Red_Background
                    Spreadsheet_Text_X = 3
                    Spreadsheet_Text_Y = Path_Tracker
                    if len(Date_Text)>Width_Check:
                        Width_Check=len(Date_Text)+1
                    Phrase+='\nTimed Path: starts '+str(time.ctime(start_timed))+' and lasts '+str(int(duration))+' days'
            if 'cost' in key2 and found == 1:
                total_cost+=key2["cost"]["ep"]
                if not 'key' in key2:
                    Spreadsheet_Text = key2['cost']['ep']
                    Spreadsheet_Text_Color_Check = False
                    Spreadsheet_Text_X = 4 + Node_Tracker
                    Spreadsheet_Text_Y = Path_Tracker
                if 'key' in key2:
                    Spreadsheet_Text = key2['cost']['ep']
                    Spreadsheet_Text = f"{Spreadsheet_Text} {Path_Dragons[0]}"
                    del Path_Dragons[0]
                    Spreadsheet_Text_Color_Check = True
                    Spreadsheet_Text_Color = Color_Formatting[Path_Tracker]
                    Spreadsheet_Text_X = 4 + Node_Tracker
                    Spreadsheet_Text_Y = Path_Tracker
                if bool(Video_Ad_Double):
                    Spreadsheet_Text = f"{Spreadsheet_Text} (2x)"
                
                Node_Tracker+=1
            if Spreadsheet_Text_Color_Check:
                ws1.write(Spreadsheet_Text_X,Spreadsheet_Text_Y,Spreadsheet_Text,Spreadsheet_Text_Color)
            if not Spreadsheet_Text_Color_Check:
                ws1.write(Spreadsheet_Text_X,Spreadsheet_Text_Y,Spreadsheet_Text)
            Phrase+='\n'
            Total_Path_Data_Double_Temp.append(Video_Ad_Double)
                 
                 
                 
        file.write(Phrase)
     
     
        Total_Path_Data.append([total_cost,key_path_cost])
        Total_Path_Data_Double.append(Total_Path_Data_Double_Temp)
     
        if not Key_Found:
            prior_path_key = False
            key_path_cost = 0
        Dragon_Output_Tracker+=4
        file.write('\n')
        if Width_Check>8:
            ws1.set_column(Path_Tracker,Path_Tracker,Width_Check)
        first_path = False
        Path_Tracker+=1
    ws1.write(Longest_Path+5,0,'To Claim Dragon')
    ws1.write(Longest_Path+6,0,'To Reach Key')
    ws1.write(Longest_Path+7,0,'Totals')
    ws1.set_column(0,0,16)
    for x in range(len(Total_Path_Data)):
        ws1.write(Longest_Path+5,x+1,Total_Path_Data[x][0])
        Text_6 = ""
        Text_7 = ""
        if x == 0:
            Text_6 = 0
            Text_7 = Total_Path_Data[x][0]
        if 0<x<=(Key_Path_Count):
            Text_6 = Total_Path_Data[x-1][1]
            Text_7 = Total_Path_Data[x-1][1]+Total_Path_Data[x][0]
        if x>Key_Path_Count:
            Text_6 = 0
            Text_7 = Total_Path_Data[x][0]
        ws1.write(Longest_Path+6,x+1,Text_6)
        ws1.write(Longest_Path+7,x+1,Text_7)
     
    merge_format = workbook.add_format({'bold':2,'align':'center'})
    merge_format.set_bg_color('#aaaaaa')
    ws1.merge_range(0,0,0,len(Total_Path_Data),'Insert Event Name ('+str(Coins)+' coins)',merge_format)

    workbook.close()