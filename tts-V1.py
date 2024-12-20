import streamlit as st
import pandas as pd
import os
import base64 

# Function to handle rating submission
def submit_ratings(selected_audio, selected_model, text_row, scores, user_name):
    scores['Audio File'] = selected_audio
    scores['Text'] = text_row.iloc[0]['Text']
    scores['Model'] = selected_model
    scores['User'] = user_name
    scores['Timestamp'] = pd.to_datetime("now")

    result_df = pd.DataFrame([scores])
    output_file = "ratings_output.xlsx"

    if os.path.exists(output_file):
        existing_df = pd.read_excel(output_file)
        combined_df = pd.concat([existing_df, result_df], ignore_index=True)
    else:
        combined_df = result_df

    combined_df.to_excel(output_file, index=False)
    return "Ratings submitted successfully!"

# Function to create a secure download link for admin
def download_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        href = f'<a href="data:file/xlsx;base64,{b64}" download="{os.path.basename(file_path)}">Download Ratings File</a>'
        return href
    else:
        return None

def main():
    st.title("TTS Audio File Rating App")

    # Admin login section
    st.sidebar.header("Admin Section")
    admin_password = st.sidebar.text_input("Enter Admin Password", type="password")
    admin_access = admin_password == "admin123"  # Replace with your secure password

    if admin_access:
        st.sidebar.success("Admin access granted.")
        if os.path.exists("ratings_output.xlsx"):
            st.sidebar.subheader("Download Ratings File")
            download_link = download_file("ratings_output.xlsx")
            if download_link:
                st.sidebar.markdown(download_link, unsafe_allow_html=True)
            else:
                st.sidebar.warning("No ratings file found.")
        else:
            st.sidebar.warning("No ratings available yet.")

    # Upload Excel file with text data
    st.sidebar.header("Upload Text Data")
    uploaded_file = st.sidebar.file_uploader("Choose an Excel file with Text column", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        if 'Text' not in df.columns or 'row_id' not in df.columns:
            st.error("The uploaded file must contain columns named 'row_id' and 'Text'.")
            return

        # Upload audio files
        st.sidebar.header("Upload All Audio Files")
        uploaded_audio_files = st.sidebar.file_uploader("Upload audio files (multiple files allowed)", type=["wav"], accept_multiple_files=True)

        if uploaded_audio_files:
            audio_files_dir = "uploaded_audio_files"
            os.makedirs(audio_files_dir, exist_ok=True)

            for audio_file in uploaded_audio_files:
                with open(os.path.join(audio_files_dir, audio_file.name), "wb") as f:
                    f.write(audio_file.read())

            # Predefined model names
            model_names = ["Google TTS", "Facebook MMS", "Indic TTS", "Venkaiah TTS"]
            selected_model = st.sidebar.selectbox("Choose a TTS model", model_names)

            model_audio_files = [f.name for f in uploaded_audio_files if selected_model.replace(" ", "") in f.name]

            if not model_audio_files:
                st.warning(f"No audio files found for the selected model: {selected_model}.")
            else:
                selected_audio = st.sidebar.selectbox("Choose an audio file", model_audio_files)

                if selected_audio:
                    st.subheader("Selected Audio and Corresponding Text")

                    try:
                        row_id = int(selected_audio.split("_")[0])
                    except ValueError:
                        st.error("Audio file naming format is incorrect. It should start with the row_id.")
                        return

                    text_row = df[df['row_id'] == row_id]

                    if not text_row.empty:
                        st.audio(os.path.join(audio_files_dir, selected_audio), format="audio/wav")
                        st.write(f"Text: {text_row.iloc[0]['Text']}")

                        user_name = st.text_input("Enter your name", "Anonymous")

                        if user_name:
                            st.subheader("Provide Ratings")
                            scores = {}
                            scores['Simple Sentences'] = st.slider("Simple Sentences", 1, 5, 1)
                            scores['Questions'] = st.slider("Questions", 1, 5, 1)
                            scores['Fluency'] = st.slider("Fluency", 1, 5, 1)
                            scores['Handling of Punctuation'] = st.slider("Handling of Punctuation", 1, 5, 1)
                            scores['Use of Technical Terms'] = st.slider("Use of Technical Terms", 1, 5, 1)
                            scores['Monotonicity'] = st.slider("Monotonicity", 1, 5, 1)

                            if st.button("Submit Ratings"):
                                message = submit_ratings(selected_audio, selected_model, text_row, scores, user_name)
                                st.success(message)
                    else:
                        st.warning(f"No matching text found for row_id: {row_id}.")
                else:
                    st.warning(f"No audio file selected for the model {selected_model}.")
        else:
            st.warning("Please upload audio files.")

if __name__ == "__main__":
    main()

