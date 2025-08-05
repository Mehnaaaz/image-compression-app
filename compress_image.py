import numpy as np
from PIL import Image
from sklearn.decomposition import PCA

def compress_image(image_path, quality_percentage, output_path):
    """
    Compress image using PCA while preserving RGB colors
    
    Args:
        image_path (str): Path to input image
        quality_percentage (float): Quality percentage (10-100)
        output_path (str): Path to save compressed image
    """
    try:
        # Load image and convert to RGB (handles all formats)
        img = Image.open(image_path)
        
        # Convert to RGB if not already (handles RGBA, P, L, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        original_shape = img_array.shape
        
        # Get image dimensions
        height, width, channels = original_shape
        
        # Calculate number of components based on quality
        # Use the smaller dimension to avoid overfitting
        max_components = min(height, width)
        n_components = max(1, int(max_components * quality_percentage / 100))
        n_components = min(n_components, max_components)
        
        # Process each color channel separately
        compressed_channels = []
        
        for channel in range(channels):
            # Extract single channel
            channel_data = img_array[:, :, channel]
            
            # Apply PCA to this channel
            pca = PCA(n_components=n_components)
            
            # Fit and transform
            channel_reduced = pca.fit_transform(channel_data)
            
            # Inverse transform to reconstruct
            channel_reconstructed = pca.inverse_transform(channel_reduced)
            
            # Ensure values are in valid range [0, 255]
            channel_reconstructed = np.clip(channel_reconstructed, 0, 255)
            
            compressed_channels.append(channel_reconstructed)
        
        # Stack channels back together
        img_compressed_array = np.stack(compressed_channels, axis=2)
        
        # Convert back to uint8
        img_compressed_array = img_compressed_array.astype(np.uint8)
        
        # Create PIL Image from array
        img_compressed = Image.fromarray(img_compressed_array, 'RGB')
        
        # Save with JPEG compression
        # You can adjust the quality parameter for additional compression
        jpeg_quality = max(10, min(95, int(quality_percentage)))
        img_compressed.save(output_path, 'JPEG', quality=jpeg_quality, optimize=True)
        
        print(f"Image compressed successfully: {image_path} -> {output_path}")
        print(f"Original shape: {original_shape}, PCA components: {n_components}")
        
    except Exception as e:
        print(f"Error compressing image: {str(e)}")
        raise e

def compress_image_alternative(image_path, quality_percentage, output_path):
    """
    Alternative compression method using JPEG quality only
    (Simpler approach that might work better for some use cases)
    """
    try:
        # Load and convert to RGB
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate JPEG quality from percentage
        jpeg_quality = max(10, min(95, int(quality_percentage)))
        
        # Save with JPEG compression
        img.save(output_path, 'JPEG', quality=jpeg_quality, optimize=True)
        
        print(f"Image compressed with JPEG quality {jpeg_quality}%")
        
    except Exception as e:
        print(f"Error in alternative compression: {str(e)}")
        raise e