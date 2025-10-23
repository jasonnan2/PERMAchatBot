import streamlit as st
import pandas as pd
import os
import json
from streamlit_modal import Modal

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
        width: 90% !important;       /* Make modal wider */
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
SUMMARY_DIR = "./assignmentChatPromptOnlyIgnoreLowCorr/technicalSummary"
OUTPUT_DIR = "./assignmentChatPromptOnlyIgnoreLowCorr/technicalSummary"
ASSIGNMENT_CSV = './assignmentChatPromptOnlyIgnoreLowCorr/'+'assignments.csv'

# Helper function to get available names
def get_names():
    csv_files = [f.replace(".csv", "") for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
    summary_files = [f.replace("_simulatedUser.txt", "") for f in os.listdir(SUMMARY_DIR) if f.endswith("_simulatedUser.txt")]
    output_files = [f.replace("_simulatedUser.txt", "") for f in os.listdir(OUTPUT_DIR) if f.endswith("_simulatedUser.txt")]
    # Keep names that exist in all three folders
    names = sorted(set(csv_files) & set(summary_files) & set(output_files))
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

@st.dialog("All Assignments")
def show_dialog():
    st.write("### All Assignments")
    st.dataframe(assignmentDF)
    if st.button("Close"):
        st.rerun()
###-----------------------------------------------------------------------------------------###
# App title
st.title("Participant Data Viewer")

col1, col2, col3= st.columns(3, vertical_alignment="bottom")  # Adjust ratios if needed

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

    if view_button:
        show_dialog()



    csv_path = os.path.join(CSV_DIR, f"{selected_name}.csv")
    summary_path = os.path.join(SUMMARY_DIR, f"{selected_name}_simulatedUser.txt")
    output_path = os.path.join(OUTPUT_DIR, f"{selected_name}_simulatedUser.txt")

    # Load data
    df = load_csv(selected_name)
    summary_text = parse_text_file(summary_path)
    output_text = parse_text_file(output_path)

    # Wider horizontal layout
    col1, col2 = st.columns([2, 2], gap="large")

    with col1:
        st.subheader("CSV Data")
        st.dataframe(df, use_container_width=True, height=650)

    with col2:
        st.subheader("Technical Report")
        st.text_area("Technical Report", summary_text, height=650)

    # with col3:
    #     st.subheader("End User Summary")
    #     st.text_area("End User Summary", output_text, height=650)
        
