import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

st.set_page_config(page_title="ToDo List App", page_icon=":clipboard:")
st.title("ToDo List Rat :clipboard:")

# Perform SQL query on the Google Sheet.
@st.cache_data(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return pd.DataFrame(rows)

# Replace 'load_data' and 'save_data' functions with the new helper functions
def load_data():
    sheet_url = st.secrets["private_gsheets_url"]
    data = run_query(f'SELECT * FROM "{sheet_url}"')
    data.columns = ["Task", "Status"]
    return data

def save_data(data):
    data_as_dict = data.to_dict(orient='records')
    query = f'INSERT INTO "{sheet_url}" (Task, Status) VALUES '
    query += ', '.join([f'("{row["Task"]}", "{row["Status"]}")' for row in data_as_dict])

    conn.execute(f'DELETE FROM "{sheet_url}" WHERE "Task" IS NOT NULL')
    conn.execute(query)

def delete_completed_tasks():
    data = load_data()
    data = data[data['Status'] != 'Completed']
    save_data(data)

# The rest of your code remains the same

def add_task(task):
    data = load_data()
    data = data.append({"Task": task, "Status": "Pending"}, ignore_index=True)
    save_data(data)

def update_task_status(task, status):
    data = load_data()
    data.loc[data['Task'] == task, 'Status'] = status
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
