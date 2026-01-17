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
    input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 1rem !important;
        border: none !important;
        background-color: #f8fafc !important;
        font-weight: bold !important;
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
    
    .icon-box {
        background: #4f46e5;
        width: 64px;
        height: 64px;
        border-radius: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem auto;
    }
    </style>
    
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <div class="main-card">
        <div class="icon-box"><i class="fas fa-layer-group" style="color:white; font-size: 24px;"></i></div>
        <h1 class="main-title">Multi-Loop Render</h1>
        <p class="sub-title">Sync Images, GIFs & Video with Audio</p>
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
    link.href = 'data:application/octet-stream;base64,{b64}';
    link.download = '{file_name}';
    link.dispatchEvent(new MouseEvent('click'));
    </script>
    """
    st.components.v1.html(dl_link, height=0)

if not os.path.exists("temp"):
    os.makedirs("temp")

# --- UI Layout ---
with st.container():
    # 1. Visual Upload
    st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase;'>Visual Source (Image, GIF, Video)</label>", unsafe_allow_html=True)
    visual_file = st.file_uploader("Visual", type=["jpg", "png", "jpeg", "gif", "mp4", "mov"], label_visibility="collapsed")
    
    # 2. Audio Upload
    st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase;'>Optional Audio (Auto-loops to duration)</label>", unsafe_allow_html=True)
    audio_file = st.file_uploader("Audio", type=["mp3", "wav", "m4a", "aac"], label_visibility="collapsed")

    # 3. Parameters
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase;'>Total Duration (Sec)</label>", unsafe_allow_html=True)
        duration = st.number_input("Duration", min_value=1, value=10, label_visibility="collapsed")
    with col2:
        st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase;'>Output Format</label>", unsafe_allow_html=True)
        out_format = st.selectbox("Format", ["mp4", "gif"], label_visibility="collapsed")

    st.markdown("<label style='font-size: 10px; font-weight: 900; color: #94a3b8; text-transform: uppercase;'>Output Filename</label>", unsafe_allow_html=True)
    custom_name = st.text_input("Filename", value="render_output", label_visibility="collapsed")

    # 4. Generate Button
    if st.button("Start Processing"):
        if not visual_file:
            st.error("Please upload a visual file first!")
        else:
            vis_ext = visual_file.name.split(".")[-1].lower()
            vis_path = os.path.join("temp", f"input_v.{vis_ext}")
            output_path = os.path.join("temp", f"{custom_name}.{out_format}")
            
            with open(vis_path, "wb") as f:
                f.write(visual_file.getbuffer())

            is_image = vis_ext in ["jpg", "png", "jpeg"]
            
            with st.status("Mastering your loop...", expanded=True) as status:
                cmd = ["ffmpeg", "-y"]
                
                # Input Logic for Images vs Moving Media
                if is_image:
                    cmd += ["-loop", "1", "-i", vis_path]
                else:
                    cmd += ["-stream_loop", "-1", "-i", vis_path]
                
                # Audio Logic
                if audio_file:
                    aud_path = os.path.join("temp", "input_a.mp3")
                    with open(aud_path, "wb") as f:
                        f.write(audio_file.getbuffer())
                    cmd += ["-stream_loop", "-1", "-i", aud_path]

                # Duration and Encoding
                cmd += ["-t", str(duration)]

                if out_format == "mp4":
                    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p"]
                    if is_image:
                        cmd += ["-tune", "stillimage"] # Keep size tiny for images
                    
                    if audio_file:
                        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
                    else:
                        cmd += ["-an"]
                else:
                    # High quality GIF palette logic
                    cmd += ["-vf", "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"]

                cmd.append(output_path)
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    st.error(f"Error: {result.stderr}")
                else:
                    status.update(label="Process Complete!", state="complete", expanded=False)

            if os.path.exists(output_path):
                trigger_auto_download(output_path, f"{custom_name}.{out_format}")
                with open(output_path, "rb") as f:
                    st.download_button(
                        label=f"📥 SAVE {custom_name.upper()}.{out_format.upper()}",
                        data=f,
                        file_name=f"{custom_name}.{out_format}",
                        mime="video/mp4" if out_format=="mp4" else "image/gif",
                        use_container_width=True
                    )
                st.balloons()

# --- Deploy Checklist ---
# 1. requirements.txt -> streamlit
# 2. packages.txt -> ffmpeg
