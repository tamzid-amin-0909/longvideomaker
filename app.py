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

    /* PREMIUM DOWNLOAD BUTTON UI */
    div.stDownloadButton > button {
        width: 100%;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border-radius: 1.25rem !important;
        padding: 22px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.15em !important;
        border: none !important;
        box-shadow: 0 15px 35px rgba(79, 70, 229, 0.4) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }

    div.stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 20px 45px rgba(79, 70, 229, 0.5) !important;
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
        <div class="icon-box"><i class="fas fa-video" style="color:white; font-size: 24px;"></i></div>
        <h1 class="main-title">Video Render</h1>
        <p class="sub-title">Professional Static Processing</p>
    </div>
    """, unsafe_allow_html=True)

# Helper function for Auto-Download
def trigger_auto_download(file_path, file_name):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    dl_link = f"""
    <script>
    var link = document.createElement('a');
    link.href = 'data:video/mp4;base64,{b64}';
    link.download = '{file_name}';
    link.dispatchEvent(new MouseEvent('click'));
    </script>
    """
    st.components.v1.html(dl_link, height=0)

# Create temp directory
if not os.path.exists("temp"):
    os.makedirs("temp")

# --- UI Layout ---
with st.container():
    # 1. Image Upload & Preview
    uploaded_file = st.file_uploader("Upload Frame Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
        img_path = os.path.join("temp", "input.jpg")
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    else:
        st.markdown("""
            <div style="height: 128px; width: 100%; background: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 1rem; display: flex; align-items: center; justify-content: center; flex-direction: column; color: #94a3b8;">
                <i class="fas fa-image" style="font-size: 24px; margin-bottom: 8px;"></i>
                <span style="font-size: 10px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.1em;">No Image Loaded</span>
            </div>
        """, unsafe_allow_html=True)

    # 2. Inputs
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase;'>Duration (Seconds)</label>", unsafe_allow_html=True)
        duration = st.number_input("Duration", min_value=1, value=3600, label_visibility="collapsed")
    with col2:
        st.markdown("<label style='font-size: 10px; font-weight: 900; color: #4f46e5; text-transform: uppercase;'>Time</label>", unsafe_allow_html=True)
        readable_time = str(timedelta(seconds=duration))
        st.markdown(f"<div style='font-weight: bold; color: #4f46e5; padding-top: 5px;'>{readable_time}</div>", unsafe_allow_html=True)

    st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase;'>Output Filename</label>", unsafe_allow_html=True)
    custom_name = st.text_input("Filename", value="render_output", label_visibility="collapsed")

    # 3. Generate Button
    if st.button("Start Rendering"):
        if not uploaded_file:
            st.error("Please upload an image first!")
        else:
            output_path = os.path.join("temp", f"{custom_name}.mp4")
            
            with st.status("Encoding at light speed...", expanded=True) as status:
                cmd = [
                    "ffmpeg", "-y", "-loop", "1", "-framerate", f"1/{duration}",
                    "-i", "temp/input.jpg", "-c:v", "libx264", "-t", str(duration),
                    "-pix_fmt", "yuv420p", "-r", f"1/{duration}", output_path
                ]
                
                subprocess.run(cmd, capture_output=True)
                status.update(label="Render Complete!", state="complete", expanded=False)
            
            # 4. Download Area & Auto-Download
            if os.path.exists(output_path):
                # Auto-Download Trigger
                trigger_auto_download(output_path, f"{custom_name}.mp4")
                
                # Premium Manual Download Button
                with open(output_path, "rb") as f:
                    st.download_button(
                        label=f"📥 SAVE {custom_name.upper()}.MP4",
                        data=f,
                        file_name=f"{custom_name}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                st.balloons()

# --- Deploy Checklist ---
# 1. requirements.txt -> streamlit
# 2. packages.txt -> ffmpeg
