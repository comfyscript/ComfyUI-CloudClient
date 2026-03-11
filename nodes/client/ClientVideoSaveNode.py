import io
import av
import torch
import numpy as np
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
            },
            "optional": {
                "audio": ("AUDIO", {"default": None}),
            }
        }

    RETURN_TYPES = ("IMAGE", "VIDEO_BUFFER",)
    RETURN_NAMES = ("last_image", "video_buffer",)
    FUNCTION = "images_to_video_buffer"
    CATEGORY = "video"
    OUTPUT_NODE = True

    def images_to_video_buffer(self, images, prefix, fps=24, quality=23, format="mp4", audio=None):
        img_array = images.cpu().numpy()
        img_array = (img_array * 255).astype(np.uint8)

        match format:
            case "gif":
                data_stream = images_to_gif(img_array, fps)
            case "webm":
                data_stream = images_to_webm(img_array, fps, quality)
            case _:
                data_stream = images_to_mp4(img_array, fps, quality)

        if audio is not None and format != "gif":
            data_stream = self._mux_audio(data_stream, audio, format)

        PromptServer.instance.send_sync("server_client_data", {
            "files": [{
                "filename": generate_filename(prefix, format),
                "data": base64.b64encode(data_stream).decode('utf-8'),
                "format": format
            }]
        })

        return images[-1], data_stream

    def _mux_audio(self, video_bytes: bytes, audio: dict, format: str) -> bytes:
        waveform = audio["waveform"]   # shape: (batch, channels, samples)
        sample_rate = audio["sample_rate"]

        # Collapse batch dim: (batch, channels, samples) → (channels, samples)
        if waveform.ndim == 3:
            waveform = waveform[0]

        audio_np = waveform.cpu().float().numpy()
        channels, num_samples = audio_np.shape
        layout = "stereo" if channels == 2 else "mono"

        av_format   = "webm" if format == "webm" else "mp4"
        audio_codec = "libvorbis" if format == "webm" else "aac"

        # ---- Open source video ----
        in_container = av.open(io.BytesIO(video_bytes), "r")
        in_video_stream = in_container.streams.video[0]

        # ---- Build output container ----
        out_buf = io.BytesIO()
        out_container = av.open(out_buf, "w", format=av_format)

        # Stream-copy video (no re-encode)
        out_video = out_container.add_stream_from_template(in_video_stream)

        # Add audio stream — pass layout via options dict; do NOT set .channels directly
        out_audio = out_container.add_stream(
            audio_codec,
            rate=sample_rate,
            options={"ac": str(channels), "channel_layout": layout}
        )

        # Remux video packets without re-encoding
        for packet in in_container.demux(in_video_stream):
            if packet.dts is None:
                continue
            packet.stream = out_video
            out_container.mux(packet)

        in_container.close()

        # Encode and mux audio in fixed-size chunks
        frame_size = out_audio.codec_context.frame_size or 1024
        for offset in range(0, num_samples, frame_size):
            chunk = audio_np[:, offset: offset + frame_size]
            # Pad last chunk to keep frame_size fixed (required by AAC/Vorbis)
            if chunk.shape[1] < frame_size:
                chunk = np.pad(chunk, ((0, 0), (0, frame_size - chunk.shape[1])))
            frame = av.AudioFrame.from_ndarray(chunk, format="fltp", layout=layout)
            frame.rate = sample_rate
            frame.pts = offset
            for packet in out_audio.encode(frame):
                out_container.mux(packet)

        # Flush encoder
        for packet in out_audio.encode(None):
            out_container.mux(packet)

        out_container.close()
        return out_buf.getvalue()
