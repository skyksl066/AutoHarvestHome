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
from movement import moveTo


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
        self.window = master
        self.moveTimes = 0
        self.times = 0
    
    def default(self):
        wincap = self.window.wincap
        albion = self.window.albion
        if len(self.window.centers) > 0 and not albion.battling and self.moveTimes < 5:
            closest_object = nearest_object(self.window.centers, self.window.confidences, wincap.screen_center)
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
                self.in_pick()
                if albion.speed < 5.5:
                    # 移動前先騎馬
                    pyautogui.press('a')
                    sleep(5)
        else:
            current = (albion.X, albion.Y)
            target = (self.window.start_X, self.window.start_Y)
            if not is_near_target(current, target) or self.moveTimes > 4:
                if current[0] == 0 and current[1] == 0:
                    logger.info('Please set start position first.')
                    return
                logger.info('Move to start position.')
                area = (wincap.left, wincap.top, wincap.right, wincap.bottom)
                moveTo(self, wincap.hwnd, area, current, target)
                sleep(2)
                self.moveTimes = 0
    
    def back_start_pos(self):
        wincap = self.window.wincap
        albion = self.window.albion
        if len(self.window.centers) > 0 and not albion.battling:
            closest_object = nearest_object(self.window.centers, self.window.confidences, wincap.screen_center)
            logger.info(f"Moving to: {closest_object[0]}, {closest_object[1]}")
            try:
                pyautogui.moveTo(closest_object[0], closest_object[1], duration=0.2)
            except:
                pass
            if is_pickaxe() and not albion.battling:
                logger.info("click")
                pyautogui.click(button="left")
                # 移動時間
                sleep(4)
                self.in_pick()
                if albion.speed < 5.5:
                    # 移動前先騎馬
                    pyautogui.press('a')
                    sleep(5)
                logger.info('Move to start position.')
                current = (albion.X, albion.Y)
                target = (self.window.start_X, self.window.start_Y)
                area = (wincap.left, wincap.top, wincap.right, wincap.bottom)
                moveTo(self, wincap.hwnd, area, current, target)
                sleep(2)
    
    def run(self):
        wincap = self.window.wincap
        albion = self.window.albion
        wincap.set_focus(wincap.hwnd)
        if albion.battling:
            self.fight()
        if albion.KnockedDown > 1:
            logger.info(f'KnockedDown {albion.KnockedDown}')
            albion.KnockedDown = 0
            wincap.close_window()
        
        if self.window.bot_mode == 'default':
            self.default()
        elif self.window.bot_mode == 'back start pos':
            self.back_start_pos()
        elif self.window.bot_mode == 'script':
            logger.info('script.')

    def in_pick(self):
        times = 0
        while True:
            if self.window.albion.is_pickaxe:
                self.moveTimes = 0
                logger.info("picking")
            else:
                break  # 符合條件，退出迴圈
            if self.window.albion.battling:
                break  # 戰鬥退出迴圈
            if times > 5:
                self.window.albion.is_pickaxe = False
                break  # 卡 pick過長強制退出
            sleep(1)
            times += 1
        

    def fight(self):
        logger.info("fighting")
        self.times += 1
        pyautogui.press("space")
        for key in ['q', 'w', 'e']:
            if not self.window.albion.battling:
                return
            elif self.times > 5:
                self.times = 0
                self.window.albion.battling = False
                self.window.albion.causerId = None
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
    delta_x = target[0] - current[0]
    delta_y = target[1] - current[1]
    return abs(delta_x) < 5 and abs(delta_y) < 5


if __name__ == "__main__":
    print(nearest_object([[115, 397], [0, 0]], [0.8, 1], [500, 500]))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    