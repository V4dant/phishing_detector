from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import re
import urllib.parse
from feature_extraction import extract_features_from_url  # Your custom extractor
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the saved model
try:
    model = joblib.load('phishing_model.pkl')
    logger.info(f"Model loaded successfully. Expects {model.n_features_in_} features.")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None


def validate_url(url):
    """Validate if the input is a proper URL"""
    if not url or len(url.strip()) == 0:
        return False, "URL cannot be empty"

    url = url.strip()

    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    # Basic URL validation
    try:
        parsed = urllib.parse.urlparse(url)
        if not parsed.netloc:
            return False, "Invalid URL format"
        return True, url
    except Exception:
        return False, "Invalid URL format"


def get_prediction_explanation(prediction, url):
    """Generate explanation for the prediction"""
    if prediction == 1:  # Phishing
        return "This URL shows characteristics commonly associated with phishing sites. Be cautious and verify the source before proceeding."
    else:  # Legitimate
        return "This URL appears to be legitimate based on our analysis. However, always remain vigilant when sharing personal information online."


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if not model:
        return render_template('index.html',
                               url="",
                               prediction="🔴 Error: Model not loaded",
                               explanation="The prediction model could not be loaded. Please contact the administrator.")

    url = request.form.get('url', '').strip()

    # Validate URL
    is_valid, processed_url_or_error = validate_url(url)
    if not is_valid:
        return render_template('index.html',
                               url=url,
                               prediction="🔴 Invalid URL",
                               explanation=processed_url_or_error)

    processed_url = processed_url_or_error

    try:
        # Extract features
        features = extract_features_from_url(processed_url)
        logger.info(f"Extracted features count: {len(features) if isinstance(features, list) else 'dict'}")

        # Handle feature processing
        if isinstance(features, dict):
            features.pop('status', None)  # Remove label if present
            features = list(features.values())

        # Ensure correct feature length
        expected_len = model.n_features_in_
        if len(features) < expected_len:
            features.extend([0] * (expected_len - len(features)))
            logger.warning(f"Padded features with zeros to length: {len(features)}")
        elif len(features) > expected_len:
            features = features[:expected_len]
            logger.warning(f"Trimmed features to length: {len(features)}")

        # Make prediction
        features_array = np.array(features).reshape(1, -1)
        prediction = model.predict(features_array)[0]
        confidence = model.predict_proba(features_array)[0].max() if hasattr(model, 'predict_proba') else None

        result = "🔴 Phishing" if prediction == 1 else "🟢 Legitimate"
        explanation = get_prediction_explanation(prediction, processed_url)

        # Add confidence to explanation if available
        if confidence:
            explanation += f" (Confidence: {confidence:.2%})"

        logger.info(f"Prediction for {processed_url}: {result}")

    except Exception as e:
        logger.error(f"Prediction error for {url}: {str(e)}")
        result = "🔴 Error"
        explanation = f"An error occurred during analysis: {str(e)}"
        processed_url = url

    return render_template('index.html',
                           url=processed_url,
                           prediction=result,
                           explanation=explanation)


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API endpoint for programmatic access"""
    if not model:
        return jsonify({'error': 'Model not loaded'}), 500

    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400

    url = data['url'].strip()

    # Validate URL
    is_valid, processed_url_or_error = validate_url(url)
    if not is_valid:
        return jsonify({'error': processed_url_or_error}), 400

    processed_url = processed_url_or_error

    try:
        features = extract_features_from_url(processed_url)

        if isinstance(features, dict):
            features.pop('status', None)
            features = list(features.values())

        expected_len = model.n_features_in_
        if len(features) < expected_len:
            features.extend([0] * (expected_len - len(features)))
        elif len(features) > expected_len:
            features = features[:expected_len]

        features_array = np.array(features).reshape(1, -1)
        prediction = model.predict(features_array)[0]
        confidence = model.predict_proba(features_array)[0].max() if hasattr(model, 'predict_proba') else None

        result = {
            'url': processed_url,
            'is_phishing': bool(prediction),
            'prediction': "phishing" if prediction == 1 else "legitimate",
            'confidence': float(confidence) if confidence else None
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"API prediction error for {url}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html',
                           url="",
                           prediction="🔴 Server Error",
                           explanation="An internal server error occurred. Please try again later."), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)