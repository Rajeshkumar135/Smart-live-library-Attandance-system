import streamlit as st
import cv2
import pytesseract
import pandas as pd
import re
from datetime import datetime
import os
import time

# 📁 Setup CSV file
csv_file = "attendance.csv"
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=["Regd.No", "Date", "Time", "Status"])
    df.to_csv(csv_file, index=False)

# 📌 Streamlit UI
st.set_page_config(layout="wide")
st.markdown("### 🧾 Smart 📚 Library Live Attendance System")
start = st.checkbox("📽️ Start Live Attendance")

# Layout: 2 columns → left: camera, right: match indicator
col1, col2 = st.columns([3, 1])
frame_window = col1.image([])
match_status = col2.empty()  # Placeholder for green/red indicator

# Last scan time to prevent duplicate saves
last_scan_time = {}

# 🔁 Status toggler: Alternate IN/OUT
def get_next_status(regd):
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        last = df[df["Regd.No"] == regd].tail(1)
        if not last.empty and last["Status"].values[0] == "IN":
            return "OUT"
    return "IN"

# 📄 OCR & Save Function
def process_frame(frame):
    global last_scan_time
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    regd_match = re.search(r'\bGU-\d{4}-\d{3,4}\b', text)

    if regd_match:
        regd = regd_match.group()
        current_time = time.time()

        # Avoid saving same Regd within 5 seconds
        if regd in last_scan_time and current_time - last_scan_time[regd] < 5:
            match_status.markdown("⚠️ **Already Scanned Recently**", unsafe_allow_html=True)
            return False

        date = datetime.now().strftime("%Y-%m-%d")
        time_now = datetime.now().strftime("%H:%M:%S")
        status = get_next_status(regd)

        df = pd.read_csv(csv_file)
        df = pd.concat([df, pd.DataFrame([{"Regd.No": regd, "Date": date, "Time": time_now, "Status": status}])],
                       ignore_index=True)
        df.to_csv(csv_file, index=False)

        last_scan_time[regd] = current_time  # Update last scan time
        match_status.markdown("✅ **Match Found**", unsafe_allow_html=True)
        return True
    else:
        match_status.markdown("❌ **No Match**", unsafe_allow_html=True)
        return False

# 📷 Webcam Loop
if start:
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera error")
            break

        frame_window.image(frame, channels="BGR")
        process_frame(frame)

        # Short delay for smooth stream
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
else:
    st.info("🛑 Attendance not started")

# 📄 Show CSV in Expander
with st.expander("📄 View Attendance CSV"):
    df = pd.read_csv(csv_file)
    st.dataframe(df)

# 🗑️ Delete All Data Button
if st.button("🗑️ Delete All Attendance Records"):
    df = pd.DataFrame(columns=["Regd.No", "Date", "Time", "Status"])
    df.to_csv(csv_file, index=False)
    st.success("✅ All records deleted successfully!")
