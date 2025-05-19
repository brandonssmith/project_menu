# Cursor Projects Menu

A simple menu application to manage and launch your Cursor projects.

## Features

- Automatically lists all projects from your project code directory
- Double-click to launch projects
- Supports Python, Node.js, and other project types
- Modern and clean user interface
- Mouse hover shows description information from README
- Follow-up provided for Node and other projects which require a browser launch

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python menu_app.py
```

## Building the Executable

To create a standalone executable:

```bash
pyinstaller --onefile --windowed menu_app.py
```

The executable will be created in the `dist` directory.

## Usage

1. Launch the application
2. Browse through your projects in the list
3. Double-click any project to launch it
4. The application will automatically detect the project type and launch it appropriately

## Project Detection

The application will automatically detect:
- Python projects (looks for .py files or requirements.txt)
- Node.js projects (looks for package.json)
- Other project types (attempts to find and run the main file) 