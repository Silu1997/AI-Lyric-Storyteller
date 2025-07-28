import streamlit as st
import replicate
import os
import time

# --- Configuration & Setup ---
# Set page configuration for better aesthetics
st.set_page_config(page_title="🎵 AI Lyric Storyteller 🖼️", page_icon="📝", layout="centered")

# --- UI Elements ---
st.title("🎵 AI Lyric Storyteller 🖼️")
st.markdown(
    """
    Transform your favorite song lyrics into a captivating visual narrative!
    Enter lyrics line by line, and the AI will generate corresponding images
    to create a unique, AI-powered storyboard.
    """
)

st.warning("Ensure your `REPLICATE_API_TOKEN` is set as an environment variable before running. Check the console for errors!")

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

# Slider for image generation steps (higher = better quality, slower)
num_inference_steps = st.slider(
    "Image Detail/Quality (Inference Steps):",
    min_value=20,
    max_value=75,
    value=50,
    step=5,
    help="Higher values lead to more detailed images but take longer to generate."
)

# Button to trigger image generation
if st.button("Generate Visual Story"):
    # Check if API token is set
    if not os.getenv("REPLICATE_API_TOKEN"):
        st.error("Error: REPLICATE_API_TOKEN environment variable not set. Please set it to your Replicate API key.")
    # Check if lyrics are provided
    elif not lyrics_input.strip(): # .strip() removes leading/trailing whitespace
        st.warning("Please enter some lyrics to generate a visual story.")
    else:
        # Split lyrics into individual lines/phrases
        lyric_lines = [line.strip() for line in lyrics_input.split('\n') if line.strip()]

        if not lyric_lines:
            st.warning("No valid lyric lines found after processing. Please ensure each line has content.")
        else:
            st.info(f"Generating {len(lyric_lines)} images for your story. This may take a while...")

            # Container for generated images
            image_columns = st.columns(min(3, len(lyric_lines))) # Display up to 3 columns, adjust based on number of lines
            current_col_idx = 0

            # Iterate through each lyric line and generate an image
            for i, line in enumerate(lyric_lines):
                # Construct the prompt for the AI model
                # Enhance the prompt to guide the AI for better results
                prompt = f"digital art, vibrant, highly detailed, cinematic, --ar 16:9, a visual scene representing the mood and imagery of: '{line}'"

                with st.spinner(f"Generating image for: '{line}'..."):
                    try:
                        # Call the Replicate API for text-to-image generation
                        # Using Stable Diffusion XL for better quality if available, or v1.5
                        # You can choose a different model version from Replicate if preferred
                        output = replicate.run(
                            "runwayml/stable-diffusion-v1-5:c27f689a6bc8ea238bb97825af5e61cf886bb7885b5420310709875f0f3536c1", # Stable Diffusion v1.5 # SDXL model
                            # "stability-ai/stable-diffusion:ac732df83ee47b6b653aea6b56c0f87d63d2dc547d0e74f73bce38bbabfbf079", # SD v1.5 model
                            input={
                                "prompt": prompt,
                                "num_inference_steps": num_inference_steps,
                                "width": 1024, # SDXL default, adjust for other models if needed
                                "height": 768, # SDXL default
                                "guidance_scale": 7.5 # Controls adherence to prompt vs creativity
                            }
                        )

                        if output and len(output) > 0:
                            # Display the image in a column
                            with image_columns[current_col_idx]:
                                st.image(output[0], caption=f"'{line}'", use_column_width=True)
                            current_col_idx = (current_col_idx + 1) % len(image_columns) # Cycle through columns
                        else:
                            st.error(f"Failed to generate image for: '{line}'. No output received from AI.")

                    except replicate.exceptions.ReplicateException as e:
                        st.error(f"Replicate API Error for '{line}': {e}. Please check your API key, prompt, or Replicate usage limits.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred for '{line}': {e}.")
                time.sleep(1) # Small delay to prevent hitting API rate limits too quickly, if applicable

            st.success("Visual story generation complete!")
            st.markdown(
                """
                ---
                **About this Story:**
                Each image above was uniquely generated by a powerful Text-to-Image AI model (like Stable Diffusion)
                based on your provided lyrical lines. This demonstrates **Generative AI's ability to interpret
                and visualize textual narratives sequentially**, creating a unique visual accompaniment to
                creative writing.
                """
            )

