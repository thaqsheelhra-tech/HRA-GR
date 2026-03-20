import streamlit as st
import os
from datetime import date
from app import get_db, UPLOAD_FOLDER

st.header("Company Policies & Documents")

tab1, tab2 = st.tabs(["Upload", "Library"])

with tab1:
    uploaded_file = st.file_uploader("Upload PDF / Word / Image", type=["pdf", "docx", "png", "jpg", "jpeg"])
    title = st.text_input("Document Title (optional)")

    if uploaded_file and st.button("Upload Document"):
        filename = uploaded_file.name
        safe_name = filename.replace(" ", "_")
        path = os.path.join(UPLOAD_FOLDER, safe_name)

        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with get_db() as conn:
            conn.execute(
                "INSERT INTO policies (filename, title, uploaded_at) VALUES (?, ?, ?)",
                (safe_name, title.strip() or filename, date.today())
            )
            conn.commit()

        st.success(f"Uploaded: **{filename}**")

with tab2:
    with get_db() as conn:
        docs = conn.execute("SELECT * FROM policies ORDER BY uploaded_at DESC").fetchall()

    if not docs:
        st.info("No documents uploaded yet.")
    else:
        for doc in docs:
            col1, col2 = st.columns([4,1])
            col1.write(f"**{doc['title'] or doc['filename']}**  •  {doc['uploaded_at']}")
            if col2.button("Download", key=f"dl_{doc['id']}"):
                with open(os.path.join(UPLOAD_FOLDER, doc['filename']), "rb") as f:
                    st.download_button(
                        label="Click to download",
                        data=f,
                        file_name=doc['filename'],
                        mime="application/octet-stream",
                        key=f"btn_{doc['id']}"
                    )
