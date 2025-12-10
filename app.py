import streamlit as st
import os
import tempfile
from PIL import Image, ImageDraw
import io
import numpy as np
from streamlit_drawable_canvas import st_canvas # New Library
from grpc_client import run_prediction, scan_blueprint

st.set_page_config(page_title="Bobyard AI Detector", layout="wide")
st.title("One-Shot Blueprint Scanner 🏗️")

tab1, tab2 = st.tabs(["🔍 Simple Comparator", "🗺️ Smart Scanner (The Hook)"])

# ==========================================
# TAB 1: KEEP AS IS (Good for debugging)
# ==========================================
with tab1:
    st.info("Upload two separate images to compare them.")
    c1, c2 = st.columns(2)
    ref_file = c1.file_uploader("Reference Symbol", type=["png", "jpg"], key="ref1")
    query_file = c2.file_uploader("Query Image", type=["png", "jpg"], key="query1")
    
    if ref_file and query_file and st.button("Compare", key="btn1"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tf1:
            tf1.write(ref_file.getvalue()); path1 = tf1.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tf2:
            tf2.write(query_file.getvalue()); path2 = tf2.name
        res = run_prediction(path1, path2)
        if res and res.is_match: st.success(f"Match! Score: {res.similarity_score:.2f}")
        else: st.error(f"No Match. Score: {res.similarity_score:.2f}")
        os.remove(path1); os.remove(path2)

# ==========================================
# TAB 2: THE BOBYARD WORKFLOW
# ==========================================
with tab2:
    st.markdown("### 1. Upload Blueprint & Select Target")
    
    blueprint_file = st.file_uploader("Upload Blueprint PDF/Image", type=["png", "jpg", "jpeg"], key="blue_canvas")
    
    if blueprint_file:
        # Load and Resize Image for Display (otherwise canvas is too big)
        original_image = Image.open(blueprint_file).convert("RGB")
        w, h = original_image.size
        aspect_ratio = w / h
        
        # Display width (responsive)
        display_width = 700 
        display_height = int(display_width / aspect_ratio)
        
        # Calculate Scale Factor (To translate canvas coords back to real pixels)
        scale_factor = w / display_width
        
        st.write("👉 **Draw a box around the symbol you want to find:**")
        
        # DRAWING CANVAS
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Transparent Orange
            stroke_width=2,
            stroke_color="#FF0000",
            background_image=original_image.resize((display_width, display_height)),
            update_streamlit=True,
            height=display_height,
            width=display_width,
            drawing_mode="rect",
            key="canvas",
        )

        # CHECK IF USER DREW A BOX
        if canvas_result.json_data is not None:
            objects = canvas_result.json_data["objects"]
            
            if len(objects) > 0:
                # Get the last drawn box
                box = objects[-1] 
                
                # Scale coords back to original image size
                real_x = int(box["left"] * scale_factor)
                real_y = int(box["top"] * scale_factor)
                real_w = int(box["width"] * scale_factor)
                real_h = int(box["height"] * scale_factor)
                
                # Crop the "One Shot" symbol
                cropped_symbol = original_image.crop((real_x, real_y, real_x + real_w, real_y + real_h))
                
                # Preview the selection
                st.sidebar.markdown("---")
                st.sidebar.image(cropped_symbol, caption="Target Symbol (One-Shot)", width=150)
                
                if st.sidebar.button("🚀 Scan Entire Blueprint"):
                    with st.spinner("Analyzing Blueprint..."):
                        
                        # Save Symbol and Blueprint to temp files for the gRPC client
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tf_sym:
                            cropped_symbol.save(tf_sym, format="PNG")
                            path_sym = tf_sym.name
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tf_blue:
                            # We can just save the original bytes we already have
                            blueprint_file.seek(0)
                            tf_blue.write(blueprint_file.read())
                            path_blue = tf_blue.name

                        # CALL SERVER
                        result = scan_blueprint(path_sym, path_blue)

                        # CLEANUP
                        os.remove(path_sym)
                        os.remove(path_blue)

                        # DRAW RESULTS
                        if result:
                            draw_img = original_image.copy()
                            draw = ImageDraw.Draw(draw_img)
                            
                            # Draw boxes on full resolution image
                            for match in result.matches:
                                draw.rectangle(
                                    [match.x, match.y, match.x + match.width, match.y + match.height],
                                    outline="lime",
                                    width=5
                                )
                            
                            st.success(f"Found {len(result.matches)} matches!")
                            st.image(draw_img, caption="Detection Results", use_column_width=True)
                        else:
                            st.error("Scan failed.")
            else:
                st.info("Draw a rectangle on the image to select a symbol.")