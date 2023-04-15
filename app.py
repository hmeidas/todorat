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

# Perform SQL query on the Google Sheet.
@st.cache_data(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["private_gsheets_url"]

def load_data(sheet_url):
    rows = run_query(f'SELECT * FROM "{sheet_url}"')
    data = pd.DataFrame(rows, columns=["Task", "Status"])
    return data

def save_data(sheet_url, data):
    data_as_dict = data.to_dict(orient='records')
    query = f'INSERT INTO "{sheet_url}" (Task, Status) VALUES '
    query += ', '.join([f'("{row["Task"]}", "{row["Status"]}")' for row in data_as_dict])

    conn.execute(f'DELETE FROM "{sheet_url}" WHERE "Task" IS NOT NULL')
    conn.execute(query)

def update_task_status(sheet_url, task, new_status):
    data = load_data(sheet_url)
    data.loc[data['Task'] == task, 'Status'] = new_status
    save_data(sheet_url, data)

def delete_completed_tasks(sheet_url):
    data = load_data(sheet_url)
    data = data[data['Status'] != 'Completed']
    save_data(sheet_url, data)

st.title("To-Do List")
st.write("Add, update, and delete tasks in your to-do list.")

task_input = st.text_input("New Task:")

if st.button("Add Task"):
    if task_input.strip() == "":
        st.warning("Please enter a non-empty task.")
    else:
        update_task_status(sheet_url, task_input, "Pending")

for _, row in load_data(sheet_url).iterrows():
    col1, col2, _ = st.beta_columns([5, 1, 1])

    with col1:
        st.write(f"**{row['Task']}**")

    with col2:
        if st.button("Mark as Completed", key=row['Task']):
            update_task_status(sheet_url, row['Task'], "Completed")

if st.button("Delete Completed Tasks"):
    delete_completed_tasks(sheet_url)
