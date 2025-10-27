# Task Server

This project contains the code for the Next.js application used as the task server during the experiments. It is built on [Next.js](https://nextjs.org). Running the application requires a JavaScript runtime such as [Bun](https://bun.sh/) or [Node.js](https://nodejs.org/). This the project was created using [Bun](https://bun.sh) (version `v1.3.0`) and the examples will use Bun commands, but the project can also be run in Node.js.

## Getting Started

To get started with the task server, follow these steps:

1. **Copy the json file and images from the `dataset` folder**

   Ensure that you have the necessary dataset files in the `public` directory of the `task-server` folder. You can copy them from the `dataset` folder in the root of the repository:

   ```bash
   cp ../dataset/out/filtered_dataset.json ./data/
   cp -r ../dataset/out/images ./public/
   ```
2. **Install dependencies:**
   ```bash
   bun install
   ```
3. **Run the development server:**
   ```bash
   bun dev
   ```
4. **Open the application:**
   Visit [http://localhost:3000](http://localhost:3000) in your browser.

## Functionality

The application provides a user interface for participants to solve maths problems. It loads problems from a JSON file and displays them along with any associated images. Participants can submit their answers, which are then recorded for later analysis.

The home screen contains several buttons for different functionalities:

- Buttons to load specific example tasks (not used in the study) for demonstration purposes.
- A button to start a task set that was used during the study.

Below the buttons is an area where past results are displayed, showing the participant ID, task set ID and a link to detailed results. Result storage is handled locally on the hosts file system in the `data/solutions/` folder.
