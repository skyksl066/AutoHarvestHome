## 如何自行訓練模型

若要針對特定資料集訓練自己的 YOLO 模型，可遵循以下步驟：

### 標註圖片

- 安裝並使用 LabelImg 工具標註圖片。
- 使用 Anaconda 安裝 LabelImg：

```Anaconda prompt
conda create --name=labelImg python=3.8
conda activate labelImg
pip install pyqt5
pip install labelImg
```

- 執行 LabelImg：

```Anaconda prompt
labelImg
```

- 以 YOLO 格式儲存標註資訊的文字檔，便於訓練 YOLO 模型時使用。
![Image](https://github.com/skyksl066/AutoHarvestHome/raw/main/docs/images/labelImg.png?raw=true)

### 資料集目錄結構

按以下目錄結構存放標註好的圖片和對應的標註檔案：

```
albion
├── images
│   └── train
│       ├── albion0.png
│       ├── albion1.png
│       └── albion2.png
└── labels
    └── train
        ├── albion0.txt
        ├── albion1.txt
        └── albion2.txt
```

### 資料集 YAML 設定檔

準備訓練程式使用的 `albion.yaml` 設定檔，示例內容如下：

```yaml
path: ../datasets/albion  # 資料根目錄
train: images/train       # 訓練用資料集（相對於 path）
val: images/train         # 驗證用資料集（相對於 path）
test:                     # 測試用資料集（相對於 path，可省略）

names:
  0: fiber-2
  1: fiber-3
  #... (更多類別)

nc: 13  # 分類數量，根據資料集類別數量設定
```

### 訓練 YOLOv5 模型

使用 YOLOv5 原始碼進行模型訓練：

```bash
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt
python train.py --img-size 640 --batch 16 --epochs 500 \
  --data albion.yaml --weights yolov5s.pt

# --img-size 可以指定影像的大小，對於偵測比較小的物件時，可以加大影像的大小，預設的影像大小為 640。
# --weights 則可用來指定預訓練的模型。
# --epochs 訓練的次數。
```

### 模型訓練結果

訓練完成後，模型及相關訓練資訊會放在 `runs/train/exp` 目錄。其中 `result.png` 顯示模型收斂情況，最佳模型參數 `best.pt` 存放在 `runs/train/exp/weights` 目錄中。

![Image](https://github.com/skyksl066/AutoHarvestHome/raw/main/docs/images/train-results.png?raw=true)
![Image](https://github.com/skyksl066/AutoHarvestHome/raw/main/docs/images/train-results1.jpg?raw=true)

### 使用模型進行預測

利用自訓練 YOLO 模型進行預測：

```bash
python detect.py --weight runs/train/exp/weights/best.pt \
  --source eggs-test.jpg --iou-thres 0.3 --conf-thres 0.5
  
# --iou-thres 是設定 IoU 門檻值
# --conf-thres 則是設定信心門檻值
```

預測結果位於 `runs/detect/exp` 目錄下。
![Image](https://github.com/skyksl066/AutoHarvestHome/raw/main/docs/images/detect-results.png?raw=true)

### 將模型轉換為 ONNX 格式

```
python export.py --data /data/albion.yaml --weights runs/train/exp/weights/best.pt --include onnx
```

轉換後的模型檔案為 `best.onnx`。若轉換失敗，編輯 `export.py` 中的 `do_constant_folding=True` 設定為 `False`。

## 參考資料

https://officeguide.cc/pytorch-yolo-v5-object-egg-detection-models-tutorial-examples/