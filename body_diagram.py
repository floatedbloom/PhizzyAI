import streamlit as st
import streamlit_image_coordinates as ic
import os
from PIL import Image

def render_body_diagram():
    image_path = os.path.join("media", "front.png")
    mask_path = os.path.join("media", "frontmask.png")
    display_width, display_height = 600, 900
    image = Image.open(image_path).convert("RGBA").resize((display_width, display_height))
    mask = Image.open(mask_path).convert("RGB").resize((display_width, display_height))
    st.write("Click on the body diagram below:")
    result = ic.streamlit_image_coordinates(
        image_path,
        key="body-diagram",
        width=display_width,
        height=display_height,
    )
    if result is not None:
        x, y = result['x'], result['y']
        clicked_color = mask.getpixel((x, y))
        image_pixels = image.load()
        mask_pixels = mask.load()
        for i in range(display_width):
            for j in range(display_height):
                if mask_pixels[i, j] == clicked_color:
                    # Highlight color (e.g., semi-transparent red)
                    r, g, b, a = image_pixels[i, j]
                    image_pixels[i, j] = (255, 0, 0, 180)
        st.write(f"You clicked at: x={x}, y={y}")
        st.image(image, use_container_width=True)
    else:
        st.image(image, use_container_width=True)
