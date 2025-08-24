import torch
import numpy as np
from PIL import Image
import requests
import io
import base64
import uuid
from typing import Dict, Any, Tuple, Optional

class MemoryImageNode:
    def __init__(self):
        self.cache = {}  # Dictionary to store images in memory

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "cache_key": ("STRING", {"default": "image_1"}),
                "operation": (["store", "retrieve", "upload", "download", "list_keys"], {"default": "retrieve"}),
            },
            "optional": {
                "input_image": ("IMAGE",),
                "remote_url": ("STRING", {"default": ""}),
                "upload_data": ("STRING", {"default": ""}),  # base64 encoded image
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("cached_image", "cache_info")
    FUNCTION = "process_cache"
    CATEGORY = "utils"

    def process_cache(self, cache_key: str, operation: str,
                      input_image: Optional[torch.Tensor] = None,
                      remote_url: str = "",
                      upload_data: str = "") -> Tuple[torch.Tensor, str]:

        if operation == "store":
            return self._store_image(cache_key, input_image)
        elif operation == "retrieve":
            return self._retrieve_image(cache_key)
        elif operation == "upload":
            return self._upload_image(cache_key, upload_data)
        elif operation == "download":
            return self._download_image(cache_key, remote_url)
        elif operation == "list_keys":
            return self._list_keys()
        else:
            return self._create_empty_tensor(), f"Unknown operation: {operation}"

    def _store_image(self, cache_key: str, input_image: torch.Tensor) -> Tuple[torch.Tensor, str]:
        if input_image is None:
            return self._create_empty_tensor(), "No input image provided"

        # Store the tensor directly in cache
        self.cache[cache_key] = input_image.clone()
        info = f"Stored image in cache with key: {cache_key}"
        return input_image, info

    def _retrieve_image(self, cache_key: str) -> Tuple[torch.Tensor, str]:
        if cache_key not in self.cache:
            empty_tensor = self._create_empty_tensor()
            return empty_tensor, f"Key '{cache_key}' not found in cache"

        cached_image = self.cache[cache_key]
        info = f"Retrieved image from cache: {cache_key}"
        return cached_image, info

    def _upload_image(self, cache_key: str, upload_data: str) -> Tuple[torch.Tensor, str]:
        if not upload_data:
            return self._create_empty_tensor(), "No upload data provided"

        try:
            # Decode base64 image data
            image_data = base64.b64decode(upload_data)
            pil_image = Image.open(io.BytesIO(image_data))

            # Convert PIL to tensor
            tensor_image = self._pil_to_tensor(pil_image)

            # Store in cache
            self.cache[cache_key] = tensor_image
            info = f"Uploaded and cached image with key: {cache_key}"
            return tensor_image, info

        except Exception as e:
            return self._create_empty_tensor(), f"Upload failed: {str(e)}"

    def _download_image(self, cache_key: str, remote_url: str) -> Tuple[torch.Tensor, str]:
        if not remote_url:
            return self._create_empty_tensor(), "No URL provided"

        try:
            response = requests.get(remote_url, timeout=30)
            response.raise_for_status()

            # Convert downloaded image to PIL
            pil_image = Image.open(io.BytesIO(response.content))

            # Convert PIL to tensor
            tensor_image = self._pil_to_tensor(pil_image)

            # Store in cache
            self.cache[cache_key] = tensor_image
            info = f"Downloaded and cached image from {remote_url} with key: {cache_key}"
            return tensor_image, info

        except Exception as e:
            return self._create_empty_tensor(), f"Download failed: {str(e)}"

    def _list_keys(self) -> Tuple[torch.Tensor, str]:
        keys = list(self.cache.keys())
        info = f"Cache keys: {', '.join(keys) if keys else 'Empty cache'}"
        return self._create_empty_tensor(), info

    def _pil_to_tensor(self, pil_image: Image.Image) -> torch.Tensor:
        # Ensure RGB mode
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Convert to numpy array
        np_image = np.array(pil_image).astype(np.float32) / 255.0

        # Convert to tensor with shape [1, H, W, C] (batch, height, width, channels)
        tensor_image = torch.from_numpy(np_image)[None,]

        return tensor_image

    def _create_empty_tensor(self) -> torch.Tensor:
        # Create a small black image as placeholder
        return torch.zeros((1, 64, 64, 3), dtype=torch.float32)
