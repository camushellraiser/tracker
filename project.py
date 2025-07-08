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

# --- Custom Storage Location ---
BASE_DIR = "/Users/emmanuel.lizares/Documents/Logger"
DATA_FILE = os.path.join(BASE_DIR, "project_status.json")
ATTACH_DIR = os.path.join(BASE_DIR, "attachments")

# Ensure storage directories exist
os.makedirs(BASE_DIR, exist_ok=True)
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

# --- Sidebar: Select Project ---
st.sidebar.markdown("---")
st.sidebar.header("🔎 Select Project")
search_term = st.sidebar.text_input("Search Project ID", key="search_proj")
sorted_projects = sorted(
    projects.keys(),
    key=lambda x: projects[x].get('created_at',''),
    reverse=True
)
filtered = [p for p in sorted_projects if not search_term or search_term.lower() in p.lower()]
options = [""] + filtered
selected = st.sidebar.selectbox("Select Project", options, key="selected_project")

# --- Sidebar: Tools ---
st.sidebar.markdown("---")
st.sidebar.header("🛠️ Tools")
for name, link in [
    ("Naming Generator","https://namegenerator-3ssw2srhrtzbkcvl69gftj.streamlit.app/"),
    ("URL Converter","https://urlconverter-gbqjtnrs6padndtgialfur.streamlit.app/"),
    ("Generate Links","https://aemurlconverter-2urshaxxvjifdezn9ex5hf.streamlit.app/#aem-linguistic-review-links-converter")
]:
    st.sidebar.markdown(f"<a href='{link}' target='_blank'><button>{name}</button></a>", unsafe_allow_html=True)

# --- Save & Reset ---
st.sidebar.markdown("---")
if st.sidebar.button("💾 Save Progress"):
    save_data()
    st.sidebar.success("Progress saved.")
if st.sidebar.button("🔄 Reset"):
    st.session_state.clear()
    st.experimental_rerun()

# --- Title ---
st.title("📋 Project Step Tracker")

# --- Overview ---
st.subheader("📊 Overview")
data = []
for pid,pdata in projects.items():
    total = len(COMMON_STEPS) + (len(PRODUCT_STEPS) if 'Product' in pdata['types'] else 0) + (len(MARKETING_STEPS) if 'Marketing' in pdata['types'] else 0) + 1
    done = sum(pdata['steps'].values())
    pct = int(done/total*100) if total else 0
    data.append({'Project':pid,'% Complete':pct,'URL':pdata['url']})
if data:
    df = pd.DataFrame(data).head(10)
    html = df.to_html(index=False,classes='custom')
    st.markdown(f"<div style='max-height:300px;overflow-y:auto;'>{html}</div>",unsafe_allow_html=True)

# --- Details ---
if selected:
    st.header(f"Project {selected}")
    pdata = projects[selected]
    pdata['url'] = st.text_input("Project URL", pdata['url'], key='url')
    pdata['notes'] = st.text_area("Notes", pdata['notes'], key='notes')
    st.markdown("**Common Steps**")
    for s in COMMON_STEPS:
        pdata['steps'][s] = st.checkbox(s,value=pdata['steps'][s],key=s)
    pdata['types'] = st.multiselect("Request Type",['Marketing','Product'],default=pdata['types'])
    if 'Product' in pdata['types']:
        st.markdown("**Product Steps**")
        for s in PRODUCT_STEPS:
            pdata['steps'][s] = st.checkbox(s,value=pdata['steps'][s],key=s)
    if 'Marketing' in pdata['types']:
        st.markdown("**Marketing Steps**")
        for s in MARKETING_STEPS:
            pdata['steps'][s] = st.checkbox(s,value=pdata['steps'][s],key=s)
    pdata['steps'][FINAL_STEP] = st.checkbox(FINAL_STEP,value=pdata['steps'][FINAL_STEP])
    save_data()
