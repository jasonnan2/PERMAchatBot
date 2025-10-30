import streamlit as st
import pandas as pd
import os
import json
from streamlit_modal import Modal
from PIL import Image
from natsort import natsorted
Image.MAX_IMAGE_PIXELS = None  # disable limit

# Use full screen width
st.set_page_config(page_title="Participant Data Viewer", layout="wide")

# Custom CSS to remove Streamlit's max-width constraint
st.markdown(
    """
    <style>
        .block-container {
            max-width: 90% !important;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        .stTextArea textarea {
            font-size: 14px !important;
            line-height: 1.4 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    /* Target modal container */
    .stModal > div[data-testid="stModalDialog"] {
        width: 120% !important;       /* Make modal wider */
        max-width: 1200px !important; /* Optional max width */
    }
    </style>
    """,
    unsafe_allow_html=True
)

def parse_text_file(path):
    text_raw = load_text(path)
    try:
        data = json.loads(text_raw)
        if isinstance(data, list) and len(data) > 0 and "content" in data[0]:
            return data[0]["content"]
        else:
            return text_raw
    except json.JSONDecodeError:
        return text_raw

# Define folder paths
CSV_DIR = "./dataForLLM/"
SUMMARY_DIR = "./assignmentChatAddSatisfaction/technicalSummary"
BINNED_DIR = "./BinnedFigures/"
ASSIGNMENT_CSV = './assignmentChatAddSatisfaction/'+'assignments.csv'

# Helper function to get available names
def get_names():
    csv_files = [f.replace(".csv", "") for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
    summary_files = [f.replace("_simulatedUser.txt", "") for f in os.listdir(SUMMARY_DIR) if f.endswith("_simulatedUser.txt")]
    binned_files = [f.replace("_shap.jpg", "") for f in os.listdir(BINNED_DIR) if f.endswith("_shap.jpg")]
    # Keep names that exist in all three folders
    names = natsorted(set(csv_files) & set(summary_files) & set(binned_files))
    return names

# Load data
@st.cache_data
def load_csv(name):
    path = os.path.join(CSV_DIR, f"{name}.csv")
    return pd.read_csv(path)

@st.cache_data
def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

modal = Modal("Assignment Preview", key="data_modal")

@st.dialog("All Assignments", width = "large")
def show_dialog():
    st.write("### All Assignments")
    st.dataframe(assignmentDF)
    if st.button("Close"):
        st.rerun()

@st.dialog("Participant Data", width = "large")
def show_data(df):
    st.write("Participant Data")
    st.dataframe(df, use_container_width=True)
    if st.button("Close"):
        st.rerun()
###-----------------------------------------------------------------------------------------###
# App title
st.title("Participant Data Viewer")

col1, col2, col3, col4= st.columns(4, vertical_alignment="bottom")  # Adjust ratios if needed

# Detect names and select one
names = get_names()
assignmentDF = pd.read_csv(ASSIGNMENT_CSV).iloc[:, 1:]
cols = assignmentDF.columns.tolist()
cols = [cols[-1]] + cols[:-1]
assignmentDF = assignmentDF[cols]

if not names:
    st.error("No matching data found in the folders.")
else:

    view_button = col1.button('View All Assignments')
    selected_name = col2.selectbox("Select a name", names)
    humanAssigned = assignmentDF['humanAssigned'][assignmentDF['SubID']==selected_name].item()
    col3.markdown(f"**Human Assigned Intervention:** {humanAssigned}")
    view_data = col4.button('View Participant Data')

    if view_button:
        show_dialog()
    
    if view_data:
        df = load_csv(selected_name).iloc[:,1:]
        show_data(df)
        
    csv_path = os.path.join(CSV_DIR, f"{selected_name}.csv")
    summary_path = os.path.join(SUMMARY_DIR, f"{selected_name}_simulatedUser.txt")
    binned_path = os.path.join(BINNED_DIR, f"{selected_name}_shap.jpg")

    # Load data
   
    summary_text = parse_text_file(summary_path)
    binned_img = Image.open(binned_path)
    binned_img.thumbnail((5000, 5000))  # resize for display

    # Wider horizontal layout
    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.image(binned_img, caption="Binned Data", use_container_width=True)

    with col2:
        # st.subheader("Technical Report")
        st.text_area("Technical Report", summary_text, height=650)
