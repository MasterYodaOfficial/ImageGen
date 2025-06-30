import aiohttp
import json
import loguru
from enum import Enum
from openai import AsyncOpenAI
from typing import Optional, List, Tuple, Union
import base64
from io import BytesIO
from aiogram.types import InputFile


class ImageMode(str, Enum):
    square = "square"
    horizontal = "horizontal"
    vertical = "vertical"


class ImageModel(str, Enum):
    NEUROIMG = "neuroimg"
    DALLE2 = "dall-e-2"
    DALLE3 = "dall-e-3"
    GPT_IMAGE_1 = "gpt-image-1"


class ImageGenerator:
    def __init__(self, neuroimg_api_key: str, openai_api_key: str):
        self.neuroimg_api_key = neuroimg_api_key
        self.openai_api_key = openai_api_key
        self.openai_client = AsyncOpenAI(
            api_key=openai_api_key,
            base_url="https://api.proxyapi.ru/openai/v1",
        )

    @staticmethod
    def get_image_size(mode: ImageMode) -> tuple[int, int]:
        if mode == ImageMode.square:
            return 1024, 1024
        elif mode == ImageMode.horizontal:
            return 1024, 640
        elif mode == ImageMode.vertical:
            return 640, 1024
        raise ValueError("Invalid image mode")

    @staticmethod
    def get_image_size_openai(mode: ImageMode) -> str:
        if mode == ImageMode.square:
            return "1024x1024"
        elif mode == ImageMode.horizontal:
            return "1792x1024"
        elif mode == ImageMode.vertical:
            return "1024x1792"
        raise ValueError("Invalid image mode")

    @staticmethod
    def get_model_choices() -> List[Tuple[str, str, str]]:
        """
        Возвращает список доступных моделей для генерации изображений.
        Каждый элемент содержит:
        - Отображаемое имя модели
        - Значение модели для callback
        - Краткое описание модели

        :return: Список кортежей (display_name, callback_value, description)
        """
        return [
            (
                "NeuroArt",
                ImageModel.NEUROIMG.value,
                "🎨 Реалистичные изображения через neuroimg.art"
            ),
            (
                "DALL·E 2",
                ImageModel.DALLE2.value,
                "⚡ Быстрая генерация от OpenAI"
            ),
            (
                "DALL·E 3",
                ImageModel.DALLE3.value,
                "🌟 Самые качественные изображения от OpenAI"
            ),
            (
                "GPT-Image",
                ImageModel.GPT_IMAGE_1.value,
                "🤖 Экспериментальная модель от OpenAI"
            )
        ]

    async def generate(
            self,
            prompt: str,
            model: ImageModel,
            mode: ImageMode = ImageMode.square
    ) -> Union[str, InputFile, None]:
        """Генерирует изображение и возвращает URL или base64 строку"""
        if model == ImageModel.NEUROIMG:
            return await self._generate_neuroimg(prompt, mode)
        elif model == ImageModel.GPT_IMAGE_1:
            result = await self._generate_gpt_image(prompt, mode)
            if not result:
                return None
            image_data = base64.b64decode(result)
            file = InputFile(BytesIO(image_data), filename="image.png")
            return file
        else:
            return await self._generate_dalle(prompt, mode, model.value)

    async def _generate_neuroimg(self, prompt: str, mode: ImageMode) -> Optional[str]:
        """Генерация через neuroimg.art API"""
        width, height = self.get_image_size(mode)
        payload = {
            "token": self.neuroimg_api_key,
            "model": "RealisticVision-V4fp8_e4m3fn",
            "prompt": prompt,
            "width": width,
            "height": height,
            "sampler": "DPM++ 2M Karras",
            "steps": 35,
            "stream": True
        }

        timeout = aiohttp.ClientTimeout(total=360)
        for attempt in range(2):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                            "https://neuroimg.art/api/v1/generate",
                            json=payload
                    ) as response:
                        async for line in response.content:
                            if line:
                                status = json.loads(line)
                                if status["status"] == "SUCCESS":
                                    return status['image_url']
            except Exception as ex:
                loguru.logger.error(f"Neuroimg error (attempt {attempt + 1}): {ex}")
        return None

    async def _generate_dalle(
            self,
            prompt: str,
            mode: ImageMode,
            model: str
    ) -> Optional[str]:
        """Генерация через DALL-E API"""
        size = self.get_image_size_openai(mode)
        for attempt in range(2):
            try:
                response = await self.openai_client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                    n=1,
                    quality="standard"
                )
                return response.data[0].url
            except Exception as ex:
                loguru.logger.error(f"DALL-E error (attempt {attempt + 1}): {ex}")
        return None

    async def _generate_gpt_image(
            self,
            prompt: str,
            mode: ImageMode
    ) -> Optional[str]:
        """Генерация через GPT-Image-1 API"""
        # Для GPT-Image-1 размеры не указываются в API
        for attempt in range(2):
            try:
                response = await self.openai_client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    n=1,
                    response_format="b64_json",
                    moderation="low"
                )
                return response.data[0].b64_json
            except Exception as ex:
                loguru.logger.error(f"GPT-Image error (attempt {attempt + 1}): {ex}")
        return None