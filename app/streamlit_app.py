import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Employee Manager", layout="centered")
st.title("Employee Management (FastAPI + Postgres)")

with st.form("add_emp"):
    st.subheader("Add New Employee")
    first = st.text_input("First Name")
    last  = st.text_input("Last Name")
    email = st.text_input("Email")
    age   = st.number_input("Age", min_value=0, step=1)
    salary= st.number_input("Salary", min_value=0.0, step=1000.0, format="%.2f")
    submitted = st.form_submit_button("Add")
    if submitted:
        r = requests.post(f"{API}/employee", json={
            "first_name": first, "last_name": last,
            "email": email, "age": int(age), "salary": float(salary)
        })
        if r.status_code == 201:
            st.success("Employee added")
        else:
            st.error(f"Error: {r.text}")

st.subheader("All Employees")
r = requests.get(f"{API}/employees")
if r.ok:
    data = r.json()
    st.dataframe(data)
    ids = [str(e["id"]) for e in data]   
    choice = st.selectbox("Delete by ID", options=[""] + ids)

if st.button("Delete") and choice:
    delr = requests.delete(f"{API}/employee/{choice}")
    st.success("Deleted" if delr.status_code == 204 else delr.text)

st.subheader("Stats")
col1, col2 = st.columns(2)
with col1:
    ra = requests.get(f"{API}/stats/median-age")
    st.metric("Median Age", ra.json().get("median_age"))
with col2:
    rs = requests.get(f"{API}/stats/median-salary")
    st.metric("Median Salary", rs.json().get("median_salary"))

st.caption("Backend must be running on 127.0.0.1:8000")
