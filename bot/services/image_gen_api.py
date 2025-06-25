import aiohttp
import json
from enum import Enum
# from openai import OpenAI
from openai import AsyncOpenAI
import loguru

from bot.utils.keys import KEY_IMAGE_GEN, KEY_OPENAI


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

def get_image_size_openai(mode: ImageMode) -> str:
    if mode == ImageMode.square:
        return "1024x1024"
    elif mode == ImageMode.horizontal:
        return "1792x1024"
    elif mode == ImageMode.vertical:
        return "1024x1792"
    else:
        raise ValueError("Неверный режим изображения")


async def generate_image_stream(prompt: str, mode: ImageMode = ImageMode.square, api_key: str = KEY_IMAGE_GEN):
    """
    https://neuroimg.art/
    """
    timeout = aiohttp.ClientTimeout(total=360)
    width, height = get_image_size(mode)
    payload = {
        "token": api_key,
        "model": "RealisticVision-V4fp8_e4m3fn",
        "prompt": prompt,
        "width": width,
        "height": height,
        "sampler": "DPM++ 2M Karras",
        "steps": 35,
        "stream": True
    }
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for attempt in range(2):
            try:
                async with session.post(
                        "https://neuroimg.art/api/v1/generate",
                        json=payload
                ) as response:

                    async for line in response.content:
                        if line:
                            status = json.loads(line)
                            if status["status"] == "SUCCESS":
                                return status['image_url']
            except BaseException as ex:
                loguru.logger.debug(ex)
        return None


async def generate_dalle_image(
        prompt: str,
        mode: ImageMode = ImageMode.square,
        api_key: str = KEY_OPENAI,
        model: str = "dall-e-3"
):
    """
    Генерирует изображение через OpenAI DALL-E 3 API
    Возвращает URL сгенерированного изображения

    :param prompt: Текст запроса для генерации
    :param mode: Режим изображения (квадратное, горизонтальное, вертикальное)
    :param api_key: API ключ OpenAI
    :param model: Модель для генерации (по умолчанию dall-e-3)
    :return: URL изображения или None в случае ошибки
    """
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.proxyapi.ru/openai/v1",
    )

    size = get_image_size_openai(mode)

    for attempt in range(2):
        try:
            response = await client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                n=1,
                quality="standard"
            )
            return response.data[0].url
        except Exception as ex:
            loguru.logger.error(f"Attempt {attempt + 1} failed: {ex}")
            if attempt == 1:  # Если это была последняя попытка
                return None
