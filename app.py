import streamlit as st
from PIL import Image
from io import BytesIO
import auth
from utils import extract_text, simplify_text, text_to_speech
from datetime import datetime

# ------------------- CSS -------------------
st.markdown("""
<style>
/* Page background */
body { background-color: #f5f5f5; }

/* Header */
h1 { color: #4B8BBE; font-family: 'Segoe UI', sans-serif; font-weight:700; text-align:center; }
h4 { color:#333; font-family:'Segoe UI', sans-serif; }

/* Card */
.card {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

/* Buttons */
.stButton>button {
    background-color: #4B8BBE;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 8px 16px;
}
.stButton>button:hover { background-color: #357ABD; color: white; }

/* Sidebar */
[data-testid="stSidebar"] { background-color: #e6f0fa; }

/* Textarea */
textarea { border-radius: 8px; border:1px solid #ccc; padding:8px; font-family:'Segoe UI',sans-serif; }
</style>
""", unsafe_allow_html=True)

# ------------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="MediExplain",
    page_icon="assets/app_icon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------- SESSION STATE -------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# ------------------- HEADER -------------------
st.markdown("<h1>MediExplain</h1><p style='text-align:center; color:#555;'>Handwritten Prescription Interpreter</p>", unsafe_allow_html=True)

# ------------------- AUTHENTICATION -------------------
if not st.session_state.logged_in:
    choice = st.radio("Select Action", ["Login", "Sign Up"], horizontal=True)
    if choice=="Sign Up":
        st.subheader("Create a New Account")
        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")
        if st.button("Sign Up"):
            if auth.add_user(new_user, new_pass):
                st.success("Account created! Please login.")
            else:
                st.error("Username already exists.")
    else:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if auth.check_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username}!")
            else:
                st.error("Username/password incorrect")

# ------------------- DASHBOARD / APP -------------------
if st.session_state.logged_in:
    st.sidebar.title(f"Hello, {st.session_state.username}")
    menu_choice = st.sidebar.radio("Menu", ["Dashboard", "History", "Profile"])

    # ------------------- DASHBOARD -------------------
    if menu_choice=="Dashboard":
        st.header("📄 Dashboard")
        st.write("Upload your handwritten prescription below:")

        uploaded_file = st.file_uploader("Drag & Drop or Click to Upload", type=["png","jpg","jpeg"])

        # Language selector
        target_lang = st.selectbox("Select language to translate", ["English","Hindi","Telugu","Spanish","French","German"])
        lang_map = {"English":"en", "Hindi":"hi","Telugu":"te","Spanish":"es","French":"fr","German":"de"}
        lang_code = lang_map.get(target_lang, "en")

        if uploaded_file:
            try:
                image = Image.open(uploaded_file)
                col1,col2 = st.columns([1,2])

                # ----- Left column: Image preview -----
                with col1:
                    st.markdown('<div class="card"><h4>Prescription Preview</h4></div>', unsafe_allow_html=True)
                    st.image(image, use_column_width=True)

                # ----- Right column: Tabs -----
                with col2:
                    extracted_text = extract_text(image)
                    simplified_text = simplify_text(extracted_text, target_lang=lang_code)
                    audio_file = text_to_speech(simplified_text)

                    tabs = st.tabs(["📝 Extracted Text","🗣️ Simplified Text","🔊 Audio"])

                    with tabs[0]:
                        st.markdown('<div class="card"><h4>Extracted Text</h4></div>', unsafe_allow_html=True)
                        st.text_area("", extracted_text, height=200, key="dashboard_extracted")
                        st.download_button("Download Extracted Text", data=extracted_text, file_name="extracted_text.txt", key="download1")

                    with tabs[1]:
                        st.markdown('<div class="card"><h4>Simplified / Translated Text</h4></div>', unsafe_allow_html=True)
                        st.text_area("", simplified_text, height=200, key="dashboard_simplified")
                        st.download_button("Download Simplified Text", data=simplified_text, file_name="simplified_text.txt", key="download2")

                    with tabs[2]:
                        st.markdown('<div class="card"><h4>Audio Instructions</h4></div>', unsafe_allow_html=True)
                        st.audio(audio_file, format="audio/mp3")
                        st.download_button("Download Audio", data=audio_file, file_name="instructions.mp3", mime="audio/mp3", key="download3")

                # Save history
                auth.save_history(
                    username=st.session_state.username,
                    file_name=uploaded_file.name,
                    extracted_text=extracted_text,
                    simplified_text=simplified_text
                )
                st.success("✅ Prescription processed successfully!")

            except Exception as e:
                st.error(f"❌ Error processing image: {e}")
        else:
            # Placeholder
            try:
                placeholder = Image.open("assets/placeholder_image.png")
                st.image(placeholder, caption="Upload a prescription to get started", use_column_width=True)
            except:
                st.info("Upload a prescription to get started")

    # ------------------- HISTORY -------------------
    elif menu_choice=="History":
        st.header("📜 History")
        history_records = auth.get_user_history(st.session_state.username)
        if history_records:
            for i, record in enumerate(history_records):
                st.markdown(f'<div class="card"><h4>{record["file_name"]} ({record["timestamp"]})</h4></div>', unsafe_allow_html=True)
                st.text_area("Extracted Text", record['extracted_text'], height=100, key=f"hist_extracted_{i}")
                st.text_area("Simplified Text", record['simplified_text'], height=100, key=f"hist_simplified_{i}")
                st.download_button("Download Extracted Text", record['extracted_text'], file_name=f"{record['file_name']}_extracted.txt", key=f"download_hist1_{i}")
                st.download_button("Download Simplified Text", record['simplified_text'], file_name=f"{record['file_name']}_simplified.txt", key=f"download_hist2_{i}")
        else:
            st.info("No prescription history available.")

    # ------------------- PROFILE -------------------
    elif menu_choice=="Profile":
        st.header("👤 Profile")
        st.write(f"**Username:** {st.session_state.username}")

        new_pass = st.text_input("New Password", type="password")
        if st.button("Change Password"):
            if new_pass:
                auth.add_user(st.session_state.username, new_pass)
                st.success("✅ Password updated successfully!")
            else:
                st.warning("Enter a valid password.")

        if st.button("Logout"):
            st.session_state.logged_in=False
            st.session_state.username=""
            st.experimental_rerun()