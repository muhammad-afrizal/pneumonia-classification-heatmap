import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import matplotlib.pyplot as plt
import tempfile
import os

# Set page config
st.set_page_config(
    page_title="Pneumonia Classification",
    page_icon="🫁",
    layout="wide"
)

# Title and description
st.title("🫁 Pneumonia Classification with Visual Heatmap")
st.markdown("""
This application uses deep learning to classify chest X-ray images as Normal or Pneumonia.
Upload an X-ray image to get the classification result along with visual explanations.
""")

# Load model
@st.cache_resource
def load_model():
    try:
        model = tf.keras.models.load_model("../modelPneumonia.h5")
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.info("Please make sure modelPneumonia.h5 is in the parent directory")
        return None

model = load_model()

if model is not None:
    # Define labels
    labels = ["Normal", "Pneumonia"]
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a chest X-ray image...", 
        type=["jpg", "jpeg", "png"],
        help="Upload a chest X-ray image for pneumonia classification"
    )
    
    if uploaded_file is not None:
        # Display the uploaded image
        col1, col2 = st.columns(2)
        
        with col1:
            # Read and display original image
            image = Image.open(uploaded_file)
            st.subheader("Uploaded X-ray Image")
            st.image(image, caption="Original Image", use_column_width=True)
        
        with col2:
            # Process image for prediction
            # Convert to grayscale and resize
            img = image.convert('L').resize((150, 150))
            img_array = np.array(img)
            
            # Apply CLAHE for contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(8, 8))
            img_clahe = clahe.apply(img_array)
            
            # Normalize and prepare for model
            img_clahe_normalized = img_clahe / 255.0
            img_input = img_clahe_normalized.reshape(1, 150, 150, 1)
            
            # Make prediction
            with st.spinner('Analyzing the image...'):
                pred = model.predict(img_input)[0][0]
                prediction = labels[int(pred >= 0.5)]
                confidence = (pred if pred >= 0.5 else 1 - pred) * 100
                
                # Display results
                st.subheader("Prediction Results")
                
                if prediction == "Normal":
                    st.success(f"✅ **{prediction}**")
                    st.metric(label="Confidence", value=f"{confidence:.2f}%")
                    st.info("The model indicates this X-ray appears normal. However, this result should not replace professional medical diagnosis.")
                else:
                    st.error(f"⚠️ **{prediction}**")
                    st.metric(label="Confidence", value=f"{confidence:.2f}%")
                    st.warning("The model indicates signs of pneumonia. Consult with a healthcare professional for proper diagnosis.")
        
        # Additional visualizations
        st.subheader("Visual Explanations")
        
        # Generate saliency map
        with st.spinner('Generating visual explanations...'):
            # Saliency Map
            input_tensor = tf.convert_to_tensor(img_input)
            with tf.GradientTape() as tape:
                tape.watch(input_tensor)
                preds = model(input_tensor)
                top_class = tf.argmax(preds[0])
                top_output = preds[:, top_class]

            grads = tape.gradient(top_output, input_tensor)[0]
            saliency = np.abs(grads.numpy())
            saliency = np.max(saliency, axis=-1)
            saliency = (saliency - saliency.min()) / (saliency.max() - saliency.min())
        
        # Display additional visualizations
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.subheader("CLAHE Enhanced Image")
            clahe_image = Image.fromarray(img_clahe)
            st.image(clahe_image, caption="After CLAHE Enhancement", use_column_width=True)
        
        with col4:
            st.subheader("Saliency Map Overlay")
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.imshow(img_clahe, cmap='gray')
            ax.imshow(saliency[0], cmap='hot', alpha=0.5)
            ax.axis('off')
            ax.set_title('Saliency Map Overlay')
            st.pyplot(fig)
        
        with col5:
            st.subheader("Saliency Heatmap")
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            ax2.imshow(saliency[0], cmap='hot')
            ax2.axis('off')
            ax2.set_title('Saliency Heatmap')
            st.pyplot(fig2)
        
        # Show interpretation
        st.subheader("Interpretation")
        if prediction == "Normal":
            st.write("""
            The model classified this X-ray as Normal with confidence {:.2f}%.
            The highlighted areas in the saliency map show which regions the model focused on
            when determining that the image shows normal lung patterns.
            """.format(confidence))
        else:
            st.write("""
            The model classified this X-ray as Pneumonia with confidence {:.2f}%.
            The highlighted areas in the saliency map show which regions in the lungs
            showed patterns consistent with pneumonia.
            """.format(confidence))
        
        st.markdown("---")
        st.info("ℹ️ **Note:** This tool is designed for educational and research purposes. It should not be used as a substitute for professional medical diagnosis.")

else:
    st.error("Model not loaded. Please ensure modelPneumonia.h5 is in the parent directory.")
    st.stop()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    <p>Pneumonia Classification System using Deep Learning</p>
    <p>This application uses a Convolutional Neural Network (CNN) model to classify chest X-rays.</p>
</div>
""", unsafe_allow_html=True)