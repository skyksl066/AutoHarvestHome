# AutoHarvestHome
Base on [The-Gatherer-2.0](https://github.com/Riczap/The-Gatherer)

This was made using YOLOv5 and OpenCV. The model is now comaptible with CPU and GPU and it detects automaticly the best option for your computer. You can load your custom YOLO models (exported to **ONNX**) by using your own .onnx file.

- **Known Issue:** Trying to move the window of The Gatherer 2 while having the Bot Vision activated, will crash the program. (You can move the command prompt at any time without issues)

- **Note:** The Bot and the Vision are independent, you can have the bot running without the Computer Vision function activated. The model is running on the background whenever you activate either of them.
 
- **Note:** All of the parameters have default values, so you can leve them blank and it'll work fine.

## Installation
To use the new version of AutoHarvestHome you can install the dependencies either in your main python environment, using anaconda or as an executable file.
### Python
 1. Clone the repository on GitHub (Download the files).
 2. Open a console terminal and run the following command to install all of the dependencies: `pip install -r requirements.txt`
### Conda
 1. Clone the repository on GitHub (Download the files).
 2. Install Anaconda: [https://www.anaconda.com/products/distribution](https://www.anaconda.com/products/distribution)
 3. Create an Environment using the following command on the anaconda prompt: `conda create -n myenv` (you can choose any name you want for the env)
 4. Activate the environment using `conda activate myenv` and open the directory where you downloaded the source code for the bot. Run the following line to install all of the dependencies: `pip install -r requirements.txt`
 5. Now you can run the **main.py** file through the conda environment using `python main.py`

Feel free to use the code for your own projects!

## Preview
![Image](https://github.com/skyksl066/AutoHarvestHome/raw/main/docs/images/cmd.png?raw=true)
![Image](https://github.com/skyksl066/AutoHarvestHome/raw/main/docs/images/main.png?raw=true)
