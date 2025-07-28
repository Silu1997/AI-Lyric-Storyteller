---
title: AI Lyric Storyteller
emoji: 🎵
colorFrom: purple
colorTo: indigo
sdk: streamlit
sdk_version: "1.36.0" # You can check your streamlit version with `pip show streamlit` in your venv
app_file: app.py
pinned: false
---

# AI Lyric Storyteller

This application transforms song lyrics into a visual narrative using generative AI.
Simply enter your favorite lyrics, and the AI will create a sequence of images that visualize the song's story.

## How it works:
* **Text Input:** Users provide song lyrics or any short text.
* **AI Interpretation:** Each line/phrase is used as a prompt for a Text-to-Image AI model (like Stable Diffusion via Replicate).
* **Visual Output:** A series of unique images are generated, creating a visual storyline.

## Technologies Used:
* **Python**
* **Streamlit:** For the interactive web interface.
* **Replicate API:** To access powerful Text-to-Image models.

## Get Started:
1.  Enter lyrics in the text box.
2.  Click "Generate Visual Story".
3.  See your song come to life visually!