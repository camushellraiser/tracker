import streamlit as st
import os
import json
import pandas as pd
import base64
from datetime import datetime
from PIL import Image

# --- Configuration ---
st.set_page_config(
    page_title="Project Planner Logger",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Streamlit Cloud-Friendly Path ---
BASE_DIR = "Logger"
DATA_FILE = os.path.join(BASE_DIR, "project_status.json")
ATTACH_DIR = os.path.join(BASE_DIR, "attachments")
DOCS_DIR = os.path.join(BASE_DIR, "documentation")
os.makedirs(ATTACH_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

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

# --- Load documentation ---
def load_docs():
    doc_file = os.path.join(DOCS_DIR, "project_docs.json")
    if os.path.exists(doc_file):
        with open(doc_file, 'r') as f:
            return json.load(f)
    return []

def save_docs(data):
    doc_file = os.path.join(DOCS_DIR, "project_docs.json")
    with open(doc_file, 'w') as f:
        json.dump(data, f, indent=2)

if 'docs' not in st.session_state:
    st.session_state.docs = load_docs()

# --- Helpers ---
def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(st.session_state.projects, f, indent=2)

def get_csv_data():
    rows = []
    for pid, pdata in projects.items():
        total = len(COMMON_STEPS) + \
                (len(PRODUCT_STEPS) if 'Product' in pdata['types'] else 0) + \
                (len(MARKETING_STEPS) if 'Marketing' in pdata['types'] else 0) + 1
        done = sum(pdata['steps'].values())
        pct = int(done / total * 100) if total else 0
        rows.append({
            "Project ID": pid,
            "Created At": pdata.get("created_at", ""),
            "Types": ", ".join(pdata.get("types", [])),
            "URL": pdata.get("url", ""),
            "Notes": pdata.get("notes", ""),
            "% Complete": pct
        })
    return pd.DataFrame(rows)

# --- CSS Styles ---
st.markdown("""
    <style>
    th { text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.title("📋 Project Step Tracker")

# --- Overview Section ---
st.subheader("📊 Overview")
data = get_csv_data()
if not data.empty:
    html = data.head(10).to_html(index=False, classes='custom')
    st.markdown(f"<div style='max-height:300px;overflow-y:auto;'>{html}</div>", unsafe_allow_html=True)

# --- Project Details Section ---
if 'selected_project' in st.session_state and st.session_state.selected_project:
    selected = st.session_state.selected_project
    st.header(f"Project {selected}")
    tabs = st.tabs(["🬭 Project Management", "📌 Documentation"])

    # --- Project Management Tab ---
    with tabs[0]:
        pdata = projects[selected]
        pdata['url'] = st.text_input("Project URL", pdata['url'], key='url')
        pdata['notes'] = st.text_area("Notes", pdata['notes'], key='notes')
        st.markdown("**Common Steps**")
        for s in COMMON_STEPS:
            pdata['steps'][s] = st.checkbox(s, value=pdata['steps'][s], key=f"{selected}_{s}")
        pdata['types'] = st.multiselect("Request Type", ['Marketing', 'Product'], default=pdata['types'])
        if 'Product' in pdata['types']:
            st.markdown("**Product Steps**")
            for s in PRODUCT_STEPS:
                pdata['steps'][s] = st.checkbox(s, value=pdata['steps'][s], key=f"{selected}_{s}")
        if 'Marketing' in pdata['types']:
            st.markdown("**Marketing Steps**")
            for s in MARKETING_STEPS:
                pdata['steps'][s] = st.checkbox(s, value=pdata['steps'][s], key=f"{selected}_{s}")
        pdata['steps'][FINAL_STEP] = st.checkbox(FINAL_STEP, value=pdata['steps'][FINAL_STEP], key=f"{selected}_{FINAL_STEP}")

        if pdata['url']:
            st.markdown(f"<br><a href='{pdata['url']}' target='_blank'><button style='background-color:#dc3545;color:white;padding:6px 12px;border:none;border-radius:4px;'>Go To Request</button></a>", unsafe_allow_html=True)

        save_data()

    # --- Documentation Tab ---
    with tabs[1]:
        st.markdown("### 📌 Project Documentation")

        with st.expander("Upload New Screenshot"):
            uploaded_file = st.file_uploader("Upload PNG/JPG Screenshot", type=["png", "jpg", "jpeg"])
            desc = st.text_input("Add a short description")
            if st.button("Save Screenshot"):
                if uploaded_file:
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    file_ext = os.path.splitext(uploaded_file.name)[1]
                    new_fname = f"screenshot_{timestamp}{file_ext}"
                    filepath = os.path.join(DOCS_DIR, new_fname)
                    with open(filepath, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.session_state.docs.append({
                        "file": new_fname,
                        "desc": desc,
                        "time": timestamp
                    })
                    save_docs(st.session_state.docs)
                    st.success("Screenshot saved.")
                else:
                    st.warning("Please upload an image.")

        if st.session_state.docs:
            st.markdown("### 🖼️ Saved Documentation")
            for doc in sorted(st.session_state.docs, key=lambda x: x['time'], reverse=True):
                col1, col2 = st.columns([1, 4])
                with col1:
                    img_path = os.path.join(DOCS_DIR, doc['file'])
                    st.image(img_path, width=150)
                with col2:
                    st.markdown(f"**Description:** {doc['desc']}")
                    st.markdown(f"*Saved at:* {doc['time']}")

# --- Preserve selected project between reruns ---
else:
    selected = st.sidebar.selectbox("Select Project", [""] + list(projects.keys()), key="selected_project")
