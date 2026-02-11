from .nodes.client.ClientImageSaveNode import ImageSaveNode
from .nodes.client.ClientVideoSaveNode import VideoSaveNode
from .nodes.remote.RemoteImageLoader import RemoteImageLoader
from .nodes.memory.MemoryImageNode import MemoryImageNode
from .nodes.memory.TemporaryImagePreview import TemporaryImagePreview
from .nodes.input.InputDataToImage import InputDataToImage

# Node Registration for ComfyUI
NODE_CLASS_MAPPINGS = {
    "ClientImageDownloadNode": ImageSaveNode,
    "ClientVideoDownloadNode": VideoSaveNode,
    "ServerMemoryImageNode": MemoryImageNode,
    "RemoteImageLoader": RemoteImageLoader,
    "TemporaryImagePreview": TemporaryImagePreview,
    "InputDataToImage": InputDataToImage
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ClientImageDownloadNode": "Client Image Download",
    "ClientVideoDownloadNode": "Client Video Download",
    "RemoteImageLoader": "Remote Image Loader",
    "ServerMemoryImageNode": "Server Memory Image Node",
    "TemporaryImagePreview": "Temporary Image Preview",
    "InputDataToImage": "Input Data to Image"
}