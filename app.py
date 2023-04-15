import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from gsheetsdb import connect

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)

sheets_api = build("sheets", "v4", credentials=creds)

conn = connect(credentials=credentials)

SPREADSHEET_ID = "1LgjHf-yoF2t_e-4jZ-bKO4eHpgJBvdXBBPe7UCir1KA"

st.set_page_config(page_title="ToDo List App", page_icon=":clipboard:")


st.title("ToDo List Rat :clipboard:")



# Helper function to read data from Google Sheets
def load_data_from_sheets():
    result = sheets_api.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A1:B").execute()
    data = pd.DataFrame(result["values"][1:], columns=result["values"][0])
    return data

# Helper function to write data to Google Sheets
def write_data_to_sheets(data):
    data_to_write = [data.columns.tolist()] + data.values.tolist()
    body = {"values": data_to_write}
    sheets_api.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A1", valueInputOption="RAW", body=body).execute()

# Replace 'load_data' and 'save_data' functions with the new helper functions
load_data = load_data_from_sheets
save_data = write_data_to_sheets

def add_task(task):
    data = load_data()
    data = data.append({"Task": task, "Status": "Pending"}, ignore_index=True)
    save_data(data)

def update_task_status(task, status):
    data = load_data()
    data.loc[data['Task'] == task, 'Status'] = status
    save_data(data)

def delete_completed_tasks():
    data = load_data()
    data = data[data['Status'] != 'Completed']
    save_data(data)

task = st.text_input("Enter a task")

if st.button("Add Task"):
    if task:
        add_task(task)
        st.success(f"Added task: {task}")
    else:
        st.warning("Please enter a task.")

if not st.session_state.get('tasks_updated'):
    st.session_state.tasks_updated = False

data = load_data()

if not data.empty:
    pending_tasks = data[data['Status'] == 'Pending']
    completed_tasks = data[data['Status'] == 'Completed']

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pending Tasks")
        for index, row in pending_tasks.iterrows():
            task_key = f"pending-{row['Task']}"
            task_status = st.checkbox(f"{row['Task']}", value=False, key=task_key)
            if task_status:
                update_task_status(row['Task'], "Completed")
                st.experimental_rerun()

    with col2:
        st.subheader("Completed Tasks")
        for index, row in completed_tasks.iterrows():
            task_key = f"completed-{row['Task']}"
            task_status = st.checkbox(f"{row['Task']}", value=True, key=task_key)
            if not task_status:
                update_task_status(row['Task'], "Pending")
                st.experimental_rerun()

    if st.button("Delete Completed Tasks"):
        delete_completed_tasks()
        st.session_state.tasks_updated = not st.session_state.tasks_updated
        st.experimental_rerun()
