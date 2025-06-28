# Face Comparison Tool

This is a simple desktop GUI tool written in Python that uses facial recognition to compare a newly selected image against a folder of known images ("headshots"). If a match is found, it allows for manual review and renaming of the new image.

## Features

- Uses `face_recognition` to compare faces
- Graphical interface built with `tkinter`
- Displays matches side-by-side
- Allows renaming of matched image from the GUI
- Automatically saves unmatched images for future comparisons

## Requirements

- Python 3.7+
- Required packages:
  - `face_recognition`
  - `Pillow`
  - `uuid`
  - `tkinter` (included with standard Python installations)

## Installation

1. Clone the repository:
    git clone https://github.com/ashleypavey/face-comparison-tool.git
    cd face-comparison-tool

2. Install dependencies:
    pip install -r requirements.txt

3. Set the `HEADSHOT_FOLDER` and `DEFAULT_OPEN_PATH` variables in the script to your desired folder paths.

## Usage

1. Run the script:
    python face_comparison_tool.py

2. A window will open allowing you to select an image.

3. The tool compares the selected image to the known images in the headshot folder.

4. If matches are found, they will be shown in a scrollable window for manual review and optional renaming.

## Notes

- The `HEADSHOT_FOLDER` stores all known and new images.
- The script uses a UUID to avoid filename collisions when saving new images.
  
