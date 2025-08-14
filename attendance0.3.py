import streamlit as st
import cv2
import pytesseract
import pandas as pd
import re
from datetime import datetime
import os

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

# 🔁 Status toggler: Alternate IN/OUT
def get_next_status(regd):
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        last = df[df["Regd.No"] == regd].tail(1)
        if not last.empty and last["Status"].values[0] == "IN":
            return "OUT"
    return "IN"

#  OCR & Save Function
def process_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    regd_match = re.search(r'\bGU-\d{4}-\d{3,4}\b', text)

    if regd_match:
        regd = regd_match.group()
        date = datetime.now().strftime("%Y-%m-%d")
        time_now = datetime.now().strftime("%H:%M:%S")
        status = get_next_status(regd)
        
        df = pd.read_csv(csv_file)
        df = pd.concat([df, pd.DataFrame([{"Regd.No": regd, "Date": date, "Time": time_now, "Status": status}])], ignore_index=True)
        df.to_csv(csv_file, index=False)
        
        match_status.markdown("✅ **Match Found**", unsafe_allow_html=True)
        return True
    else:
        match_status.markdown("❌ **No Match**", unsafe_allow_html=True)
        return False

# 📷 Webcam Loop
if start:
    cap = cv2.VideoCapture(0)
    while start:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera error")
            break
        
        frame_window.image(frame, channels="BGR")
        process_frame(frame)
        cv2.waitKey(3000)  # Wait 3 seconds
else:
    st.info("🛑 Attendance not started")

# 📂 Show CSV in Expander
with st.expander("📄 View Attendance CSV"):
    df = pd.read_csv(csv_file)
    st.dataframe(df)

# 🗑️ Delete All Data Button
if st.button("🗑️ Delete All Attendance Records"):
    df = pd.DataFrame(columns=["Regd.No", "Date", "Time", "Status"])
    df.to_csv(csv_file, index=False)
    st.success("✅ All records deleted successfully!")
