# 👁️ Netra AI
### AI-Assisted Eye Screening for Underserved Communities

**Netra AI** is an offline-first eye-screening assistance prototype designed to support healthcare workers in rural and underserved areas through image processing and experimental AI.

## ✨ Key Features
- 👤 Patient registration and record management
- 📸 External-eye image upload and screening
- 🔍 Image quality checks (brightness, blur and resolution)
- 🤖 Experimental AI classification
- 📋 Screening history and CSV export
- 💾 Local data storage using SQLite

## 🛠️ Tech Stack
- **Language:** Python
- **Interface:** Streamlit
- **AI Model:** TensorFlow / Keras, MobileNetV2
- **Image Processing:** OpenCV, Pillow, NumPy
- **Database:** SQLite

## ⚙️ Run Locally

```bash
git clone https://github.com/rachitat7/netra-ai.git
cd netra-ai

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## 🧠 AI Model
- Based on MobileNetV2 transfer learning.
- Currently classifies external-eye images into **Normal** and **Blepharitis**.
- Trained on a small dataset; further validation and improvement are needed.

## 🚀 Future Scope
- Larger and more diverse training datasets
- Improved model accuracy and reliability
- Additional eye-screening capabilities
- Multilingual and smartphone-friendly access
- Clinical evaluation and validation

## ⚠️ Disclaimer
Netra AI is an experimental academic prototype, not a medical diagnostic tool. Its predictions are not clinically validated and must not replace professional eye examinations.

---

**Built with ❤️ for accessible eye-care support.**
