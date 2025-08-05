app.py

from flask import Flask, render_template, request
import joblib
import numpy as np
from feature_extraction import extract_features_from_url  # Your custom extractor

app = Flask(__name__)

# Load the saved model
model = joblib.load('phishing_model.pkl')

print(f"Model expects {model.n_features_in_} features as input.")  # Debug print


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    url = request.form['url']
    try:
        features = extract_features_from_url(url)
        print(f"Extracted features count: {len(features)}")

        # If features is dict, convert to list after removing label key
        if isinstance(features, dict):
            features.pop('status', None)  # Remove label if present
            features = list(features.values())

        # Pad features with zeros if less than expected
        expected_len = model.n_features_in_
        if len(features) < expected_len:
            features.extend([0] * (expected_len - len(features)))
            print(f"Padded features with zeros to length: {len(features)}")
        elif len(features) > expected_len:
            features = features[:expected_len]  # Or raise error if preferred
            print(f"Trimmed features to length: {len(features)}")

        features_array = np.array(features).reshape(1, -1)
        prediction = model.predict(features_array)[0]
        result = "🔴 Phishing" if prediction == 1 else "🟢 Legitimate"
    except Exception as e:
        result = f"Error: {e}"
    return render_template('index.html', url=url, prediction=result)


if __name__ == '__main__':
    app.run(debug=True)


index.html

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Phishing URL Detector</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}" />
</head>
<body>
  <div class="container">
    <h1>🔍 Phishing URL Detection</h1>

    <!-- Dark Mode Toggle -->
    <button id="toggle-theme" aria-label="Toggle Dark Mode">🌙 Dark Mode</button>

    <!-- Explanation Section -->
    <section class="info">
      <h2>Why Check URLs?</h2>
      <p>
        Phishing is a cyber attack where attackers try to steal your sensitive information by tricking you with fake websites. Always verify URLs before entering personal info!
      </p>
    </section>

    <!-- URL Input Form -->
    <form action="/predict" method="post" id="url-form">
      <input type="text" name="url" placeholder="Enter URL to check" required autocomplete="off" />
      <button type="submit">Check</button>
    </form>

    <!-- Prediction Result -->
    {% if prediction %}
    <section class="result {% if prediction == '🟢 Legitimate' %}success{% else %}error{% endif %}" id="result-section">
      <p><strong>URL:</strong> <span id="result-url">{{ url }}</span></p>
      <p><strong>Prediction:</strong> <span id="result-text">{{ prediction }}</span></p>

      <!-- Copy to Clipboard -->
      <button id="copy-url">Copy URL</button>
      <button id="copy-prediction">Copy Prediction</button>

      <!-- Optional: Detailed Explanation -->
      {% if explanation %}
      <div class="explanation">
        <h3>Why?</h3>
        <p>{{ explanation }}</p>
      </div>
      {% endif %}
    </section>
    {% endif %}

    <!-- Security Tips -->
    <section class="tips">
      <h2>Security Tips</h2>
      <ul>
        <li>Don’t click suspicious or unexpected links.</li>
        <li>Check the URL spelling carefully.</li>
        <li>Look for HTTPS and a valid certificate.</li>
        <li>Use two-factor authentication whenever possible.</li>
      </ul>
    </section>

    <!-- Footer -->
    <footer>
      <p>Made by Your Name | <a href="https://www.linkedin.com/in/yourprofile" target="_blank" rel="noopener">LinkedIn</a></p>
    </footer>
  </div>

  <script>
    // Dark Mode Toggle
    const toggleBtn = document.getElementById('toggle-theme');
    toggleBtn.addEventListener('click', () => {
      document.body.classList.toggle('dark-mode');
      toggleBtn.textContent = document.body.classList.contains('dark-mode') ? '☀️ Light Mode' : '🌙 Dark Mode';
    });

    // Copy Buttons
    const copyUrlBtn = document.getElementById('copy-url');
    const copyPredictionBtn = document.getElementById('copy-prediction');

    if (copyUrlBtn) {
      copyUrlBtn.addEventListener('click', () => {
        const urlText = document.getElementById('result-url').textContent;
        navigator.clipboard.writeText(urlText).then(() => alert('URL copied to clipboard!'));
      });
    }

    if (copyPredictionBtn) {
      copyPredictionBtn.addEventListener('click', () => {
        const predText = document.getElementById('result-text').textContent;
        navigator.clipboard.writeText(predText).then(() => alert('Prediction copied to clipboard!'));
      });
    }
  </script>
