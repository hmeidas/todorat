import streamlit as st
import pandas as pd
from gsheetsdb import connect
from datetime import datetime

# Connect to the database
conn = connect()

# Authenticate with Google Sheets
st.set_credentials("path/to/credentials.json")

@st.cache_data
def load_data(sheet_url):
    query = f'SELECT * FROM "{sheet_url}" WHERE "Task" IS NOT NULL'
    return pd.read_sql(query, conn)

@st.cache_data
def save_data(sheet_url, data):
    conn.execute(f'DELETE FROM "{sheet_url}" WHERE "Task" IS NOT NULL')
    conn.insert_rows(sheet_url, data.values.tolist())

def update_task_status(sheet_url, task, status):
    data = load_data(sheet_url)
    data.loc[data["Task"] == task, "Status"] = status
    save_data(sheet_url, data)

sheet_url = "https://docs.google.com/spreadsheets/d/1SAMPLE-SHEET-ID/edit"
data = load_data(sheet_url)

st.title("To-Do List")

st.subheader("Current tasks:")
todolist = data[["Task", "Status"]]
st.write(todolist)

# Switch columns
st.subheader("Switched columns:")
st.write(todolist[["Status", "Task"]])

# Remove "Mark as completed" text
st.subheader("Without 'Mark as completed' text:")
tasks = data[data["Status"] != "Completed"]["Task"]
for task in tasks:
    if st.button(f"Complete: {task}"):
        update_task_status(sheet_url, task, "Completed")
        st.success(f"Task '{task}' marked as completed.")
