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

# --- Streamlit Cloud-Friendly Path ---
BASE_DIR = "Logger"
DATA_FILE = os.path.join(BASE_DIR, "project_status.json")
ATTACH_DIR = os.path.join(BASE_DIR, "attachments")
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

# --- Sidebar: Useful Links ---
st.sidebar.markdown("---")
st.sidebar.header("🔗 Useful Links")
link_styles = """
    <style>
    .custom-button a button {
        width: 100% !important;
        margin-bottom: 6px;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: bold;
    }
    .btn-wordbee { background-color: #f0ad4e; color: white; }
    .btn-aem { background-color: #5bc0de; color: white; }
    .btn-planner { background-color: #5cb85c; color: white; }
    </style>
"""
st.markdown(link_styles, unsafe_allow_html=True)
st.sidebar.markdown('<div class="custom-button"><a href="https://crg.eu.wordbee-translator.com/a/crg/Access/Login.aspx?x=." target="_blank"><button class="btn-wordbee">Wordbee</button></a></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="custom-button"><a href="https://author-prod-use1.aemprod.thermofisher.net/sites.html/content" target="_blank"><button class="btn-aem">AEM</button></a></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="custom-button"><a href="https://planner.cloud.microsoft/webui/plan/MdrsNgHhOESzfIwUgXl0C2QAHawF/view/board?tid=a8029e02-891d-4bb6-86d1-1831ab11ed72" target="_blank"><button class="btn-planner">Planner</button></a></div>', unsafe_allow_html=True)

# --- Sidebar: Tools ---
st.sidebar.markdown("---")
st.sidebar.header("🛠️ Tools")
st.markdown("""
    <style>
    .custom-tools a button {
        width: 100% !important;
        margin-bottom: 6px;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: bold;
        background-color: #eee;
    }
    .custom-tools a:nth-child(1) button { background-color: #d9edf7; }
    .custom-tools a:nth-child(2) button { background-color: #fcf8e3; }
    .custom-tools a:nth-child(3) button { background-color: #dff0d8; }
    </style>
""", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="custom-tools">
    <a href='https://namegenerator-3ssw2srhrtzbkcvl69gftj.streamlit.app/' target='_blank'><button>Naming Generator</button></a>
    <a href='https://urlconverter-gbqjtnrs6padndtgialfur.streamlit.app/' target='_blank'><button>URL Converter</button></a>
    <a href='https://aemurlconverter-2urshaxxvjifdezn9ex5hf.streamlit.app/#aem-linguistic-review-links-converter' target='_blank'><button>Generate Links</button></a>
</div>
""", unsafe_allow_html=True)

# --- Sidebar: Save & Reset ---
st.sidebar.markdown("---")
if st.sidebar.button("💾 Save Progress"):
    save_data()
    st.sidebar.success("Progress saved.")
if st.sidebar.button("🔄 Reset"):
    st.session_state.clear()
    st.experimental_rerun()

# --- Sidebar: Export / Import Section ---
st.sidebar.markdown("---")
st.sidebar.header("📦 Export / Import")

# Export JSON
st.sidebar.markdown("**⬇️ Export Current Log**", unsafe_allow_html=True)
json_str = json.dumps(projects, indent=2)
b64 = base64.b64encode(json_str.encode()).decode()
fname = f"project_log_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
href = f'<a href="data:file/json;base64,{b64}" download="{fname}">📁 Download JSON</a>'
st.sidebar.markdown(href, unsafe_allow_html=True)

# Import JSON
st.sidebar.markdown("**⬆️ Import JSON File**", unsafe_allow_html=True)
uploaded_json = st.sidebar.file_uploader("Choose a file", type="json", label_visibility="collapsed")
if uploaded_json:
    try:
        loaded_data = json.load(uploaded_json)
        if isinstance(loaded_data, dict):
            projects.update(loaded_data)
            st.session_state.projects = projects
            save_data()
            st.sidebar.success("✅ JSON data loaded.")
        else:
            st.sidebar.error("⚠️ Invalid JSON structure.")
    except Exception as e:
        st.sidebar.error(f"Error loading JSON: {e}")

# Export CSV
st.sidebar.markdown("**📄 Export Summary**", unsafe_allow_html=True)
if st.sidebar.button("Download CSV"):
    df = get_csv_data()
    csv = df.to_csv(index=False).encode('utf-8')
    csv_fname = f"project_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    st.sidebar.download_button(
        label="📄 Export Summary as CSV",
        data=csv,
        file_name=csv_fname,
        mime="text/csv"
    )

# --- Main Title ---
st.title("📋 Project Step Tracker")

# --- Overview Section ---
st.subheader("📊 Overview")
data = get_csv_data()
if not data.empty:
    html = data.head(10).to_html(index=False, classes='custom')
    st.markdown(f"<div style='max-height:300px;overflow-y:auto;'>{html}</div>", unsafe_allow_html=True)

# --- Project Details Section ---
if selected:
    st.header(f"Project {selected}")
    pdata = projects[selected]
    pdata['url'] = st.text_input("Project URL", pdata['url'], key='url')
    pdata['notes'] = st.text_area("Notes", pdata['notes'], key='notes')
    st.markdown("**Common Steps**")
    for s in COMMON_STEPS:
        pdata['steps'][s] = st.checkbox(s, value=pdata['steps'][s], key=s)
    pdata['types'] = st.multiselect("Request Type", ['Marketing', 'Product'], default=pdata['types'])
    if 'Product' in pdata['types']:
        st.markdown("**Product Steps**")
        for s in PRODUCT_STEPS:
            pdata['steps'][s] = st.checkbox(s, value=pdata['steps'][s], key=s)
    if 'Marketing' in pdata['types']:
        st.markdown("**Marketing Steps**")
        for s in MARKETING_STEPS:
            pdata['steps'][s] = st.checkbox(s, value=pdata['steps'][s], key=s)
    pdata['steps'][FINAL_STEP] = st.checkbox(FINAL_STEP, value=pdata['steps'][FINAL_STEP])
    save_data()
