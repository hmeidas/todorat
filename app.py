import streamlit as st
import pandas as pd

st.set_page_config(page_title="ToDo List App", page_icon=":clipboard:")

# Define the background image CSS
background_image_css = """
<style>
body {
background-image: url("https://www.radiofrance.fr/s3/cruiser-production/2021/04/527d6b25-172b-4ea6-99f0-1ed26250fdd2/560x315_dents.jpg");
background-size: cover;
background-repeat: no-repeat;
background-attachment: fixed;
}
</style>
"""

# Add the background image CSS to the app
st.markdown(background_image_css, unsafe_allow_html=True)

st.title("ToDo List Rat :clipboard:")

# Rest of your app code
# ...


def load_data():
    try:
        data = pd.read_csv("tasks.csv")
    except FileNotFoundError:
        data = pd.DataFrame(columns=["Task", "Status"])
    return data

def save_data(data):
    data.to_csv("tasks.csv", index=False)

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
