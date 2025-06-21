import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetV2B0
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, GlobalAveragePooling2D, Dropout, Dense

st.set_page_config(page_title="🔍 E-Waste Object Classifier", layout="centered")
st.title("🔋 E-Waste Image Classifier")
st.markdown("Upload an image to classify it as Phone, Laptop, Battery, etc.")

IMG_SIZE = 128

# ==== Build Model (Dummy - Not Trained) ====
@st.cache_resource
def build_model():
    base_model = EfficientNetV2B0(weights='imagenet', include_top=False, input_tensor=Input(shape=(IMG_SIZE, IMG_SIZE, 3)))
    base_model.trainable = False
    x = GlobalAveragePooling2D()(base_model.output)
    x = Dropout(0.2)(x)
    output = Dense(10, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=output)
    return model

model = build_model()

# ==== Define Labels ====
class_labels = ['Phone', 'Laptop', 'Battery', 'Mouse', 'Keyboard', 'TV', 'Charger', 'Camera', 'Printer', 'Remote']

# ==== Upload File ====
uploaded_file = st.file_uploader("📷 Upload an E-Waste Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Resize and preprocess image
    img_array = np.array(image.resize((IMG_SIZE, IMG_SIZE))) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    st.info("Predicting (random mock prediction for now)...")

    # === Dummy random prediction (replace this with model.predict later) ===
    dummy_probs = np.random.dirichlet(np.ones(len(class_labels)), size=1)[0]
    predicted_class = class_labels[np.argmax(dummy_probs)]

    st.success(f"🔍 Predicted Category: **{predicted_class}**")

    st.subheader("🔢 Prediction Probabilities")
    for i, prob in enumerate(dummy_probs):
        st.write(f"{class_labels[i]}: {prob:.4f}")