</body>
</html>

style.css

/* Base styling */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f2f4f8;
  color: #333;
  margin: 0;
  padding: 0;
  transition: background-color 0.3s, color 0.3s;
}

/* Dark Mode */
body.dark-mode {
  background: #121212;
  color: #eee;
}

.container {
  max-width: 600px;
  margin: 60px auto;
  background: #fff;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s, color 0.3s;
}

body.dark-mode .container {
  background: #1e1e1e;
  color: #eee;
}

/* Header */
h1 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 20px;
  user-select: none;
}

body.dark-mode h1 {
  color: #aad4ff;
}

/* Dark mode toggle */
#toggle-theme {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: background-color 0.3s;
}

#toggle-theme:hover {
  background: #0056b3;
}

/* Explanation Section */
.info {
  background: #e7f3ff;
  border-left: 6px solid #007bff;
  padding: 15px 20px;
  margin-bottom: 30px;
  border-radius: 8px;
  color: #333;
}

body.dark-mode .info {
  background: #003766;
  color: #cce4ff;
  border-left-color: #aad4ff;
}

/* Form */
form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

input[type="text"] {
  width: 100%;
  padding: 14px;
  border: 1.5px solid #ccc;
  border-radius: 10px;
  font-size: 17px;
  transition: border-color 0.3s ease;
}

input[type="text"]:focus {
  border-color: #007bff;
  outline: none;
}

button[type="submit"] {
  padding: 14px;
  background-color: #007bff;
  border: none;
  color: white;
  border-radius: 10px;
  font-size: 17px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button[type="submit"]:hover {
  background-color: #0056b3;
}

/* Result Display */
.result {
  margin-top: 25px;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  padding: 20px;
  border-radius: 10px;
  user-select: text;
  position: relative;
}

.result.success {
  background-color: #d4edda;
  color: #155724;
}

.result.error {
  background-color: #f8d7da;
  color: #721c24;
}

/* Copy Buttons */
#copy-url, #copy-prediction {
  margin: 10px 5px 0;
  padding: 8px 16px;
  font-size: 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  color: white;
}

#copy-url {
  background-color: #17a2b8;
}

#copy-url:hover {
  background-color: #117a8b;
}

#copy-prediction {
  background-color: #28a745;
}

#copy-prediction:hover {
  background-color: #1e7e34;
}

/* Explanation inside result */
.explanation {
  margin-top: 20px;
  background: #fff3cd;
  color: #856404;
  padding: 15px;
  border-radius: 8px;
  font-size: 16px;
  text-align: left;
}

body.dark-mode .explanation {
  background: #665c00;
  color: #fff8a1;
}

/* Security Tips Section */
.tips {
  margin-top: 40px;
  background: #e8f5e9;
  border-left: 6px solid #28a745;
  padding: 20px;
  border-radius: 10px;
  color: #2f6627;
}

body.dark-mode .tips {
  background: #264d18;
  color: #cce9a2;
  border-left-color: #7dd77d;
}

.tips ul {
  list-style-type: disc;
  margin-left: 20px;
}

/* Footer */
footer {
  margin-top: 40px;
  text-align: center;
  font-size: 14px;
  color: #666;
  user-select: none;
}

body.dark-mode footer {
  color: #aaa;
}

/* Responsive */
@media (max-width: 640px) {
  .container {
    margin: 40px 20px;
    padding: 25px;
  }

  input[type="text"], button[type="submit"], #toggle-theme {
    font-size: 16px;
  }

  .result {
    font-size: 16px;
  }
}


