import base64
import io
import numpy as np
from PIL import Image
import torch

class InputDataToImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data_uri": ("STRING", {
                    "multiline": True,
                    "default": ""
                })
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"
    CATEGORY = "image"

    def load_image(self, data_uri):
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
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if needed
        if image.mode == 'RGBA':
            # Split alpha channel for mask
            image_rgb = image.convert('RGB')
            alpha = image.split()[-1]
            mask = np.array(alpha).astype(np.float32) / 255.0
            mask = torch.from_numpy(mask)[None,]
        else:
            image_rgb = image.convert('RGB')
            mask = torch.ones((1, image.size[1], image.size[0]), dtype=torch.float32)

        # Convert to ComfyUI format (batch, height, width, channels)
        image_np = np.array(image_rgb).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_np)[None,]

        return (image_tensor, mask)