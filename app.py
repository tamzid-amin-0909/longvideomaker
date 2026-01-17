import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import subprocess
from datetime import timedelta

# --- Page Config ---
st.set_page_config(page_title="Video Render Pro", layout="centered")

# Hide Streamlit UI elements
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;} .stApp {background: #f1f5f9;}</style>", unsafe_allow_html=True)

if not os.path.exists("temp"):
    os.makedirs("temp")

# --- THE UI (HTML/JS/Tailwind) ---
def render_custom_ui():
    html_code = """
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

    <div id="wrapper" class="flex items-center justify-center p-4 font-sans">
        <div class="w-full max-w-md bg-white/90 backdrop-blur-lg rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.1)] p-10 border border-white">
            
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-indigo-600 rounded-2xl shadow-lg shadow-indigo-200 mb-4">
                    <i class="fas fa-video text-white text-2xl"></i>
                </div>
                <h2 class="text-2xl font-black text-slate-800 tracking-tight">Video Render</h2>
                <p class="text-slate-500 text-sm font-medium">Professional Static Processing</p>
            </div>

            <div class="space-y-6">
                <div id="preview-container" onclick="document.getElementById('hidden-file-input').click()" 
                     class="relative group h-40 w-full bg-slate-50 rounded-[2rem] border-2 border-dashed border-slate-200 overflow-hidden flex items-center justify-center cursor-pointer transition-all hover:border-indigo-400">
                    <img id="img-preview" class="hidden h-full w-full object-cover">
                    <div id="preview-placeholder" class="text-slate-400 flex flex-col items-center">
                        <i class="fas fa-cloud-upload-alt mb-2 text-2xl"></i>
                        <span class="text-[10px] font-black uppercase tracking-widest">Tap to select image</span>
                    </div>
                    <input type="file" id="hidden-file-input" class="hidden" accept="image/*" onchange="previewImage(this)">
                </div>

                <div class="grid grid-cols-1 gap-4">
                    <div>
                        <div class="flex justify-between mb-1 px-1">
                            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Duration (Seconds)</label>
                            <span id="time-display" class="text-[10px] font-bold text-indigo-500 uppercase">00:00:00</span>
                        </div>
                        <input type="number" id="duration" value="3600" oninput="updateTimeText()"
                            class="w-full bg-slate-50 border-none rounded-2xl py-4 px-5 text-slate-700 font-bold focus:ring-2 focus:ring-indigo-500 outline-none">
                    </div>

                    <div>
                        <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1 px-1 block">Output Filename</label>
                        <input type="text" id="filename" value="render_output" 
                            class="w-full bg-slate-50 border-none rounded-2xl py-4 px-5 text-slate-700 font-bold focus:ring-2 focus:ring-indigo-500 outline-none">
                    </div>
                </div>

                <button onclick="runGenerator()" id="main-btn" class="w-full bg-slate-900 hover:bg-indigo-600 text-white font-black py-5 rounded-2xl shadow-xl transition-all active:scale-[0.98] uppercase text-xs tracking-widest">
                    Start Rendering
                </button>

                <div id="status-box" class="hidden flex items-center justify-center gap-3 p-4 rounded-2xl bg-indigo-50 border border-indigo-100">
                    <div class="w-2 h-2 bg-indigo-600 rounded-full animate-ping"></div>
                    <span class="text-indigo-600 text-[10px] font-black uppercase">Encoding Video...</span>
                </div>
            </div>
        </div>
    </div>

    <script>
    let selectedImageBase64 = "";

    function updateTimeText() {
        const sec = parseInt(document.getElementById('duration').value) || 0;
        const h = Math.floor(sec / 3600).toString().padStart(2, '0');
        const m = Math.floor((sec % 3600) / 60).toString().padStart(2, '0');
        const s = (sec % 60).toString().padStart(2, '0');
        document.getElementById('time-display').innerText = h + ":" + m + ":" + s;
    }

    function previewImage(input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                selectedImageBase64 = e.target.result;
                document.getElementById('img-preview').src = e.target.result;
                document.getElementById('img-preview').classList.remove('hidden');
                document.getElementById('preview-placeholder').classList.add('hidden');
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    function runGenerator() {
        if (!selectedImageBase64) { alert("Please select an image first!"); return; }
        
        const btn = document.getElementById('main-btn');
        const status = document.getElementById('status-box');
        btn.style.display = 'none';
        status.classList.remove('hidden');

        // Send data back to Streamlit
        const data = {
            img: selectedImageBase64,
            dur: document.getElementById('duration').value,
            name: document.getElementById('filename').value
        };
        
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: data
        }, '*');
    }
    updateTimeText();
    </script>
    """
    return components.html(html_code, height=700)

# --- BACKEND LOGIC ---

# Render the UI and capture the returned values
ui_data = render_custom_ui()

# If the user clicked "Start Rendering" in the UI
if ui_data and 'img' in ui_data:
    try:
        duration = ui_data['dur']
        custom_name = ui_data['name']
        img_data = ui_data['img'].split(",")[1] # Remove the "data:image/jpeg;base64," part
        
        # Save image to temp
        with open("temp/input.jpg", "wb") as f:
            f.write(base64.b64decode(img_data))
            
        output_path = f"temp/{custom_name}.mp4"
        
        # FFmpeg Command
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-framerate", f"1/{duration}",
            "-i", "temp/input.jpg", "-c:v", "libx264", "-t", str(duration),
            "-pix_fmt", "yuv420p", "-r", f"1/{duration}", output_path
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        if os.path.exists(output_path):
            st.success("✨ Render Complete!")
            
            # --- Better Download UI ---
            with open(output_path, "rb") as f:
                st.download_button(
                    label=f"📥 SAVE {custom_name.upper()}.MP4",
                    data=f,
                    file_name=f"{custom_name}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
            
            # Additional visual confirmation
            st.balloons()
            
    except Exception as e:
        st.error(f"Error during render: {e}")
