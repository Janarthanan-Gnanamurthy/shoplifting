from roboflow import Roboflow
from config import *


# Roboflow config
USE_ROBOFLOW = True
ROBOFLOW_API_KEY = "cJeZnj4wrGxLXIrwBmii"
ROBOFLOW_WORKSPACE = "fastnuces-uakqb"
ROBOFLOW_PROJECT = "fyp-shoplift"
ROBOFLOW_VERSION = 1




def download_roboflow_dataset():
    rf = Roboflow(api_key=ROBOFLOW_API_KEY)
    project = rf.workspace(ROBOFLOW_WORKSPACE).project(ROBOFLOW_PROJECT)
    version = project.version(ROBOFLOW_VERSION)

    dataset = version.download("yolov11")

    return (
        f"{dataset.location}/train/images",
        f"{dataset.location}/valid/images",
    )
