## Training Your Own Model

To train a YOLO model for your specific dataset, follow these steps:

### Image Annotation

- Install and use the LabelImg tool to annotate images.
- Use Anaconda to install LabelImg:

```Anaconda prompt
conda create --name=labelImg python=3.8
conda activate labelImg
pip install pyqt5
pip install labelImg
```

- Execute LabelImg:

```Anaconda prompt
labelImg
```

- Save annotation information in YOLO format for training the YOLO model.
![Image](https://github.com/skyksl066/AutoHarvestHome/raw/main/docs/images/labelImg.png?raw=true)

### Dataset Directory Structure

Organize annotated images and their corresponding annotation files in the following structure:

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

### Dataset YAML Configuration File

Prepare the `albion.yaml` configuration file for the training program. Here's an example content:

```yaml
path: ../datasets/albion  # Root data directory
train: images/train       # Training dataset (relative to path)
val: images/train         # Validation dataset (relative to path)
test:                     # Test dataset (relative to path, optional)

names:
  0: fiber-2
  1: fiber-3
  #... (more categories)

nc: 13  # Number of classes, set according to the dataset's category count
```

### Training YOLOv5 Model

Train the model using YOLOv5 source code:

```bash
git clone https://github.com/ultralytics/yolov5
cd yolov5
pip install -r requirements.txt
python train.py --img-size 640 --batch 16 --epochs 500 --data albion.yaml --weights yolov5s.pt --workers 0

# --img-size specifies image size, larger for detecting smaller objects, default is 640.
# --weights specifies pre-trained models.
# --epochs denotes training cycles.
```

### Model Training Results

Upon completion, the model and related training information will be in the `runs/train/exp` directory. `result.png` shows model convergence, while the best model parameters `best.pt` are stored in `runs/train/exp/weights`.

![Image](https://github.com/skyksl066/AutoHarvestHome/raw/main/docs/images/train-results.png?raw=true)
![Image](https://github.com/skyksl066/AutoHarvestHome/raw/main/docs/images/train-results1.jpg?raw=true)

### Using the Model for Predictions

Utilize the self-trained YOLO model for predictions:

```bash
python detect.py --weight runs/train/exp/weights/best.pt \
  --source eggs-test.jpg --iou-thres 0.3 --conf-thres 0.5
  
# --iou-thres sets the IoU threshold value.
# --conf-thres sets the confidence threshold value.
```

Predictions are available in the `runs/detect/exp` directory.
![Image](https://github.com/skyksl066/AutoHarvestHome/raw/main/docs/images/detect-results.png?raw=true)

### Converting the Model to ONNX Format

```
python export.py --data /data/albion.yaml --weights runs/train/exp/weights/best.pt --include onnx
```

The converted model file is `best.onnx`. If conversion fails, edit `export.py` setting `do_constant_folding=True` to `False`.

## References

https://officeguide.cc/pytorch-yolo-v5-object-egg-detection-models-tutorial-examples/