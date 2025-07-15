import os
import json
from pathlib import Path
from ultralytics import YOLO

# --- Configurable paths ---
IMAGE_DIR = Path("data/images")  # This includes subfolders like '2025-07-10'
ANNOTATED_DIR = Path("data/annotated")
OUTPUT_JSON = Path("data/yolo_detections.json")

# --- Create output directory if needed ---
ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

# --- Load YOLOv8 model ---
model = YOLO("yolov8n.pt")  # You can change to yolov8s.pt or yolov8m.pt if needed

# --- Supported extensions ---
EXTENSIONS = [".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"]

# --- Find images recursively ---
image_paths = [p for p in IMAGE_DIR.rglob("*") if p.suffix in EXTENSIONS]
print(f"✅ Found {len(image_paths)} image(s) in {IMAGE_DIR}")

# --- If no images found, raise an error ---
if not image_paths:
    raise FileNotFoundError(
        f"No image files found in {IMAGE_DIR}. "
        "Make sure your Telegram images are in this folder or its subfolders."
    )

# --- Detection results dictionary ---
all_detections = {}

# --- Run YOLOv8 on each image ---
for img_path in image_paths:
    try:
        print(f"🔍 Processing {img_path.name}")

        results = model.predict(
            source=str(img_path),
            save=True,
            project=str(ANNOTATED_DIR),
            name="",
            conf=0.25
        )

        detections = []
        for result in results:
            for box in result.boxes:
                detection = {
                    "class": model.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": [float(x) for x in box.xyxy[0].tolist()]
                }
                detections.append(detection)

        all_detections[img_path.name] = detections

    except Exception as e:
        print(f"⚠️ Skipping {img_path.name} due to error: {e}")

# --- Save all detections to a JSON file ---
with open(OUTPUT_JSON, "w") as f:
    json.dump(all_detections, f, indent=4)

print(f"\n✅ YOLO detection complete!")
print(f"📁 Detections saved to: {OUTPUT_JSON}")
print(f"🖼️ Annotated images saved to: {ANNOTATED_DIR}")
