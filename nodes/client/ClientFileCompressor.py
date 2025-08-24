class ClientFileCompressorNode:
    """
    Custom ComfyUI node that saves generated images directly to the local PC
    instead of Kaggle's cloud output folder.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {
                "images": ("IMAGE",),
                "prefix": ("STRING", {"default": "kaggle_generated"}),
                "file_format": (["PNG", "JPEG", "GIF"], {"default": "PNG"}),
            }
        }
