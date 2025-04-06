'''

    Version: 1.0.1
    Written by Apod

'''

import time

def Puzzle_Event_(Parent):
    Puzzle_Data = {'Rewards':{},'Missions':{}}
    for PR in Parent.data_view['puzzle_island']['rewards']:
        Puzzle_Data['Rewards'][PR['id']] = PR
    for PM in Parent.data_view['puzzle_island']['missions']:
        Puzzle_Data['Missions'][PM['id']] = PM

    island_event = Parent.data_view['puzzle_island']['islands'][Parent.event_number]
    Zip_fileName = island_event['zip_file'].split('.')[0].split('/')[-1]
    Asset_Zip = Parent.asset_zip_fP[0]+'puzzle_island'+Parent.asset_zip_fP[1]+Zip_fileName+'.zip'
    Parent.Assets_Output.write(f"vfx assets:{island_event['vfx_asset']}\nzip filepath:{Asset_Zip}\ncanvas url: {island_event['canvas_url']}")
    Parent.Assets_Output.close()
    m1,m2,m3,m4 = island_event['mission_queue1'],island_event['mission_queue2'],island_event['mission_queue3'],island_event['mission_queue4']
    tr,mr,lr = island_event['top_reward_queue'],island_event['middle_reward_queue'],island_event['bottom_reward_queue']

    #Name output file
    Event_Start_Date = time.ctime(island_event['start_ts'])
    Output_fP = Parent.Event_fP+'Puzzle Island Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.txt'
    file = open(Output_fP,'w')

    mission_numbers = [m1,m2,m3,m4]
    reward_numbers = [tr,mr,lr]

    for y in reward_numbers:
        if y == tr:
            file.write('Top Rewards\n')
        if y == mr:
            file.write('Middle Rewards\n')
        if y == lr:
            file.write('Bottom Rewards\n')
        for z in y:
            x=Puzzle_Data['Rewards'][z]
            found = False
            if 'chest' in x['reward']:
                Prize = 'Chest'
                Prize_Name = Parent.Chest_Naming(Parent.Chest_Ids[x['reward']['chest']])
                found = True
            if 'seeds' in x['reward']:
                Prize = 'Orbs'
                Prize_Name = str(x['reward']['seeds'][0]['amount']) + ' Orbs of ' + Parent.Local_Dict['tid_unit_'+str(x['reward']['seeds'][0]['id'])+'_name']
                found = True
            if 'egg' in x['reward']:
                Prize = 'Egg'
                Prize_Name = Parent.Local_Dict['tid_unit_'+str(x['reward']['egg'])+'_name']
                found = True
            if 'rarity_seeds' in x['reward']:
                Prize = 'Joker Orbs'
                Prize_Name = str(x['reward']['rarity_seeds'][0]['amount']) + ' of '+x['reward']['rarity_seeds'][0]['rarity']
                found = True
            if 'ep' in x['reward']:
                Prize = 'Event Coins'
                Prize_Name = x['reward']['ep']
                found = True
            if not found:
                for a in x:
                    if len(a.split('_')) > 1:
                        if a.split('_')[1]=='token':
                            Prize = 'Tokens'
                            Prize_Name = str(x['reward'][a])+' '+Parent.Elements[a.split('_')[0]]
            if x['loopable'] == 0:
                Loopable = 'No'
            if x['loopable'] == 1:
                Loopable = 'Yes'
                
            file.write(f"Pieces needed: {x['required_pieces']}, colors: {x['colors']}, Loopable?: {Loopable}, {Prize}: {Prize_Name}\n")
        file.write('\n')

    file.write('\n----Missions----\n\n')
    file.write('Missions set #1:\n')
    loopable_missions = Sort_Loopable(m1,Puzzle_Data['Missions'])
    for mission in m1:
        Mission_Info = Puzzle_Data['Missions'][mission]
        write_to_file(Mission_Info,file,Parent)
    file.write('Loop:\n')
    for mission in loopable_missions:
        Mission_Info = Puzzle_Data['Missions'][mission]
        write_to_file(Mission_Info,file,Parent)
    file.write('\n\n')

    file.write('Missions set #2:\n')
    loopable_missions = Sort_Loopable(m2,Puzzle_Data['Missions'])
    for mission in m2:
        Mission_Info = Puzzle_Data['Missions'][mission]
        write_to_file(Mission_Info,file,Parent)
    file.write('Loop:\n')
    for mission in loopable_missions:
        Mission_Info = Puzzle_Data['Missions'][mission]
        write_to_file(Mission_Info,file,Parent)
    file.write('\n\n')

    file.write('Missions set #3:\n')
    loopable_missions = Sort_Loopable(m3,Puzzle_Data['Missions'])
    for mission in m3:
        Mission_Info = Puzzle_Data['Missions'][mission]
        write_to_file(Mission_Info,file,Parent)
    file.write('Loop:\n')
    for mission in loopable_missions:
        Mission_Info = Puzzle_Data['Missions'][mission]
        write_to_file(Mission_Info,file,Parent)
    file.write('\n\n')

    file.write('Missions set #4:\n')
    loopable_missions = Sort_Loopable(m4,Puzzle_Data['Missions'])
    for mission in m4:
        Mission_Info = Puzzle_Data['Missions'][mission]
        write_to_file(Mission_Info,file,Parent)
    file.write('Loop:\n')
    for mission in loopable_missions:
        Mission_Info = Puzzle_Data['Missions'][mission]
        write_to_file(Mission_Info,file,Parent)
    file.write('\n\n')

    file.close()

