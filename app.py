import streamlit as st
import os
import base64
import subprocess
from datetime import timedelta

# --- Page Config ---
st.set_page_config(page_title="Video Render Pro", layout="centered")

# --- Perfect UI Styling (Tailwind-like) ---
st.markdown("""
    <style>
    /* Background and Global */
    .stApp {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    }
    
    /* The Main Card */
    [data-testid="stVerticalBlock"] > div:has(.main-card) {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        border-radius: 2.5rem;
        padding: 40px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        border: 1px solid white;
    }

    /* IMAGE OPENER HACK: Makes the whole box a clickable Image-Only trigger */
    .stFileUploader {
        position: absolute;
        inset: 0;
        opacity: 0;
        z-index: 20;
        cursor: pointer;
    }
    .stFileUploader section {
        padding: 0 !important;
    }

    /* Input Fields */
    input {
        border-radius: 1rem !important;
        border: none !important;
        background-color: #f8fafc !important;
        font-weight: bold !important;
        padding: 12px !important;
    }

    /* Main Button */
    div.stButton > button {
        width: 100%;
        background-color: #0f172a;
        color: white;
        border-radius: 1rem;
        padding: 18px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        border: none;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #4f46e5;
        transform: scale(0.98);
        color: white;
    }

    /* MODERN DOWNLOAD UI - Success Gradient */
    div.stDownloadButton > button {
        width: 100%;
        background: linear-gradient(90deg, #4f46e5, #6366f1) !important;
        color: white !important;
        border-radius: 1.25rem !important;
        padding: 22px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 15px 30px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    
    div.stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 20px 40px rgba(79, 70, 229, 0.4) !important;
    }

    /* Titles */
    .main-title {
        color: #1e293b;
        font-weight: 900;
        font-size: 2rem;
        text-align: center;
        letter-spacing: -0.025em;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #64748b;
        text-align: center;
        font-size: 0.875rem;
        margin-bottom: 2rem;
    }
    
    /* Icon */
    .icon-box {
        background: #4f46e5;
        width: 64px;
        height: 64px;
        border-radius: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
        box-shadow: 0 10px 20px rgba(79, 70, 229, 0.2);
    }
    </style>
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <div class="main-card">
        <div class="icon-box"><i class="fas fa-bolt" style="color:white; font-size: 24px;"></i></div>
        <h1 class="main-title">Video Render</h1>
        <p class="sub-title">Professional Static Processing</p>
    </div>
    """, unsafe_allow_html=True)

# Create temp directory
if not os.path.exists("temp"):
    os.makedirs("temp")

# --- UI Layout ---
with st.container():
    # 1. Image Upload & Preview Container
    # We create a relative container so the uploader can float on top
    st.markdown('<div style="position: relative; width: 100%;">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Select Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True, caption="Selected Image")
        img_path = os.path.join("temp", "input.jpg")
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    else:
        st.markdown("""
            <div style="height: 140px; width: 100%; background: #f8fafc; border: 2px dashed #4f46e5; border-radius: 1.5rem; display: flex; align-items: center; justify-content: center; flex-direction: column; color: #4f46e5; transition: 0.3s;">
                <i class="fas fa-camera" style="font-size: 32px; margin-bottom: 10px;"></i>
                <span style="font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.1em;">Open Image Picker</span>
                <span style="font-size: 9px; color: #94a3b8; margin-top: 4px;">Tap to select from photos</span>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("") # Spacer

    # 2. Inputs
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase; margin-left: 5px;'>Duration (Seconds)</label>", unsafe_allow_html=True)
        duration = st.number_input("Duration", min_value=1, value=3600, label_visibility="collapsed")
    with col2:
        st.markdown("<label style='font-size: 10px; font-weight: 900; color: #4f46e5; text-transform: uppercase;'>Render Length</label>", unsafe_allow_html=True)
        readable_time = str(timedelta(seconds=duration))
        st.markdown(f"<div style='font-weight: 900; color: #4f46e5; font-size: 1.1rem; padding-top: 2px;'>{readable_time}</div>", unsafe_allow_html=True)

    st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase; margin-left: 5px;'>Output Filename</label>", unsafe_allow_html=True)
    custom_name = st.text_input("Filename", value="render_output", label_visibility="collapsed")

    # 3. Generate Button
    if st.button("Start Rendering"):
        if not uploaded_file:
            st.error("Please select an image first!")
        else:
            output_path = os.path.join("temp", f"{custom_name}.mp4")
            
            with st.status("Encoding at light speed...", expanded=False) as status:
                cmd = [
                    "ffmpeg", "-y", "-loop", "1", "-framerate", f"1/{duration}",
                    "-i", "temp/input.jpg", "-c:v", "libx264", "-t", str(duration),
                    "-pix_fmt", "yuv420p", "-r", f"1/{duration}", output_path
                ]
                
                subprocess.run(cmd, capture_output=True)
                status.update(label="Render Finished!", state="complete")
            
            # Save the file path in session state so the download button stays visible
            st.session_state.file_ready = output_path

    # 4. Modern Download UI (Only shows after render)
    if 'file_ready' in st.session_state and os.path.exists(st.session_state.file_ready):
        st.markdown("<br>", unsafe_allow_html=True)
        with open(st.session_state.file_ready, "rb") as f:
            st.download_button(
                label=f"📥 Save {custom_name.upper()}.MP4",
                data=f,
                file_name=f"{custom_name}.mp4",
                mime="video/mp4",
                use_container_width=True
            )
        st.balloons()

# --- Deploy Checklist ---
# 1. requirements.txt -> streamlit
# 2. packages.txt -> ffmpeg
