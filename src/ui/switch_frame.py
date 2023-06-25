# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 22:45:46 2023

@author: Alex
"""

import customtkinter as ctk
from loguru import logger
import threading


class SwitchesFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        def switch1_event():
            master.vision_status = self.switch1.get()
            logger.info(f"Switch Vision to: {master.vision_status}")
            if master.vision_status == 'on':
                master.is_running = True
                update_thread()
            else:
                master.is_running = False
        
        def switch2_event():
            master.bot_status = self.switch2.get()
            logger.info(f"Switch Bot to: {master.bot_status}")
            if master.bot_status == 'on':
                master.is_running = True
                update_thread()
            else:
                master.is_running = False
                
        def update_thread():
            if not master.thread.is_alive():
                master.thread = threading.Thread(target=master.update_screenshot)
                master.thread.start()
        
        # Add a label to the new entry frame
        self.label1 = ctk.CTkLabel(self, text='Actions')
        self.label1.grid(row=0, column=0, columnspan=1, pady=(10, 0), padx=10, sticky="n")
        
        switch_var1 = ctk.StringVar(value="off")
        self.switch1 = ctk.CTkSwitch(self, text="Display bot's vision", command=switch1_event, variable=switch_var1, onvalue="on", offvalue="off")
        self.switch1.grid(row=1, column=0, pady=6, padx=10, sticky="nw")
        
        switch_var2 = ctk.StringVar(value="off")
        self.switch2 = ctk.CTkSwitch(self, text="Gather resources", command=switch2_event, variable=switch_var2, onvalue="on", offvalue="off")
        self.switch2.grid(row=2, column=0, pady=6, padx=10, sticky="nw")
    
    def reset_values(self):
        self.switch1.deselect()
        self.switch2.deselect()