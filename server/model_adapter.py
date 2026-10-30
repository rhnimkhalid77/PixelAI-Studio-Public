"""Optional local text-to-image adapter based on Hugging Face Diffusers.

Model weights are downloaded on first use and remain subject to their own license.
This adapter runs on the server only; never expose the server token in browser code.
"""
from functools import lru_cache
import os

@lru_cache(maxsize=1)
def _load_pipeline():
    import torch
    from diffusers import AutoPipelineForText2Image

    model_id = os.getenv("PIXELAI_MODEL_ID", "stabilityai/sdxl-turbo")
    if torch.cuda.is_available():
        dtype = torch.float16
        device = "cuda"
    else:
        dtype = torch.float32
        device = "cpu"

    pipe = AutoPipelineForText2Image.from_pretrained(
        model_id,
        torch_dtype=dtype,
        use_safetensors=True,
    )
    pipe.to(device)
    pipe.enable_attention_slicing()
    return pipe, device


def generate_image(prompt: str, seed: int | None = None) -> bytes:
    """Generate a 512px PNG; raises a clear error if dependencies/weights are absent."""
    import io
    import torch

    pipe, device = _load_pipeline()
    generator = None
    if seed is not None:
        generator = torch.Generator(device=device).manual_seed(seed)

    result = pipe(
        prompt=prompt,
        width=512,
        height=512,
        num_inference_steps=4,
        guidance_scale=0.0,
        generator=generator,
    )
    image = result.images[0]
    output = io.BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()
