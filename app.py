import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import subprocess

# --- Page Config ---
st.set_page_config(page_title="Video Render Pro", layout="centered")

# CSS to hide Streamlit default UI elements for a cleaner look
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { background-color: #f1f5f9; }
    </style>
""", unsafe_allow_html=True)

# Create a directory for uploads
if not os.path.exists("temp"):
    os.makedirs("temp")

# --- UI HTML (Your Exact Code + Streamlit Bridge) ---
def get_html_ui(img_base64=None):
    img_js = f"'{img_base64}'" if img_base64 else "null"
    
    return f"""
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

    <div id="wrapper" class="flex items-center justify-center p-4 bg-transparent font-sans">
        <div class="w-full max-w-md bg-white/80 backdrop-blur-lg rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.1)] p-10 border border-white">
            
            <div class="text-center mb-8">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-indigo-600 rounded-2xl shadow-lg shadow-indigo-200 mb-4">
                    <i class="fas fa-video text-white text-2xl"></i>
                </div>
                <h2 class="text-2xl font-black text-slate-800 tracking-tight">Video Render</h2>
                <p class="text-slate-500 text-sm font-medium">Professional Static Processing</p>
            </div>

            <div class="space-y-6">
                <div id="preview-container" class="relative group h-32 w-full bg-slate-100 rounded-2xl border-2 border-dashed border-slate-200 overflow-hidden flex items-center justify-center transition-all">
                    <img id="img-preview" class="{'hidden' if not img_base64 else ''} h-full w-full object-cover transition duration-300 group-hover:scale-110" 
                         src="{"data:image/jpeg;base64," + img_base64 if img_base64 else ''}">
                    <div id="preview-placeholder" class="{'hidden' if img_base64 else ''} text-slate-400 flex flex-col items-center">
                        <i class="fas fa-image mb-2 text-xl"></i>
                        <span class="text-xs font-bold uppercase tracking-widest text-center px-4">Upload image via Streamlit sidebar</span>
                    </div>
                </div>

                <div class="grid grid-cols-1 gap-4">
                    <div>
                        <div class="flex justify-between mb-1 px-1">
                            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Duration (Seconds)</label>
                            <span id="time-display" class="text-[10px] font-bold text-indigo-500 uppercase tracking-widest">00:00:00</span>
                        </div>
                        <input type="number" id="duration" value="3600" oninput="updateTimeText()"
                            class="w-full bg-slate-50 border-none rounded-2xl py-4 px-5 text-slate-700 font-bold focus:ring-2 focus:ring-indigo-500 transition outline-none">
                    </div>

                    <div>
                        <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1 px-1 block">Output Filename</label>
                        <div class="relative">
                            <input type="text" id="filename" value="render_output" 
                                class="w-full bg-slate-50 border-none rounded-2xl py-4 px-5 text-slate-700 font-bold focus:ring-2 focus:ring-indigo-500 transition outline-none">
                            <span class="absolute right-5 top-1/2 -translate-y-1/2 text-slate-300 font-bold">.mp4</span>
                        </div>
                    </div>
                </div>

                <button onclick="runGenerator()" id="main-btn" class="w-full group relative overflow-hidden bg-slate-900 hover:bg-indigo-600 text-white font-black py-5 rounded-2xl shadow-xl transition-all duration-300 transform active:scale-[0.98]">
                    <span id="btn-text" class="relative z-10 flex items-center justify-center gap-3 tracking-widest uppercase text-xs">
                        Start Rendering <i class="fas fa-arrow-right"></i>
                    </span>
                </button>

                <div id="status-box" class="hidden flex items-center justify-center gap-3 p-4 rounded-2xl bg-indigo-50 border border-indigo-100">
                    <div class="w-2 h-2 bg-indigo-600 rounded-full animate-ping"></div>
                    <span class="text-indigo-600 text-[10px] font-black uppercase tracking-tighter">Encoding at light speed...</span>
                </div>
            </div>
        </div>
    </div>

    <script>
    function updateTimeText() {{
        const sec = parseInt(document.getElementById('duration').value) || 0;
        const h = Math.floor(sec / 3600).toString().padStart(2, '0');
        const m = Math.floor((sec % 3600) / 60).toString().padStart(2, '0');
        const s = (sec % 60).toString().padStart(2, '0');
        document.getElementById('time-display').innerText = h + ":" + m + ":" + s;
    }}

    function runGenerator() {{
        const dur = document.getElementById('duration').value;
        const name = document.getElementById('filename').value;
        const btn = document.getElementById('main-btn');
        const status = document.getElementById('status-box');

        btn.style.display = 'none';
        status.classList.remove('hidden');

        // STREAMLIT BRIDGE: Send data to Python
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: {{duration: dur, filename: name, action: 'generate'}}
        }}, '*');
    }}

    updateTimeText();
    </script>
    """

# --- Python Logic ---

# 1. Sidebar for Image Upload (Necessary because JS can't read local files directly in Streamlit)
st.sidebar.title("📁 File Manager")
uploaded_file = st.sidebar.file_uploader("Step 1: Upload Image", type=["jpg", "jpeg", "png"])

img_base64 = None
if uploaded_file:
    # Save image for FFmpeg
    with open("temp/image.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Convert to base64 for the Preview
    img_base64 = base64.b64encode(uploaded_file.getvalue()).decode()

# 2. Render the exact UI
# The component returns 'value' from window.parent.postMessage
ui_result = components.html(get_html_ui(img_base64), height=650)

# 3. Handle the "Generate" trigger from the UI
if ui_result and ui_result.get("action") == "generate":
    if not uploaded_file:
        st.error("⚠️ Please upload an image in the sidebar first!")
    else:
        duration = ui_result.get("duration")
        custom_name = ui_result.get("filename")
        output_path = f"temp/{custom_name}.mp4"
        
        # FFmpeg Command
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-framerate", f"1/{duration}",
            "-i", "temp/image.jpg", "-c:v", "libx264", "-t", str(duration),
            "-pix_fmt", "yuv420p", "-r", f"1/{duration}", output_path
        ]
        
        try:
            subprocess.run(cmd, check=True)
            st.sidebar.success("✅ Render Complete!")
            
            # Download Button in Sidebar
            with open(output_path, "rb") as f:
                st.sidebar.download_button(
                    label="📥 Download Video",
                    data=f,
                    file_name=f"{custom_name}.mp4",
                    mime="video/mp4"
                )
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
