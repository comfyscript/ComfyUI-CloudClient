import torch
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from server import PromptServer


class TemporaryImagePreview:
    """
    A custom node that displays image preview without saving to disk.
    Uses base64 encoding to send image data directly to the UI.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "preview_image"
    OUTPUT_NODE = True
    CATEGORY = "image/preview"

    def preview_image(self, images, unique_id):
        # Convert the first image from torch tensor to PIL Image
        # ComfyUI images are in [B, H, W, C] format with values 0-1
        image_tensor = images[0]

        # Convert to numpy and scale to 0-255
        image_np = (image_tensor.cpu().numpy() * 255).astype(np.uint8)

        # Convert to PIL Image
        pil_image = Image.fromarray(image_np)

        # Encode as base64 for transmission
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG", compress_level=4)
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Send to UI without saving (using the actual node unique_id)
        PromptServer.instance.send_sync(
            "imagepreview.update",
            {
                "image": f"data:image/png;base64,{img_base64}",
                "node_id": unique_id
            }
        )

        # Pass through the images unchanged
        return (images,)
