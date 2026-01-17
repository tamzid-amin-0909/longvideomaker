import streamlit as st
import os
import base64
import subprocess
from datetime import timedelta

# --- Page Config ---
st.set_page_config(page_title="Video Render Pro", layout="centered")

# --- Perfect UI Styling ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); }
    
    /* The Main Card */
    [data-testid="stVerticalBlock"] > div:has(.main-card) {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(15px);
        border-radius: 2.5rem;
        padding: 40px;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.1);
        border: 1px solid white;
    }

    /* Modern Image Opener Trick */
    .upload-container {
        position: relative;
        height: 160px;
        width: 100%;
        background: #f8fafc;
        border: 2px dashed #cbd5e1;
        border-radius: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        color: #64748b;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .upload-container:hover {
        border-color: #4f46e5;
        background: #f1f5ff;
        color: #4f46e5;
    }

    /* Hide the actual ugly streamlit uploader but keep it clickable */
    [data-testid="stFileUploader"] {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0;
        z-index: 10;
        cursor: pointer;
    }
    [data-testid="stFileUploaderSection"] { padding: 0; }

    /* Inputs */
    input { border-radius: 1rem !important; border: none !important; background: #f1f5f9 !important; font-weight: 700 !important; }

    /* Modern Buttons */
    div.stButton > button, div.stDownloadButton > button {
        width: 100%;
        background: #0f172a !important;
        color: white !important;
        border-radius: 1.25rem !important;
        padding: 20px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        border: none !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background: #4f46e5 !important;
        transform: translateY(-2px);
    }

    /* Download Specific Styling */
    div.stDownloadButton > button {
        background: linear-gradient(90deg, #4f46e5, #6366f1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }

    .main-title { color: #1e293b; font-weight: 900; font-size: 2.25rem; text-align: center; margin-bottom: 0; }
    .sub-title { color: #64748b; text-align: center; font-size: 0.875rem; margin-bottom: 2rem; }
    .icon-box { background: #4f46e5; width: 64px; height: 64px; border-radius: 1.25rem; display: flex; align-items: center; justify-content: center; margin: 0 auto 1.5rem auto; }
    </style>
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <div class="main-card">
        <div class="icon-box"><i class="fas fa-bolt" style="color:white; font-size: 24px;"></i></div>
        <h1 class="main-title">Video Render</h1>
        <p class="sub-title">Ultra-Fast Static Processing</p>
    </div>
    """, unsafe_allow_html=True)

if not os.path.exists("temp"):
    os.makedirs("temp")

# --- UI Layout ---
with st.container():
    # 1. Image Opener Section
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        # Display Preview
        st.image(uploaded_file, use_container_width=True)
        img_path = os.path.join("temp", "input.jpg")
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.markdown('<div style="text-align:center; font-size:10px; font-weight:900; color:#4f46e5; margin-top:10px;">READY TO RENDER</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <i class="fas fa-cloud-upload-alt" style="font-size: 32px; margin-bottom: 12px; color: #4f46e5;"></i>
            <span style="font-size: 11px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.1em;">Click to Open Image</span>
            <span style="font-size: 9px; color: #94a3b8; margin-top: 5px;">JPG, PNG or JPEG</span>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("") # Spacer

    # 2. Inputs Row
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase; margin-left: 5px;'>Duration (Seconds)</label>", unsafe_allow_html=True)
        duration = st.number_input("Duration", min_value=1, value=3600, label_visibility="collapsed")
    with col2:
        st.markdown("<label style='font-size: 10px; font-weight: 900; color: #4f46e5; text-transform: uppercase;'>Total Time</label>", unsafe_allow_html=True)
        readable_time = str(timedelta(seconds=duration))
        st.markdown(f"<div style='font-weight: 900; color: #4f46e5; font-size: 18px;'>{readable_time}</div>", unsafe_allow_html=True)

    st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase; margin-left: 5px;'>Output Filename</label>", unsafe_allow_html=True)
    custom_name = st.text_input("Filename", value="render_output", label_visibility="collapsed")

    # 3. Generate Logic
    if st.button("Start Rendering"):
        if not uploaded_file:
            st.error("Select an image first!")
        else:
            output_path = os.path.join("temp", f"{custom_name}.mp4")
            with st.status("Encoding...", expanded=False) as status:
                cmd = [
                    "ffmpeg", "-y", "-loop", "1", "-framerate", f"1/{duration}",
                    "-i", "temp/input.jpg", "-c:v", "libx264", "-t", str(duration),
                    "-pix_fmt", "yuv420p", "-r", f"1/{duration}", output_path
                ]
                subprocess.run(cmd, capture_output=True)
                status.update(label="Render Finished!", state="complete")
            
            st.session_state.ready = True
            st.session_state.file = output_path

    # 4. Modern Download UI
    if 'ready' in st.session_state and os.path.exists(st.session_state.file):
        st.write("") 
        with open(st.session_state.file, "rb") as f:
            st.download_button(
                label=f"📥 Download {custom_name.upper()}.MP4",
                data=f,
                file_name=f"{custom_name}.mp4",
                mime="video/mp4",
                use_container_width=True
            )
