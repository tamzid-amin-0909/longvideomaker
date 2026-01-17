import streamlit as st
import streamlit.components.v1 as components
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

# --- IMAGE PICKER FUNCTION ---
def render_image_picker():
    html_code = """
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <div id="picker-trigger" onclick="showPicker()" class="cursor-pointer">
        <div id="display-area" style="height: 128px; width: 100%; background: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 1rem; display: flex; align-items: center; justify-content: center; flex-direction: column; color: #94a3b8; overflow: hidden;">
            <img id="chosen-img" class="hidden w-full h-full object-cover">
            <div id="placeholder-content" class="flex flex-col items-center">
                <i class="fas fa-image text-2xl mb-2"></i>
                <span class="text-[10px] font-black uppercase tracking-widest">Open Image Picker</span>
            </div>
        </div>
    </div>

    <div id="picker-overlay" class="fixed inset-0 bg-white z-50 hidden flex flex-col font-sans">
        <div class="flex justify-between items-center p-4 border-b">
            <h3 class="text-lg font-bold">Select an image</h3>
            <button onclick="hidePicker()" class="text-indigo-600 font-bold uppercase text-sm">Done</button>
        </div>
        
        <div class="grid grid-cols-2 gap-2 p-4 bg-slate-50 border-b">
            <div class="flex flex-col items-center justify-center p-4 bg-white rounded-xl shadow-sm border">
                <i class="fas fa-camera text-slate-500 mb-1"></i>
                <span class="text-xs font-bold text-slate-600">Camera</span>
            </div>
            <label class="flex flex-col items-center justify-center p-4 bg-white rounded-xl shadow-sm border cursor-pointer">
                <i class="fas fa-images text-slate-500 mb-1"></i>
                <span class="text-xs font-bold text-slate-600">Browse</span>
                <input type="file" id="file-input" class="hidden" accept="image/*" onchange="processImage(this)">
            </label>
        </div>

        <div class="flex-1 overflow-y-auto p-2 grid grid-cols-4 gap-1" id="gallery">
            <div class="aspect-square bg-slate-100 rounded"></div>
            <div class="aspect-square bg-slate-100 rounded"></div>
            <div class="aspect-square bg-slate-100 rounded"></div>
            <div class="aspect-square bg-slate-100 rounded"></div>
        </div>
    </div>

    <script>
        function showPicker() { document.getElementById('picker-overlay').classList.remove('hidden'); }
        function hidePicker() { document.getElementById('picker-overlay').classList.add('hidden'); }

        function processImage(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const base64Data = e.target.result;
                    // Update main UI preview
                    document.getElementById('chosen-img').src = base64Data;
                    document.getElementById('chosen-img').classList.remove('hidden');
                    document.getElementById('placeholder-content').classList.add('hidden');
                    
                    // Add to gallery
                    const img = document.createElement('img');
                    img.src = base64Data;
                    img.className = "aspect-square object-cover rounded";
                    document.getElementById('gallery').prepend(img);
                    
                    hidePicker();
                    
                    // Send to Streamlit
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: base64Data
                    }, '*');
                };
                reader.readAsDataURL(input.files[0]);
            }
        }
    </script>
    """
    return components.html(html_code, height=160)

# Create temp directory
if not os.path.exists("temp"):
    os.makedirs("temp")

# --- UI Layout ---
with st.container():
    # 1. Custom Image Picker Integration
    picker_data = render_image_picker()
    
    if picker_data:
        # Save the base64 image from the picker to temp
        img_data = picker_data.split(",")[1]
        img_path = os.path.join("temp", "input.jpg")
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(img_data))
        st.success("Image Loaded from Picker", icon="✅")

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
        if not picker_data:
            st.error("Please select an image through the picker first!")
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
                trigger_auto_download(output_path, f"{custom_name}.mp4")
                
                with open(output_path, "rb") as f:
                    st.download_button(
                        label=f"📥 SAVE {custom_name.upper()}.MP4",
                        data=f,
                        file_name=f"{custom_name}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                st.balloons()

# --- Next Step ---
# Would you like me to add a "Clear Gallery" button inside the picker overlay?
