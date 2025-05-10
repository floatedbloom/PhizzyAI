import streamlit as st
import streamlit_image_coordinates as ic
import os
from PIL import Image

# Define a dictionary mapping HEX colors to muscle group names (from colors.txt)
MUSCLE_GROUPS = {
    'ffff00': 'right trap',
    '00ff00': 'right shoulder',
    'ff00ff': 'right chest',
    '0000ff': 'right bicep',
    'ff0000': 'right forearm',
    '00fff8': 'right oblique',
    '2b3d29': 'left trap',
    'b7ace8': 'left shoulder',
    '4b5849': 'left chest',
    '8425d8': 'left bicep',
    '907389': 'left forearm',
    'bf93e6': 'left oblique',
    '67ff00': 'abs',
    'ff00aa': 'groin',
    'ff7000': 'right thigh',
    '816e92': 'left thigh',
    '67a095': 'right calf',
    'c3eca7': 'left calf',
}

def render_body_diagram():
    image_path = os.path.join("media", "front.png")
    mask_path = os.path.join("media", "frontmask.png")
    display_width, display_height = 600, 900
    # Use session state to persist the highlighted image
    if 'highlighted_image' not in st.session_state:
        st.session_state.highlighted_image = Image.open(image_path).convert("RGBA").resize((display_width, display_height))
    mask = Image.open(mask_path).convert("RGB").resize((display_width, display_height))
    st.write("Click on the body diagram below:")
    # Use the in-memory image for click detection
    result = ic.streamlit_image_coordinates(
        st.session_state.highlighted_image,
        key="body-diagram",
        width=display_width,
        height=display_height,
    )
    if result is not None:
        # Reset the highlighted image to the original before highlighting a new muscle
        st.session_state.highlighted_image = Image.open(image_path).convert("RGBA").resize((display_width, display_height))
        x, y = result['x'], result['y']
        clicked_color = mask.getpixel((x, y))
        image_pixels = st.session_state.highlighted_image.load()
        mask_pixels = mask.load()
        for i in range(display_width):
            for j in range(display_height):
                if mask_pixels[i, j] == clicked_color:
                    image_pixels[i, j] = (255, 0, 0, 180)  # Highlight color
        st.write(f"You clicked at: x={x}, y={y}")
