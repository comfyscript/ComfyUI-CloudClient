from .nodes.client.ClientImageSaveNode import ImageSaveNode
from .nodes.client.ClientVideoSaveNode import VideoSaveNode
from .nodes.memory.MemoryImageNode import MemoryImageNode
from .nodes.modular.file.FileCompressor import ModularFileCompressor

# Node Registration for ComfyUI
NODE_CLASS_MAPPINGS = {
    "ClientImageDownloadNode": ImageSaveNode,
    "ClientVideoDownloadNode": VideoSaveNode,

    "ServerMemoryImageNode": MemoryImageNode,

    # Should all be modular style
    "ClientImageCompressorNode": ModularFileCompressor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ClientImageCompressorNode": "Client Image Compress",
    
    "ClientImageDownloadNode": "Client Image Download",
    "ClientVideoDownloadNode": "Client Video Download",

    "ServerMemoryImageNode": "Server Memory Image Node"
}
