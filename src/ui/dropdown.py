# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 23:48:21 2023

@author: Alex
"""

import customtkinter as ctk

class DropdownFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="TestFrame", name, dropdowns=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Add a label to the new entry frame
        self.label1 = ctk.CTkLabel(self, text=name, anchor="center")
        self.label1.grid(row=0, column=0, columnspan=1, pady=(10, 0), padx=10, sticky="n")

        # Add dropdowns to the new entry frame
        self.dropdown_vars = []
        self.dropdowns = []
        row = 1
        for i, dropdown_data in enumerate(dropdowns):
            # set initial value
            dropdown_var = ctk.StringVar(value=dropdown_data["default"])
            self.dropdown_vars.append(dropdown_var)
            
            def combobox_callback(choice, index=i):
                self.dropdown_vars[index].set(choice)
            
            # Create the combobox with options
            options = dropdown_data["options"]
            combobox = ctk.CTkComboBox(self, values=options, command=combobox_callback, variable=dropdown_var)
            combobox.grid(row=row, column=0, pady=4, padx=10, sticky="nw")
            combobox.set(dropdown_data["default"])
            self.dropdowns.append(combobox)
            row += 1

        
    def get_option(self, dropdown_index):
        """Returns the selected option from the dropdown at the given index"""
        return self.dropdown_vars[dropdown_index].get()
    
    def update_option(self, index, option):
        self.dropdowns[index].configure(values=option)