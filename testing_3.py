import aiohttp
import json
import asyncio

from bot.utils.keys import KEY_IMAGE_GEN

from enum import Enum

class ImageMode(str, Enum):
    square = "square"
    horizontal = "horizontal"
    vertical = "vertical"

def get_image_size(mode: ImageMode) -> tuple[int, int]:
    if mode == ImageMode.square:
        return 1024, 1024
    elif mode == ImageMode.horizontal:
        return 1024, 640
    elif mode == ImageMode.vertical:
        return 640, 1024
    else:
        raise ValueError("Неверный режим изображения")

async def free_generate(prompt: str, mode: ImageMode = ImageMode.square, api_key: str = KEY_IMAGE_GEN):
    async with aiohttp.ClientSession() as session:
        width, height = get_image_size(mode)
        payload = {
            "token": api_key,
            "prompt": prompt,
            "stream": True,
            "width": width,
            "height": height,
        }
        async with session.post(
                "https://neuroimg.art/api/v1/free-generate",
                json=payload
        ) as response:
            # print(response.status)
            # print(response.content)
            async for line in response.content:
                if line:
                    data = json.loads(line)
                    if data["status"] == "SUCCESS":
                        # print(data["image_url"])
                        return data["image_url"]
                    # print(f"Статус: {data['status']}")

# promt = """
# Космический корабль в космосе на орбите планеты. Очень реалистично. Как будто это живая фотография."""
#
# async def main():
#     result = await free_generate(
#         prompt=promt
#     )
#     print(result)
#
# asyncio.run(main())