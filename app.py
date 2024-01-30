import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="ToDo", page_icon=":clipboard:")


st.title("ToDo Rat :clipboard:")



# Load data from Google Sheets.
def load_data():
    data = conn.read(worksheet="Sheet",
                     usecols=[0, 1]).dropna(how='all')
    return data

# Add a new task.
def add_task(task):
    try:
        new_data = pd.DataFrame({"Task": [task], "Status": ["Pending"]})
        st.session_state.data = st.session_state.data.append(new_data, ignore_index=True)
        save_data()
    except Exception as e:
        st.write(f"Exception when adding task: {e}")  # Debugging line

# Save data to Google Sheets.
def save_data():
    try:
        st.session_state.data = conn.update(data = st.session_state.data, worksheet="Sheet")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.write(f"Exception when saving data: {e}")  # Debugging line

# Update the status of a task.
def update_task_status(task, status):
    st.session_state.data.loc[st.session_state.data['Task'] == task, 'Status'] = status
    save_data()

def delete_completed_tasks():
    st.session_state.data = st.session_state.data[st.session_state.data['Status'] != 'Completed']
    save_data()

task = st.text_input("Enter a task")

if "data" not in st.session_state:
    # Create a connection object.
    st.session_state.conn = st.connection("gsheets", type=GSheetsConnection, spreadsheet="Tasks")
    st.session_state.data = load_data()
    conn = st.session_state.conn


if st.button("Add Task"):
    if task:
        add_task(task)
        st.success(f"Added task: {task}")
    else:
        st.warning("Please enter a task.")



if not st.session_state.data.empty:
    pending_tasks = st.session_state.data[st.session_state.data['Status'] == 'Pending']
    completed_tasks = st.session_state.data[st.session_state.data['Status'] == 'Completed']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pending Tasks")
        for index, row in pending_tasks.iterrows():
            task_key = f"pending-{row['Task']}"
            task_status = st.checkbox(f"{row['Task']}", value=False, key=task_key)
            if task_status:
                update_task_status(row['Task'], "Completed")

    with col2:
        st.subheader("Completed Tasks")
        for index, row in completed_tasks.iterrows():
            task_key = f"completed-{row['Task']}"
            task_status = st.checkbox(f"{row['Task']}", value=True, key=task_key)
            if not task_status:
                update_task_status(row['Task'], "Pending")

    if st.button("Delete Completed Tasks"):
        delete_completed_tasks()
