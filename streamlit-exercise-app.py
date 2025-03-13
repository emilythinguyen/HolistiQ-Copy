import streamlit as st
import time
import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os
import random

# Initialize MediaPipe Pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

# Function to extract keypoints
def get_keypoints_from_frame(frame):
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    if results.pose_landmarks:
        keypoints = np.array([(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark])
        return keypoints, results.pose_landmarks
    return None, None

# Compare user keypoints with a reference pose
def compare_keypoints(user_keypoints, reference_keypoints, threshold=0.1):
    diff = np.linalg.norm(user_keypoints - reference_keypoints)
    return diff < threshold, diff

# Analyze specific body parts and generate detailed feedback
def analyze_pose(landmarks):
    feedback = {}
    
    # Check shoulder alignment
    left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
    
    if shoulder_diff > 0.05:
        feedback["shoulders"] = "Your shoulders aren't level. Try to keep them at the same height."
    
    # Check back posture
    left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    
    # Calculate angle between shoulder, hip, and knee
    angle = calculate_angle(
        (left_shoulder.x, left_shoulder.y),
        (left_hip.x, left_hip.y),
        (left_knee.x, left_knee.y)
    )
    
    if angle < 160:
        feedback["back"] = "Your back seems to be rounded. Try to maintain a neutral spine position."
    
    # Check knee alignment
    left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
    left_knee = landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
    left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    
    knee_angle = calculate_angle(
        (left_ankle.x, left_ankle.y),
        (left_knee.x, left_knee.y),
        (left_hip.x, left_hip.y)
    )
    
    if knee_angle < 90:
        feedback["knees"] = "Your knees are bending too much. This could put strain on your joints."
    
    return feedback

# Calculate angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    
    return np.degrees(angle)

# Generate personalized improvement suggestions
def generate_improvement_tips(body_part):
    tips = {
        "shoulders": [
            "Try pulling your shoulders back and down.",
            "Imagine balancing a book on your head to help level your shoulders.",
            "Focus on engaging your upper back muscles to stabilize your shoulders."
        ],
        "back": [
            "Engage your core muscles to support your spine.",
            "Think about creating a straight line from your head to your tailbone.",
            "Try the 'proud chest' cue - imagine showing off a superhero emblem on your chest."
        ],
        "knees": [
            "Keep your knees in line with your toes.",
            "Avoid letting your knees cave inward during exercises.",
            "Try to keep a slight bend in your knees rather than locking them out completely."
        ],
        "hips": [
            "Focus on keeping your hips level during the movement.",
            "Engage your glutes to stabilize your hip position.",
            "Try to prevent your hips from rotating or tilting forward."
        ]
    }
    
    return random.choice(tips.get(body_part, ["Focus on maintaining proper form throughout the exercise."]))

# Streamlit UI
st.title("🏋️ Exercise Form Checker")
st.write("Upload a workout video, and your AI trainer will analyze your form!")

uploaded_video = st.file_uploader("Upload your workout video", type=["mp4", "mov", "avi"])

# Initialize session state for chat
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
    
if "pose_feedback" not in st.session_state:
    st.session_state.pose_feedback = {}

if uploaded_video and not st.session_state.analysis_complete:
    with st.spinner("Analyzing your form..."):
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

        # Process frames to extract keypoints
        all_feedback = {}
        for frame_idx, frame in enumerate(frames[::10]):  # Sample every 10th frame
            if frame_idx >= 10:  # Limit to 10 sampled frames for performance
                break
                
            keypoints, landmarks = get_keypoints_from_frame(frame)
            if keypoints is not None and landmarks is not None:
                frame_feedback = analyze_pose(landmarks)
                for part, feedback in frame_feedback.items():
                    if part not in all_feedback:
                        all_feedback[part] = 0
                    all_feedback[part] += 1
        
        # Keep only feedback that appears in multiple frames
        significant_feedback = {part: count for part, count in all_feedback.items() if count > 2}
        st.session_state.pose_feedback = significant_feedback
        
        # Add initial greeting to chat
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": "👋 Hi there! I've analyzed your workout video. Let me give you some feedback on your form."
        })
        
        # Add feedback messages to chat
        if significant_feedback:
            time.sleep(1)
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": "I noticed a few things we could work on to improve your form:"
            })
            
            for part in significant_feedback:
                time.sleep(1)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": f"• {generate_improvement_tips(part)}"
                })
                
            time.sleep(1)
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": "Do you want more specific tips on any of these areas? Feel free to ask!"
            })
        else:
            time.sleep(1)
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": "Your form looks pretty good! Keep it up! 💪 Feel free to ask if you need any tips to maintain good form."
            })
            
        st.session_state.analysis_complete = True
        
        # Remove the temporary file
        os.unlink(video_path)

# Display chat interface
st.subheader("💬 Chat with your AI Trainer")

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Chat input
if user_input := st.chat_input("Ask your AI trainer a question about your form..."):
    # Add user message to chat
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Generate response based on user input and previous analysis
    response = ""
    
    # Check if the user is asking about specific body parts
    lower_input = user_input.lower()
    if "shoulder" in lower_input:
        response = generate_improvement_tips("shoulders")
    elif "back" in lower_input:
        response = generate_improvement_tips("back")
    elif "knee" in lower_input:
        response = generate_improvement_tips("knees")
    elif "hip" in lower_input:
        response = generate_improvement_tips("hips")
    elif any(keyword in lower_input for keyword in ["overall", "general", "form", "posture"]):
        if st.session_state.pose_feedback:
            parts = list(st.session_state.pose_feedback.keys())
            if parts:
                response = f"Overall, focus on your {', '.join(parts[:-1]) + ' and ' + parts[-1] if len(parts) > 1 else parts[0]}. "
                response += "Remember to breathe properly and move with control rather than momentum."
            else:
                response = "Your overall form looks good! Focus on maintaining consistent form throughout your workout."
        else:
            response = "Your overall form looks good! Focus on keeping your movements controlled and maintaining proper breathing throughout."
    elif any(keyword in lower_input for keyword in ["improve", "better", "enhance", "tips", "advice"]):
        if st.session_state.pose_feedback:
            part = random.choice(list(st.session_state.pose_feedback.keys()))
            response = f"To improve your form, try this: {generate_improvement_tips(part)}"
        else:
            response = "To keep improving, focus on consistency and gradually increasing intensity. Make sure to warm up properly before each workout!"
    else:
        response = "I'm here to help with your exercise form! Could you clarify which aspect of your form you'd like feedback on?"
    
    # Add assistant response to chat
    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.write(response)

# Reset button
if st.button("Reset Analysis"):
    st.session_state.chat_messages = []
    st.session_state.analysis_complete = False
    st.session_state.pose_feedback = {}
    st.rerun()
