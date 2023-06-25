# -*- coding: utf-8 -*-
"""
Created on Mon May 29 20:06:57 2023

圖像辨識模組

@author: Alex
"""

import cv2
import numpy as np
from window_capture import WindowCapture
import os
import time
from loguru import logger

# 定義常數
INPUT_WIDTH = 640
INPUT_HEIGHT = 640
SCORE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4
CONFIDENCE_THRESHOLD = 0.4

def build_model(path="models/custom_yolov5.onnx"):
    '''
    建立模型並配置運行環境

    輸入:
    - path: 模型檔案的路徑 (預設為 "models/custom_yolov5.onnx")

    輸出:
    - net: 配置好的模型

    功能說明:
    1. 根據指定的模型檔案路徑讀取模型
    2. 根據 cuda_device_count 的值配置適當的運行環境
        - 若 cuda_device_count 大於 0，嘗試使用 CUDA 加速，並設置相應的後端和目標
        - 若 cuda_device_count 小於 0，運行在 CPU 上，設置相應的後端和目標
    3. 返回配置好的模型

    注意:
    - 模型檔案需存在於指定的路徑中

    '''
    net = cv2.dnn.readNet(path)
    cuda_device_count = cv2.cuda.getCudaEnabledDeviceCount()
    if cuda_device_count > 0:
        logger.info("Attempty to use CUDA")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)
    else:
        logger.info("Running on CPU")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    return net


def detect(image, net):
    """
    執行物件檢測，使用預訓練的深度學習模型進行推論。

    參數:
        image: numpy.ndarray
            輸入的影像。
        net: cv2.dnn_Net
            預訓練的深度學習模型。

    返回值:
        preds: numpy.ndarray
            模型的預測結果。

    功能說明:
        1. 將輸入的影像進行預處理，將其轉換為神經網絡的輸入格式。
        2. 將預處理後的輸入設置為神經網絡的輸入。
        3. 進行模型的前向傳播，獲得預測結果。
        4. 返回預測結果。
    """
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (INPUT_WIDTH, INPUT_HEIGHT), swapRB=True, crop=False)
    net.setInput(blob)
    preds = net.forward()
    return preds


def load_classes(model):
    '''
    根據模型檔案名稱取得相應的類別標籤檔案
    載入類別列表

    輸入:
    - model: 模型檔案名稱

    輸出:
    - class_list: 載入的類別列表

    功能說明:
    1. 根據指定的類別列表檔案名稱讀取檔案
    2. 將檔案中的每行類別名稱去除空白字元後存入 class_list
    3. 返回載入的類別列表

    注意:
    - 類別列表檔案需存在於 "models/" 目錄下

    參數說明:
    - model: 字符串，模型檔案的名稱（包含擴展名）

    返回值說明:
    - class_list: 列表，載入的類別列表

    '''

    # 從模型檔案名稱中取得類別列表檔案名稱
    class_name = model.split(".")[0]
    classes_name = f"{class_name}.txt"

    # 初始化類別列表
    class_list = []

    # 讀取類別列表檔案並存入 class_list
    with open(f"models/{classes_name}", "r") as f:
        class_list = [cname.strip() for cname in f.readlines()]

    # 返回載入的類別列表
    return class_list


def wrap_detection(input_image, output_data, in_confidence, allow_ids=[]):
    """
    對輸出資料進行後處理，提取物件檢測結果。

    參數:
        input_image: numpy.ndarray
            輸入影像。
        output_data: numpy.ndarray
            模型輸出的資料。

    返回值:
        result_class_ids: list
            檢測到的物件類別ID列表。
        result_confidences: list
            檢測到的物件置信度列表。
        result_boxes: list
            檢測到的物件邊界框列表。

    功能說明:
        1. 初始化物件類別ID、置信度和邊界框列表。
        2. 獲取輸出資料的行數。
        3. 獲取輸入影像的寬度、高度。
        4. 計算寬度和高度的縮放因子。
        5. 遍歷輸出資料的每一行。
        6. 檢查該行的置信度是否大於等於0.4。
        7. 獲取該行類別分數，並找到最大分數的類別ID。
        8. 如果最大分數大於0.25，則將類別ID、置信度和邊界框添加到對應的列表中。
        9. 使用非最大抑制(NMS)過濾重疊的邊界框。
        10. 根據NMS的結果，提取最終的類別ID、置信度和邊界框列表。
        11. 返回最終的結果列表。
    """
    class_ids = []
    confidences = []
    boxes = []

    rows = output_data.shape[0]

    image_width, image_height, _ = input_image.shape

    x_factor = image_width / INPUT_WIDTH
    y_factor =  image_height / INPUT_HEIGHT

    for r in range(rows):
        row = output_data[r]
        confidence = row[4]
        if confidence >= in_confidence:

            classes_scores = row[5:]
            _, _, _, max_indx = cv2.minMaxLoc(classes_scores)
            class_id = max_indx[1]
            if class_id not in allow_ids and allow_ids != []:
                continue
            if (classes_scores[class_id] > .25):

                confidences.append(confidence)

                class_ids.append(class_id)

                x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
                left = int((x - 0.5 * w) * x_factor)
                top = int((y - 0.5 * h) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                box = np.array([left, top, width, height])
                boxes.append(box)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.45) 

    result_class_ids = []
    result_confidences = []
    result_boxes = []

    for i in indexes:
        result_confidences.append(confidences[i])
        result_class_ids.append(class_ids[i])
        result_boxes.append(boxes[i])

    return result_class_ids, result_confidences, result_boxes

