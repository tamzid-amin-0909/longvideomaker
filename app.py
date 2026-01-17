import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import subprocess
from datetime import timedelta

# --- Page Config ---
st.set_page_config(page_title="Video Render Pro", layout="centered")

# --- UI Logic & Custom Image Picker ---
def render_custom_picker_ui():
    # This HTML contains the "Gallery Picker" logic from your screenshot
    html_code = """
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
        .glass-card {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(12px);
            border-radius: 2.5rem;
            border: 1px solid white;
        }
        /* Custom Scrollbar for Gallery */
        .gallery-scroll::-webkit-scrollbar { width: 4px; }
        .gallery-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>

    <div id="main-ui" class="p-4 font-sans">
        <div class="max-w-md mx-auto glass-card p-8 shadow-[0_20px_50px_rgba(0,0,0,0.1)]">
            
            <div class="text-center mb-6">
                <div class="inline-flex items-center justify-center w-14 h-14 bg-indigo-600 rounded-2xl shadow-lg mb-3">
                    <i class="fas fa-video text-white text-xl"></i>
                </div>
                <h2 class="text-xl font-black text-slate-800 uppercase tracking-tight">Video Render</h2>
            </div>

            <div id="trigger-picker" onclick="showPicker()" class="relative h-40 w-full bg-slate-50 rounded-[2rem] border-2 border-dashed border-slate-200 overflow-hidden flex items-center justify-center cursor-pointer hover:border-indigo-400 transition-all">
                <img id="preview-img" class="hidden h-full w-full object-cover">
                <div id="placeholder" class="text-slate-400 flex flex-col items-center">
                    <i class="fas fa-images mb-2 text-2xl"></i>
                    <span class="text-[10px] font-black uppercase tracking-widest">Open Image Picker</span>
                </div>
            </div>

            <div class="mt-6 space-y-4">
                <div class="flex flex-col">
                    <label class="text-[10px] font-black text-slate-400 uppercase mb-1 ml-2">Duration (Sec)</label>
                    <input type="number" id="duration" value="3600" class="bg-slate-50 border-none rounded-xl py-3 px-4 font-bold outline-none focus:ring-2 focus:ring-indigo-500">
                </div>
                <div class="flex flex-col">
                    <label class="text-[10px] font-black text-slate-400 uppercase mb-1 ml-2">Filename</label>
                    <input type="text" id="filename" value="render_output" class="bg-slate-50 border-none rounded-xl py-3 px-4 font-bold outline-none focus:ring-2 focus:ring-indigo-500">
                </div>
            </div>

            <button onclick="sendToPython()" class="w-full mt-6 bg-slate-900 hover:bg-indigo-600 text-white font-black py-4 rounded-xl shadow-xl transition-all uppercase text-xs tracking-widest">
                Start Rendering
            </button>
        </div>
    </div>

    <div id="picker-overlay" class="fixed inset-0 bg-white z-50 hidden flex flex-col">
        <div class="flex justify-between items-center p-4 border-b">
            <h3 class="text-lg font-bold text-slate-800">Select an image</h3>
            <button onclick="hidePicker()" class="text-indigo-600 font-bold uppercase text-sm">Done</button>
        </div>
        
        <div class="grid grid-cols-2 gap-2 p-4 border-b bg-slate-50">
            <div class="flex flex-col items-center justify-center p-4 bg-white rounded-xl shadow-sm border cursor-pointer">
                <i class="fas fa-camera text-slate-500 mb-1"></i>
                <span class="text-xs font-bold text-slate-600">Camera</span>
            </div>
            <label class="flex flex-col items-center justify-center p-4 bg-white rounded-xl shadow-sm border cursor-pointer">
                <i class="fas fa-images text-slate-500 mb-1"></i>
                <span class="text-xs font-bold text-slate-600">Browse</span>
                <input type="file" id="real-file" class="hidden" accept="image/*" onchange="handleFile(this)">
            </label>
        </div>

        <div class="flex-1 overflow-y-auto p-2 grid grid-cols-4 gap-1 gallery-scroll" id="gallery-grid">
            <div class="aspect-square bg-slate-100 animate-pulse rounded"></div>
            <div class="aspect-square bg-slate-100 animate-pulse rounded"></div>
            <div class="aspect-square bg-slate-100 animate-pulse rounded"></div>
            <div class="aspect-square bg-slate-100 animate-pulse rounded"></div>
        </div>
    </div>

    <script>
        let selectedBase64 = "";

        function showPicker() { document.getElementById('picker-overlay').classList.remove('hidden'); }
        function hidePicker() { document.getElementById('picker-overlay').classList.add('hidden'); }

        function handleFile(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    selectedBase64 = e.target.result;
                    document.getElementById('preview-img').src = e.target.result;
                    document.getElementById('preview-img').classList.remove('hidden');
                    document.getElementById('placeholder').classList.add('hidden');
                    hidePicker();
                    
                    // Add to gallery grid (Simulating your screenshot)
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = "aspect-square object-cover rounded cursor-pointer border-2 border-transparent hover:border-indigo-500";
                    document.getElementById('gallery-grid').prepend(img);
                };
                reader.readAsDataURL(input.files[0]);
            }
        }

        function sendToPython() {
            if(!selectedBase64) { alert("Please select an image first!"); return; }
            const data = {
                image: selectedBase64,
                duration: document.getElementById('duration').value,
                name: document.getElementById('filename').value
            };
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: data}, '*');
        }
    </script>
    """
    return components.html(html_code, height=650)

# --- Python Logic ---

if not os.path.exists("temp"):
    os.makedirs("temp")

# Execute UI and wait for data
result = render_custom_picker_ui()

if result and 'image' in result:
    try:
        # 1. Process Image
        img_b64 = result['image'].split(",")[1]
        img_path = "temp/input.jpg"
        with open(img_path, "wb") as f:
            f.write(base64.b64decode(img_b64))

        # 2. Render Settings
        dur = result['duration']
        fname = result['name']
        output_path = f"temp/{fname}.mp4"

        # 3. FFmpeg Run
        with st.status("🚀 Processing Video...", expanded=False) as status:
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-framerate", f"1/{dur}",
                "-i", img_path, "-c:v", "libx264", "-t", str(dur),
                "-pix_fmt", "yuv420p", "-r", f"1/{dur}", output_path
            ]
            subprocess.run(cmd, capture_output=True)
            status.update(label="Render Finished!", state="complete")

        # 4. Premium Download UI
        st.markdown("""
            <style>
            div.stDownloadButton > button {
                background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
                color: white !important;
                border-radius: 1.5rem !important;
                padding: 25px !important;
                font-weight: 900 !important;
                box-shadow: 0 15px 35px rgba(79, 70, 229, 0.4) !important;
                border: none !important;
            }
            </style>
        """, unsafe_allow_html=True)

        with open(output_path, "rb") as f:
            st.download_button(
                label=f"📥 SAVE {fname.upper()}.MP4",
                data=f,
                file_name=f"{fname}.mp4",
                mime="video/mp4",
                use_container_width=True
            )
        st.balloons()
        
    except Exception as e:
        st.error(f"Error: {e}")
