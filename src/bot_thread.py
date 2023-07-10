# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 15:39:04 2023

@author: Alex
"""
from time import sleep
import pyautogui
import math
import win32gui
import cv2
import numpy as np
from loguru import logger
import json
import random


def get_center(rectangles):
    '''
    獲取矩形區域的中心點座標
    
    輸入:
    - rectangles: 包含多個矩形區域的列表
    
    輸出:
    - 中心點座標的列表
    
    功能說明:
    1. 遍歷矩形區域列表，計算每個矩形的中心點座標
    2. 中心點的計算公式為 (x + (x + width)) / 2 和 (y + (y + height)) / 2
    3. 將每個矩形的中心點座標加入到中心點列表中
    4. 返回中心點座標的列表
    
    注意:
    - 該方法需要傳入包含多個矩形區域的列表(rectangles)
    - 每個矩形區域的表示方式為 [x, y, width, height]
    
    '''
    centers = []
    for i in rectangles:
        x = int((i[0]+(i[0]+i[2]))/2)
        y = int((i[1]+(i[1]+i[3]))/2)
        centers.append([x, y])
        #print(centers)
    return centers

class Bot:
    def __init__(self, master):
        self.moveTimes = 0
        self.times = 0
        self.script_index = 0
    
    def default(self, master):
        wincap = master.wincap
        albion = master.albion
        if len(master.centers) > 0 and not albion.battling and self.moveTimes < 5:
            closest_object = nearest_object(master.centers, master.confidences, wincap.screen_center)
            logger.info(f"Moving to: {closest_object[0]}, {closest_object[1]}")
            try:
                pyautogui.moveTo(closest_object[0], closest_object[1], duration=0.2)
            except:
                pass
            self.moveTimes += 1
            if is_pickaxe() and not albion.battling:
                logger.info("click")
                pyautogui.click(button="left")
                # 移動時間
                sleep(4)
                self.in_pick(master)
                if albion.speed < 5.5:
                    # 移動前先騎馬
                    pyautogui.press('a')
                    sleep(5)
        else:
            current = (albion.X, albion.Y)
            target = (master.start_X, master.start_Y)
            if not is_near_target(current, target) or self.moveTimes > 4:
                if current[0] == 0 and current[1] == 0:
                    logger.info('Please set start position first.')
                    return
                logger.info('Move to start position.')
                area = (wincap.left, wincap.top, wincap.right, wincap.bottom)
                moveTo(master, wincap.hwnd, area, current, target)
                sleep(2)
                self.moveTimes = 0
    
    def back_start_pos(self, master):
        wincap = master.wincap
        albion = master.albion
        if len(master.centers) > 0 and not albion.battling:
            closest_object = nearest_object(master.centers, master.confidences, wincap.screen_center)
            logger.info(f"Moving to: {closest_object[0]}, {closest_object[1]}")
            offset_x, offset_y = (0, 0)
            if self.moveTimes > 5:
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
            try:
                pyautogui.moveTo(closest_object[0] + offset_x, closest_object[1] + offset_y, duration=0.2)
            except:
                pass
            if is_pickaxe() and not albion.battling:
                self.moveTimes = 0
                logger.info("click")
                pyautogui.click(button="left")
                # 移動時間
                sleep(4)
                self.in_pick(master)
                if albion.speed < 5.5:
                    # 移動前先騎馬
                    pyautogui.press('a')
                    sleep(5)
                logger.info('Move to start position.')
                current = (albion.X, albion.Y)
                target = (master.start_X, master.start_Y)
                area = (wincap.left, wincap.top, wincap.right, wincap.bottom)
                moveTo(master, wincap.hwnd, area, current, target)
                sleep(2)
            else:
                self.moveTimes += 1
                
    def script(self, master):
        print(self.script_index)
        next_pos = master.script_record[self.script_index]
        current = (master.albion.X, master.albion.Y)
        print(current)
        target = (next_pos['x'], next_pos['y'])
        print(target)
        area = (master.wincap.left, master.wincap.top, master.wincap.right, master.wincap.bottom)
        moveTo(master, master.wincap.hwnd, area, current, target)
        sleep(10)
        self.script_index += 1
    
    def run(self, master):
        wincap = master.wincap
        albion = master.albion
        wincap.set_focus(wincap.hwnd)
        if albion.battling:
            self.fight(master)
        if albion.KnockedDown > 1:
            logger.info(f'KnockedDown {albion.KnockedDown}')
            albion.KnockedDown = 0
            wincap.close_window()
        
        if master.bot_mode == 'default':
            self.default(master)
        elif master.bot_mode == 'back start pos':
            self.back_start_pos(master)
        elif master.bot_mode == 'script':
            self.script(master)

    def in_pick(self, master):
        times = 0
        while True:
            if master.albion.is_pickaxe:
                self.moveTimes = 0
                logger.info("picking")
            else:
                break  # 符合條件，退出迴圈
            if master.albion.battling:
                break  # 戰鬥退出迴圈
            if times > 5:
                master.albion.is_pickaxe = False
                break  # 卡 pick過長強制退出
            sleep(1)
            times += 1
        

    def fight(self, master):
        logger.info("fighting")
        self.times += 1
        pyautogui.press("space")
        for key in ['q', 'w', 'e']:
            if not master.albion.battling:
                return
            elif self.times > 5:
                self.times = 0
                master.albion.battling = False
                master.albion.causerId = None
                pyautogui.press('s')
                return
            pyautogui.press(key)
            pyautogui.sleep(1)


def is_pickaxe():
    e = win32gui.GetIconInfo(win32gui.GetCursorInfo()[1])
    # print(e)
    return (e[1], e[2]) == (8, 7)


def nearest_object(targets, confidences, screen_center):
    max_distance = float('inf')  # 初始化最大距離為正無窮大
    max_confidence = float('-inf')  # 初始化最大信心值為負無窮大
    closest_object = None
    
    for i in range(len(targets)):
        object_location = targets[i]
        confidence = confidences[i]
        
        # Calculate distance between an object and the character
        distance = math.dist(object_location, screen_center)
        
        # Check if the current object is closer and has higher confidence
        if distance < max_distance and confidence > max_confidence:
            max_distance = distance
            max_confidence = confidence
            closest_object = object_location
    
    return closest_object


def is_near_target(current, target):
    if isinstance(target, dict):
        delta_x = target['x'] - current[0]
        delta_y = target['y'] - current[1]
    else:
        delta_x = target[0] - current[0]
        delta_y = target[1] - current[1]
    return abs(delta_x) < 5 and abs(delta_y) < 5


def read_json_text(path):
    # 讀取 JSON 檔案
    with open(path, 'r') as file:
        data = json.load(file)
    return data


def write_json_text(path, data):
    # 讀取 JSON 檔案
    with open(path, 'w+') as file:
        file.write(data)
        

def moveTo(master, hwnd, area, current, target):
    area_middle = get_middle(area)
    center_x = (area_middle[0] + area_middle[2]) // 2
    center_y = (area_middle[1] + area_middle[3]) // 2 - 40
    
    win32gui.SetForegroundWindow(hwnd)
    click_x, click_y = calculate_click_position(current[0], current[1], target[0], target[1])
    move_list = adjust_coordinates(area, (center_x, center_y), (click_x, click_y))
    for x, y in move_list:
        if master.albion.battling:
            break
        try:
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.mouseDown(button="right")
            time.sleep(0.2)
            pyautogui.mouseUp(button="right")
        except:
            pass


def get_middle(area):
    middle_left = area[0] + (area[2] // 3)
    middle_top = area[1] + (area[3] // 3)
    middle_right = area[0] + (2 * (area[2] // 3))
    middle_bottom = area[1] + (2 * (area[3] // 3))
    
    return (middle_left, middle_top, middle_right, middle_bottom)


def calculate_click_position(current_x, current_y, target_x, target_y):
    delta_x = target_x - current_x
    delta_y = target_y - current_y
    click_x = 0
    click_y = 0
    if delta_x > 0:
        click_x += delta_x * 18
        click_y += delta_x * 14
    elif delta_x < 0:
        click_x += delta_x * 18
        click_y += delta_x * 14

    if delta_y > 0:
        click_x += delta_y * 18
        click_y -= delta_y * 14
    elif delta_y < 0:
        click_x += delta_y * 18
        click_y -= delta_y * 14
        
    return click_x, click_y


def adjust_coordinates(area, center, target):
    adjusted_coordinates = []
    
    while True:
        # 檢查目標座標是否超出螢幕範圍，如果是，調整到螢幕範圍內
        if center[0] + target[0] < area[0] + 150:
            next_x = area[0] + 100
            remainder_x = center[0] - (area[0] + 100) + target[0]
        elif center[0] + target[0] > area[2] - 150:
            next_x = area[2] - 100
            remainder_x = center[0] - (area[2] - 100) + target[0]
        else:
            next_x = center[0] + target[0]
            remainder_x = 0
        
        if center[1] + target[1] < area[1] + 150:
            next_y = area[1] + 100
            remainder_y = center[1] - (area[1] + 100) + target[1]
        elif center[1] + target[1] > area[3] - 150:
            next_y = area[3] - 100
            remainder_y = center[1] - (area[3] - 100) + target[1]
        else:
            next_y = center[1] + target[1]
            remainder_y = 0
        
        adjusted_coordinates.append((next_x, next_y))
        if abs(remainder_x) <= 0 and abs(remainder_y) <= 0:
            break

        target = (remainder_x, remainder_y)
        
    return adjusted_coordinates


from window_capture import WindowCapture
import win32gui
import time
if __name__ == "__main__":
    time.sleep(5)
    file_path = f'script/3204.txt'
    script_record = read_json_text(file_path)
    next_pos = script_record[2]
    current = (123.82, 36.2)
    target = (next_pos['x'], next_pos['y'])
    wincap = WindowCapture('Albion Online Client')
    area = (wincap.left, wincap.top, wincap.right, wincap.bottom)
    area_middle = get_middle(area)
    center_x = (area_middle[0] + area_middle[2]) // 2
    center_y = (area_middle[1] + area_middle[3]) // 2 - 40
    win32gui.SetForegroundWindow(wincap.hwnd)
    click_x, click_y = calculate_click_position(current[0], current[1], target[0], target[1])
    move_list = adjust_coordinates(area, (center_x, center_y), (click_x, click_y))
    for x, y in move_list:
        try:
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.mouseDown(button="right")
            time.sleep(0.2)
            pyautogui.mouseUp(button="right")
        except:
            pass
    #moveTo(master, wincap.hwnd, area, current, target)
    #print(nearest_object([[115, 397], [0, 0]], [0.8, 1], [500, 500]))

    