def format_yolov5(frame):
    """
    將輸入的影像進行格式化處理。
    
    參數:
        frame: numpy.ndarray
            輸入的影像。
    
    返回值:
        result: numpy.ndarray
            格式化後的影像。
    
    功能說明:
        1. 獲取輸入影像的行數、列數和通道數。
        2. 計算行數和列數的最大值。
        3. 建立一個與最大值大小相等的全零影像。
        4. 將原始影像放置在全零影像的左上角。
        5. 返回格式化後的影像。
    """
    row, col, _ = frame.shape
    _max = max(col, row)
    result = np.zeros((_max, _max, 3), np.uint8)
    result[0:row, 0:col] = frame
    return result


def results_objects(frame, net, model, in_confidence, allow_ids=[]):
    '''
    對輸入的影像進行物件檢測，並返回檢測結果
    
    輸入:
    - frame: 輸入的影像，可以是原始影像
    - net: 使用的物件檢測模型
    - model: 物件分類模型
    
    輸出:
    - class_ids: 檢測到的物件類別ID列表
    - confidences: 檢測到的物件置信度列表
    - boxes: 檢測到的物件邊界框列表
    
    功能說明:
    1. 將輸入影像進行格式化處理，使其符合模型的輸入要求
    2. 使用物件檢測模型進行物件檢測，得到預測結果
    3. 使用物件分類模型對預測結果進行類別識別
    4. 提取檢測結果中的物件類別ID、置信度和邊界框
    5. 返回檢測結果
    
    注意:
    - 需要先建立好物件檢測模型和物件分類模型
    - 輸入影像需要符合物件檢測模型的輸入要求
    
    '''
    inputImage = format_yolov5(frame)
    outs = detect(inputImage, net)
    class_ids, confidences, boxes = wrap_detection(inputImage, outs[0], in_confidence, allow_ids)
    return class_ids, confidences, boxes

def results_frame(frame, class_ids, confidences, boxes, class_list):
    '''
    在輸入影像中繪製檢測結果框和標籤

    輸入:
        - frame: 輸入的影像 (NumPy 數組)
        - class_ids: 物體類別 ID 列表
        - confidences: 物體檢測置信度列表
        - boxes: 物體框座標列表 (左上角 x, y，寬度，高度)
        - class_list: 物體類別名稱列表

    輸出:
        - 經過繪製檢測結果後的影像 (NumPy 數組)

    功能說明:
        1. 使用顏色列表為每個類別分配一種顏色
        2. 遍歷每個檢測結果，繪製框和標籤
           - 使用對應的顏色繪製物體框
           - 在物體框上方繪製標籤文字
    '''
    colors = [(255, 255, 0), (0, 255, 0), (0, 255, 255), (255, 0, 0)]
    for (classid, confidence, box) in zip(class_ids, confidences, boxes):
         color = colors[int(classid) % len(colors)]
         cv2.rectangle(frame, box, color, 2)
         cv2.rectangle(frame, (box[0], box[1] - 20), (box[0] + box[2], box[1]), color, -1)
         cv2.putText(frame, f'{class_list[classid]} {confidence:.2f}', (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, .5, (0,0,0))
    return frame


def get_files_in_folder():
    '''
    獲取指定文件夾中的文件列表

    輸入:
        無

    輸出:
        file_names: 一個包含指定文件夾中所有文件名的列表

    功能說明:
        1. 定義要獲取文件列表的文件夾路徑
        2. 創建一個空的列表file_names來存儲文件名
        3. 使用os.listdir()函數遍歷指定文件夾中的所有文件和子文件夾
        4. 對於每個文件名，檢查其是否為文件（而不是子文件夾）
        5. 如果是文件，則將其文件名添加到file_names列表中
        6. 返回包含指定文件夾中所有文件名的列表file_names
    '''
    folder_path = "models"
    file_names = []
    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            file_names.append(filename)
    return file_names


def filter_models(file_names):
    '''
    過濾模型文件名，只保留擴展名為.onnx的文件
    
    輸入:
        - file_names: 一個包含多個文件名的列表
    
    輸出:
        - onnx_models: 一個僅包含擴展名為.onnx的文件名的列表
    
    功能說明:
        1. 遍歷文件名列表中的每個文件名
        2. 檢查每個文件名的擴展名是否為.onnx
        3. 如果是，則將該文件名添加到onnx_models列表中
        4. 返回僅包含擴展名為.onnx的文件名的列表onnx_models
    '''
    onnx_models = []
    for file in file_names:
        if file.split(".")[-1] == "onnx":
            onnx_models.append(file)    
    return onnx_models


if __name__ == "__main__":
    start_time = time.time()
    win = WindowCapture('Albion Online Client')
    screenshot = win.get_screenshot()
    net = build_model(f"models/rough_stone.onnx")
    class_ids, confidences, boxes = results_objects(screenshot, net, 'rough_stone.onnx')
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"程式碼執行時間：{execution_time} 秒")



