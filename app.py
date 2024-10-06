from flask import Flask, request, jsonify
import tensorflow as tf
import tensorflow_hub as hub
import librosa
import numpy as np
import pandas as pd
import os
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Timer

app = Flask(__name__)

# Load model
model = tf.keras.models.load_model('best_little.h5', compile=False)
yamnet_model_handle = 'yamnet-tensorflow2-yamnet-v1'
yamnet_model = hub.KerasLayer(yamnet_model_handle, trainable=False)

# Configure CSV file path
csv_file = os.getenv('CSV_FILE_PATH', 'detection_results.csv')

# Initialize CSV file if not exists
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=["time", "eating", "drinking", "coughing", "throat_clearing", "talking", "others"])
    df.to_csv(csv_file, index=False)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Memory store for minute-wise counts
minute_counts = defaultdict(lambda: {
    "eating": 0,
    "drinking": 0,
    "coughing": 0,
    "talking": 0,
    "throat_clearing": 0,
    "others": 0
})

def get_current_minute():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def write_counts_to_csv():
    global minute_counts
    if not minute_counts:
        return

    df = pd.DataFrame([
        {"time": minute, **counts}
        for minute, counts in sorted(minute_counts.items())
    ])
    df.to_csv(csv_file, mode='a', header=False, index=False)
    minute_counts.clear()

def reset_counts():
    write_counts_to_csv()
    now = datetime.now()
    next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
    delay = (next_minute - now).total_seconds()
    Timer(delay, reset_counts).start()

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    
    try:
        y, sr = librosa.load(file, sr=16000)
        embeddings, _, _ = yamnet_model(y)
        features = embeddings.numpy().mean(axis=0)
        features = np.expand_dims(features, axis=0)
        
        predictions = model.predict(features)
        predicted_label = np.argmax(predictions, axis=1)[0]

        # Map index to label
        index_to_label = {
            0: "eating",
            1: "drinking",
            2: "coughing",
            3: "talking",
            4: "throat_clearing",
            5: "others"
        }

        label_name = index_to_label[predicted_label]
        current_minute = get_current_minute()

        # Update minute-wise counts
        minute_counts[current_minute][label_name] += 1

        return jsonify({"label": label_name})

    except Exception as e:
        logging.error(f"Error processing file: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
UPLOAD_FOLDER = 'uploads/'  # 指定存储照片的目录
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return "No photo part", 400

    file = request.files['photo']
    if file.filename == '':
        return "No selected file", 400

    # 获取当前时间并格式化为字符串，作为文件名
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]  # 获取文件的扩展名

    # 生成新的文件名，使用当前时间命名
    new_filename = f"{current_time}{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, new_filename)

    # 保存照片
    file.save(file_path)

    return f"Photo saved as {new_filename} at {file_path}", 200
if __name__ == '__main__':
    reset_counts()  # Start the minute reset timer
    app.run(host='0.0.0.0', port=5006)
