from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import mediapipe as mp
import json
import time

app = Flask(__name__)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

def count_fingers(hand_landmarks, hand_type):
    # Get finger tip and pip landmarks
    finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
    finger_pips = [2, 6, 10, 14, 18]  # Corresponding PIP joints
    
    count = 0
    
    # Get the wrist landmark for reference
    wrist = hand_landmarks.landmark[0]
    
    # Check each finger
    for tip, pip in zip(finger_tips, finger_pips):
        tip_landmark = hand_landmarks.landmark[tip]
        pip_landmark = hand_landmarks.landmark[pip]
        
        if tip == 4:  # Thumb
            # For thumb, check based on hand type
            if hand_type == "Right":
                if tip_landmark.x < pip_landmark.x:  # Right hand thumb extended
                    count += 1
            else:  # Left hand
                if tip_landmark.x > pip_landmark.x:  # Left hand thumb extended
                    count += 1
        else:  # Other fingers
            # For other fingers, check if they're extended upward
            if tip_landmark.y < pip_landmark.y:
                count += 1
    
    return count

def generate_frames():
    cap = cv2.VideoCapture(0)
    
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            
            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)
            
            # Convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = hands.process(frame_rgb)
            
            total_count = 0
            left_count = 0
            right_count = 0
            
            # Draw hand landmarks and count fingers
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Get hand position (left or right)
                    hand_type = results.multi_handedness[idx].classification[0].label
                    
                    # Draw landmarks with different colors for each hand
                    color = (0, 255, 0) if hand_type == "Right" else (255, 0, 0)
                    mp_draw.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        mp_hands.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(color=color, thickness=2, circle_radius=4),
                        mp_draw.DrawingSpec(color=color, thickness=2)
                    )
                    
                    # Count fingers for this hand
                    finger_count = count_fingers(hand_landmarks, hand_type)
                    
                    # Update counts
                    if hand_type == "Right":
                        right_count = finger_count
                    else:
                        left_count = finger_count
                    
                    total_count += finger_count
            
            # Convert back to BGR for display
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()

def generate_counts():
    cap = cv2.VideoCapture(0)
    
    try:
        while True:
            success, frame = cap.read()
            if not success:
                break
            
            # Flip the frame horizontally
            frame = cv2.flip(frame, 1)
            
            # Convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = hands.process(frame_rgb)
            
            total_count = 0
            left_count = 0
            right_count = 0
            
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    hand_type = results.multi_handedness[idx].classification[0].label
                    finger_count = count_fingers(hand_landmarks, hand_type)
                    
                    if hand_type == "Right":
                        right_count = finger_count
                    else:
                        left_count = finger_count
                    
                    total_count += finger_count
            
            # Send the counts as SSE
            data = {
                'left': left_count,
                'right': right_count,
                'total': total_count
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.1)  # Small delay to prevent overwhelming the client
            
    finally:
        cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/count_feed')
def count_feed():
    return Response(
        generate_counts(),
        mimetype='text/event-stream'
    )

if __name__ == '__main__':
    app.run(debug=True) 