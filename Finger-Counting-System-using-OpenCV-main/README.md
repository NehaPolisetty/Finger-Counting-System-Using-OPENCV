# Finger Counting System

A real-time finger counting system using computer vision and web technologies. This project uses OpenCV and MediaPipe for hand detection and finger counting, with a modern web interface built using HTML, CSS, and Tailwind CSS.

## Features

- Real-time webcam hand detection
- Accurate finger counting
- Modern and responsive UI
- Multiple hand gesture support

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Click the "Start Counting" button on the landing page
2. Allow webcam access when prompted
3. Show your hand to the camera
4. The system will detect your hand and count the number of fingers shown

## Technologies Used

- Python
- OpenCV
- MediaPipe
- Flask
- HTML/CSS
- Tailwind CSS
- JavaScript

## Requirements

- Python 3.7+
- Webcam
- Modern web browser