import asyncio
import fal_client
import aiohttp
from nanoid import generate
from PIL import Image
import io
from .imagesize import get_closest_image_size

def random_img_fname():
    """Generate a random filename for saving images.

    Returns:
        str: Random filename with .png extension
    """
    return generate() + ".png"

async def generate_image(prompt, w=1024, h=1024, steps=20, cfg=8):
    """Generate an image using Flux AI's API.

    Args:
        prompt (str): The text description of the image to generate
        w (int): Desired width in pixels
        h (int): Desired height in pixels
        steps (int): Number of inference steps
        cfg (float): Guidance scale for image generation

    Returns:
        dict: The API response containing the generated image data
    """
    try:
        image_size = get_closest_image_size(w, h)
        handler = fal_client.submit(
            "fal-ai/flux/dev",
            arguments={
                "prompt": prompt,
                "image_size": image_size,
                "num_inference_steps": steps,
                "guidance_scale": cfg,
                "num_images": 1,
                "safety_tolerance": "6"
            },
        )
        print(f"Sending request to Flux AI with image size: {image_size}")
        result = await asyncio.to_thread(handler.get)
        return result
    except Exception as e:
        print(f"Error in generate_image: {e}")
        return None

async def download_and_save_image(image_url, save_path):
    """Download and save an image from a URL.

    Args:
        image_url (str): URL of the image to download
        save_path (str): Path where to save the image

    Returns:
        str: Path to the saved image file, or None if failed
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    image = Image.open(io.BytesIO(image_data))
                    image.save(save_path)
                    print(f"Image saved to {save_path}")
                    return save_path
                else:
                    print(f"Failed to download image: HTTP {resp.status}")
                    return None
    except Exception as e:
        print(f"Error downloading/saving image: {e}")
        return None