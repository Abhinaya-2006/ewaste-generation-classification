import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetV2B0
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, GlobalAveragePooling2D, Dropout, Dense

# === Configuration ===
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

# ==== Class Labels ====
class_labels = ['Phone', 'Laptop', 'Battery', 'Mouse', 'Keyboard', 'TV', 'Charger', 'Camera', 'Printer', 'Remote']

# ==== Sidebar: Enhancements & Info ====
st.sidebar.header("⚙️ Settings")
enhance_contrast = st.sidebar.checkbox("Enhance Contrast", value=False)
show_model_summary = st.sidebar.checkbox("Show Model Summary")

if show_model_summary:
    with st.expander("📄 Model Summary"):
        stringlist = []
        model.summary(print_fn=lambda x: stringlist.append(x))
        summary_string = "\n".join(stringlist)
        st.text(summary_string)

# ==== Image Upload ====
uploaded_file = st.file_uploader("📷 Upload an E-Waste Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')

    if enhance_contrast:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)

    st.image(image, caption="🖼️ Uploaded Image", use_column_width=True)

    # ==== Preprocess ====
    img_array = np.array(image.resize((IMG_SIZE, IMG_SIZE))) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    st.info("Predicting (dummy mock prediction for now)...")

    # ==== Mock Prediction ====
    dummy_probs = np.random.dirichlet(np.ones(len(class_labels)), size=1)[0]
    predicted_class = class_labels[np.argmax(dummy_probs)]

    st.success(f"🔍 **Predicted Category: {predicted_class}**")

    # ==== Top-3 Predictions ====
    st.subheader("🏅 Top-3 Predictions")
    top_3_indices = np.argsort(dummy_probs)[-3:][::-1]
    for idx in top_3_indices:
        st.write(f"🔹 {class_labels[idx]} — **{dummy_probs[idx]*100:.2f}%**")

    # ==== Full Class Probabilities ====
    st.subheader("📊 Class Probability Scores")
    for i, prob in enumerate(dummy_probs):
        st.progress(prob)
        st.write(f"{class_labels[i]}: {prob:.4f}")
