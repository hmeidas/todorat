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

@st.cache(ttl=600, allow_output_mutation=True)
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    data = [row._asdict() for row in rows]
    return data

def load_data(sheet_url):
    query = f'SELECT * FROM "{sheet_url}"'
    rows = conn.execute(query)
    data = pd.DataFrame(rows, columns=["Task", "Status", "Due Date"])
    return data


# Save data
def save_data(sheet_url, data):
    conn.execute(f'DELETE FROM "{sheet_url}" WHERE "Task" IS NOT NULL')
    for _, row in data.iterrows():
        conn.execute(f'INSERT INTO "{sheet_url}" ("Task", "Status", "Due Date") VALUES (%s, %s, %s)', row)

# Update task status
def update_task_status(sheet_url, task, status):
    data = load_data(sheet_url)
    data.loc[data["Task"] == task, "Status"] = status
    save_data(sheet_url, data)

# Streamlit app
st.title("To-Do List")

sheet_url =  st.secrets["private_gsheets_url"]

if sheet_url:
    data = load_data(sheet_url)

    for _, row in data.iterrows():
        col1, col2, col3 = st.columns(3)
        if row["Status"] == "Pending":
            with col1:
                check = st.checkbox("Mark as Completed", key=row["Task"])
                if check:
                    update_task_status(sheet_url, row["Task"], "Completed")
            with col2:
                st.text(row["Task"])
            with col3:
                st.text(row["Due Date"])
        else:
            with col1:
                st.text("Completed")
            with col2:
                st.text(row["Task"])
            with col3:
                st.text(row["Due Date"])
                
    if st.button("Refresh"):
        data = load_data(sheet_url)
