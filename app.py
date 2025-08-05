from flask import Flask, request, send_file, jsonify, render_template
import os
import uuid
from compress_image import compress_image

app = Flask(__name__)

# Configure folders
UPLOAD_FOLDER = 'static/uploads'
DOWNLOAD_FOLDER = 'static/downloads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and compression"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        quality = float(request.form.get('quality', 80))
        
        # Validate file selection
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            return jsonify({'error': 'Invalid file type. Please use JPG, PNG, WebP, BMP, or TIFF.'}), 400
        
        if file and file.filename:
            # Generate unique filenames
            if not file_extension:
                file_extension = '.jpg'
                
            upload_filename = f"upload_{uuid.uuid4().hex}{file_extension}"
            download_filename = f"compressed_{uuid.uuid4().hex}.jpg"
            
            # Save uploaded file
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], upload_filename)
            file.save(upload_path)
            
            # Get original file size
            original_size = os.path.getsize(upload_path)
            
            # Compress image
            download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], download_filename)
            
            try:
                compress_image(upload_path, quality, download_path)
                
                # Get compressed file size
                compressed_size = os.path.getsize(download_path)
                compression_ratio = ((original_size - compressed_size) / original_size) * 100
                
                # Clean up uploaded file
                os.remove(upload_path)
                
                return jsonify({
                    'success': True,
                    'download_path': f'/download/{download_filename}',
                    'message': 'Image compressed successfully!',
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': round(compression_ratio, 1),
                    'filename': download_filename
                }), 200
                
            except Exception as compression_error:
                # Clean up uploaded file on compression error
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                print(f"Compression error: {str(compression_error)}")
                return jsonify({'error': 'Failed to compress image. Please try again.'}), 500
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Handle file downloads"""
    try:
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
            
        # Send file with proper filename
        return send_file(
            file_path, 
            as_attachment=True, 
            download_name=f'compressed_{filename}',
            mimetype='image/jpeg'
        )
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        return jsonify({'error': 'Error downloading file'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Image Compression API'}), 200

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 10MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Image Compression Server...")
    print("Server will be available at: http://localhost:5000")
    print("Make sure to place index.html in the templates/ folder")
    app.run(debug=True, host='0.0.0.0', port=5000)