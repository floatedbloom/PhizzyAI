import streamlit as st
import streamlit_image_coordinates as ic
import os
import json
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

    # Load body part data from body.json
    with open("body.json", "r") as f:
        body_data = json.load(f)

    if 'highlighted_image' not in st.session_state:
        st.session_state.highlighted_image = Image.open(image_path).convert("RGBA").resize((display_width, display_height))
    mask = Image.open(mask_path).convert("RGB").resize((display_width, display_height))

    # Add color selector for pain level
    color_option = st.radio(
        "Select pain level color:",
        ["Red (High Pain)", "Orange (Medium Pain)", "Grey (No Pain)"],
        index=0,
        horizontal=True
    )
    color_map = {
        "Red (High Pain)": ((255, 0, 0, 180), '8'),
        "Orange (Medium Pain)": ((255, 165, 0, 180), '5'),
        "Grey (No Pain)": ((128, 128, 128, 180), '1')
    }
    painlevel_to_color = {
        '8': (255, 0, 0, 180),
        '5': (255, 165, 0, 180),
        '1': (128, 128, 128, 180),
        '0': (128, 128, 128, 180),
        '': (128, 128, 128, 180),
        None: (128, 128, 128, 180)
    }
    highlight_color, pain_level = color_map[color_option]

    # Pre-highlight muscles based on body.json pain_level
    image_pixels = st.session_state.highlighted_image.load()
    mask_pixels = mask.load()
    for hex_color, muscle_name in MUSCLE_GROUPS.items():
        if muscle_name in body_data:
            pl = str(body_data[muscle_name].get('pain_level', ''))
            color = painlevel_to_color.get(pl, (128, 128, 128, 180))
            # Find all pixels in mask matching this muscle's color
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            for i in range(display_width):
                for j in range(display_height):
                    if mask_pixels[i, j] == rgb:
                        image_pixels[i, j] = color

    st.write("Click on the body diagram below:")
    result = ic.streamlit_image_coordinates(
        st.session_state.highlighted_image,
        key="body-diagram",
        width=display_width,
        height=display_height,
    )

    if result is not None:
        st.session_state.highlighted_image = Image.open(image_path).convert("RGBA").resize((display_width, display_height))
        x, y = result['x'], result['y']
        clicked_color = mask.getpixel((x, y))
        image_pixels = st.session_state.highlighted_image.load()
        mask_pixels = mask.load()

        for i in range(display_width):
            for j in range(display_height):
                if mask_pixels[i, j] == clicked_color:
                    image_pixels[i, j] = highlight_color  # Use selected highlight color

        # Find the body part name based on the clicked color
        hex_color = '%02x%02x%02x' % clicked_color[:3]
        body_part = MUSCLE_GROUPS.get(hex_color, "Unknown")

        if body_part in body_data:
            @st.dialog(f"{body_part} Info")
            def popup(body_part):
                info = body_data[body_part]
                st.write(f"Pain Points: {', '.join(info['pain_points'])}")
                st.write(f"Pain Level: {info['pain_level']}")
                st.write(f"Warnings: {', '.join(info['warnings'])}")
                st.write(f"Exercises: {', '.join(info['exercises'])}")
            popup(body_part)
        else:
            st.write("No data available for this body part.")

#function to return pain points from highleted image
def get_pain_points_from_image():
    pass