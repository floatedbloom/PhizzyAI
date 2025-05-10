import streamlit as st
import streamlit_image_coordinates as ic
import os
from PIL import Image, ImageDraw

def render_body_diagram():
    image_path = os.path.join("media", "front.webp")
    # Load the image
    image = Image.open(image_path).convert("RGBA")
    # Set a fixed display size
    display_width = 600
    display_height = 900  # Adjust as needed for your image aspect ratio
    image = image.resize((display_width, display_height))
    # Get click coordinates
    st.write("Click on the body diagram below:")
    result = ic.streamlit_image_coordinates(
        image_path,
        key="body-diagram",
        width=display_width,
        height=display_height,
    )
    # If clicked, draw a red ellipse to highlight a muscle group
    if result is not None:
        draw = ImageDraw.Draw(image)
        x, y = result['x'], result['y']  # Use coordinates as provided
        muscle_width, muscle_height = 60, 30
        draw.ellipse((x-muscle_width//2, y-muscle_height//2, x+muscle_width//2, y+muscle_height//2), fill=(255,0,0,128), outline=(255,0,0,255))
        st.write(f"You clicked at: x={x}, y={y}")
        st.image(image, use_container_width=True)
    else:
        st.image(image, use_container_width=True)
