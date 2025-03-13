import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

# Function to extract keypoints
def get_keypoints_from_frame(frame):
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    if results.pose_landmarks:
        keypoints = np.array([(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark])
        return keypoints
    else:
        return None

# Function to extract frames from video
def extract_frames(video_path, interval=1):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    count = 0
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        if count % int(fps * interval) == 0:
            frames.append(frame)
        count += 1
    cap.release()
    return frames

# Function to compare keypoints
def compare_keypoints(user_keypoints, reference_keypoints, threshold=0.1):
    diff = np.linalg.norm(user_keypoints - reference_keypoints)
    return diff < threshold, diff

# Function to generate feedback
def generate_feedback(diff_score):
    if diff_score < 0.05:
        return "✅ Perfect Form!"
    elif diff_score < 0.15:
        return "⚠️ Good, but minor improvements needed."
    else:
        return "❌ Needs Improvement! Check posture."

# Streamlit UI
st.title("🏋️ Exercise Form Checker")
st.write("Upload a workout video, and get AI-powered feedback on your form.")

# Upload Video
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())

    # Extract frames from the video
    frames = extract_frames(video_path, interval=1)
    
    if frames:
        st.image(frames[0], caption="Extracted Frame for Analysis", use_column_width=True)

        # Extract keypoints
        keypoints_list = [get_keypoints_from_frame(frame) for frame in frames if get_keypoints_from_frame(frame) is not None]

        if keypoints_list:
            reference_keypoints = keypoints_list[0]  # First frame as reference
            feedback_list = []
            for user_keypoints in keypoints_list:
                is_correct, diff_score = compare_keypoints(user_keypoints, reference_keypoints)
                feedback_list.append(generate_feedback(diff_score))

            # Display feedback
            st.subheader("💬 Feedback on Your Form")
            for i, feedback in enumerate(feedback_list[:5]):  # Show feedback for first 5 frames
                st.write(f"Frame {i+1}: {feedback}")
        else:
            st.warning("No keypoints detected. Please try another video.")
    else:
        st.warning("No frames extracted from the video. Please upload a valid workout video.")
