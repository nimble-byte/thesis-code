# Dataset Preparation

This folder contains the code used to create the custom dataset for the study. The main script is `main.py`, which processes the MathVista dataset to filter and format the problems according to the study requirements.

## Getting Started

If you set up the repository wide Python environment as described in the main `README.md`, you can the script directly. If you haven't set up the environment yet, follow the steps outlined in the [main README](../README.md) first.

To run the dataset preparation script, use the following command from the `dataset` directory:

```sh
python ./main.py
```

This will generate a filtered dataset in both CSV and JSON formats, along with downloading the associated images into the `out/` directory.

> [!IMPORTANT]
> Please give the script some time to complete, as it needs to download the complete `testmini` split of the MathVista dataset and process each entry. It produces no console output.
