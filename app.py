
import streamlit as st
import os
import time
import requests
import json

# --- Configuration & Setup ---
# Set page configuration for better aesthetics
st.set_page_config(page_title="🎵 AI Lyric Storyteller 🖼️", page_icon="📝", layout="centered")

# --- Gemini API Configuration ---
# IMPORTANT: Never hardcode API keys in production. Use environment variables.
# You will set this in Hugging Face Space secrets as GEMINI_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Using the latest Imagen 3.0 model for image generation
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict"

st.title("🎵 AI Lyric Storyteller 🖼️")
st.markdown(
    """
    Transform your favorite song lyrics into a captivating visual narrative!
    Enter lyrics line by line, and the AI will generate corresponding images
    to create a unique, AI-powered storyboard.
    """
)

if not GEMINI_API_KEY:
    st.error("Error: GEMINI_API_KEY environment variable not set. Please set it in Hugging Face Space secrets.")
    st.markdown(
        """
        ### API Key Troubleshooting Steps:
        1.  **Generate a new Gemini API Key:** Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) and create a fresh API key for a new project.
        2.  **Enable Generative Language API:** In your Google Cloud project (the one associated with your API key), ensure the "Generative Language API" is explicitly enabled. You can find this in the Google Cloud Console under "APIs & Services" -> "Enabled APIs & services".
        3.  **Link a Billing Account:** Even for free tier usage, some advanced Google APIs require a billing account to be linked to the project in Google Cloud. Make sure this is set up.
        4.  **Update Secret in Hugging Face:** Go to your Hugging Face Space settings, delete the old `GEMINI_API_KEY` secret, and add the new one.
        """
    )
    st.stop() # Stop the app if API key is missing

# Initialize session state for storing images if not already present
if 'all_generated_images' not in st.session_state:
    st.session_state.all_generated_images = []

# Text area for user to input lyrics
lyrics_input = st.text_area(
    "Enter song lyrics (one line or short phrase per line recommended for best results):",
    height=200,
    placeholder="""
Oh, the sun shines bright today
Birds are singing in the trees
A gentle breeze whispers through the leaves
Bringing peace to my soul
""",
    help="Each line or short phrase will be used to generate a separate image. Keep phrases descriptive!"
)

# Number of images to generate (Gemini API allows batch generation)
num_images_per_line = st.slider(
    "Number of images per lyric line (Choose 1 for faster results):",
    min_value=1,
    max_value=2, # Limiting to 2 for faster generation and less resource usage
    value=1,
    step=1,
    help="Generating more images per line takes longer and uses more API credits."
)

if st.button("Generate Visual Story"):
    if not lyrics_input.strip():
        st.warning("Please enter some lyrics to generate a visual story.")
    else:
        # Clear previous images when new generation starts
        st.session_state.all_generated_images = [] 
        lyric_lines = [line.strip() for line in lyrics_input.split('\n') if line.strip()]

        if not lyric_lines:
            st.warning("No valid lyric lines found after processing. Please ensure each line has content.")
        else:
            st.info(f"Generating {num_images_per_line} image(s) for each of your {len(lyric_lines)} lines. This might take a while!")

            # Iterate through each lyric line and generate image(s)
            for i, line in enumerate(lyric_lines):
                # Construct the prompt for the AI model
                # Enhance the prompt to guide the AI for better results
                # Add instructions for the model using natural language
                prompt_text = f"digital art, cinematic, vibrant, highly detailed, a visual scene representing the mood and imagery of: '{line}'"

                with st.spinner(f"Composing image(s) for: '{line}'..."):
                    try:
                        # --- Call the Gemini API for Image Generation ---
                        headers = {
                            "Content-Type": "application/json"
                        }
                        payload = {
                            "instances": {
                                "prompt": prompt_text
                            },
                            "parameters": {
                                "sampleCount": num_images_per_line # How many images to generate
                            }
                        }

                        # Implement exponential backoff for API calls
                        max_retries = 5
                        for attempt in range(max_retries):
                            try:
                                response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, json=payload)
                                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                                result = response.json()
                                break # If successful, break retry loop
                            except requests.exceptions.RequestException as e:
                                if attempt < max_retries - 1:
                                    sleep_time = 2 ** attempt # Exponential backoff
                                    st.warning(f"API call failed, retrying in {sleep_time} seconds (attempt {attempt + 1}/{max_retries})... Error: {e}")
                                    time.sleep(sleep_time)
                                else:
                                    raise # Re-raise if all retries fail

                        if result and result.get('predictions'):
                            for j, prediction in enumerate(result['predictions']):
                                if prediction.get('bytesBase64Encoded'):
                                    image_url = f"data:image/png;base64,{prediction['bytesBase64Encoded']}"
                                    st.session_state.all_generated_images.append({
                                        "url": image_url,
                                        "caption": f"'{line}' (Image {j+1})"
                                    })
                                else:
                                    st.error(f"Failed to retrieve image data for '{line}' (Image {j+1}).")
                        else:
                            st.error(f"Failed to generate image for: '{line}'. Unexpected AI response.")

                    except requests.exceptions.RequestException as e:
                        st.error(f"Gemini API Error for '{line}': {e}. Please check your API key, network, or Google Cloud quotas.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred for '{line}': {e}.")
                time.sleep(1) # Small delay to prevent hitting API rate limits too quickly, if applicable

            st.success("Visual story generation complete!")
            
# Display previously generated images from session state
if st.session_state.all_generated_images:
    st.markdown("---") # Separator for generated images
    st.subheader("Your Generated Visual Story:")
    num_cols = min(3, len(st.session_state.all_generated_images)) # Max 3 columns
    cols = st.columns(num_cols)
    for idx, image_data in enumerate(st.session_state.all_generated_images):
        with cols[idx % num_cols]:
            st.image(image_data["url"], caption=image_data["caption"], use_column_width=True)


st.markdown(
    """
    ---
    **How it works:**
    This application utilizes Google's **Imagen 3.0** model via the Gemini API
    to synthesize images from your text description. When you enter a prompt,
    it's sent to the Gemini API, which runs the powerful AI model on
    Google's infrastructure. The generated image data is then returned and
    displayed directly in your browser. This demonstrates the power of
    **text-to-image generative AI** in visualizing narratives.
    """
)

