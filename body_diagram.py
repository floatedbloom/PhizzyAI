import streamlit as st
import streamlit_image_coordinates as ic
import os
from PIL import Image

# Define a dictionary mapping HEX colors to muscle group names
MUSCLE_GROUPS = {
    '#ff0000': "Left Forearm",
    '#0000ff': "Left Upper Arm",
    '#00ffff': "Left Side",
    '#ffa500': "Left Thigh",
    '#00ff00': "Abs",
    '#ff00ff': "Left Chest",
    '#ffff00': "Neck",
    '#008000': "Right Chest",
    '#800080': "Right Upper Arm",
    '#808080': "Right Forearm",
    '#800000': "Right Side",
    '#808000': "Right Thigh",
    '#008080': "Left Calf",
    '#adff2f': "Right Calf",
    '#ff1493': "Groin",
    '#a9a9a9': "Other"
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
