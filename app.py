import streamlit as st
import time
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os

# Initialize MediaPipe Pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

# Function to extract keypoints
def get_keypoints_from_frame(frame):
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    if results.pose_landmarks:
        keypoints = np.array([(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark])
        return keypoints
    return None

# Compare user keypoints with a reference pose
def compare_keypoints(user_keypoints, reference_keypoints, threshold=0.1):
    diff = np.linalg.norm(user_keypoints - reference_keypoints)
    return diff < threshold, diff

# Generate feedback based on difference score
def generate_feedback(diff_score):
    if diff_score < 0.05:
        return "✅ Perfect Form!"
    elif diff_score < 0.15:
        return "⚠️ Good, but minor improvements needed."
    else:
        return "❌ Needs Improvement! Check posture."

# Streamlit UI
st.title("🏋️ Exercise Form Checker")
st.write("Upload a workout video, and AI will analyze your form!")

uploaded_video = st.file_uploader("Upload your workout video", type=["mp4", "mov", "avi"])

feedback_results = []  # Store feedback

if uploaded_video:
    # Save uploaded file to a temporary location
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_video.read())
    video_path = tfile.name

    # Open video file and extract frames
    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        frames.append(frame)
    cap.release()

    st.write(f"Extracted {len(frames)} frames for analysis.")

    # Process frames to extract keypoints
    keypoints_list = [get_keypoints_from_frame(frame) for frame in frames if get_keypoints_from_frame(frame) is not None]

    if keypoints_list:
        reference_keypoints = keypoints_list[0]  # Use first frame as reference

        for idx, user_keypoints in enumerate(keypoints_list[:5]):  # Analyze first 5 frames
            _, diff_score = compare_keypoints(user_keypoints, reference_keypoints)
            feedback = generate_feedback(diff_score)
            feedback_results.append(f"Frame {idx+1}: {feedback}")

        st.subheader("💡 Feedback on Your Form:")
        for feedback in feedback_results:
            st.write(feedback)

        st.success("✅ Form analysis complete!")

    else:
        st.error("No valid keypoints detected in video. Try another video.")

# ----------------- 💬 Chat-Based Exercise Feedback -----------------
st.subheader("💬 Chat-Based Exercise Feedback")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message("assistant"):
        st.write(message)

if feedback_results:
    for idx, feedback in enumerate(feedback_results[:5]):  # First 5 feedbacks
        message = feedback
        st.session_state.chat_history.append(message)
        time.sleep(0.5)  # Simulate a slight delay for chat effect
        with st.chat_message("assistant"):
            st.write(message)

user_input = st.text_input("Ask about your form:")

if user_input:
    response = "Try keeping your core engaged and back straight." if "improve" in user_input.lower() else "You’re doing great! Keep it up!"
    st.session_state.chat_history.append(f"You: {user_input}")
    st.session_state.chat_history.append(f"AI Trainer: {response}")

    with st.chat_message("user"):
        st.write(user_input)
    with st.chat_message("assistant"):
        st.write(response)
