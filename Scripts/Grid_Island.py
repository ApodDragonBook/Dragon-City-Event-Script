import time
import numpy as np
import PIL.Image,PIL.ImageDraw,PIL.ImageFont

def Grid_Event_(Parent):
	grid_data = Parent.data_view['grid_island']
	item = Parent.data_view['chests']['chests']
	event_number = Parent.Event_Date_Dict[Parent.Events_Available_String.get()]
	Grid_Event = grid_data['islands'][Parent.event_number]
	
	Zip_fileName = Grid_Event['zip_file'].split('.')[0].split('/')[-1]
	Asset_Zip = Parent.asset_zip_fP[0]+'grid_island'+Parent.asset_zip_fP[1]+Zip_fileName+'_optim.zip'
	Parent.Assets_Output.write(f"tid name:{Grid_Event['tid_name']}\nzip filepath:{Asset_Zip}\nisland title: {Grid_Event['analytics_id']}\ncanvas url: {Grid_Event['canvas_assets_url']}\nbackground: {Grid_Event['background_plist']}\nforeground: {Grid_Event['foregrounds_plists']}")
	Parent.Assets_Output.close()
	
	board_grid = np.zeros((grid_data['episodes'][Parent.event_number]['board_size'][0],grid_data['episodes'][Parent.event_number]['board_size'][1]),dtype='uint8')
	board_grid.fill(255)
	
	
	
	Locations_Of_Interest = []
	for x in grid_data['squares']:
		x_loc = x['x']
		y_loc = x['y']
		if x['type'] == 'CHEST':
		 
			if x['type_id'] in Parent.Chests_Desired:
				board_grid[x_loc-1,y_loc-1] = 75
				Locations_Of_Interest.append(x['id'])
			if x['type_id'] not in Parent.Chests_Desired:
				board_grid[x_loc-1,y_loc-1] = 150
		if x['type'] == 'DRAGON':
			board_grid[x_loc-1,y_loc-1] = 0
			Locations_Of_Interest.append(x['id'])

	board_expand = np.zeros((100*board_grid.shape[0],100*board_grid.shape[1]),'uint8')
	for x in range(board_grid.shape[0]):
		for y in range(board_grid.shape[1]):
			if board_grid[x,y]>0:
				board_expand[100*x:100*x+100,100*y:100*y+100] = board_grid[x,y]

	width = 7
	wall_value = 0
	for x in Parent.data_view['grid_island']['squares']:
		if "wall" in x:
			if x['wall'] == 'V':
				board_expand[(x['x']-1)*100:(x['x']-1)*100+width,(x['y']-1)*100:(x['y'])*100] = wall_value
			if x['wall'] == 'H':
				board_expand[(x['x']-1)*100:(x['x'])*100,(x['y']-1)*100:(x['y']-1)*100+width] = wall_value
			if x['wall'] == 'H+V':
				board_expand[(x['x']-1)*100:(x['x']-1)*100+width,(x['y']-1)*100:(x['y'])*100] = wall_value
				board_expand[(x['x']-1)*100:(x['x'])*100,(x['y']-1)*100:(x['y']-1)*100+width] = wall_value
	board_expand[0,:] = wall_value
	board_expand[-1,:] = wall_value
	board_expand[:,0] = wall_value
	board_expand[:,-1] = wall_value
	board_out = PIL.Image.fromarray(np.transpose(board_expand))
	board_out.save(Parent.Output_fP_Start[Parent.Event_Chosen.get()]+'Board_Template.jpg')
	Image_Input = PIL.Image.open(Parent.Output_fP_Start[Parent.Event_Chosen.get()]+'Board_Template.jpg')
	Image_Draw = PIL.ImageDraw.Draw(Image_Input)
	
	Dragon_File = open(Parent.Output_fP_Start[Parent.Event_Chosen.get()]+'Dragon_List.txt','w')
	Dragon_Counter = 1
	for x in grid_data['squares']:
		if x['claim_cost']>0:
			Number = x['claim_cost']
			Image_Draw.text((100*(x['x']-1)+20*(4-len(str(Number))),100*(x['y']-1)),str(Number),fill=255,font=PIL.ImageFont.truetype("arial.ttf", 40))
			if x['id'] in Locations_Of_Interest and x['type_id'] in Parent.Chests_Desired:
				Chest_Number = np.argwhere(x['type_id']==np.array(Parent.Chests_Desired))[0][0]+1
				X_Location = 100*(x['x']-1)+20*(4-len(str(Number)))
				Y_Location = 100*(x['y']-1)+50
				Image_Draw.text((X_Location,Y_Location),str(Chest_Number),fill=255,font=PIL.ImageFont.truetype("arial.ttf", 40))
			if x['id'] in Locations_Of_Interest and x['type'] == 'DRAGON':
				if 'tid_unit_'+str(x['type_id'])+'_name' in Parent.Local_Dict:
					Dragon_File.write(f"D{Dragon_Counter}: {Parent.Local_Dict['tid_unit_'+str(x['type_id'])+'_name']}\n")
				else:
					Dragon_File.write(f"D{Dragon_Counter}: {Parent.Dragon_Info[x['type_id']]['name']}\n")
				X_Location = 100*(x['x']-1)+20*(4-len(str(Number)))
				Y_Location = 100*(x['y']-1)+50
				Image_Draw.text((X_Location,Y_Location),'D'+str(Dragon_Counter),fill=255,font=PIL.ImageFont.truetype("arial.ttf", 40))
				Dragon_Counter+=1
	Dragon_File.close()
	
	Event_Start_Date = time.ctime(Parent.data_view['grid_island']['islands'][0]['start_ts'])
	Image_Input.save(Parent.Output_fP_Start[Parent.Event_Chosen.get()]+'Grid Board Output Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.jpg')
	
	Grid_Output_Key = open(Parent.Output_fP_Start[Parent.Event_Chosen.get()]+'Grid Key Starting - '+str(int(Event_Start_Date[8:10]))+' '+Event_Start_Date[4:7]+' '+Event_Start_Date[-4:]+'.txt','w')
	
	for chest_drawing in range(len(Parent.Chests_Desired_Names)):
		Grid_Output_Key.write(f"#{chest_drawing+1} - {Parent.Chests_Desired_Names[chest_drawing]}\n")
	Grid_Output_Key.close()
