#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced MediaPipe Pose Detection for Tkinter GUI
"""

import cv2
import mediapipe as mp
import numpy as np
import time  
import datetime
import os

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Create directory for saved images
if not os.path.exists('saved_images'):
    os.makedirs('saved_images')

def calculate_angle(a, b, c):
    """Calculate the angle between three points"""
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def save_pose_image(image, counter=0):
    """Save the current frame with pose detection overlay"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"saved_images/pose_detection_{timestamp}_rep_{counter}.jpg"
    success = cv2.imwrite(filename, image)
    if success:
        print(f"✓ POSE IMAGE SAVED: {filename}")
        return filename
    else:
        print(f"✗ FAILED TO SAVE: {filename}")
        return None

def run_pose_detection(cam_index=0):
    """Main pose detection function with enhanced features"""
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print(f"Error: Could not open camera {cam_index}")
        # Try default camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open any camera")
            return
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Curl counter variables
    counter = 0
    stage = None
    last_save_time = 0
    save_cooldown = 1  # seconds between saves
    
    print("=" * 50)
    print("MediaPipe Pose Detection Started!")
    print("Press 'S' to save image with pose detection")
    print("Press 'Q' to quit")
    print("=" * 50)
    
    with mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to capture frame")
                break
                
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Make detection
            results = pose.process(image)
            
            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Extract landmarks and calculate angles
            try:
                landmarks = results.pose_landmarks.landmark
                
                # Get coordinates for left arm
                shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, 
                           landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, 
                        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, 
                        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                
                # Calculate angle
                angle = calculate_angle(shoulder, elbow, wrist)
                
                # Visualize angle
                cv2.putText(image, f"{angle:.1f}°", 
                           tuple(np.multiply(elbow, [image.shape[1], image.shape[0]]).astype(int)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                
                # Curl counter logic
                if angle > 160:
                    stage = "down"
                if angle < 30 and stage == 'down':
                    stage = "up"
                    counter += 1
                    print(f"Rep count: {counter}")
                    
            except Exception as e:
                # Continue without landmarks if detection fails
                pass
            
            # Render pose detections
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, 
                    results.pose_landmarks, 
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2), 
                    mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                )
            
            # Status box
            cv2.rectangle(image, (0, 0), (350, 120), (245, 117, 16), -1)
            
            # Rep data
            cv2.putText(image, 'REPS', (15, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(counter), (15, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Stage data
            cv2.putText(image, 'STAGE', (120, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, stage or "N/A", (120, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Angle data
            try:
                cv2.putText(image, 'ANGLE', (250, 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(image, f"{angle:.1f}°", (250, 80), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
            except:
                pass
            
            # Save instructions
            cv2.putText(image, "Press 'S' to SAVE image with pose detection", 
                       (10, image.shape[0] - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, "Press 'Q' to QUIT", 
                       (10, image.shape[0] - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Display image
            cv2.imshow('MediaPipe Pose Detection - Press S to Save', image)
            
            # Handle key presses
            key = cv2.waitKey(10) & 0xFF
            current_time = time.time()
            
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('s') or key == ord('S'):
                # Cooldown to prevent multiple rapid saves
                if current_time - last_save_time > save_cooldown:
                    filename = save_pose_image(image, counter)
                    if filename:
                        # Show save confirmation on screen
                        cv2.putText(image, "✓ IMAGE SAVED!", 
                                   (image.shape[1]//2 - 120, 50), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                        cv2.imshow('MediaPipe Pose Detection - Press S to Save', image)
                        cv2.waitKey(500)  # Show confirmation for 500ms
                    last_save_time = current_time
                
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("MediaPipe Pose Detection Stopped")

# Legacy functions for backward compatibility
def simple_pose_detection():
    """Simple pose detection without counter (for testing)"""
    cap = cv2.VideoCapture(0)
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                break
                
            # Recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Make detection
            results = pose.process(image)
            
            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Render detections
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                    mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                )
            
            cv2.imshow('MediaPipe Feed', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

# Main execution
if __name__ == "__main__":
    # Test camera connection first
    print("Testing camera connection...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        if ret:
            print("Camera test: SUCCESS")
            # Run the enhanced pose detection
            run_pose_detection()
        else:
            print("Camera test: FAILED - Cannot read frames")
    else:
        print("Camera test: FAILED - Cannot open camera")
    
    print("Program ended")