import io
from PIL import Image

# Converting tensor images to gif
def images_to_gif(img_array, fps):
    """Create GIF using PIL"""
    batch_size, height, width, channels = img_array.shape

    # Convert frames to PIL images
    frames = []
    for i in range(batch_size):
        frame_data = img_array[i]
        if channels == 4:
            pil_img = Image.fromarray(frame_data, 'RGBA')
            pil_img = pil_img.convert('RGB')  # GIF doesn't handle alpha well
        else:
            pil_img = Image.fromarray(frame_data, 'RGB')
        frames.append(pil_img)

    # Save as GIF
    buffer = io.BytesIO()
    frames[0].save(
        buffer,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),  # PIL wants milliseconds
        loop=0
    )

    buffer.seek(0)
    data_stream = buffer.getvalue()
    buffer.close()

    # Returning the data stream for downloading (if necessary)
    return data_stream