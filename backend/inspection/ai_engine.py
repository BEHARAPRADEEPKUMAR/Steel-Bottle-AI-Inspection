from pathlib import Path
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"

BOTTLE_MODEL_PATH = MODELS_DIR / "bottle_detector_best.pt"
DEFECT_MODEL_PATH = MODELS_DIR / "defect_detector_best.pt"


print("Bottle model:", BOTTLE_MODEL_PATH)
print("Defect model:", DEFECT_MODEL_PATH)


bottle_model = YOLO(str(BOTTLE_MODEL_PATH))
defect_model = YOLO(str(DEFECT_MODEL_PATH))


print("Bottle detector loaded successfully")
print("Defect detector loaded successfully")