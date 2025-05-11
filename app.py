import pytesseract
import cv2
import os
import re
from PIL import Image
from flask import Flask, request, render_template_string

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Marvel Rivals Purchase Detector</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #1a1a1a; color: #f2f2f2; text-align: center; }
        .container { margin-top: 50px; }
        input[type=file], input[type=submit] {
            padding: 10px;
            border-radius: 5px;
            border: none;
            margin-top: 10px;
        }
        input[type=submit] {
            background-color: #0078D7;
            color: white;
            cursor: pointer;
        }
        .result-box {
            background-color: #333;
            padding: 20px;
            margin-top: 30px;
            border-radius: 10px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Marvel Rivals Purchase Detector</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="receipt" accept="image/*" required><br>
            <input type="submit" value="Analyze Receipt">
        </form>
        {% if result %}
        <div class="result-box">
            <h2>Result</h2>
            <pre>{{ result }}</pre>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text(image):
    return pytesseract.image_to_string(image, lang='eng')

def detect_purchase(text, game_title="Marvel Rivals"):
    text_lower = text.lower()
    if game_title.lower() in text_lower:
        date_match = re.search(r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}', text)
        amount_match = re.search(r'(rs\.?|₹)\s?(\d+[.,]?\d*)', text_lower)
        details = {
            "Game Detected": game_title,
            "Date": date_match.group(0) if date_match else "Date not found",
            "Amount": amount_match.group(0) if amount_match else "Amount not found",
            "Raw Text Snippet": text[:500]
        }
        return True, details
    return False, {}

@app.route('/', methods=['GET', 'POST'])
def upload_receipt():
    result = None
    if request.method == 'POST':
        file = request.files['receipt']
        if file:
            file_path = 'temp_upload.jpg'
            file.save(file_path)
            image = preprocess_image(file_path)
            text = extract_text(image)
            os.remove(file_path)
            found, details = detect_purchase(text)
            if found:
                result = f"✅ Marvel Rivals purchase detected!\n\nDetails:\n" + "\n".join(f"{k}: {v}" for k, v in details.items())
            else:
                result = "❌ No Marvel Rivals purchase found in the uploaded image."
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == '__main__':
    app.run(debug=True)
