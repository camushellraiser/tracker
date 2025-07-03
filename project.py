import streamlit as st
import os
import json
import pandas as pd
import base64
from datetime import datetime

# --- Configuration ---
st.set_page_config(
    page_title="Project Planner Logger",
    layout="wide",
    initial_sidebar_state="expanded"
)
DATA_FILE = "project_status.json"
ATTACH_DIR = "attachments"

# Ensure attachments directory exists
os.makedirs(ATTACH_DIR, exist_ok=True)

# --- Define steps ---
COMMON_STEPS = [
    "Verify if the request is complete",
    "Create folder for project in shared location",
    "Generate names",
    "Rename request"
]
PRODUCT_STEPS = [
    "Create inclusion list",
    "Export XML files from Iris",
    "Create Wordbee order",
    "Add details from Wordbee order into the request",
    "Provide quote to requester once Hiromi confirms",
    "Once requester confirms convert the request to project",
    "Set it to in progress",
    "Import translated files into Iris",
    "Create ticket for Wendy to import the translated content",
    "Close request"
]
MARKETING_STEPS = [
    "Convert the URLs to the proper format",
    "Create the AEM project",
    "Add the correct pages to the AEM project",
    "Export the XML files from the AEM project",
    "Clean the exported files (remove unnecessary files)",
    "Re-zip the files",
    "Create Wordbee order",
    "Create the AEM Linguistic Review Links",
    "Add details from Wordbee order into the request",
    "Provide quote to requester once Hiromi confirms",
    "Once requester confirms convert the request to project",
    "Set it to in progress",
    "Import translated files into AEM",
    "Perform a functional review",
    "Create a card for the linguistic reviewer",
    "Accept translations",
    "Close the request"
]
FINAL_STEP = "Make sure the shared folder is properly updated"
ALL_STEPS = COMMON_STEPS + PRODUCT_STEPS + MARKETING_STEPS + [FINAL_STEP]

# --- Load or initialize projects ---
if 'projects' not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            st.session_state.projects = json.load(f)
    else:
        st.session_state.projects = {}
projects = st.session_state.projects

# --- Helpers ---
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(st.session_state.projects, f, indent=2)

# --- Sidebar: Add New Project ---
st.sidebar.header("➕ New Project ID")
new_pid = st.sidebar.text_input("Project ID", "GTS", key="new_id")
if st.sidebar.button("Add Project"):
    pid = new_pid.strip()
    if not pid or pid.upper() == "GTS":
        st.sidebar.error("Please replace 'GTS' with a valid Project ID.")
    elif pid in projects:
        st.sidebar.error("This Project ID is already registered.")
    else:
        projects[pid] = {
            'created_at': datetime.now().isoformat(),
            'types': [],
            'url': '',
            'notes': '',
            'steps': {step: False for step in ALL_STEPS},
            'attachments': []
        }
        os.makedirs(os.path.join(ATTACH_DIR, pid), exist_ok=True)
        save_data()
        st.sidebar.success(f"Project {pid} added.")

# --- Sidebar: Search & Select Project ---
st.sidebar.markdown("---")
st.sidebar.header("🔎 Search & Select Project")
search_term = st.sidebar.text_input("Search Project ID", key="search_proj")
sorted_projects = sorted(projects.keys(), key=lambda x: projects[x]['created_at'], reverse=True)
filtered_projects = [p for p in sorted_projects if not search_term or search_term.lower() in p.lower()]
select_options = [""] + filtered_projects
selected = st.sidebar.selectbox("Select Project", select_options, key="selected_project")

# --- Sidebar: Tools ---
st.sidebar.markdown("---")
st.sidebar.header("🛠️ Tools")
tools = [
    ("Naming Generator", "https://namegenerator-3ssw2srhrtzbkcvl69gftj.streamlit.app/"),
    ("URL Converter", "https://urlconverter-gbqjtnrs6padndtgialfur.streamlit.app/"),
    ("Generate Links", "https://aemurlconverter-2urshaxxvjifdezn9ex5hf.streamlit.app/#aem-linguistic-review-links-converter")
]
for name, link in tools:
    html = f"<a href='{link}' style='text-decoration:none;'><button style='width:100%; margin:4px 0; padding:8px; background-color:#44475a; color:white; border:none; border-radius:4px;'>{name}</button></a>"
    st.sidebar.markdown(html, unsafe_allow_html=True)

# --- Sidebar: Save & Reset ---
st.sidebar.markdown("---")
if st.sidebar.button("💾 Save Progress"):
    save_data()
    st.sidebar.success("Progress saved.")
if st.sidebar.button("🔄 Reset"):
    st.session_state.clear()
    st.experimental_rerun()

# --- Main Title ---
st.title("📋 Project Step Tracker")

# --- CSS & Tooltip with best practice (image on hover) ---
# Load tooltip image
tooltip_b64 = ''
if os.path.exists('languageselection.jpg'):
    with open('languageselection.jpg', 'rb') as img:
        tooltip_b64 = base64.b64encode(img.read()).decode()
