# -*- coding: utf-8 -*-
"""
Created on Fri Jun  2 22:25:35 2023

捕獲遊戲訊息

@author: Alex
"""
import subprocess
import json
from loguru import logger
import pyautogui
import math


def calculate_direction(current_x, current_y, target_x, target_y):
    # 計算目標角度（從 X 軸正方向逆時針方向）
    angle = math.atan2(target_y - current_y, target_x - current_x)
    
    # 將弧度轉換為角度
    angle_degrees = math.degrees(angle)
    
    # 將角度映射到 12 點鐘方向（0 到 360 度之間）
    clock_direction = (60 - angle_degrees) % 360
    clock_direction = (clock_direction + 360) % 360
    clock_direction = 12 if clock_direction == 0 else int(clock_direction / 30) + 3
    
    return clock_direction


class AlbionCapture:
    def __init__(self, window):
        self.window = window
        self.process = subprocess.Popen(["plugins/AlbionCapture.exe"], stdout=subprocess.PIPE)
        self.UserObjectId = None
        self.Username = None
        self.MapIndex = None
        self.KnockedDown = 0
        self.is_pickaxe = False
        self.pickObjectId = None
        self.battling = False
        self.causerId = None
        self.speed = 0
        self.X = 0
        self.Y = 0
        
        
    def run(self):
        while True:
            try:
                output = self.process.stdout.readline().decode().strip()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    self._deserialize(output)
            except Exception as err:
                logger.error(err)
        # 等待程序执行完成
        self.process.wait()
    
    def resetValue(self):
        self.KnockedDown = 0
        self.is_pickaxe = False
        self.battling = False
        self.causerId = None
        self.pickObjectId = None
        self.MapIndex = None
        
    def _deserialize(self, jsonStr):
        result = json.loads(jsonStr)
        if result['Type'] == 'Response':
            self._response(result)
            # print(result)
        elif result['Type'] == 'Event':
            self._event(result)
            # print(result)
        elif result['Type'] == 'Request':
            self._request(result)
    
    def _request(self, value):
        if value['Code'] == 21:
            self.X = value['Position'][0]
            self.Y = value['Position'][1]
            self.speed = value['Speed']
            self.window.title(f"Google Chrome - {self.Username}({round(self.X, 1)}, {round(self.Y, 1)})")
        # 要求採集
        if value['Code'] == 46:
            self.is_pickaxe = True
            self.pickObjectId = value['ObjectId']
    
    def _response(self, value):
        # 進入地圖
        if value['Code'] == 2:
            self.UserObjectId = value['UserObjectId']
            self.Username = value['Username']
            self.MapIndex = value['MapIndex']
            logger.info(f'Join game Username: {self.Username}, Map: {value["UniqueName"]}')
            self.window.title(f"Google Chrome - {self.Username}")
    
    def _event(self, value):
        # 血量變化
        if value['Code'] == 6:
            if self.UserObjectId == value['ObjectId']:
                self.causerId = value['CauserId']
                self.battling = True
            if self.causerId == value['ObjectId'] and value['NewHealthValue'] == 0:
                pyautogui.press('s')
                self.causerId = None
                self.battling = False
        # 物件狀態更新
        if value['Code'] == 42:
            if self.pickObjectId == value['ObjectId'] and value['Count'] == 0:
                self.pickObjectId = None
                self.is_pickaxe = False
        # 聲望更新
        if value['Code'] == 77:
            pass
        # 倒下
        if value['Code'] == 157 and self.UserObjectId == value['ObjectId']:
            self.KnockedDown += 1
        # 發現高品質
        if value['Code'] == 36 and value['CauserId'] == None:
            Position = value['Position']
            direction = calculate_direction(self.X, self.Y, Position[0], Position[1])
            logger.info(f"Find HignLevel Direction: {direction}, X: {Position[0]}, Y: {Position[1]}, Tier: {value['Tier']}, QualityLevel: {value['QualityLevel']}")

if __name__ == "__main__":
    albion_capture = AlbionCapture()
    albion_capture.run()
    