import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="ToDo", page_icon=":clipboard:")
st.title("ToDo Rat :clipboard:")

# Create a connection object. Removed the spreadsheet parameter as recommended
conn = st.connection("gsheets", type=GSheetsConnection)

# Load data from Google Sheets.
def load_data():
    data = conn.read(worksheet="Sheet", usecols=[0, 1, 2]).dropna(how='all')
    return data

# Add a new task.
def add_task(task, category):
    try:
        new_data = pd.DataFrame({"Task": [task], "Status": ["Pending"], "Category": [category]})
        st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
        save_data()
    except Exception as e:
        st.write(f"Exception when adding task: {e}")

# Save data to Google Sheets.
def save_data():
    try:
        st.session_state.data = conn.update(data=st.session_state.data, worksheet="Sheet")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.write(f"Exception when saving data: {e}")

# Update the status of a task.
def update_task_status(task, status):
    st.session_state.data.loc[st.session_state.data['Task'] == task, 'Status'] = status
    save_data()

def delete_completed_tasks():
    st.session_state.data = st.session_state.data[st.session_state.data['Status'] != 'Completed']
    save_data()

# Input fields
col_input1, col_input2 = st.columns(2)
with col_input1:
    task = st.text_input("Enter a task")
with col_input2:
    category = st.text_input("Enter a category")

if "data" not in st.session_state:
    st.session_state.data = load_data()

if st.button("Add Task"):
    if task and category:
        add_task(task, category)
        st.success(f"Added task: {task} ({category})")
    else:
        st.warning("Please enter both a task and a category.")

if not st.session_state.data.empty:
    st.subheader("Filter Tasks")
    
    # Filtering options
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        columns = st.session_state.data.columns.tolist()
        filter_col = st.selectbox("Filter by column", ["All"] + columns)
    
    with col_filter2:
        if filter_col != "All":
            unique_vals = ["All"] + sorted(st.session_state.data[filter_col].unique().tolist())
            filter_val = st.selectbox("Select value", unique_vals)
        else:
            filter_val = "All"
    
    # Apply filters
    if filter_col != "All" and filter_val != "All":
        filtered_data = st.session_state.data[st.session_state.data[filter_col] == filter_val]
    else:
        filtered_data = st.session_state.data
    
    # Display filtered data in columns
    pending_tasks = filtered_data[filtered_data['Status'] == 'Pending']
    completed_tasks = filtered_data[filtered_data['Status'] == 'Completed']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Pending Tasks ({len(pending_tasks)})")
        for index, row in pending_tasks.iterrows():
            task_key = f"pending-{row['Task']}-{index}"
            task_label = f"{row['Task']} [{row['Category']}]"
            task_status = st.checkbox(task_label, value=False, key=task_key)
            if task_status:
                update_task_status(row['Task'], "Completed")

    with col2:
        st.subheader(f"Completed Tasks ({len(completed_tasks)})")
        for index, row in completed_tasks.iterrows():
            task_key = f"completed-{row['Task']}-{index}"
            task_label = f"{row['Task']} [{row['Category']}]"
            task_status = st.checkbox(task_label, value=True, key=task_key)
            if not task_status:
                update_task_status(row['Task'], "Pending")

    if st.button("Delete Completed Tasks"):
        delete_completed_tasks()
