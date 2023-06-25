# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 17:03:44 2023

@author: Alex
"""

import customtkinter as ctk
from onnx_detextion import load_classes, build_model
from loguru import logger


class ModelFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        def comboBox1_callback(choice):
            master.model = choice
            master.class_list = load_classes(master.model)
            master.net = build_model(f"models/{master.model}")          
            logger.info(f"Using: {choice}")

        def comboBox2_callback(choice):
            master.allow_ids = []
            if choice != 'ALL':
                master.allow_ids = [master.class_list.index(choice)]
            logger.info(f"Set Class to: {choice}")

        def slider_event(value):
            # 信心值拉條
            master.confidence = round(value, 2)
            logger.info(f"Set confidence to: {master.confidence}")

        # Add a label to the new entry frame
        self.label1 = ctk.CTkLabel(self, text='Model Select')
        self.label1.grid(row=0, column=0, columnspan=1, pady=(10, 0), padx=10, sticky="n")
        
        self.comboBox1 = ctk.CTkComboBox(self, values=master.models, command=comboBox1_callback)
        self.comboBox1.grid(row=1, column=0, pady=4, padx=15, sticky="nw")
        self.comboBox1.set(master.model)
        
        self.label2 = ctk.CTkLabel(self, text='Class Select')
        self.label2.grid(row=2, column=0, columnspan=1, pady=0, padx=10, sticky="n")
        
        options = master.class_list
        options.insert(0, 'ALL')
        self.comboBox2 = ctk.CTkComboBox(self, values=options, command=comboBox2_callback)
        self.comboBox2.grid(row=3, column=0, pady=4, padx=15, sticky="nw")
        self.comboBox2.set('ALL')
        
        self.label3 = ctk.CTkLabel(self, text='Confidence Slider')
        self.label3.grid(row=4, column=0, columnspan=1, pady=0, padx=10, sticky="n")
        
        self.slider = ctk.CTkSlider(self, from_=0, to=1, width=150, number_of_steps=100, command=slider_event)
        self.slider.grid(row=5, column=0, pady=(0, 10), padx=10, sticky="n")
        self.slider.set(master.confidence)
