# Thesis Code

This repository contains various code snippets and scripts used for my master thesis. All code is written in Python and organized into the following main folders:

## Folder Structure

The following main folders are included in this repository. Each folder contains its own `README.md` with specific instructions and details.

- `dataset/` — Code to create the custom dataset used for the study.
- `evaluation/` — Scripts for evaluating the results of the study and generating plots.
- `task-server/` - Tool used to provide the maths problems to participants during the study.

## Python Environment

A single, shared Python environment is used for all code in this repository. The recommended version is **Python 3.12** (see below for setup instructions).

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

## NextJS Application

The `task-server` folder contains a NextJS application used to serve the maths problems to participants during the study. It was created using [Bun](https://bun.sh) (version `v1.2.18`) and the application was bootstrapped with the command `bun create next` command.

To set up and run the NextJS application, follow these steps:

1. **Navigate to the task-server directory:**
   ```sh
   cd task-server
   ```

2. **Install Node.js dependencies:**
   ```sh
   bun install
   ```

3. **Run the NextJS application:**
   ```sh
   bun run dev
   ```

## Included Libraries

For archival purposes, the libraries used are committed to this project including the relevant `venv`. These installations were performed using an M4 MacBook Pro running macOS Tahoe 26.0.1 with Python 3.12.12. Due to the differences in architecture and operating systems, Python packages might not work as expected on non-Apple Silicon Macs or non-ARM architectures.

**Compatibility on Windows or x86 architectures is not guaranteed.**

## Notes

- Make sure to activate the virtual environment before running any scripts.
- The NextJS application was created using Bun, but it should be compatible with Node.js and Deno as well.
- Significant portions of the code for the task server were written using GitHub Copilot
