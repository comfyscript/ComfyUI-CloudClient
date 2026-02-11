import requests
import numpy as np
import torch
from PIL import Image
from io import BytesIO


class RemoteImageLoader:
    """
    A ComfyUI custom node that downloads images from HTTP/HTTPS URLs,
    handles 301/302 redirects, and outputs them as ComfyUI image tensors.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {
                    "default": "",
                    "multiline": False,
                }),
                "timeout": ("INT", {
                    "default": 30,
                    "min": 5,
                    "max": 120,
                    "step": 1,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "load_image"
    CATEGORY = "image/loaders"

    def load_image(self, url, timeout=30):
        """
        Downloads an image from a URL and converts it to ComfyUI format.

        Args:
            url: HTTP/HTTPS URL to download image from
            timeout: Request timeout in seconds

        Returns:
            Tuple containing the image tensor in ComfyUI format (B, H, W, C)
        """
        try:
            # Download image with redirect following
            # requests follows redirects by default with allow_redirects=True
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(
                url,
                allow_redirects=True,  # Follows 301, 302 redirects
                timeout=timeout,
                headers=headers,
                stream=True
            )

            # Check if request was successful
            response.raise_for_status()

            # Load image from response content
            image = Image.open(BytesIO(response.content))

            # Convert to RGB if necessary (handle RGBA, grayscale, etc.)
            if image.mode == 'RGBA':
                # Create white background for transparency
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert PIL Image to numpy array
            image_np = np.array(image).astype(np.float32) / 255.0

            # Convert to torch tensor with shape (1, H, W, C) for ComfyUI
            image_tensor = torch.from_numpy(image_np)[None,]

            return (image_tensor,)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download image from URL: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to process image: {str(e)}")