# -*- coding: utf-8 -*-
"""
Created on Mon May 29 20:06:57 2023

視窗、截圖模組

@author: Alex
"""

import numpy as np
import win32gui, win32api, win32con
import cv2
import pyautogui

class WindowCapture:
    def __init__(self, window_name=None):
        '''
        初始化函數，用於設置捕捉視窗的相關屬性
        
        輸入:
        - window_name: 視窗名稱 (可選)
        
        功能說明:
        1. 如果未提供視窗名稱，則將捕捉目標設置為整個桌面窗口
        2. 如果提供了視窗名稱，則通過該名稱尋找指定視窗
        3. 如果找不到指定視窗，則拋出異常
        4. 獲取捕捉視窗的位置和大小
        5. 設置相關屬性 (left, top, right, bottom, width, height) 為捕捉視窗的位置和大小
        
        注意:
        - 該方法用於初始化捕捉視窗的相關屬性，並確保能夠正確捕捉到指定視窗
        - 如果未提供視窗名稱，將捕捉整個桌面窗口
        - 如果提供了視窗名稱，但找不到對應視窗，將拋出異常
        '''
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
        #Call specific window to capture
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception("Window not found: {}".format(window_name))
        self.left, self.top, self.right, self.bottom, self.width, self.height = self.get_window_position_size(self.hwnd)
        self.screen_center = [int(self.width)/2, int(self.height)/2]
        
    def set_focus(self, hwnd):
        win32gui.SetForegroundWindow(hwnd)
        
    def get_window_position_size(self, hwnd):
        '''
        獲取視窗的位置和大小
        
        輸入:
        - self: 對象本身
        - hwnd: 視窗的句柄
        
        輸出:
        - 視窗的左上角座標 (left, top)
        - 視窗的右下角座標 (right, bottom)
        - 視窗的寬度 (width)
        - 視窗的高度 (height)
        
        功能說明:
        1. 使用win32gui.GetWindowRect()函數獲取視窗的位置和大小
        2. 根據左上角和右下角座標計算視窗的寬度和高度
        3. 返回視窗位置和大小的相關資訊
        
        注意:
        - 該方法需要傳入視窗的句柄(hwnd)
        
        '''
        # 獲取視窗位置和大小
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        
        # 檢查並修正視窗位置和大小
        if left < 0:
            left = 0
        if top < 0:
            top = 0
    
        # 獲取桌面大小
        desktop_width, desktop_height = win32api.GetSystemMetrics(win32con.SM_CXSCREEN), win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    
        # 檢查並修正視窗大小
        if right > desktop_width:
            right = desktop_width
        if bottom > desktop_height:
            bottom = desktop_height
        
        # 計算視窗寬度和高度
        width = right - left
        height = bottom - top
        
        return (left, top, right, bottom, width, height)
    
    
    def get_screenshot(self):
        '''
        截取屏幕截圖並進行後續處理
    
        輸入:
        - self: 對象本身
    
        輸出:
        - cropped_img: 剪裁後的圖片
    
        功能說明:
        1. 使用pyautogui進行屏幕截圖
        2. 將截取的圖像轉換為NumPy數組
        3. 將圖像的通道從RGBA轉換為RGB格式
        4. 根據指定的範圍剪裁圖片
        5. 返回剪裁後的圖片
    
        注意:
        - 該方法需要在具有屏幕截圖權限的環境中執行

        '''
        # 使用pyautogui進行截圖
        image = pyautogui.screenshot()
        
        # 將圖像轉換為NumPy數組
        img = np.array(image)
        
        # 將圖像通道從RGBA轉換為RGB
        img = img[:, :, :3]
        
        # 剪裁圖片
        cropped_img = img[self.top:self.bottom, self.left:self.right]
        
        return cropped_img
    
    def close_window(self):
        # 发送关闭窗口消息
        win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
    
    @staticmethod
    def list_window_names():
        '''
        列出當前打開的所有視窗的名稱
    
        輸入: 無
        輸出: 返回包含視窗名稱的列表
        功能說明:
            1. 使用 `win32gui` 模組的 `EnumWindows` 函數遍歷所有視窗
            2. 對每個視窗調用回調函數 `winEnumHandler`
            3. 如果視窗是可見的且具有非空的窗口名稱，則將其添加到 `windows` 列表中
            4. 返回包含所有視窗名稱的列表作為結果
        '''
        windows = []
   
        def winEnumHandler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                winName = win32gui.GetWindowText(hwnd)
                if winName != '':
                    # print(hex(hwnd), win32gui.GetWindowText(hwnd))
                    windows.append(winName)
        
        win32gui.EnumWindows(winEnumHandler, None)
        return windows

if __name__ == "__main__":
    win = WindowCapture('Albion Online Client')
    a = win.list_window_names()
    screenshot = win.get_screenshot()
    # 將圖片轉換為OpenCV格式
    screenshot_cv = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    # 顯示圖片
    cv2.destroyAllWindows()
    cv2.imshow("Screenshot", screenshot_cv)
    cv2.waitKey(0)