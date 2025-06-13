import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Config
CSV_FILE = "attendance.csv"
ADMIN_PASSWORD = "Swecha@SOAI"  # Change this for security

# UI
st.set_page_config("AI Attendance System", layout="centered")
st.title("📋 Summer of AI - Attendance Portal")

# Sidebar: Default to User Login
mode = st.sidebar.radio("Select Mode", ["Admin Login", "User Login"], index=1)

# --------------------- ADMIN PANEL ---------------------
if mode == "Admin Login":
    st.header("🔐 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Access granted.")

        uploaded = st.file_uploader("Upload CSV (must contain at least 'email')", type=["csv"])
        if uploaded:
            df = pd.read_csv(uploaded)

            if 'email' not in df.columns:
                st.error("CSV must contain an 'email' column.")
            else:
                # Ensure 'username' column exists
                if 'username' not in df.columns:
                    df['username'] = ""

                # Add today's date column
                today = datetime.now().strftime("%Y-%m-%d")
                if today not in df.columns:
                    df[today] = ""

                # Save to file
                df.to_csv(CSV_FILE, index=False)
                st.success("Email list uploaded and initialized!")

        # View and download
        if os.path.exists(CSV_FILE):
            st.subheader("📄 Current Attendance")
            df = pd.read_csv(CSV_FILE)
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Attendance CSV", csv, "updated_attendance.csv", "text/csv")

            # Attendance stats
            today = datetime.now().strftime("%Y-%m-%d")
            if today in df.columns:
                total = len(df)
                marked = df[today].str.contains("✅").sum()
                st.metric("✅ Attendance Marked", f"{marked}/{total} ({marked/total:.0%})")

    elif password != "":
        st.error("Incorrect password.")

# --------------------- USER PANEL ---------------------
elif mode == "User Login":
    st.header("👤 Mark Your Attendance")

    if not os.path.exists(CSV_FILE):
        st.warning("Admin has not uploaded the email list yet.")
    else:
        df = pd.read_csv(CSV_FILE)
        today = datetime.now().strftime("%Y-%m-%d")

        # Ensure necessary columns
        if today not in df.columns:
            df[today] = ""
        if 'username' not in df.columns:
            df['username'] = ""

        # Input
        email = st.text_input("Enter your registered email").strip().lower()
        username = st.text_input("Enter your Code.Swecha username").strip().lower()

        if st.button("Submit"):
            if email in df['email'].str.lower().values:
                idx = df[df['email'].str.lower() == email].index[0]

                # Update or validate username
                current_username = str(df.at[idx, 'username']).strip().lower()
                if not current_username:
                    df.at[idx, 'username'] = username
                elif current_username != username:
                    st.warning("⚠️ Username does not match previous entry, updating to new username.")
                    df.at[idx, 'username'] = username

                # Mark attendance
                if df.at[idx, today] == "✅":
                    st.info("You have already marked your attendance today.")
                else:
                    df.at[idx, today] = "✅"
                    df.to_csv(CSV_FILE, index=False)
                    st.success("Attendance marked successfully ✅")
            else:
                st.error("❌ Your email is not registered. Please contact coordinators.")
