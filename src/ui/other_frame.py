# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 17:03:44 2023

@author: Alex
"""

import customtkinter as ctk
from loguru import logger
from window_capture import WindowCapture
from bot_thread import is_near_target, read_json_text

class OtherFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        def comboBox1_callback(choice):
            master.wincap = WindowCapture(choice)
            logger.info(f'Game name: {choice}.')
            logger.info(f"Game resolution: {master.wincap.width}x{master.wincap.height}.")

        def comboBox2_callback(choice):
            master.bot_mode = choice
            logger.info(f"Set Mode to: {choice}.")
            if choice == 'script':
                file_path = f'script/{master.albion.MapIndex}.txt'
                try:
                    master.script_record = read_json_text(file_path)
                    if is_near_target((master.albion.X, master.albion.Y), master.script_record[0]):
                        logger.info(f'{file_path} loaded.')
                    else:
                        logger.info(f'Please move to {master.script_record[0]}.')
                        self.comboBox2.set('default')
                except FileNotFoundError:
                    logger.error(f'File not found: {file_path}, Please create the script first or load map first.')
                    self.comboBox2.set('default')

        self.label1 = ctk.CTkLabel(self, text='Window Select')
        self.label1.grid(row=0, column=0, columnspan=1, pady=(10, 0), padx=10, sticky="n")
        
        self.comboBox1 = ctk.CTkComboBox(self, values=master.windows, command=comboBox1_callback)
        self.comboBox1.grid(row=1, column=0, pady=4, padx=15, sticky="nw")
        self.comboBox1.set('Albion Online Client')
        
        self.label2 = ctk.CTkLabel(self, text='Bot Mode Select')
        self.label2.grid(row=2, column=0, columnspan=1, pady=0, padx=10, sticky="n")
        
        self.comboBox2 = ctk.CTkComboBox(self, values=['default', 'back start pos', 'script'], command=comboBox2_callback)
        self.comboBox2.grid(row=3, column=0, pady=(4, 10), padx=15, sticky="nw")
        self.comboBox2.set('default')
