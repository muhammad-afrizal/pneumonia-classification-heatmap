# Pneumonia Classification - Streamlit Version

This is the Streamlit version of the pneumonia classification system. It provides the same functionality as the Flask version but in a Streamlit interface optimized for deployment on Streamlit Community Cloud.

## Features

- Upload chest X-ray images for classification
- Real-time pneumonia detection (Normal vs Pneumonia)
- Visual heatmaps showing which areas influenced the decision
- CLAHE image enhancement for better contrast
- Confidence scores for predictions

## Requirements

- streamlit==1.30.0
- tensorflow==2.15.0
- opencv-python==4.8.1.78
- Pillow==10.1.0
- numpy==1.24.3
- matplotlib==3.7.3

## How to Run

1. Make sure you have the model file `modelPneumonia.h5` in the parent directory
2. Install requirements: `pip install -r requirements.txt`
3. Run with: `streamlit run app.py`

## Deployment

This version is designed for deployment on Streamlit Community Cloud:
1. Push your code to a GitHub repository
2. Connect to Streamlit Community Cloud
3. Make sure your model file is accessible