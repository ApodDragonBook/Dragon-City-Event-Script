import time

def Runner_Event_(Parent):
	run = Parent.data_view['runner_island']
	run_i = run['islands']
	Runner_Data = {'Missions':{},'Milestone Rewards':{},'Rewards':{},'Mission Pool':{}}
	for mission in run['missions']:
		Runner_Data['Missions'][mission['id']] = mission
	for mr in run['milestone_rewards']:
		Runner_Data['Milestone Rewards'][mr['id']] = mr
	for mr in run['rewards']:
		Runner_Data['Rewards'][mr['id']] = mr
	for mp in run['mission_pool']:
		Runner_Data['Mission Pool'][mp['id']] = mp
	

	runner_event = run['islands'][Parent.event_number]
	Zip_fileName = runner_event['zip_file'].split('.')[0].split('/')[-1]
	Asset_Zip = Parent.asset_zip_fP[0]+'runner_island'+Parent.asset_zip_fP[1]+Zip_fileName+'.zip'
	Parent.Assets_Output.write(f"zip filepath:{Asset_Zip}")
	Parent.Assets_Output.close()

	#Name output file
	Event_Start_Date = time.ctime(runner_event['start_ts'])
	Output_fP = Parent.Event_fP+'Runner Island Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.txt'
	file = open(Output_fP,'w')

	file.write('Missions\n')
	file.write('--------\n')
	for mission_pool in runner_event['mission_pool']:
		pool = Runner_Data['Mission Pool'][mission_pool]['missions']
		for mission_running in pool:
			Mission_Type = Parent.Change_Mission_Name_Dict[Runner_Data['Missions'][mission_running]['type']]
			file.write(f'Type - {Mission_Type}, Required - {Runner_Data["Missions"][mission_running]["goal_points"]}\n')
		file.write('\n')


	file.write('Rewards\n')
	file.write('--------\n')
	for rewards in runner_event['milestone_rewards']:
		milestone = Runner_Data['Milestone Rewards'][rewards]
		Runner_Reward = Runner_Data['Rewards'][milestone['reward_id']]['reward'][0]
		Runner_Double_Check = Runner_Data['Rewards'][milestone['reward_id']]
		reward_text = ' '
		double_text = ''
		if 'double_with_video_ad' in Runner_Double_Check:
			if Runner_Double_Check['double_with_video_ad']:
				double_text = ' [Video Double: Yes]'
		if 'chest' in Runner_Reward:
			reward_text = Parent.Chest_Naming(Parent.Chest_Ids[Runner_Reward['chest']])
		elif 'seeds' in Runner_Reward:
			reward_text = str(Runner_Reward['seeds'][0]['amount'])+' orbs of '+Parent.Local_Dict['tid_unit_'+str(Runner_Reward['seeds'][0]['id'])+'_name']
		elif 'egg' in Runner_Reward:
			reward_text = Parent.Local_Dict['tid_unit_'+str(Runner_Reward['egg'])+'_name']
		elif 'c' in Runner_Reward:
			reward_text = str(Runner_Reward['c'])+' gems'
		elif 'perks' in Runner_Reward:
			reward_text = str(Runner_Reward['perks'][0]['quantity'])+' '+Parent.Perks[Runner_Reward['perks'][0]['id']]
			if Runner_Reward['perks'][0]['quantity']>1:
				reward_text+='s'
		elif 'ep' in Runner_Reward:
			reward_text = str(Runner_Reward['ep'])+' event coins'
		else:
			for key,value in Runner_Rewards:
				if 'tokens' in key.split('_') and len(key.split('_'))>1:
					reward_text = str(Runner_Rewards[key]) +' '+ Parent.Elements[key.split('_')[0]]+' tokens'
		file.write(f"Points - {milestone['points']}, Reward - {reward_text} {double_text}\n")
	 
	file.close()