st.markdown(f"""
<style>
  /* Table styling */
  table.custom {{ width:100%; border-collapse: collapse; }}
  table.custom th, table.custom td {{ padding:8px; border:1px solid #444; }}
  table.custom th {{ background-color:#333; color:white; text-align:center; }}
  table.custom td:nth-child(2) {{ text-align:center; }}
  /* Tooltip container */
  .tooltip {{ position: relative; display: inline-block; }}
  .tooltip-icon {{ font-size: 16px; color: #888; margin-left: 4px; vertical-align: middle; }}
  /* Hidden tooltip content */
  .tooltip-content {{
    visibility: hidden;
    width: 200px;
    background-color: #222;
    border: 1px solid #555;
    padding: 4px;
    position: absolute;
    z-index: 999;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    border-radius: 4px;
  }}
  /* Tooltip arrow */
  .tooltip-content::after {{
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: #222 transparent transparent transparent;
  }}
  /* Show on hover */
  .tooltip:hover .tooltip-content {{ visibility: visible; opacity: 1; }}
  .tooltip img {{ max-width: 100%; height: auto; display: block; }}
</style>
""", unsafe_allow_html=True)

# --- Overview Table ---
overview = []
for pid, pdata in projects.items():
    types = pdata['types']
    total = len(COMMON_STEPS) + (len(PRODUCT_STEPS) if 'Product' in types else 0) + (len(MARKETING_STEPS) if 'Marketing' in types else 0) + 1
    done = sum(pdata['steps'].values())
    pct = int(done/total*100) if total else 0
    overview.append({'Project': pid, '% Complete': pct, 'URL': pdata['url']})
if overview:
    st.subheader("📊 Overview")
    df = pd.DataFrame(overview).head(10)
    html = df.to_html(index=False, classes='custom', escape=True)
    st.markdown(f"<div style='max-height:300px; overflow-y:auto;'>{html}</div>", unsafe_allow_html=True)

# --- Project Details ---
if selected:
    pdata = projects[selected]
    st.markdown(f"<h2>Project {selected}</h2>", unsafe_allow_html=True)
    with st.expander("Details", expanded=True):
        pdata['url'] = st.text_input("Project URL", pdata['url'], key=f"url_{selected}")
        pdata['notes'] = st.text_area("Notes", pdata['notes'], key=f"notes_{selected}")
        st.markdown("**Common Steps**")
        for step in COMMON_STEPS:
            val = st.checkbox(step, value=pdata['steps'][step], key=f"c_{selected}_{step}")
            pdata['steps'][step] = val
        pdata['types'] = st.multiselect("Request Type", ['Marketing','Product'], default=pdata['types'], key=f"type_{selected}")
        if 'Product' in pdata['types']:
            st.markdown("---\n**Product Steps**")
            for step in PRODUCT_STEPS:
                val = st.checkbox(step, value=pdata['steps'][step], key=f"p_{selected}_{step}")
                pdata['steps'][step] = val
                if 'Marketing' in pdata['types']:
            st.markdown("---
**Marketing Steps**")
            for step in MARKETING_STEPS:
                # For the special step, render tooltip
                if step == 'Create the AEM project':
                    cols = st.columns([0.9, 0.1])
                    with cols[0]:
                        val = st.checkbox(step, value=pdata['steps'][step], key=f"m_{selected}_{step}")
                        pdata['steps'][step] = val
                    with cols[1]:
                        tooltip_html = (
                            f"<div class='tooltip'>"
                            f"<span class='tooltip-icon'>🛈</span>"
                            f"<div class='tooltip-content'><img src='data:image/jpeg;base64,{tooltip_b64}' /></div>"
                            f"</div>"
                        )
                        st.markdown(tooltip_html, unsafe_allow_html=True)
                else:
                    val = st.checkbox(step, value=pdata['steps'][step], key=f"m_{selected}_{step}")
                    pdata['steps'][step] = val
        st.markdown("---")
        val = st.checkbox(FINAL_STEP, value=pdata['steps'][FINAL_STEP], key=f"f_{selected}")
        pdata['steps'][FINAL_STEP] = val
        save_data()
        files = st.file_uploader("Attachments", accept_multiple_files=True, key=f"a_{selected}")
        if files:
            adir = os.path.join(ATTACH_DIR, selected)
            os.makedirs(adir, exist_ok=True)
            for f in files:
                with open(os.path.join(adir, f.name), 'wb') as out:
                    out.write(f.getbuffer())
            pdata['attachments'] = os.listdir(adir)
        if pdata.get('attachments'):
            st.markdown("**Attachments**")
            for fn in pdata['attachments']:
                with open(os.path.join(ATTACH_DIR, selected, fn), 'rb') as fp:
                    st.download_button(fn, fp.read(), file_name=fn)
