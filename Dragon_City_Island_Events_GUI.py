import json
import time
import requests
import os
from os.path import isdir
import numpy as np
import sys
import PIL.Image,PIL.ImageDraw,PIL.ImageFont
import tkinter as tk
from tkinter import ttk
import urllib3
import threading
from Scripts.Fog_Island import Fog_Event_
from Scripts.Grid_Island import Grid_Event_
from Scripts.Heroic_Race import Heroic_Race_Event_
from Scripts.Maze_Island import Maze_Event_
from Scripts.Puzzle_Island import Puzzle_Event_
from Scripts.Runner_Island import Runner_Event_
from Scripts.Tower_Island import Tower_Event_

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class GUI(tk.Tk):
    def __init__(self):
        print('Requesting information before opening GUI')
     
        self.url='https://dc-3rdparty.socialpointgames.com/game-config'

        Credentials_File = ""
        if 'Credentials.txt' in os.listdir():
            Credentials = 'Credentials.txt'
            Credentials_File = open(Credentials,'r')
            Credential_Info = Credentials_File.readline()
            Credentials_File.close()
            UserId = Credential_Info.split(',')[0]
            authToken = Credential_Info.split(',')[1]
            self.arguments={'userId':UserId,'authToken':authToken}
        if 'Credentials.json' in os.listdir():
            Credentials = 'Credentials.json'
            Credentials_File = json.load(open(Credentials,'r'))
            self.arguments={'userId':Credentials_File['userId'],'authToken':Credentials_File['authToken']}
        if Credentials_File == "":
            self.arguments={'userId':str(sys.argv[1]),'authToken':str(sys.argv[2])}
         
        self.data = requests.post(self.url,self.arguments,verify=False)
        self.data_view = self.data.json()['game_data']['config']
     
        Local_JSON = requests.get('http://sp-translations.socialpointgames.com/deploy/dc/ios/prod/dc_ios_en_prod_wetd46pWuR8J5CmS.json').json()
        self.Dragon_Info,self.Chest_Ids,self.Dragon_Book_IDs,self.Chest_Information,self.Chest_Tokens_Info = {},{},{},{},{}
        for chest in self.data_view['chests']['chests']:
            self.Chest_Ids[chest['id']] = {"chest_name_key":chest['chest_name_key'],"img_name":chest['img_name']}
            self.Chest_Information[chest['id']] = chest
            if 'chest_token' in chest['img_name'] and 'v2' in chest['img_name']:
                self.Chest_Tokens_Info[chest['img_name']] = 'Token Chest ('+chest['img_name'].split('v2')[0].split('token')[-1].capitalize()+')'
        self.Local_Dict = {}
        for x in Local_JSON:
            for y in x:
                self.Local_Dict[y] = x[y]
        for drag in self.data_view['items']:
            if drag['group_type'] == 'DRAGON':
                self.Dragon_Info[drag['id']] = drag.copy()
        for drag in self.data_view['dragon_book']['collection_numbers']:
            self.Dragon_Book_IDs[drag['dragon_id']] = drag['number']
     
        Preferences_File = open('Preferences.txt')
        self.Preferences = {}
        for line in Preferences_File:
            True_Line = line[1:].split('\n')[0]
            if line[0]=='@':
                line_split = True_Line.split("=")
                self.Preferences[line_split[0]] = line_split[1]
            if line[0]=='+':
                line_split = True_Line.split(',')
                self.Preferences[line_split[0]] = {}
                for setting in range(len(line_split)-1):
                    settingKey,settingValue = line_split[setting+1].split('=')[0][1:],line_split[setting+1].split('=')[1]
                    self.Preferences[line_split[0]][settingKey] = settingValue
        self.Style_Preferences = self.Preferences[self.Preferences["WindowModeSet"]].copy()
        Preferences_File.close()
        
        self.Maze_Color_Check_Status = False
        self.Maze_Colors = []
     
        self.Elements = {'ph':'Physical','e':'Terra','f':'Flame','w':'Sea','p':'Nature','i':'Ice','m':'Metal','el':'Electric','d':'Dark','li':'Light','wd':'Wind','wr':'War','pu':'Pure','pr':'Primal','l':'Legend','ch':'Chaos','bt':'Beauty','hp':'Happy','so':'Soul','dr':'Dream','mg':'Magic','ti':'Time'}
        self.Perks = {1:'Breeding Perk'}
        self.Rarities = {'C':'Common','R':'Rare','V':'Very Rare','E':'Epic','L':'Legendary','M':'Mythical','H':'Heroic'}
        self.Image_Formats = {"DRAGON":"http://dci-static-s1.socialpointgames.com/static/dragoncity/mobile/ui/dragons/ui_",
            "CHEST":"https://dca-static-s1.socialpointgames.com/static/dragoncity/mobile/ui/chests/ui_",
            "DECO":"https://dca-static-s1.socialpointgames.com/static/dragoncity/mobile/ui/decorations/ui_",
            "HABITAT":"https://dca-static-s1.socialpointgames.com/static/dragoncity/mobile/ui/habitats/ui_",
            "BUILDING":"https://dca-static-s1.socialpointgames.com/static/dragoncity/mobile/ui/buildings/ui_"}
        self.Asset_Versioning = {'Chests':{}}
        for asset in self.data_view['asset_versioning']['chests']:
            self.Asset_Versioning['Chests'][asset['name']] = {'Format':asset['format'],"Version":asset['asset_version']}
        
        self.Chests_Desired = []
        self.Chests_Desired_Names = []
        
        # GUI = Tk()
        tk.Tk.__init__(self)
        self.GUI_Canvas = tk.Canvas(self, relief = 'raised',bg=self.Preferences[self.Preferences["WindowModeSet"]]["WindowBackground"])
        self.GUI_Canvas.pack(fill=tk.BOTH, expand=tk.YES)
     
        self.Event_Order_Tracker = tk.IntVar()
        self.Event_Order_Tracker.set(self.Preferences["EventDateOrder"])
     
        Event_Label = tk.Label(self,text='Event Type',bg=self.Style_Preferences["WindowBackground"],fg=self.Style_Preferences["WindowForeground"])
        self.Event_Selected = tk.IntVar()
        self.Event_Chosen = tk.StringVar()
        self.Event_Chosen.set('Select One')
        self.Event_Chosen.trace('w',self.Event_Menu_List_Creation)

        self.Event_List_Box = tk.Listbox(self,selectmode="SINGLE",exportselection=0)
        self.Event_List_Box.bind('<<ListboxSelect>>',self.Event_Box_Selection)
        self.Event_List_Box.insert(1,"Fog Island")
        self.Event_List_Box.insert(2,"Grid Island")
        self.Event_List_Box.insert(3,"Heroic Race")
        self.Event_List_Box.insert(4,"Maze Island")
        self.Event_List_Box.insert(5,"Puzzle Island")
        self.Event_List_Box.insert(6,"Runner Island")
        self.Event_List_Box.insert(7,"Tower Island")
        self.Event_List_Box.configure(bg=self.Style_Preferences["MenuBackground"],fg=self.Style_Preferences["MenuForeground"],highlightcolor=self.Style_Preferences["MenuListActiveForeground"], selectbackground=self.Style_Preferences["MenuListActiveBackground"],highlightthickness=0)
        self.Event_Frame = tk.Frame(self)
        self.Event_Scrollbar = tk.Scrollbar(self.Event_Frame)
        self.Event_Scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
     
        self.Event_Dates_List_Box = tk.Listbox(self.Event_Frame,selectmode="SINGLE",yscrollcommand=self.Event_Scrollbar.set,width=30,exportselection=0)
        self.Event_Dates_List_Box.configure(bg=self.Style_Preferences["MenuBackground"],fg=self.Style_Preferences["MenuForeground"],highlightcolor=self.Style_Preferences["MenuListActiveForeground"], selectbackground=self.Style_Preferences["MenuListActiveBackground"],highlightthickness=0)
        self.Event_Dates_List_Box.insert(1,'            Select Event Type')
        self.Event_Dates_List_Box.bind('<<ListboxSelect>>',self.Event_Dates_Box_Selection)
        self.Event_Dates_List_Box.pack(side=tk.LEFT)
        self.Event_Scrollbar.config(command=self.Event_Dates_List_Box.yview)
        self.Events_Listed = 0
        
        self.asset_zip_fP = ['/mobile/ui/','/HD/dxt5/']
     
        self.test_new_method = []
        self.test_new_method_var = [tk.IntVar() for _ in range(100)]
     
        Events_Available_Label = tk.Label(self,text='Events Available',bg=self.Style_Preferences["WindowBackground"],fg=self.Style_Preferences["WindowForeground"])
        self.Events_Available_String = tk.StringVar()
        self.Events_Available_String.set('Select Event Date [Start date - End date]')
        # self.Events_Available_String.set(self.Event_Dates_List_Box.get(0))
     
        self.style = ttk.Style()
        self.style.theme_use('alt')
        self.bg_color, self.fg_color = tk.StringVar(),tk.StringVar()
        if self.Preferences['WindowModeSet'] == 'Dark Mode':
            self.bg_color.set('black')
            self.fg_color.set('white')
        if self.Preferences['WindowModeSet'] == 'Light Mode':
            self.bg_color.set('white')
            self.fg_color.set('black')
     
        self.style.map('TCombobox', fieldbackground=[('disabled', self.bg_color.get())])
        self.style.map('TCombobox', selectbackground=[('disabled', self.bg_color.get())])
        self.style.map('TCombobox', selectforeground=[('disabled', self.fg_color.get())])
        self.style.map('TCombobox', background=[('disabled', self.bg_color.get())])
        self.style.map('TCombobox', foreground=[('disabled', self.fg_color.get())])

        self.Events_Available_Menu = ttk.Combobox(self,textvariable=self.Events_Available_String)
        self.Events_Available_Menu.configure(state='disabled')
     
     
        Event_Date_Order_Reverse_Button = tk.Checkbutton(self,text='Reverse order of event dates',variable=self.Event_Order_Tracker,bg=self.Style_Preferences["WidgetBackground"],fg=self.Style_Preferences["WidgetForeground"],selectcolor=self.Style_Preferences["CheckmarkColor"])
        self.Event_Order_Tracker.trace('w',self.Event_Menu_List_Creation)
     
        self.Non_Basic_Chest_All_Selection_Check = tk.IntVar()
        self.Non_Basic_Chest_All_Selection_Check.set(1)
        self.Chest_All_Selection_Check = tk.IntVar()
        self.Chest_All_Selection_Check.set(self.Preferences['ChestSelectionStatus'])
        Chest_All_Selection_Button = tk.Checkbutton(self,text='Select All Chests',variable=self.Chest_All_Selection_Check,bg=self.Style_Preferences["WidgetBackground"],fg=self.Style_Preferences["WidgetForeground"],selectcolor=self.Style_Preferences["CheckmarkColor"])
     
        Start_Button = tk.Button(self,text='Start Processing Event Selected',command=self.Event_Processing,bg=self.Style_Preferences["MenuBackground"],fg=self.Style_Preferences["MenuForeground"])
        Save_Config_Button = tk.Button(self,text='Save Config',command=self.Save_Config_File,bg=self.Style_Preferences["MenuBackground"],fg=self.Style_Preferences["MenuForeground"])
     
        Label_Horizontal,Event_Choice_Spacing,Entry_Horizontal,Start_Button_Spacing,Events_Available_Spacing,Puzzle_Island_Draw_Spacing,Reload_Excel_Spacing,Event_Label_Spacing = tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar(),tk.IntVar()
        gap = 30
        Label_Horizontal.set(100)
        Entry_Horizontal.set(200)
        Event_Label_Spacing.set(20)
        Event_Choice_Spacing.set(Event_Label_Spacing.get()+int(2*gap)+25)
        Start_Button_Spacing.set(Event_Choice_Spacing.get()+int(3*gap)-10)
     
        Event_Label_Canvas = self.GUI_Canvas.create_window(Entry_Horizontal.get()-125,Event_Label_Spacing.get(),window=Event_Label)
        Event_Menu_Canvas = self.GUI_Canvas.create_window(Entry_Horizontal.get()-125,Event_Choice_Spacing.get(),window=self.Event_List_Box,height=120,width=85)
        Events_Available_Label_Canvas = self.GUI_Canvas.create_window(Entry_Horizontal.get()+47,20,window=Events_Available_Label)
        Events_Available_Menu_Canvas = self.GUI_Canvas.create_window(Entry_Horizontal.get()+60,Event_Choice_Spacing.get(),window=self.Event_Frame,width=200,height=120)
     
        Start_Button_Canvas = self.GUI_Canvas.create_window(Entry_Horizontal.get()-75,Start_Button_Spacing.get(),window=Start_Button)
        Save_Config_Button_Canvas = self.GUI_Canvas.create_window(Entry_Horizontal.get()+80,Start_Button_Spacing.get(),window=Save_Config_Button)
     
        self.Menu_Bar = tk.Menu(self)
        self.Options_Menu = tk.Menu(self.Menu_Bar,tearoff=0)
        self.Options_Menu.add_checkbutton(label="Reverse Order of Event Dates",onvalue=1,offvalue=0,variable=self.Event_Order_Tracker)
        self.Options_Menu.add_checkbutton(label="Select All Chests",onvalue=1,offvalue=0,variable=self.Chest_All_Selection_Check)
        self.Options_Menu.add_checkbutton(label="Select All Non-Basic Chests",onvalue=1,offvalue=0,variable=self.Non_Basic_Chest_All_Selection_Check)
        self.Menu_Bar.add_cascade(label="Options",menu=self.Options_Menu)
     
        self.config(menu=self.Menu_Bar)
     
        self.Running_Status = self.GUI_Canvas.create_text(Entry_Horizontal.get()-75,Start_Button_Spacing.get()+gap,text='Running',fill='red')
        self.Completed_Status = self.GUI_Canvas.create_text(Entry_Horizontal.get()-75,Start_Button_Spacing.get()+gap,text='Completed',fill='green')
     
        self.GUI_Canvas.itemconfigure(self.Running_Status,state='hidden')
        self.GUI_Canvas.itemconfigure(self.Completed_Status,state='hidden')
     
        self.title("Dragon City Events")
        w = 425 # width for the Tk self
        h = Start_Button_Spacing.get()+2*gap # height for the Tk root
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight() # height of the screen
        x = (ws/4) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    def Event_Box_Selection(self,*args):
        self.Event_Chosen.set(self.Event_List_Box.get(self.Event_List_Box.curselection()))

    def Event_Dates_Box_Selection(self,*args):
        self.Events_Available_String.set(self.Event_Dates_List_Box.get(self.Event_Dates_List_Box.curselection()))

    def Chest_Naming(self,key):
        name_key,img_name = key['chest_name_key'],key['img_name']
        Chest_Name = ''
        if name_key in self.Local_Dict:
            Chest_Name = self.Local_Dict[name_key]
        if img_name in self.Chest_Tokens_Info:
            Chest_Name = self.Chest_Tokens_Info[img_name]
        return Chest_Name
     
    def Gather_Desired_Chests_List(self):
        Necessary = False
        self.Maze_Color_Check_Status = False
        self.Chest_List = []
        if self.Event_Chosen.get() == 'Maze Island':
            self.Maze_Colors,self.Maze_Dictionary = Maze_Event_(self)
            for reward in self.Maze_Dictionary['Rewards']:
                if 'chest' in self.Maze_Dictionary['Rewards'][reward]:
                    self.Chest_List.append(self.Maze_Dictionary['Rewards'][reward]['chest'])
                    Necessary = True
            self.Maze_Color_Check_Status = True
        if self.Event_Chosen.get() == 'Grid Island':
            for square in self.data_view['grid_island']['squares']:
                if square['type'] == 'CHEST':
                    self.Chest_List.append(square['type_id'])
                    Necessary = True
        if self.Event_Chosen.get() in ['Fog Island','Fog Island - Quick']:
            for square in self.data_view['fog_island']['squares']:
                if square['type'] == 'CHEST':
                    self.Chest_List.append(square['type_id'])
                    Necessary = True
            if self.Event_Chosen.get() == 'Fog Island - Quick':
                Chest_Counts = np.unique(self.Chest_List,return_counts=True)
                Chest_Array = np.zeros((len(Chest_Counts[0]),2))
                Chest_Array[:,0],Chest_Array[:,1] = Chest_Counts[0],Chest_Counts[1]
                Chest_Array = Chest_Array[(-1*Chest_Array[:,1]).argsort()]
                Chest_Ignore = [chest for chest in Chest_Array[:2,0]]
                Chest_Temp = self.Chest_List
                self.Chest_List = [chest for chest in Chest_Temp if not chest in Chest_Ignore]
                Necessary = True
        if self.Event_Chosen.get() == 'Tower Island':
            for square in self.data_view['tower_island']['squares']:
                if square['type'] == 'SINGLE_REWARD' and 'chest' in square['rewards_array'][0]:
                    self.Chest_List.append(square['rewards_array'][0]['chest'])
                    Necessary = True

        self.Chests_Found = np.unique(self.Chest_List)
        self.Chest_Names = []
        Chest_ID_Temp = {}
        for chest in self.Chests_Found:
            Chest_Info = self.Chest_Information[chest]
            Chest_Name = ''
            if Chest_Info['chest_name_key'] in self.Local_Dict:
                Chest_Name = self.Local_Dict[Chest_Info['chest_name_key']]
                if not Chest_Name in self.Chest_Names:
                    self.Chest_Names.append(Chest_Name)
            if Chest_Name in Chest_ID_Temp:
                Chest_ID_Temp[Chest_Name]['Chest IDs'].append(Chest_Info['id'])
            if not Chest_Name in Chest_ID_Temp:
                Chest_ID_Temp[Chest_Name] = {'Chest IDs':[],'Selected':0}
                Chest_ID_Temp[Chest_Name]['Chest IDs'].append(Chest_Info['id'])

        self.Chest_ID = []
        for x in Chest_ID_Temp:
            # for chest in Chest_ID_Temp[x]['Chest IDs']:
                # self.Chest_ID.append(chest)
            self.Chest_ID.append(Chest_ID_Temp[x]['Chest IDs'])

        if self.Chest_All_Selection_Check.get() != 1 and Necessary:
            self.Chest_Popup = tk.Tk()
            self.Chest_Canvas = tk.Canvas(self.Chest_Popup, relief = 'raised')
            self.Chest_Canvas.pack(fill=tk.BOTH, expand=tk.YES)

            self.chest_selection_status_list = []
            self.Chest_Checkbuttons =[]
            for chest_option in range(len(self.Chest_Names)):
                self.chest_selection_status_list.append(0)
                self.Chest_Checkbuttons.append(self.New_Checkbutton(chest_option))
             
            self.Continue_Button = tk.Button(self.Chest_Popup,text='Continue With Selected Chests',command=self.Finish)
            Continue_Button_Canvas = self.Chest_Canvas.create_window(200,375,window=self.Continue_Button)
            self.Cancel_Button = tk.Button(self.Chest_Popup,text='Cancel',command=self.Cancel)
            Cancel_Button_Canvas = self.Chest_Canvas.create_window(350,375,window=self.Cancel_Button)
            self.Select_All_Button = tk.Button(self.Chest_Popup,text='Select All',command=self.Select_All_Chests)
            Select_All_Button_Canvas = self.Chest_Canvas.create_window(425,375,window=self.Select_All_Button)
            self.Clear_All_Button = tk.Button(self.Chest_Popup,text='Clear All',command=self.Clear_All_Chests)
            Clear_All_Button_Canvas = self.Chest_Canvas.create_window(500,375,window=self.Clear_All_Button)
     
            self.Chest_Popup.title("Select Chests from the Event")
            w1 = 600 # width for the Tk Chest_Popup
            h1 = 400 # height for the Tk root
            ws1 = self.Chest_Popup.winfo_screenwidth() # width of the screen
            hs1 = self.Chest_Popup.winfo_screenheight() # height of the screen
            x1 = (2*ws1/3) - (w1/2)
            y1 = (hs1/2) - (h1/2)
            self.Chest_Popup.geometry('%dx%d+%d+%d' % (w1, h1, x1, y1))
            self.Chest_Popup.mainloop()
     
        if self.Chest_All_Selection_Check.get() == 1:
            if self.Non_Basic_Chest_All_Selection_Check.get() == 1:
                for count, chest in enumerate(self.Chest_ID):
                    if chest[0] > 10000:
                        self.Chests_Desired.append(chest)
                        self.Chests_Desired_Names.append(self.Chest_Names[count])
            if self.Non_Basic_Chest_All_Selection_Check == 0:
                self.Chests_Desired = self.Chest_ID
                self.Chests_Desired_Names = self.Chest_Names
            self.Data_Processing()
     
    def Chest_Selected(self,*args):
        self.chest_selection_status_list[args[0]] = (self.chest_selection_status_list[args[0]] + 1 ) % 2

    def New_Checkbutton(self,*args):
        Chest_Select = ttk.Checkbutton(self.Chest_Popup,text=self.Chest_Names[args[0]],command = lambda: self.Chest_Selected(args[0]),variable=self.test_new_method_var[args[0]])
        Chest_Select.state(['!alternate'])
        Chest_Select_Canvas = self.Chest_Canvas.create_window(100+200*(int(args[0]/10)),50+29*(args[0]%10),window=Chest_Select)
        self.test_new_method.append(Chest_Select)
        return Chest_Select_Canvas

    def Finish(self):
        self.Chest_Popup.destroy()
        self.Chests_Desired = []
        self.Chest_Names_Desired = []
        for chests_available in range(len(self.Chest_Names)):
            if self.chest_selection_status_list[chests_available] == 1:
                for chest_num in self.Chest_ID[chests_available]:
                    self.Chests_Desired.append(chest_num)
                # self.Chests_Desired.append(self.Chest_ID[chests_available])
                self.Chest_Names_Desired.append(self.Chest_Names[chests_available])
        # self.Data_Processing(self.Chests_Desired,self.Chest_Names_Desired)
        self.Data_Processing()
    
    def Cancel(self):
        self.Chest_Popup.destroy()
    
    def Select_All_Chests(self):
        for chest in range(len(self.chest_selection_status_list)):
            self.chest_selection_status_list[chest] = 1
            self.test_new_method[chest].state(['selected'])
    
    def Clear_All_Chests(self):
        for chest in range(len(self.chest_selection_status_list)):
            self.chest_selection_status_list[chest] = 0
            self.test_new_method[chest].state(['!selected'])
     
         

    def Event_Processing(self,*args):
        self.Change_Mission_Name_Dict = {'food':'Collect Food','gold':'Collect Gold','feed':'Feed Your Dragons','hatch':'Hatch Dragons','breed':'Breed Dragons','pvp':'League','arena':'Arena'}
     
        self.Initial_fP = os.getcwd()
        self.Output_fP_Start = {'Maze Island':self.Initial_fP+'/Maze_Island/','Heroic Race':self.Initial_fP+'/Heroic_Races/','Grid Island':self.Initial_fP+'/Grid_Island/','Runner Island':self.Initial_fP+'/Runner_Island/','Puzzle Island':self.Initial_fP+'/Puzzle_Island/','Puzzle Island Draw':self.Initial_fP+'/Puzzle_Island/','Fog Island':self.Initial_fP+'/Fog_Island/','Tower Island':self.Initial_fP+'/Tower_Island/','Fog Island - Quick':self.Initial_fP+'/Fog_Island/'}
        self.event_number = self.Event_Date_Dict[self.Events_Available_String.get()]
        
        if self.Event_Chosen.get() == "Select One":
            return
            
        if not isdir(self.Output_fP_Start[self.Event_Chosen.get()]):
            os.mkdir(self.Output_fP_Start[self.Event_Chosen.get()])
     
        if not isdir(self.Output_fP_Start[self.Event_Chosen.get()]+self.Events_Available_String.get()):
            os.mkdir(self.Output_fP_Start[self.Event_Chosen.get()]+self.Events_Available_String.get())
        self.Output_fP_Start[self.Event_Chosen.get()]+=self.Events_Available_String.get()+'/'
     
        if self.Event_Chosen.get() in ['Grid Island','Fog Island','Fog Island - Quick','Tower Island','Maze Island']:
            self.Gather_Desired_Chests_List()
        else:
            self.Data_Processing()
         
    def Data_Processing(self,*args):
        self.GUI_Canvas.itemconfigure(self.Running_Status,state='normal')
        self.update()
        # self.Chests_Desired = args[0]
        # if args[0] != []:
            # self.Chests_Desired_Names = args[1]
        self.Assets_Output = open(self.Output_fP_Start[self.Event_Chosen.get()]+'Assets.txt','w')
        self.Event_fP = self.Output_fP_Start[self.Event_Chosen.get()]
        a_time = time.time()
     
        #-----------------------------------------------------------------------------------------------
     
     
        #-----------------------------------------------------------------------------------------------
     
        if self.Event_Chosen.get() in ['Fog Island','Fog Island - Quick']:
            Fog_Event_(self)
     
        if self.Event_Chosen.get() == 'Grid Island':
            Grid_Event_(self)
     
        if self.Event_Chosen.get() == 'Heroic Race':
            Heroic_Race_Event_(self)
     
        if self.Event_Chosen.get() == 'Maze Island':
            Maze_Event_(self)
     
        if self.Event_Chosen.get() == 'Puzzle Island':
            Puzzle_Event_(self)
     
        if self.Event_Chosen.get() == 'Runner Island':
            Runner_Event_(self)
     
        if self.Event_Chosen.get() == 'Tower Island':
            Tower_Event_(self)
        
        # self.Assets_Output.close()
        print(f'Completed the {self.Event_Chosen.get()} for {self.Events_Available_String.get()} in {np.round(time.time()-a_time,4)} seconds')
        self.GUI_Canvas.itemconfigure(self.Running_Status,state='hidden')
        self.GUI_Canvas.itemconfigure(self.Completed_Status,state='normal')
        self.update()
     
        # self.after(5,self.GUI_Canvas.itemconfigure(self.Completed_Status,state='hidden'))

    def Event_Date_List_Compiling(self):
        self.Event_Date_Dict = {}
        event_date_dic = {}
        event_date_number_list_temp = []
        event_id_list = []
        counter = 0
        for island in self.Event_Information[self.Event_Chosen.get()]:

            if 'availability' in island:
                Starting_Date = island['availability']['from']
                Ending_Date = island['availability']['to']
         
            if 'start_ts' in island:
                Starting_Date = island['start_ts']
                Ending_Date = island['end_ts']
             
            Date_Range = f"[{island['id']}] {int(time.ctime(Starting_Date)[8:10])} {time.ctime(Starting_Date)[4:7]} {time.ctime(Starting_Date)[20:24]} - {int(time.ctime(Ending_Date)[8:10])} {time.ctime(Ending_Date)[4:7]} {time.ctime(Ending_Date)[20:24]}"
            event_date_dic[island['id']] = Date_Range
            event_date_number_list_temp.append(island['id'])
            self.Event_Date_Dict[Date_Range] = counter
            counter +=1
     
        self.Event_Order_True_False = {0:False,1:True}
        event_date_number_list_temp.sort(reverse=self.Event_Order_True_False[self.Event_Order_Tracker.get()])
        event_date_number_list = []
     
        for x in event_date_number_list_temp:
            if not x in event_date_number_list:
                event_date_number_list.append(x)
        return [event_date_dic[x] for x in event_date_number_list]
     
    def Event_Menu_List_Creation(self,*args):
        if self.Event_Chosen.get() == 'Select One':
            return
     
        if self.Event_Selected.get() == 0:
            self.Event_Selected.set(1)
            self.style.map('TCombobox', fieldbackground=[('readonly', self.bg_color.get())])
            self.style.map('TCombobox', selectbackground=[('readonly', self.bg_color.get())])
            self.style.map('TCombobox', selectforeground=[('readonly', self.fg_color.get())])
            self.style.map('TCombobox', background=[('readonly', self.bg_color.get())])
            self.style.map('TCombobox', foreground=[('readonly', self.fg_color.get())])
            self.Events_Available_Menu.config(state='readonly')

        self.Event_Date_List = ['Select Event Date First [Start date - End date]']
        self.Event_Information = {
                            'Fog Island':self.data_view['fog_island']['islands'],
                            'Fog Island - Quick':self.data_view['fog_island']['islands'],
                            'Grid Island':self.data_view['grid_island']['islands'],
                            'Heroic Race':self.data_view['heroic_races']['islands'],
                            'Maze Island':self.data_view['maze_island']['islands'],
                            'Puzzle Island':self.data_view['puzzle_island']['islands'],
                            'Runner Island':self.data_view['runner_island']['islands'],
                            'Tower Island':self.data_view['tower_island']['islands'],
                            }
        self.Event_Date_List+=self.Event_Date_List_Compiling()
        self.Events_Available_String.set('Select Event Date [Start date - End date]')
        self.Events_Available_Menu.config(values=self.Event_Date_List)
        self.Events_Available_String.set(self.Event_Date_List[int(self.Preferences['DefaultEventNumber'])])
        self.Event_Dates_List_Box.delete(0,tk.END)
        for count,event in enumerate(self.Event_Date_List):
            if count != 0:
                self.Event_Dates_List_Box.insert(count+1,event)
        self.Events_Listed = count-1

    def Save_Config_File(self):
        print('Saving config file')
        save_time = time.time()
        json.dump(self.data_view,open('Config.json','w'))
        print(f'Successfully saved config file after {np.round(time.time()-save_time,3)} seconds')
     
if __name__ == "__main__":
    GUI_Start = GUI()
    GUI_Start.mainloop()
