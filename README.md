# Thesis Code

This repository contains various code snippets and scripts used for my master thesis. All code is written in Python and organized into the following main folders:

## Folder Structure

- `dataset/` — Code to create the custom dataset used for the study.
- `evaluation/` — Scripts for evaluating the results of the study and generating plots.
- `task-server` - Tool used to provide the maths problems to participants during the study.

## Python Environment

A single, shared Python environment is used for all code in this repository. The recommended version is **Python 3.13+** (see below for setup instructions).

All dependencies are listed in `requirements.txt` at the root of the repository. This ensures a consistent environment for running all scripts.

## Setup Guide

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd thesis-code
   ```

2. **Create a virtual environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Run scripts:**
   You can now run scripts from any folder using the shared environment. For example:
   ```sh
   python dataset/main.py
   ```

## Notes

- Make sure to activate the virtual environment before running any scripts.
- If you add new dependencies, run `pip freeze > requirements.txt` to update the requirements file.