def write_to_file(Mission_Info,file,Parent):
    Moves_Given = Mission_Info['moves']
    Skip_Cost = Mission_Info['skip_cost']['c']
    Action_Required = ""
    if Mission_Info['activity_type'] ==  'TOURNAMENT_MATCH':
        if Mission_Info["required_amount"] == 1:
            Action_Required = f'Win {Mission_Info["required_amount"]} quest fight\n'
        if Mission_Info["required_amount"] > 1:
            Action_Required = f'Win {Mission_Info["required_amount"]} quest fights\n'
    if Mission_Info['activity_type'] == 'COLLECT_GOLD':
        Action_Required = f"Collect {int(Mission_Info['required_amount']/1000)}k gold\n"
    if Mission_Info['activity_type'] == 'FEED_DRAGON':
        Action_Required = f"Feed {int(Mission_Info['required_amount']/1000)}k food\n"
    if Mission_Info['activity_type'] ==  'BREED_ELEMENTS':
        if len(Mission_Info["specific"]) == 1:
            Action_Required = f'Breed an egg that has {Parent.Elements[Mission_Info["specific"][0]]} element - {Mission_Info["required_amount"]}\n'
        if len(Mission_Info["specific"]) > 1:
            Action_Required = f'Breed an egg that has {Parent.Elements[Mission_Info["specific"][0]]} + {Parent.Elements[Mission_Info["specific"][1]]} element - {Mission_Info["required_amount"]}\n'
    if Mission_Info['activity_type'] ==  'HATCH_ELEMENTS':
        if len(Mission_Info["specific"]) == 1:
            Action_Required = f'Hatch a dragon that has {Parent.Elements[Mission_Info["specific"][0]]} element - {Mission_Info["required_amount"]}\n'
        if len(Mission_Info["specific"]) > 1:
            Action_Required = f'Hatch a dragon that has {Parent.Elements[Mission_Info["specific"][0]]} + {Parent.Elements[Mission_Info["specific"][1]]} element - {Mission_Info["required_amount"]}\n'
    if Mission_Info['activity_type'] ==  'LEAGUES':
        if Mission_Info["required_amount"] == 1:
            Action_Required = f'Win {Mission_Info["required_amount"]} league fight\n'
        if Mission_Info["required_amount"] > 1:
            Action_Required = f'Win {Mission_Info["required_amount"]} league fights\n'
    if Mission_Info['activity_type'] == 'COLLECT_FOOD':
        Action_Required = f"Collect {int(Mission_Info['required_amount']/1000)}k food\n"
    if Mission_Info['activity_type'] ==  'PVP_ARENAS':
        if Mission_Info["required_amount"] == 1:
            Action_Required = f'Win {Mission_Info["required_amount"]} arena fight\n'
        if Mission_Info["required_amount"] > 1:
            Action_Required = f'Win {Mission_Info["required_amount"]} arena fights\n'
    Output_Message = f"Moves: {Moves_Given}, Skip: {Skip_Cost} - Action: {Action_Required}"
    file.write(Output_Message)

def Sort_Loopable(Missions,Mission_Data):
    
    loopable_missions = []
    
    for mission in Missions:
        if Mission_Data[mission]['loopable'] == 1:
            loopable_missions.append(mission)
    
    
    return loopable_missions