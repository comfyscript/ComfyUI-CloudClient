import base64
import datetime
from io import BytesIO

import numpy as np
import pyzipper
from PIL import Image
from server import PromptServer


class ModularFileCompressor:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",)
            },
            "optional": {

            }
        }

    RETURN_TYPES = ("BASE64_STREAM",)
    FUNCTION = "compress_file"
    CATEGORY = "image"
    OUTPUT_NODE = True

    def compress_file(self, images):
        # Convert tensor to numpy
        img_array = images.cpu().numpy()
        img_array = (img_array * 255).astype(np.uint8)
        prefix = "image"
        file_format = 'png'
        # Generate timestamp for unique filenames
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_buffer = BytesIO()

        with pyzipper.AESZipFile(zip_buffer, 'w', compression=pyzipper.ZIP_DEFLATED, compresslevel=6) as zipf:
            zipf.setpassword("special_stuff".encode('utf-8'))
            zipf.setencryption(pyzipper.WZ_AES, nbits=256)

            # Process each image in the batch
            for i in range(len(img_array)):
                # Convert numpy array to PIL Image
                img = Image.fromarray(img_array[i])

                # Create filename with timestamp and index
                filename = f"{prefix}_{timestamp}_{i + 1:03d}"
                full_filename = f"{filename}.{file_format.lower()}"

                # Create buffer for image data
                img_buffer = BytesIO()

                # Save image to buffer in specified format
                img.save(img_buffer, format="PNG")

                # Add to password-protected zip
                zipf.writestr(full_filename, img_buffer.getvalue())

        # Get the compressed archive
        zip_buffer.seek(0)
        archive_data = zip_buffer.getvalue()

        # Convert to base64 for download
        archive_b64 = base64.b64encode(archive_data).decode('utf-8')

        # Send to Client
        PromptServer.instance.send_sync("server_client_data", {
            "files": [{
                "filename": "test.zip",
                "data": archive_b64,
                "format": "zip"
            }]
        })

        return (archive_b64,)
