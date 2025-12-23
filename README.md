<img width="1918" height="855" alt="image" src="https://github.com/user-attachments/assets/f711b135-c555-43af-af9a-32c18fafd3a2" />

https://www.linkedin.com/feed/update/urn:li:activity:7404613343975485441/

Here is a professional, portfolio-ready `README.md`. It is written to highlight the specific "One-Shot" technical challenge you solved, making it perfect for showing to recruiters or the Bobyard team.

Copy the code block below and save it as **`README.md`** in your project root.

````markdown
# 🏗️ One-Shot Symbol Detector (Bobyard AI Challenge)

> **The Problem:** Standard AI needs 1,000 images to learn what a "valve" looks like.  
> **The Solution:** This AI learns new symbols from **one single example** provided by the user in real-time.



## 📋 Overview

This project is an implementation of **One-Shot Learning** applied to architectural blueprints. It allows a user to identify specific symbols (valves, switches, fire hydrants) in a dense technical drawing without ever retraining the model.

Instead of traditional classification, this system uses a **Siamese Network (ResNet18 Backbone)** to calculate geometric similarity between a reference patch and the rest of the document.

### ✨ Key Features
* **One-Shot Detection:** User draws a box around *one* symbol, and the AI finds all other instances.
* **gRPC Backend:** High-performance, strictly typed communication between the inference engine and the UI.
* **Interactive UI:** Streamlit frontend with a drawable canvas for real-time user selection.
* **Computer Vision Pipeline:** Implements Sliding Window Scanning and Non-Max Suppression (NMS) to handle noisy blueprints.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10
* **ML Framework:** PyTorch (ResNet18)
* **API Protocol:** gRPC & Protocol Buffers (Protobuf)
* **Frontend:** Streamlit & Streamlit Drawable Canvas
* **Computer Vision:** OpenCV / PIL / NumPy

---

## 🚀 Installation

### Prerequisites
* **Python 3.10** (Critical: Newer versions like 3.13 are not yet supported by some ML dependencies).

### 1. Clone & Environment Setup
```bash
# Clone the repository
git clone [https://github.com/yourusername/one-shot-detector.git](https://github.com/yourusername/one-shot-detector.git)
cd one-shot-detector

# Create a virtual environment (Python 3.10)
python -m venv venv

# Activate the environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
````

### 2\. Install Dependencies

```bash
# Upgrade pip to ensure wheel compatibility
python -m pip install --upgrade pip

# Install the required libraries
pip install -r requirements.txt
```

### 3\. Generate gRPC Code

This compiles the Protocol Buffer definitions into Python code.

```bash
python -m grpc_tools.protoc -I protos --python_out=generated --grpc_python_out=generated protos/symbol_detector.proto
```

-----

## 🏃‍♂️ How to Run

You will need **two terminal windows**.

### Terminal 1: Start the Inference Server

The "Brain" of the application. It loads the PyTorch model and listens on port 50051.

```bash
python server/grpc_server.py
```

*Expected Output:* `One Shot Detector Server started on port 50051...`

### Terminal 2: Start the UI

The "Face" of the application.

```bash
streamlit run client/app.py
```

*This will automatically open your browser to `http://localhost:8501`*

-----

## 🎮 Usage Workflow

1.  Go to the **"Smart Scanner"** tab in the web interface.
2.  **Upload a Blueprint:** Choose a PDF or Image containing symbols.
3.  **Draw a Box:** Use your mouse to draw a rectangle around **one** example of the symbol you want to find.
4.  **Click Scan:** The system will extract your selection, convert it to a vector embedding, and scan the rest of the document.
5.  **View Results:** Matches will be highlighted with green bounding boxes.

-----

## 📂 Project Structure

```text
one_shot_detector/
│
├── protos/                 # gRPC Protocol Definitions
│   └── symbol_detector.proto
│
├── generated/              # Auto-generated gRPC Python code
│   ├── symbol_detector_pb2.py
│   └── symbol_detector_pb2_grpc.py
│
├── server/                 # The Backend (Inference Engine)
│   ├── grpc_server.py      # Main entry point
│   ├── model.py            # Siamese Network (ResNet18) logic
│   └── scanner.py          # Sliding Window & Non-Max Suppression
│
├── client/                 # The Frontend
│   ├── app.py              # Streamlit UI
│   └── grpc_client.py      # Client-side API wrapper
│
└── requirements.txt        # Dependencies
```

-----

## ⚙️ Configuration & Tuning

If the detector is being too strict or too loose, you can adjust the thresholds in `server/scanner.py`:

  * **`threshold` (Default: 0.85):** Lower this to 0.70 to find more matches (risk of false positives). Raise it to 0.90 for strict matching.
  * **`iou_threshold` (Default: 0.1):** Controls "Non-Max Suppression". If boxes are overlapping too much, lower this value.

-----

## 🐛 Troubleshooting

**Error: `ModuleNotFoundError: No module named 'generated'`** *Fix:* Ensure you ran the `grpc_tools.protoc` command in the Installation step.

**Error: `ImportError: cannot import name 'runtime_version' ...`** *Fix:* Your generated code is out of sync. Re-run the `grpc_tools.protoc` command.

**Error: `Failed to build wheels for grpcio`** *Fix:* You are likely using Python 3.12 or 3.13. Please switch to **Python 3.10** and reinstall requirements.

```
```

