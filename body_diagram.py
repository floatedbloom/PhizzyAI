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

    # Define pain level to color mapping
    painlevel_to_color = {
        '1': (128, 128, 128, 180),  # Gray for pain levels 1-3
        '2': (128, 128, 128, 180),
        '3': (128, 128, 128, 180),
        '4': (255, 165, 0, 180),  # Orange for pain levels 4-7
        '5': (255, 165, 0, 180),
        '6': (255, 165, 0, 180),
        '7': (255, 165, 0, 180),
        '8': (255, 0, 0, 180),    # Red for pain levels 8-10
        '9': (255, 0, 0, 180),
        '10': (255, 0, 0, 180),
        '0': (128, 128, 128, 180),
        '': (128, 128, 128, 180),
        None: (128, 128, 128, 180)
    }

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
                    pass  # Remove the logic that changes the clicked body part to red

        # Find the body part name based on the clicked color
        hex_color = '%02x%02x%02x' % clicked_color[:3]
        body_part = MUSCLE_GROUPS.get(hex_color, "Unknown")

        if body_part in body_data and st.session_state.get("last_clicked") != (x, y):
            # Update the last clicked position
            st.session_state["last_clicked"] = (x, y)

            # Use session state to track popup visibility
            popup_key = f"popup_{body_part}"
            if popup_key not in st.session_state:
                st.session_state[popup_key] = True  # Initialize the flag

            if st.session_state[popup_key]:
                @st.dialog(f"{body_part} Info")
                def popup():
                    info = body_data[body_part]
                    st.write(f"Pain Points: {', '.join(info['pain_points'])}")
                    st.write(f"Pain Level: {info['pain_level']}")
                    st.write(f"Warnings: {', '.join(info['warnings'])}")
                    st.write(f"Exercises: {', '.join(info['exercises'])}")

                    # Add a close button to explicitly close the popup
                    if st.button("Close"):
                        st.session_state[popup_key] = False

                popup()

        else:
            st.write("No data available for this body part.")

        # Update JSON: set pain_level to '8' for this muscle
        if body_part in MUSCLE_GROUPS:
            muscle_name = MUSCLE_GROUPS[hex_color]
            if muscle_name in body_data:
                body_data[muscle_name]['pain_level'] = '8'
            else:
                body_data[muscle_name] = {
                    'pain_points': [],
                    'pain_level': '8',
                    'warnings': [],
                    'exercises': []
                }
            with open("body.json", "w") as f:
                json.dump(body_data, f, indent=2)
            # Toggle selection
            if muscle_name in st.session_state.selected_muscles:
                st.session_state.selected_muscles.remove(muscle_name)
            else:
                st.session_state.selected_muscles.add(muscle_name)
            st.experimental_rerun()
            st.write(f"You clicked on: **{muscle_name.title()}**")

#function to return pain points from highleted image
def get_pain_points_from_image():
    pass