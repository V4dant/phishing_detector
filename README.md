🔐 Phishing URL Detection Using Machine Learning

This project aims to detect phishing URLs by leveraging machine learning techniques to classify URLs as **phishing** or **legitimate**. The model uses multiple URL features along with WHOIS and DNS information to accurately identify malicious URLs, helping to enhance cybersecurity.

📋 Features

- Extraction of 80+ URL features including length, special characters, IP usage, domain info, and WHOIS data
- Data preprocessing and cleaning for high-quality model input
- Machine learning models trained with Scikit-learn and XGBoost classifiers
- Model evaluation with accuracy, precision, recall, and confusion matrix metrics
- Flask-based web application for real-time URL phishing detection via a user-friendly interface
- Responsive frontend built with HTML, CSS

🛠 Technology Stack

- Python 3.x
- Flask (Web framework)
- Scikit-learn, XGBoost (Machine learning)
- Pandas, NumPy (Data manipulation)
- python-whois, tldextract (Domain & WHOIS extraction)
- HTML, CSS (Frontend)
- PyCharm (Development IDE)

📁 Project Structure
phishing_detector/
├── app.py # Flask web application
├── phishing_model.pkl # Trained ML model file
├── feature_extraction.py # URL feature extraction utilities
├── phishing.csv # Dataset used for training/testing
├── requirements.txt # Python dependencies
├── templates/
│ └── index.html # Frontend HTML page
├── static/
│ └── style.css # CSS styles
└── README.md # Project documentation

🚀 How to Run Locally

1. Clone the repository
   git clone https://github.com/V4dant/phishing_detector.git
   cd phishing_detector

2.Create a virtual environment and activate it
On macOS/Linux:
python3 -m venv venv
source venv/bin/activate
On Windows:
python -m venv venv
venv\Scripts\activate

3.Install dependencies
pip install -r requirements.txt

4.Run the Flask application
python app.py

5.Open your browser and go to
http://localhost:5000
Enter a URL to test if it is phishing or safe.

📈 Model Performance
Achieves approximately 96% accuracy on the testing dataset
Model uses Random Forest and XGBoost classifiers for robust detection

