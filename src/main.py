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
from movement import moveTo
import cv2
import sys
import os
import keyboard
from ui.switch import SwitchesFrame
from ui.dropdown import DropdownFrame
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
        self.start_X = 0
        self.start_Y = 0
        # 初始化WindowCapture
        self.wincap = WindowCapture(None)
        # 初始化AlbionCapture
        self.albion = AlbionCapture(self)
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
        
        def confidence_slider_event(value):
            # 信心值拉條
            self.confidence = round(value, 2)
            logger.info(f"Set confidence to: {self.confidence}")
            
        def update_thread():
            if not self.thread.is_alive():
                self.thread = threading.Thread(target=self.update_screenshot)
                self.thread.start()

        def vision_switch_event():
            switch = self.actions_frame.switches[0]
            self.vision_status = switch.get()
            logger.info(f"Switch Vision to: {self.vision_status}")
            if self.vision_status == 'on':
                self.is_running = True
                update_thread()
            else:
                self.is_running = False
                
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
                    
        def bot_switch_event():
            switch = self.actions_frame.switches[1]
            self.bot_status = switch.get()
            logger.info(f"Switch Bot to: {self.bot_status}")
            if self.bot_status == 'on':
                self.is_running = True
                update_thread()
            else:
                self.is_running = False
                
        def update_info():
            '''
            更新信息
        
            輸入: 無
            輸出: 無
            功能說明:
                1. 關閉監看視窗
                2. 重置 `actions_frame` 的值
                3. 將機器人狀態和視覺狀態設置為 "off"
                4. 獲取選擇的 ONNX 模型並載入類別列表
                5. 建立模型並設置為網路模型
                6. 打印正在使用的模型
                7. 獲取遊戲名稱並初始化 `WindowCapture` 對象
                8. 打印遊戲分辨率
            '''
            # 將機器人狀態和視覺狀態設置為 "off"
            self.bot_status="off"
            self.vision_status="off"
            self.script_status="off"
            self.start_X = self.albion.X
            self.start_Y = self.albion.Y
            self.albion.resetValue()
            
            # 重置 actions_frame 的值
            self.actions_frame.reset_values()
            
            # 獲取選擇的 ONNX 模型並載入類別列表
            self.model = self.dropdown_box.get_option(1)
            self.class_list = load_classes(self.model)
            self.dropdown_box.update_option(2, self.class_list)
            class_name = self.dropdown_box.get_option(2)
            self.allow_ids = []
            if class_name != 'ALL':
                self.allow_ids = [self.class_list.index(class_name)]

            # 建立模型並設置為網路模型
            self.net = build_model(f"models/{self.model}")          
            logger.info(f"Using: {self.model}")
            
            # 獲取遊戲名稱並初始化 WindowCapture 對象
            logger.info(f'Game name: {self.dropdown_box.get_option(0)}')
            window_name = self.dropdown_box.get_option(0)
            self.wincap = WindowCapture(window_name)
            
            # 打印遊戲分辨率
            logger.info(f"Game resolution: {self.wincap.width}x{self.wincap.height}")


        #Creating Objects
        # 監看視窗開關 開掛開關
        switches_data = [
            {"text": "Display bot's vision", "command": vision_switch_event},
            {"text": "Gather resources", "command": bot_switch_event},
            {"text": "Run script", "command": script_switch_event}
        ]
        self.actions_frame = SwitchesFrame(self, name="Actions", switches=switches_data)
        # 選擇模式
        dropdowns_data = [
            {"text": "Select game name", "default": "Albion Online Client", "options": self.windows},
            {"text": "Select detection model", "default": "albion.onnx", "options": self.models},
            {"text": "Select class", "default": "ALL", "options": self.class_list}
        ]
        self.dropdown_box = DropdownFrame(self, name="Select", dropdowns=dropdowns_data)
        # 存檔按鈕
        self.update_info_button = ctk.CTkButton(self, text="Save changes", command=update_info)
        # 信心值
        self.confidence_slider = ctk.CTkSlider(self, from_=0, to=1, width=150, number_of_steps=100, command=confidence_slider_event)
        self.confidence_slider.set(self.confidence)
        
        #Drawing Objects
        self.actions_frame.grid(row=0, column=0, pady=12, padx=10)
        self.dropdown_box.grid(row=0, column=1, pady=12, padx=10, sticky='n')
        self.update_info_button.grid(row=1, column=0, padx=20, pady=10, sticky='n')
        self.confidence_slider.grid(row=1, column=1, padx=20, pady=10, sticky='n')


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
                #self.wincap.set_focus(self.wincap.hwnd)
                #if self.albion.battling:
                    #self.bot.fight()
                #self.bot.go_to()
                #if self.albion.KnockedDown > 1:
                    #logger.info(f'KnockedDown {self.albion.KnockedDown}')
                    #self.albion.KnockedDown = 0
                    #self.wincap.close_window()
            
            
    def monitor(self, key):
        '''停止程序bot'''
        if key.name == 'f12':
            # 重置 actions_frame 的值
            self.vision_status = "off"
            self.bot_status = "off"
            self.script_status = "off"
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
