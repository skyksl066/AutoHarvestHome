# -*- coding: utf-8 -*-
"""
Created on Mon May 29 20:06:57 2023

主程式
Move Albion Client to the corner of the screen

@author: Alex
"""
import customtkinter as ctk
from onnx_detextion import filter_models, get_files_in_folder, build_model, load_classes, results_objects, results_frame
from bot_thread import get_center, Bot
from window_capture import WindowCapture
from albion_capture import AlbionCapture
import cv2
import sys
import os
import keyboard
from ui.switch_frame import SwitchesFrame
from ui.model_frame import ModelFrame
from ui.other_frame import OtherFrame
import time
import threading
from loguru import logger
import json


# Set custom theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        '''
        初始化
        '''
        # 繼承 customtkinter
        super().__init__()

        # 取得model列表
        self.models = filter_models(get_files_in_folder())
        # 預設第一個model
        self.model = self.models[0]
        # 載入預設類別
        self.class_list = load_classes(self.model)
        # 建立模型
        self.net = build_model(f"models/{self.model}")
        self.is_running = False
        self.confidence = 0.4
        self.script_record = []
        self.allow_ids = []
        
        self.vision_status = "off"
        self.bot_status = "off"
        self.script_status = 'off'
        self.bot_mode = 'default'
        self.start_X = 0
        self.start_Y = 0
        # 初始化WindowCapture
        self.wincap = WindowCapture(None)
        # 初始化AlbionCapture
        self.albion = AlbionCapture(self)
        # 初始化Bot
        self.bot = Bot(self)
        # 取得視窗列表
        self.windows = self.wincap.list_window_names()
        self.class_ids, self.confidences, self.boxes, self.centers = [], [], [], []
        self.albion_capture_thread = threading.Thread(target=self.albion.run)
        self.albion_capture_thread.start()
        self.thread = threading.Thread(target=self.update_screenshot)
        
        # 視窗大小
        try:
            setting = read_json_text('ui/setting.txt')
            self.geometry(setting['geometry'])
        except:
            self.geometry("380x220")
        # 視窗標題
        self.title("Google Chrome")
        # 視窗圖片
        self.iconbitmap("wanderingeye.ico")

        # 關閉視窗事件
        self.protocol("WM_DELETE_WINDOW", self.on_close)
  
        def script_switch_event():
            switch = self.actions_frame.switches[2]
            self.script_status = switch.get()
            if self.script_status == 'on':
                file_path = f'script/{self.albion.MapIndex}.txt'
                try:
                    self.script_record = read_json_text(file_path)
                    logger.info(f"Switch run script to: {self.script_status}")
                    if is_near_target((self.albion.X, self.albion.Y), self.script_record[0]):
                        logger.info(f'{file_path} loaded')
                    else:
                        switch.deselect()
                        self.script_status = 'off'
                        logger.info(f'Please move to {self.script_record[0]}')
                except FileNotFoundError:
                    logger.error(f'File not found: {file_path}, Please create the script first or load map first.')
                    switch.deselect()
                    self.script_status = 'off'
            else:
                logger.info(f"Switch run script to: {self.script_status}")
         
        def update_info():
            # 將機器人狀態和視覺狀態設置為 "off"
            self.bot_status="off"
            self.vision_status="off"
            self.start_X = self.albion.X
            self.start_Y = self.albion.Y
            logger.info(f"Start position: ({self.start_X}, {self.start_Y})")
            self.albion.resetValue()
            
            # 重置 actions_frame 的值
            self.actions_frame.reset_values()
            window = self.other_frame.comboBox1.get()
            self.wincap = WindowCapture(window)
            logger.info(f'Game name: {window}')
            logger.info(f"Game resolution: {self.wincap.width}x{self.wincap.height}")

        #Creating Objects
        self.actions_frame = SwitchesFrame(master=self)
        self.model_frame = ModelFrame(master=self)
        self.other_frame = OtherFrame(master=self)
        # 存檔按鈕
        self.update_info_button = ctk.CTkButton(self, text="Save changes", command=update_info)
        
        #Drawing Objects
        self.actions_frame.grid(row=0, column=0, pady=12, padx=10, sticky='nsew',columnspan=2)
        self.model_frame.grid(row=1, column=0, pady=12, padx=10, sticky='n')
        self.other_frame.grid(row=1, column=1, pady=12, padx=10, sticky='n')
        self.update_info_button.grid(row=2, column=0, padx=20, pady=10, sticky='n')

    def update_screenshot(self):
        '''timer'''
        while self.is_running:
            if(self.vision_status == "on" or self.bot_status == "on") and not self.albion.battling:
                self.screenshot = self.wincap.get_screenshot()
                self.class_ids, self.confidences, self.boxes = results_objects(self.screenshot, self.net, self.model, self.confidence, self.allow_ids)
                self.centers = get_center(self.boxes)
            
            if self.vision_status == "on":
                # 標記框框
                self.frame = results_frame(self.screenshot, self.class_ids, self.confidences, self.boxes, self.class_list)
                # 啟動監看視窗
                cv2.imshow("Computer Vision", self.frame)
                cv2.waitKey(1)
            elif self.vision_status == "off":
                # 關閉監看視窗
                cv2.destroyAllWindows()
            if self.bot_status=="on":
                self.bot.run()

    def monitor(self, key):
        '''停止程序bot'''
        if key.name == 'f12':
            # 重置 actions_frame 的值
            self.vision_status = "off"
            self.bot_status = "off"
            self.albion.resetValue()
            self.after(0, self.actions_frame.reset_values)
            logger.info("F12 key pressed, bot_status off")
        '''紀錄移動點'''
        if key.name == 'f7':
            self.script_record.append({"x": self.albion.X, "y": self.albion.Y})
            logger.info(f'append record: "x":{self.albion.X}, "y": {self.albion.Y}')
        '''存檔移動點'''
        if key.name == 'f8':
            # 將列表轉換為集合，消除重複元素
            unique_data_set = set(tuple(d.items()) for d in self.script_record)
            # 將集合轉換回列表
            unique_data = [dict(item) for item in unique_data_set]
            file_path = f'script/{self.albion.MapIndex}.txt'
            with open(file_path, 'w+') as file:
                file.write(json.dumps(unique_data))
            logger.info(f'save script to: {file_path}')
        '''截圖'''
        if key.name == 'print screen':
            logger.info('print screen')
            screenshot = self.wincap.get_screenshot()
            file_name = str(int(time.time()))
            cv2.imwrite(f"models/datasets/AutoSave/images/train/{file_name}.png", screenshot)
    
    def on_close(self):
        path = 'ui/setting.txt'
        write_json_text(path, json.dumps({"geometry": self.geometry()}))
        logger.info("Closing")
        # 關閉監看視窗
        cv2.destroyAllWindows()
        self.destroy()
        keyboard.unhook_all()
        self.albion.process.terminate()
        app.quit()
        os._exit(0)


def read_json_text(path):
    # 讀取 JSON 檔案
    with open(path, 'r') as file:
        data = json.load(file)
    return data


def write_json_text(path, data):
    # 讀取 JSON 檔案
    with open(path, 'w+') as file:
        file.write(data)


def is_near_target(current, target):
    delta_x = target['x'] - current[0]
    delta_y = target['y'] - current[1]
    return abs(delta_x) < 10 and abs(delta_y) < 10


if __name__ == "__main__":
    app = App()
    logger.info('If the title name is "None", please reload the map or logout and login.')
    keyboard.on_press(app.monitor)
    app.mainloop()
