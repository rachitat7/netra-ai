
import streamlit as st
import sqlite3
import json
import os
from datetime import datetime
from PIL import Image
from image_processing import prepare_image, check_image_quality

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Netra AI",
    page_icon="👁️",
    layout="wide"
)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "netra_ai.db")
IMAGE_DIR = os.path.join(APP_DIR, "screening_images")

os.makedirs(IMAGE_DIR, exist_ok=True)

# --------------------------------------------------
# OPTIONAL AI MODEL CONNECTION
# --------------------------------------------------

# The app works without a model.
# When a properly trained model is available, create
# model.py with a predict_image(image_path) function.

try:
    from model import predict_image
    AI_AVAILABLE = True
except ImportError:
    predict_image = None
    AI_AVAILABLE = False
except Exception:
    predict_image = None
    AI_AVAILABLE = False


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_connection():
    return sqlite3.connect(DB_PATH)


def initialise_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            symptoms TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            screening_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            image_path TEXT,
            image_type TEXT,
            image_quality TEXT,
            ai_result TEXT,
            worker_review TEXT,
            referral TEXT,
            notes TEXT,
            created_at TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
        )
    """)

    conn.commit()
    conn.close()


initialise_database()


def add_patient(name, age, gender, symptoms):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients
        (name, age, gender, symptoms, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        age,
        gender,
        symptoms,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    patient_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return patient_id


def get_patients():

    conn = get_connection()

    rows = conn.execute("""
        SELECT patient_id, name, age, gender, symptoms
        FROM patients
        ORDER BY patient_id DESC
    """).fetchall()

    conn.close()

    return rows


def save_screening(
    patient_id,
    image_path,
    image_type,
    image_quality,
    ai_result,
    worker_review,
    referral,
    notes
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO screenings (
            patient_id,
            image_path,
            image_type,
            image_quality,
            ai_result,
            worker_review,
            referral,
            notes,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        image_path,
        image_type,
        image_quality,
        json.dumps(ai_result),
        worker_review,
        referral,
        notes,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    conn.close()


def get_screenings():

    conn = get_connection()

    rows = conn.execute("""
        SELECT
            screenings.screening_id,
            patients.name,
            patients.age,
            screenings.image_type,
            screenings.image_quality,
            screenings.worker_review,
            screenings.referral,
            screenings.created_at,
            screenings.ai_result,
            screenings.notes
        FROM screenings
        JOIN patients
        ON screenings.patient_id = patients.patient_id
        ORDER BY screenings.screening_id DESC
    """).fetchall()

    conn.close()

    return rows


# --------------------------------------------------
# DESIGN
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #F7F2EC;
    color: #403747;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

h1 {
    color: #76546F !important;
    font-weight: 800 !important;
}

h2, h3 {
    color: #66516D !important;
}

p, label {
    color: #554C57;
}

.stButton > button {
    background: linear-gradient(135deg, #A982A2, #88749F);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1rem;
    font-weight: 600;
}

.stButton > button:hover {
    background: #76546F;
    color: white;
    border: none;
}

[data-testid="stFileUploader"] {
    background-color: #F0E8EF;
    border: 1px dashed #B58BA8;
    border-radius: 14px;
    padding: 15px;
}

hr {
    border-color: #DED2DC;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("# 👁️ Netra AI")
    st.caption("Bringing Eye Care Closer to Everyone.")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Register Patient",
            "New Screening",
            "Patient Records",
            "About Netra AI"
        ]
    )

    st.divider()

    if AI_AVAILABLE:
        st.success("AI model connected")
    else:
        st.warning("AI model not connected")

    st.caption("Offline-first screening assistance")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "Dashboard":

    st.title("👁️ Netra AI")

    st.subheader("Bringing Eye Care Closer to Everyone.")

    st.write(
        "A low-cost, offline-first eye screening assistance "
        "platform designed to support healthcare workers "
        "in underserved communities."
    )

    st.divider()

    patients = get_patients()
    screenings = get_screenings()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Registered Patients", len(patients))

    with col2:
        st.metric("Screenings Recorded", len(screenings))

    with col3:
        st.metric(
            "AI Model",
            "Connected" if AI_AVAILABLE else "Not connected"
        )

    st.divider()

    st.header("Screening Workflow")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #EDE1EC, #F7EDF3);
            padding: 25px;
            border-radius: 18px;
            min-height: 180px;
        ">
            <h2>👤 Patient Registration</h2>
            <p>Register patient details and record symptoms.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #E1ECE5, #EFF5F0);
            padding: 25px;
            border-radius: 18px;
            min-height: 180px;
        ">
            <h2>📷 Eye Screening</h2>
            <p>Upload an image, check its quality and record screening findings.</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.info(
        "Netra AI supports preliminary screening and referral "
        "workflows. It does not replace professional eye examination "
        "or provide a medical diagnosis."
    )


# --------------------------------------------------
# PATIENT REGISTRATION
# --------------------------------------------------

elif page == "Register Patient":

    st.title("👤 Patient Registration")

    st.write("Enter the patient's basic information.")

    with st.form("patient_registration"):

        name = st.text_input("Patient Name")

        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=18
            )

        with col2:
            gender = st.selectbox(
                "Gender",
                ["Not specified", "Female", "Male", "Other"]
            )

        symptoms = st.text_area(
            "Symptoms or observations",
            placeholder="Example: blurred vision, redness, discomfort..."
        )

        submitted = st.form_submit_button(
            "Register Patient",
            use_container_width=True
        )

        if submitted:

            if not name.strip():
                st.error("Please enter the patient's name.")

            else:

                patient_id = add_patient(
                    name.strip(),
                    age,
                    gender,
                    symptoms.strip()
                )

                st.success(
                    f"Patient registered successfully. Patient ID: {patient_id}"
                )


# --------------------------------------------------
# NEW SCREENING
# --------------------------------------------------

elif page == "New Screening":

    st.title("📷 New Eye Screening")

    st.write(
        "Select a registered patient and upload an appropriate "
        "eye image for preliminary screening."
    )

    patients = get_patients()

    if not patients:

        st.warning("Please register a patient before starting screening.")

    else:

        patient_options = {
            f"ID {p[0]} - {p[1]} (Age: {p[2]})": p[0]
            for p in patients
        }

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys())
        )

        patient_id = patient_options[selected_patient]

        st.divider()

        image_type = st.selectbox(
            "Image Type",
            [
                "Retinal fundus image",
                "External eye image",
                "Anterior-segment image"
            ]
        )

        st.info(
            "Different eye conditions require different image types. "
            "Only conditions supported by the selected imaging method "
            "and a validated model should be analysed."
        )

        uploaded_file = st.file_uploader(
            "Upload Eye Image",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded_file is not None:

            image = Image.open(uploaded_file).convert("RGB")

            st.subheader("Uploaded Image")

            st.image(
                image,
                caption="Uploaded image",
                use_container_width=True
            )

            processed_image, original_size = prepare_image(image)

            quality = check_image_quality(image)

            st.divider()

            st.subheader("Image Quality Check")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Width", f"{original_size[0]} px")

            with col2:
                st.metric("Height", f"{original_size[1]} px")

            with col3:
                st.metric("Processed Size", "224 × 224")

            st.write("**Quality observations:**")

            for message in quality["messages"]:
                st.write("• " + message)

            if quality["status"] == "Review required":
                st.warning(
                    "Image quality may be unsuitable. "
                    "Consider capturing another image."
                )
            else:
                st.success(
                    "No basic image-quality issue was detected. "
                    "This does not establish medical suitability."
                )

            st.divider()

            st.subheader("AI Screening")

            ai_result = {
                "status": "Not connected",
                "message": "No AI disease prediction has been performed."
            }

            if AI_AVAILABLE:

                if st.button("Run AI Screening", use_container_width=True):

                    try:

                        temp_path = os.path.join(
                            IMAGE_DIR,
                            "temporary_model_input.png"
                        )

                        processed_image.save(temp_path)

                        ai_result = predict_image(temp_path)

                        st.session_state["ai_result"] = ai_result
                        st.success("Model inference completed.")

                    except Exception as error:

                        st.error(
                            "AI model could not process this image. "
                            "Please check the model integration."
                        )

                        st.caption(str(error))

                ai_result = st.session_state.get("ai_result", ai_result)

                if ai_result.get("status") == "Not connected":
                    st.info("Select Run AI Screening to use the connected model.")
                else:
                    st.write("**Model output:**")
                    st.json(ai_result)

            else:

                st.warning(
                    "A trained AI model is not connected. "
                    "This prototype can check basic image properties "
                    "and record a healthcare worker's assessment, "
                    "but it cannot detect eye diseases yet."
                )

            st.divider()

            st.subheader("Healthcare Worker Review")

            worker_review = st.selectbox(
                "Screening observation",
                [
                    "Not yet assessed",
                    "No concern observed",
                    "Further examination recommended",
                    "Unable to assess"
                ]
            )

            referral = st.selectbox(
                "Referral decision",
                [
                    "Pending healthcare worker decision",
                    "Routine follow-up",
                    "Specialist examination recommended",
                    "Urgent medical assessment recommended"
                ]
            )

            notes = st.text_area(
                "Additional notes",
                placeholder="Enter observations or referral details..."
            )

            if st.button("Save Screening Record", use_container_width=True):

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                image_path = os.path.join(
                    IMAGE_DIR,
                    f"patient_{patient_id}_{timestamp}.png"
                )

                image.save(image_path)

                current_ai_result = st.session_state.get(
                    "ai_result",
                    {
                        "status": "Not connected",
                        "message": "No AI prediction performed."
                    }
                )

                save_screening(
                    patient_id,
                    image_path,
                    image_type,
                    quality["status"],
                    current_ai_result,
                    worker_review,
                    referral,
                    notes
                )

                st.session_state.pop("ai_result", None)

                st.success(
                    "Screening record saved successfully on this device."
                )


# --------------------------------------------------
# PATIENT RECORDS
# --------------------------------------------------

elif page == "Patient Records":

    st.title("📁 Patient Records")

    st.write(
        "View locally stored patient information and screening history."
    )

    patients = get_patients()

    st.subheader("Registered Patients")

    if patients:

        patient_data = []

        for p in patients:

            patient_data.append({
                "Patient ID": p[0],
                "Name": p[1],
                "Age": p[2],
                "Gender": p[3],
                "Symptoms": p[4]
            })

        st.dataframe(
            patient_data,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No patients registered yet.")

    st.divider()

    st.subheader("Screening History")

    screenings = get_screenings()

    if screenings:

        for record in screenings:

            (
                screening_id,
                name,
                age,
                image_type,
                quality,
                review,
                referral,
                created_at,
                ai_result,
                notes
            ) = record

            with st.expander(
                f"Screening #{screening_id} | {name} | {created_at}"
            ):

                st.write(f"**Age:** {age}")
                st.write(f"**Image type:** {image_type}")
                st.write(f"**Image quality:** {quality}")
                st.write(f"**Worker review:** {review}")
                st.write(f"**Referral:** {referral}")
                st.write(f"**Notes:** {notes}")

                try:
                    st.write("**AI result:**")
                    st.json(json.loads(ai_result))
                except Exception:
                    st.write("No AI result available.")

    else:
        st.info("No screening records available.")

    if screenings:

        export_rows = []

        for r in screenings:

            export_rows.append({
                "Screening ID": r[0],
                "Patient": r[1],
                "Age": r[2],
                "Image Type": r[3],
                "Image Quality": r[4],
                "Worker Review": r[5],
                "Referral": r[6],
                "Date": r[7],
                "AI Result": r[8],
                "Notes": r[9]
            })

        import pandas as pd

        csv_data = pd.DataFrame(export_rows).to_csv(index=False)

        st.download_button(
            "Download Screening Records (CSV)",
            data=csv_data,
            file_name="netra_ai_screening_records.csv",
            mime="text/csv"
        )


# --------------------------------------------------
# ABOUT
# --------------------------------------------------

elif page == "About Netra AI":

    st.title("About Netra AI")

    st.subheader("The Problem")

    st.write(
        "Rural and underserved health centres often lack "
        "ophthalmologists and specialised screening equipment. "
        "This can delay the identification of eye conditions."
    )

    st.subheader("Our Proposed Solution")

    st.write(
        "Netra AI aims to provide an affordable, offline-first "
        "screening workflow that supports healthcare workers "
        "with image quality checks, AI-assisted analysis of "
        "supported conditions, patient records and referral guidance."
    )

    st.subheader("Feasibility")

    st.write(
        "The prototype uses Python and Streamlit, local image "
        "processing and an SQLite database. A trained model can "
        "be integrated for local inference on compatible hardware."
    )

    st.subheader("Scalability")

    st.write(
        "The system can be extended with additional validated "
        "models, supported image types, languages and clinic-level "
        "record management."
    )

    st.subheader("Current Limitations")

    st.write("""
    - A trained multi-disease model is not included by default.
    - Image-quality checks are basic technical checks, not clinical validation.
    - Compatible retinal imaging hardware may be required.
    - The prototype has not been clinically validated.
    - Patient data is stored locally and needs appropriate access controls
      before real-world deployment.
    """)

    st.subheader("Our Approach")

    st.write(
        "We aim to address these limitations through appropriate "
        "image capture, validated datasets, model testing, healthcare "
        "worker review, data protection and gradual deployment."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Netra AI | Preliminary eye screening assistance | "
    "Not a substitute for professional medical diagnosis."
)




