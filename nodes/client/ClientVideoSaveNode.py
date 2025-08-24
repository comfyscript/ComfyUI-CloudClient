import io
import av
import torch
import numpy as np
from PIL import Image
import base64
from ...utils.gif import images_to_gif
from ...utils.webm import images_to_webm
from ...utils.mp4 import images_to_mp4
from ...utils.filename import generate_filename

from server import PromptServer

class VideoSaveNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "prefix": ("STRING", {"default": "animated"}),
                "fps": ("INT", {"default": 16, "min": 1, "max": 60, "step": 1}),
                "quality": ("INT", {"default": 23, "min": 0, "max": 51, "step": 1}),
                "format": (["webm", "mp4", "gif"], {"default": "webm"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "VIDEO_BUFFER",)
    RETURN_NAMES = ("images", "video_buffer",)
    FUNCTION = "images_to_video_buffer"
    CATEGORY = "video"
    OUTPUT_NODE = True

    def images_to_video_buffer(self, images, prefix, fps=24, quality=23, format="mp4"):
        # Convert tensor to numpy
        img_array = images.cpu().numpy()
        img_array = (img_array * 255).astype(np.uint8)

        match format:
            case "gif":
                data_stream = images_to_gif(img_array,fps)
            case "webm":
                data_stream = images_to_webm(img_array, fps,quality)
            case _:
                data_stream = images_to_mp4(img_array,fps, quality)

        # Send to Client
        PromptServer.instance.send_sync("server_client_data", {
            "files": [{
                "filename": generate_filename(prefix,format),
                "data": base64.b64encode(data_stream).decode('utf-8'),
                "format": format
            }]
        })

        # Returning Images and Video Buffer
        return images, data_stream