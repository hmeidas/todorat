import streamlit as st
import pandas as pd

st.set_page_config(page_title="ToDo List App", page_icon=":clipboard:")

st.title("ToDo List Rat :clipboard:")

@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

public_gsheets_url = "https://docs.google.com/spreadsheets/d/1LgjHf-yoF2t_e-4jZ-bKO4eHpgJBvdXBBPe7UCir1KA/edit?usp=share_link"
data = load_data(public_gsheets_url)

def save_data(data):
    data.to_csv("tasks.csv", index=False)

def add_task(task):
    data = load_data(public_gsheets_url)
    data = data.append({"Task": task, "Status": "Pending"}, ignore_index=True)
    save_data(data)

def update_task_status(task, status):
    data = load_data(public_gsheets_url)
    data.loc[data['Task'] == task, 'Status'] = status
    save_data(data)

def delete_completed_tasks():
    data = load_data(public_gsheets_url)
    data = data[data['Status'] != 'Completed']
    save_data(data)

task = st.text_input("Enter a task")

if st.button("Add Task"):
    if task:
        add_task(task)
        st.success(f"Added task: {task}")
    else:
        st.warning("Please enter a task.")

data = load_data(public_gsheets_url)

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
        st.experimental_rerun()
