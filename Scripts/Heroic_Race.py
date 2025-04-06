from openpyxl import load_workbook
import time, datetime
from os.path import isfile
import numpy as np

def Heroic_Race_Event_(Parent):
	HR = Parent.data_view['heroic_races']
	HR_i = Parent.data_view['heroic_races']['islands']
	Heroic_Race = {'Rewards':{},'Laps':{},'Nodes':{},'Missions':{},'Encounters':{},'Enemies':{},'Lap Rewards':{}}
	for value in HR['rewards']:
		Heroic_Race['Rewards'][value['id']] = value
	for value in HR['laps']:
		Heroic_Race['Laps'][value['id']] = value
	for value in HR['nodes']:
		Heroic_Race['Nodes'][value['id']] = value
	for value in HR['missions']:
		Heroic_Race['Missions'][value['id']] = value
	for value in HR['encounters']:
		Heroic_Race['Encounters'][value['id']] = value
	for value in HR['enemies']:
		Heroic_Race['Enemies'][value['id']] = value
	for value in HR['lap_rewards']:
		Heroic_Race['Lap Rewards'][value['id']] = value
	
	def Excel_Output(Lap_Number,Node_Number,Mission,Heroic_Dragon,current_worksheet,Total,Pool,Wait,Time,text,Mission_Number,text_format):
		#hex_color = {0:'0',1:'1',2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'a',11:'b',12:'c',13:'d',14:'e',15:'f'}
	 
		Type_Column = {
			'gold':{'Column':'E','bg':''},
			'food':{'Column':'F','bg':''},
			'feed':{'Column':'G','bg':''},
			'breed':{'Column':'H','bg':''},
			'hatch':{'Column':'I','bg':''},
			'fight':{'Column':'J','bg':''},
			'league':{'Column':'K','bg':''}
			}
		Output_Row = 14 + 22*(Lap_Number-1)+4*(Node_Number-1)
		Mission_Row = 15 + 22*(Lap_Number-1) + 2*(Node_Number-1) + Mission_Number
		Lap_Info_Row = 14 + 22*(Lap_Number-1)
		# print(Lap_Number,Node_Number,Output_Row,Mission_Row,Lap_Info_Row)
		current_worksheet[Type_Column[Mission]['Column']+str(Output_Row)] = Total
		current_worksheet[Type_Column[Mission]['Column']+str(Output_Row+1)] = Pool
		current_worksheet[Type_Column[Mission]['Column']+str(Output_Row+2)] = Wait
		current_worksheet[Type_Column[Mission]['Column']+str(Output_Row+3)] = Time
		current_worksheet["N"+str(Mission_Row)] = text
		if Node_Number == 1 and Mission_Number == 1:
			Lap_Info = "Heroic Race: "+Heroic_Dragon+" - Lap "+str(Lap_Number)
			current_worksheet["M"+str(Lap_Info_Row)] = Lap_Info
	 
	#Define variables
	HR_Event = HR_i[Parent.event_number]
	Laps_Used = HR_Event['laps']
	Lap_Rewards = HR['lap_rewards'][Parent.event_number]['lap_rewards']
	
	Zip_fileName = HR_Event['zip_file'].split('.')[0].split('/')[-1]
	Asset_Zip = Parent.asset_zip_fP[0]+'heroic_races'+Parent.asset_zip_fP[1]+Zip_fileName+'.zip'
	Parent.Assets_Output.write(f"tid name:{HR_Event['canvas_assets_url']}\nzip filepath:{Asset_Zip}\nisland title: {HR_Event['island_title_tid']}")
	Parent.Assets_Output.close()

	#Name output file
	Event_Start_Date = time.ctime(HR_Event['start_ts'])
	Output_fP = Parent.Event_fP+'Heroic Race Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.txt'
	file = open(Output_fP,'w')
	Kedai_Template_Input_fP = Parent.Initial_fP+'/Heroic_Races/'+'Kedai_Template.xlsx'
	Kedai_Template_Output_fP = Parent.Event_fP+'Heroic Race Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.xlsx'
	if isfile(Kedai_Template_Input_fP):
		current_workbook = load_workbook(Kedai_Template_Input_fP)
		current_worksheet = current_workbook.active
		# Text_Format = current_worksheet.add_format({'set_bg_color':'#262626','set_font_color':'white','set_align':'center','set_align':'vcenter'})

	#Find name of Heroic
	Heroic_Race_Dragon = Parent.Local_Dict['tid_unit_'+str(HR_Event['dragon_race_id'])+'_name']

	#Find the Race data and write to file
	Lap_Counter = 1
	for Laps_Seen in Laps_Used:
		file.write(f'Heroic Race: {Heroic_Race_Dragon} - Lap {Lap_Counter}\n')
		for Lap_Reward_Check in Lap_Rewards:
			if int(Lap_Reward_Check) == Lap_Counter:
				for key in Lap_Rewards[Lap_Reward_Check]:
					if key == 'limited_time':
						for reward in Lap_Rewards[Lap_Reward_Check]['reward'][0]:
							reward_name = ''
							if reward == 'seed':
								reward_name = Parent.Local_Dict['tid_unit_'+str(Lap_Rewards[Lap_Reward_Check]['reward'][0]['seed'][0]['id'])+'_name']
							if reward == 'chest':
								reward_name = Parent.Chest_Naming(Parent.Chest_Ids[Lap_Rewards[Lap_Reward_Check]['reward'][0]['chest']])
						file.write(f"Timed Lap: Prize x{Lap_Rewards[Lap_Reward_Check]['multiplier']} ({int(Lap_Rewards[Lap_Reward_Check]['limited_time']/3600)}h)\n")
	 
		Lap_Info = Heroic_Race['Laps'][Laps_Seen]
		Nodes_Used = Lap_Info['nodes']
		Node_Counter = 1
	 
		for Node_Seen in Nodes_Used:
			Node_Info = Heroic_Race['Nodes'][Node_Seen]
			Mission_Info = Node_Info['missions']
			Mission_Counter = 0
			for Mission_Used in Mission_Info:
				Mission_Counter+=1
				Missions_Data = Heroic_Race['Missions'][Mission_Used]
				Goal_Points = Missions_Data['goal_points']
				if Missions_Data['spawn_time']==1:
					Pool = '-'
					Wait = '-'
					Total_Wait = '-'
				if Missions_Data['spawn_time']!=1:
					Pool = Missions_Data['pool_size']
					Wait = ''
					Mission_Time = Missions_Data['spawn_time']
					if Missions_Data['spawn_time'] >= 86400:
						Wait += str(int(Missions_Data['spawn_time']/86400))+'d '
						Mission_Time = Missions_Data['spawn_time']%86400
					Wait_Time = str(datetime.timedelta(seconds=Mission_Time)).split(':')
					if int(Wait_Time[0]) > 0:
						Wait += Wait_Time[0]+'h '
					if int(Wait_Time[1]) > 0:
						Wait += Wait_Time[1]+'m '
					if int(Wait_Time[2]) > 0:
						Wait += Wait_Time[2]+'s'
				 
					Total_Wait = ''
					Total_Wait_Time = (Missions_Data['goal_points']-Missions_Data['pool_size'])*Missions_Data['spawn_time']
					if Total_Wait_Time >= 86400:
						Total_Wait += str(int(Total_Wait_Time/86400))+'d '
						Mission_Time = Total_Wait_Time%86400
					Wait_Time = str(datetime.timedelta(seconds=Total_Wait_Time)).split(':')
					if int(Wait_Time[0]) > 0:
						Total_Wait += Wait_Time[0]+'h '
					if int(Wait_Time[1]) > 0:
						Total_Wait += Wait_Time[1]+'m '
					if int(Wait_Time[2]) > 0:
						Total_Wait += Wait_Time[2]+'s'
			 
				if Missions_Data['type'] != 'pvp':
					Mission_Type = Missions_Data['type']
					if Missions_Data['type'] == 'fight':
						battle_wait_times = []
						Total_Wait_Time = 0
						for encount in Parent.data_view['heroic_races']['encounters']:
							if Missions_Data['encounter'] == encount['id']:
								Goal_Points = len(encount['enemies'])
								for enemy in range(len(encount['enemies'])-1):
									for enem in Parent.data_view['heroic_races']['enemies']:
										if encount['enemies'][enemy+1] == enem['id']:
											battle_wait_times.append(enem['cooldown'])
											Total_Wait_Time += enem['cooldown']
						Wait = ''
						for x in range(len(np.unique(battle_wait_times))):
							Wait_Time_1 = str(datetime.timedelta(seconds=int(str(np.unique(battle_wait_times)[x])))).split(':')
							if int(Wait_Time_1[0]) > 0:
								Wait += Wait_Time_1[0]+'h'
							if int(Wait_Time_1[1]) > 0:
								Wait += Wait_Time_1[1]+'m'
							if int(Wait_Time_1[2]) > 0:
								Wait += Wait_Time_1[2]+'s'
							if x<len(np.unique(battle_wait_times))-1:
								Wait+='- '
							 
						 
						if Total_Wait != 0:
							Total_Wait = ''
							Wait_Time = str(datetime.timedelta(seconds=Total_Wait_Time)).split(' day, ')
							if len(Wait_Time) == 1:
								Wait_Time = Wait_Time[0].split(':')
								if int(Wait_Time[0]) > 0:
									Total_Wait += Wait_Time[0]+'h '
								if int(Wait_Time[1]) > 0:
									Total_Wait += Wait_Time[1]+'m '
								if int(Wait_Time[2]) > 0:
									Total_Wait += Wait_Time[2]+'s'
							if len(Wait_Time) == 2:
								Total_Wait+=Wait_Time[0]+'d '
								Wait_Time = Wait_Time[1].split(':')
								if int(Wait_Time[0]) > 0:
									Total_Wait += Wait_Time[0]+'h '
								if int(Wait_Time[1]) > 0:
									Total_Wait += Wait_Time[1]+'m '
								if int(Wait_Time[2]) > 0:
									Total_Wait += Wait_Time[2]+'s'
						 
				if Missions_Data['type'] == 'pvp':
					Mission_Type = 'league'
				file.write(f"	Lap {Lap_Counter} - Node {Node_Counter}: Task-{Mission_Type}, Number-{Goal_Points}, Pool-{Pool}, Wait-{Wait}, Total Wait-{Total_Wait}\n")
				if isfile(Kedai_Template_Input_fP):
					Text = "	Lap "+str(Lap_Counter)+" - Node "+str(Node_Counter)+": Task-"+str(Mission_Type)+", Number-"+str(Goal_Points)+", Pool-"+str(Pool)+", Wait-"+str(Wait)+", Total Wait-"+str(Total_Wait)
					Excel_Output(Lap_Counter,Node_Counter,Mission_Type,Heroic_Race_Dragon,current_worksheet,Goal_Points,Pool,Wait,Total_Wait,Text,Mission_Counter,[])
			Node_Counter+=1
			file.write('\n')
		file.write('\n')
		Lap_Counter+=1
	file.close()
	
	if isfile(Kedai_Template_Input_fP):
		current_workbook.save(filename=Kedai_Template_Output_fP)
	
	fileOut = open(Parent.Event_fP+'Heroic_Race_Lap-Dragon_Rewards.txt','w')
	fileOut.write("Lap Rewards\n")
	
	
	HRreward = HR['lap_rewards'][Parent.event_number]['lap_rewards']
	for reward in HRreward:
		R = HRreward[reward]['reward'][0]
		Text = ''
		if 'c' in R:
			Text = str(R['c'])+' Gems'
		if 'chest' in R:
			Text = Parent.Chest_Naming(Parent.Chest_Ids[R['chest']])
		if 'seeds' in R:
			Text = str(R['seeds'][0]['amount'])+' orbs of '+Parent.Local_Dict['tid_unit_'+str(R['seeds'][0]['id'])+'_name']
		if 'rarity_seeds' in R:
			Text = str(R['rarity_seeds'][0]['amount'])+' '+Parent.Rarities[R['rarity_seeds'][0]['rarity']]+' Joker Orbs'
		if 'egg' in R:
			if isinstance(R['egg'],list):
				Text = Parent.Local_Dict['tid_unit_'+str(R['egg'][0])+'_name']
			else:
				Text = Parent.Local_Dict['tid_unit_'+str(R['egg'])+'_name']
		 
		if 'skin' in R:
			Text = 'Heroic Skin'
		if 'trade_tickets' in R:
			reward_info = R['trade_tickets'][0]
			Text = f"{reward_info['amount']} {Parent.Rarities[reward_info['rarity']]} essence"
		if Text == '':
			if 'limited_time' in HRreward[reward]:
				fileOut.write(f"Lap #{int(reward)+1}: {HRreward[reward]['reward']} [Timed Lap: Rewards x{HRreward[reward]['multiplier']}]\n")
			if not 'limited_time' in HRreward[reward]:
				fileOut.write(f"Lap #{int(reward)+1}: {HRreward[reward]['reward']}\n")
		if Text != '':
			if 'limited_time' in HRreward[reward]:
				fileOut.write(f"Lap #{int(reward)+1}: {Text} [Timed Lap: Rewards x{HRreward[reward]['multiplier']}]\n")
			if not 'limited_time' in HRreward[reward]:
				fileOut.write(f"Lap #{int(reward)+1}: {Text}\n")
	
	reward_list_number = HR['islands'][Parent.event_number]['rewards'][0]
	fileOut.write("\n\nReward Dragons\n")
	for reward in HR['rewards']:
		if reward_list_number == reward['id']:
			dragon_rewards = reward['rewards'][0]['egg']
			for egg in dragon_rewards:
				Name = Parent.Local_Dict['tid_unit_'+str(egg)+'_name']
				Rarity = Parent.Dragon_Info[egg]['dragon_rarity']
					 
				fileOut.write(f"{Name} - {Rarity}\n")
	fileOut.close()
