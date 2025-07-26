from datasets import load_dataset
import os
import csv
import json

from task_metadata import selected_item_ids, task_difficulties, task_sets, task_translations

ds = load_dataset("AI4Math/MathVista", split="testmini")

output_csv_path = os.path.join(os.getcwd(), "dataset", "data/filtered_dataset.csv")
output_JSON_path = os.path.join(os.getcwd(), "dataset", "data/filtered_dataset.json")
images_dir = os.path.join(os.getcwd(), "dataset", "data/images")
os.makedirs(images_dir, exist_ok=True)

csv_columns = [
    "pid",
    "question",
    "translation",
    "image",
    "choices",
    "answer",
    "img_height",
    "img_width",
    "difficulty",
    "set",
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
            "translation": task_translations.get(item["pid"], "Keine Übersetzung verfügbar"),
            "image": image_filename,
            "choices": item['choices'],
            "answer": item["answer"],
            "img_height": item["metadata"]["img_height"],
            "img_width": item["metadata"]["img_width"],
            "difficulty": task_difficulties.get(item["pid"], "unknown"),
            "set": task_sets.get(item["pid"], "unknown"),
        }
        filtered_rows.append(row)

with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, delimiter=";", lineterminator="\n", fieldnames=csv_columns)
    writer.writeheader()
    for row in filtered_rows:
        writer.writerow(row)

with open(output_JSON_path, "w", encoding="utf-8") as jsonfile:
    json.dump(filtered_rows, jsonfile, ensure_ascii=False, indent=4)
