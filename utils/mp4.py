import io
import av
from PIL import Image

# For encoding images to mp4 format
def images_to_mp4(img_array, fps, quality):
    """Create MP4 using av (your original code)"""
    batch_size, height, width, channels = img_array.shape
    buffer = io.BytesIO()

    container = av.open(buffer, mode='w', format='mp4')
    stream = container.add_stream('h264', fps)
    stream.width = width
    stream.height = height
    stream.pix_fmt = 'yuv420p'
    stream.options = {'crf': str(quality)}

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

    for packet in stream.encode():
        container.mux(packet)

    container.close()
    buffer.seek(0)
    data_stream = buffer.getvalue()
    buffer.close()

    # Returning data stream to save
    return data_stream
