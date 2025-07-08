"""
This script filters the MathVista dataset to include only items with specific 'pid' values and saves the filtered dataset to disk.

Steps:
1. Load the MathVista dataset using the Hugging Face datasets library.
2. Define a list of selected item IDs (pids) to filter.
3. Filter the dataset to include only items whose 'pid' is in the selected list.
4. Save the filtered dataset to the 'data/filtered_dataset' directory.
5. Save images to 'data/images' and the rest of the data as CSV, linking images by pid.
"""

from datasets import load_dataset

# List of selected item IDs (pids) to filter from the dataset
selected_item_ids = ["54", "273", "280", "318", "355", "455", "478", "505", "549", "599", "669", "690", "708", "798", "855"]

# Load the MathVista dataset
ds = load_dataset("AI4Math/MathVista", split="testmini")
