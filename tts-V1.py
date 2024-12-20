import streamlit as st
import pandas as pd
import os

def submit_ratings(selected_audio, selected_model, text_row, scores, user_name):
    # Create a dictionary to store the ratings and related information
    scores['Audio File'] = selected_audio
    scores['Text'] = text_row.iloc[0]['Text']
    scores['Model'] = selected_model
    scores['User'] = user_name
    scores['Timestamp'] = pd.to_datetime("now")  # Optional, to track when ratings were submitted

    # Convert ratings to DataFrame
    result_df = pd.DataFrame([scores])

    output_file = "ratings_output.xlsx"

    if os.path.exists(output_file):
        # Read existing ratings and append the new ones
        existing_df = pd.read_excel(output_file)
        combined_df = pd.concat([existing_df, result_df], ignore_index=True)
    else:
        # If the file doesn't exist, create a new one
        combined_df = result_df

    # Save the updated DataFrame to Excel
    combined_df.to_excel(output_file, index=False)
    return "Ratings submitted successfully!"

def main():
    st.title("TTS Audio File Rating App")

    # Upload Excel file with text data
    st.sidebar.header("Upload Text Data")
    uploaded_file = st.sidebar.file_uploader("Choose an Excel file with Text column", type=["xlsx"])

    if uploaded_file:
        # Read uploaded Excel file
        df = pd.read_excel(uploaded_file)

        if 'Text' not in df.columns or 'row_id' not in df.columns:
            st.error("The uploaded file must contain columns named 'row_id' and 'Text'.")
            return

        # User input for model directory
        st.sidebar.header("Upload All Audio Files")
        uploaded_audio_files = st.sidebar.file_uploader("Upload audio files (multiple files allowed)", type=["wav"], accept_multiple_files=True)

        if uploaded_audio_files:
            # Save uploaded audio files temporarily
            audio_files_dir = "uploaded_audio_files"
            os.makedirs(audio_files_dir, exist_ok=True)

            for audio_file in uploaded_audio_files:
                with open(os.path.join(audio_files_dir, audio_file.name), "wb") as f:
                    f.write(audio_file.read())

            # Predefined model names
            model_names = ["Google TTS", "Facebook MMS", "Indic TTS", "Venkaiah TTS"]

            selected_model = st.sidebar.selectbox("Choose a TTS model", model_names)

            # Filter audio files for the selected model
            model_audio_files = [f.name for f in uploaded_audio_files if selected_model.replace(" ", "") in f.name]

            if not model_audio_files:
                st.warning(f"No audio files found for the selected model: {selected_model}.")
            else:
                # Dropdown for selecting audio file
                selected_audio = st.sidebar.selectbox("Choose an audio file", model_audio_files)

                if selected_audio:
                    # Display corresponding text
                    st.subheader("Selected Audio and Corresponding Text")

                    # Extract row_id from the audio file name (assuming format: row_id_model_filename.extension)
                    try:
                        row_id = int(selected_audio.split("_")[0])
                    except ValueError:
                        st.error("Audio file naming format is incorrect. It should start with the row_id.")
                        return

                    text_row = df[df['row_id'] == row_id]

                    if not text_row.empty:
                        st.audio(os.path.join(audio_files_dir, selected_audio), format="audio/wav")
                        st.write(f"Text: {text_row.iloc[0]['Text']}")

                        # Collect user name before submitting ratings
                        user_name = st.text_input("Enter your name", "Anonymous")

                        if user_name:
                            # Collect ratings
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
