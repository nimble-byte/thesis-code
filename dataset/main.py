from datasets import load_dataset
import os
import csv
import json

selected_item_ids = [
    "54",
    "273",
    "280",
    "318",
    "355",
    "455",
    "478",
    "505",
    "549",
    "599",
    "669",
    "690",
    "708",
    "798",
    "855",
]

ds = load_dataset("AI4Math/MathVista", split="testmini")

output_csv_path = os.path.join(os.getcwd(), "dataset", "data/filtered_dataset.csv")
images_dir = os.path.join(os.getcwd(), "dataset", "data/images")
os.makedirs(images_dir, exist_ok=True)

csv_columns = [
    "pid",
    "question",
    "image",
    "choices",
    "answer",
    "img_height",
    "img_width",
]

filtered_rows = []

for item in ds:
    if item["pid"] in selected_item_ids:
        image_filename = f"{item['pid']}.png"
        image_path = os.path.join(images_dir, image_filename)
        image = item["decoded_image"]
        image.save(image_path)

        row = {
            "pid": item["pid"],
            "question": item["question"],
            "image": image_filename,
            "choices": json.dumps(item["choices"]),
            "answer": item["answer"],
            "img_height": item["metadata"]["img_height"],
            "img_width": item["metadata"]["img_width"],
        }
        filtered_rows.append(row)

with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for row in filtered_rows:
        writer.writerow(row)
