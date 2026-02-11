import base64
import io
import numpy as np
from PIL import Image
import torch
import requests

class InputDataToImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data_uri": ("STRING", {
                    "multiline": True,
                    "default": ""
                }),
                "timeout": ("INT", {
                    "default": 30,
                    "min": 5,
                    "max": 120,
                    "step": 1,
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"
    CATEGORY = "image"

    def load_image(self, data_uri, timeout=30):
        # Check if input is a URL
        if data_uri.startswith('http://') or data_uri.startswith('https://'):
            image = self._load_from_url(data_uri, timeout)
        else:
            # Handle as data URI or base64
            image = self._load_from_data_uri(data_uri)

        # Process image and extract mask
        if image.mode == 'RGBA':
            # Split alpha channel for mask
            image_rgb = image.convert('RGB')
            alpha = image.split()[-1]
            mask = np.array(alpha).astype(np.float32) / 255.0
            mask = torch.from_numpy(mask)[None,]
        else:
            image_rgb = image.convert('RGB')
            # Create full opacity mask
            mask = torch.ones((1, image.size[1], image.size[0]), dtype=torch.float32)

        # Convert to ComfyUI format (batch, height, width, channels)
        image_np = np.array(image_rgb).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_np)[None,]

        return (image_tensor, mask)

    def _load_from_url(self, url, timeout):
        """Download image from HTTP/HTTPS URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(
                url,
                allow_redirects=True,
                timeout=timeout,
                headers=headers,
                stream=True
            )

            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download image from URL: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to process image from URL: {str(e)}")

    def _load_from_data_uri(self, data_uri):
        """Load image from data URI or raw base64"""
        try:
            # Parse the data URI
            if data_uri.startswith('data:'):
                # Extract the base64 data after the comma
                header, encoded = data_uri.split(',', 1)
            else:
                # Assume it's just base64 without the data URI prefix
                encoded = data_uri

            # Decode base64 to bytes
            image_bytes = base64.b64decode(encoded)

            # Convert to PIL Image
            return Image.open(io.BytesIO(image_bytes))

        except Exception as e:
            raise Exception(f"Failed to decode data URI: {str(e)}")