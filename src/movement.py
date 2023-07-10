# -*- coding: utf-8 -*-
"""
Created on Mon May 29 20:06:57 2023

@author: Alex
"""

import win32api
import win32process
import win32gui
import win32con
import struct
import pyautogui
import time
import json
import os

# 定義常數
MEMORY_ADDRESS = 0x1B6A4612BC0
FOLDER_PATH = os.getcwd()


def get_window_position_size(hwnd):
    # 獲取視窗位置和大小
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    
    # 計算視窗寬度和高度
    width = right - left
    height = bottom - top
    
    return (left, top, width, height)


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
        click_y += delta_x * 18
    elif delta_x < 0:
        click_x += delta_x * 18
        click_y += delta_x * 18

    if delta_y > 0:
        click_x += delta_y * 18
        click_y -= delta_y * 18
    elif delta_y < 0:
        click_x += delta_y * 18
        click_y -= delta_y * 18
        
    return click_x, click_y


def get_position(hwnd):
    try:
        # 獲取目標進程的句柄
        process_id = win32process.GetWindowThreadProcessId(hwnd)[1]
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, process_id)
        
        # 一次性讀取連續的記憶體塊
        buffer = win32process.ReadProcessMemory(handle, MEMORY_ADDRESS, 8)
        
        # 解析記憶體數據
        x, y = struct.unpack('2f', buffer)
        
        return (x, y)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # 關閉進程句柄
        win32api.CloseHandle(handle)


def move(hwnd, area, script):
    area_middle = get_middle(area)
    center_x = (area_middle[0] + area_middle[2]) // 2
    center_y = (area_middle[1] + area_middle[3]) // 2 - 40

    points = read_json_script(os.path.join(FOLDER_PATH, f'script/{script}.json'))
    win32gui.SetForegroundWindow(hwnd)
    for point in points:
        current_x, current_y = get_position(hwnd)
        print(current_x, current_y)
        click_x, click_y = calculate_click_position(current_x, current_y, point['X'], point['Y'])
        print(click_x, click_y)
        pyautogui.click(center_x + click_x, center_y + click_y, button='right')
        time.sleep(1.5)
    
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
            #pyautogui.click(button="right")
            time.sleep(0.2)
            pyautogui.mouseUp(button="right")
        except:
            pass


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


if __name__ == '__main__':
    hwnd = win32gui.FindWindow(None, "Albion Online Client")
    area = get_window_position_size(hwnd)
    # move(hwnd, area, 'Dusklight Fen')
    area_middle = get_middle(area)
    moveTo(hwnd, area, (109.79, 157.75), (94.45, 133.05))





