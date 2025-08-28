import io
from typing import Tuple, Optional, BinaryIO
from PIL import Image


class ImageProcessor:
    THUMBNAIL_SIZE = (200, 200)
    MEDIUM_SIZE = (800, 800)
    LARGE_SIZE = (1920, 1920)
    
    @staticmethod
    def is_image(content_type: str) -> bool:
        image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp']
        return content_type.lower() in image_types
    
    @staticmethod
    def get_image_info(file_data: bytes) -> Optional[Tuple[int, int, str]]:
        try:
            with Image.open(io.BytesIO(file_data)) as img:
                width, height = img.size
                format = img.format.lower() if img.format else 'unknown'
                return width, height, format
        except Exception as e:
            print(f"Error getting image info: {e}")
            return None
    
    @staticmethod
    def create_thumbnail(file_data: bytes) -> Optional[bytes]:
        try:
            with Image.open(io.BytesIO(file_data)) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                # Create thumbnail
                img.thumbnail(ImageProcessor.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                
                # Save to bytes
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                return output.read()
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None
    
    @staticmethod
    def resize_image(file_data: bytes, max_size: Tuple[int, int]) -> Optional[bytes]:
        try:
            with Image.open(io.BytesIO(file_data)) as img:
                # Only resize if image is larger than max_size
                if img.width > max_size[0] or img.height > max_size[1]:
                    # Convert RGBA to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = rgb_img
                    
                    # Resize maintaining aspect ratio
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Save to bytes
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=90, optimize=True)
                    output.seek(0)
                    return output.read()
                else:
                    return file_data
        except Exception as e:
            print(f"Error resizing image: {e}")
            return None
    
    @staticmethod
    def optimize_image(file_data: bytes) -> Optional[bytes]:
        try:
            with Image.open(io.BytesIO(file_data)) as img:
                # Convert RGBA to RGB if necessary for JPEG
                if img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                # Resize if too large
                if img.width > ImageProcessor.LARGE_SIZE[0] or img.height > ImageProcessor.LARGE_SIZE[1]:
                    img.thumbnail(ImageProcessor.LARGE_SIZE, Image.Resampling.LANCZOS)
                
                # Save optimized
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                return output.read()
        except Exception as e:
            print(f"Error optimizing image: {e}")
            return None