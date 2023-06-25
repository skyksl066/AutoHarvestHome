# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 22:45:46 2023

@author: Alex
"""

import customtkinter as ctk

class SwitchesFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="TestFrame", name, switches=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Add a label to the new entry frame
        self.label1 = ctk.CTkLabel(self, text=name, anchor="center")
        self.label1.grid(row=0, column=0, columnspan=1, pady=(10, 0), padx=10, sticky="n")

        # Add switches to the new entry frame
        self.switch_vars = []
        self.switches = []
        row = 1
        for i, switch_data in enumerate(switches):
            switch_var = ctk.StringVar(value="off")
            switch = ctk.CTkSwitch(self, text=switch_data["text"], variable=switch_var, onvalue="on", offvalue="off", command=switch_data["command"])
            switch.grid(row=row, column=0, pady=6, padx=10, sticky="nw")
            self.switch_vars.append(switch_var)
            self.switches.append(switch)
            row += 1


    def reset_values(self):
        for switch in self.switches:
            switch.deselect()