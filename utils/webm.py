import io
import av
from PIL import Image

# For converting images to webm format
def images_to_webm(img_array, fps, quality):
    """Create WebM using av"""
    batch_size, height, width, channels = img_array.shape
    buffer = io.BytesIO()

    container = av.open(buffer, mode='w', format='webm')
    stream = container.add_stream('libvpx-vp9', fps)  # VP9 codec
    stream.width = width
    stream.height = height
    stream.pix_fmt = 'yuv420p'
    stream.options = {'crf': str(quality)}

    # Process frames
    for i in range(batch_size):
        frame_data = img_array[i]

        if channels == 3:
            pil_img = Image.fromarray(frame_data, 'RGB')
        elif channels == 4:
            pil_img = Image.fromarray(frame_data, 'RGBA')
            pil_img = pil_img.convert('RGB')
        else:
            raise ValueError(f"Unsupported channel count: {channels}")

        frame = av.VideoFrame.from_image(pil_img)

        for packet in stream.encode(frame):
            container.mux(packet)

    # Flush
    for packet in stream.encode():
        container.mux(packet)

    container.close()
    buffer.seek(0)
    data_stream = buffer.getvalue()
    buffer.close()

    # Returning data stream to use
    return data_stream