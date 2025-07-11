import aiohttp
import json
from bot.logger import logger
from enum import Enum
from openai import AsyncOpenAI
from typing import Optional, List, Tuple, Union
import base64
from aiogram.types import BufferedInputFile
from bot.utils.keys import KEY_OPENAI, KEY_IMAGE_GEN


class ImageMode(str, Enum):
    square = "square"
    horizontal = "horizontal"
    vertical = "vertical"


class ImageQuality(str, Enum):
    standard = "standard"
    hd = "hd"
    low = "low"
    medium = "medium"
    high = "high"


class ImageModel(str, Enum):
    NEUROIMG = "neuroArt"
    GPT_LOW = "gpt-image-1-low"
    GPT_MEDIUM = "gpt-image-1-medium"
    GPT_HIGH = "gpt-image-1-high"
    DALLE = "dall-e-3"
    DALLE_HD = "dall-e-3-hd"


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
    def get_image_size_dalle(mode: ImageMode) -> str:
        if mode == ImageMode.square:
            return "1024x1024"
        elif mode == ImageMode.horizontal:
            return "1792x1024"
        elif mode == ImageMode.vertical:
            return "1024x1792"
        raise ValueError("Invalid image mode")

    @staticmethod
    def get_image_size_openai(mode: ImageMode) -> str:
        if mode == ImageMode.square:
            return "1024x1024"
        elif mode == ImageMode.horizontal:
            return "1536x1024"
        elif mode == ImageMode.vertical:
            return "1024x1536"
        raise ValueError("Invalid image mode")

    @staticmethod
    def get_model_choices() -> List[Tuple[str, str, str]]:
        return [
            (
                "NeuroArt",
                ImageModel.NEUROIMG.value,
                "🎨 Художественная генерация изображения через neuroimg.art"
            ),
            (
                "Gpt-image-1-low",
                ImageModel.GPT_LOW.value,
                "Мультимодульная модель от OpenAI Low"
            ),
            (
                "Gpt-image-1-medium",
                ImageModel.GPT_MEDIUM.value,
                "Мультимодульная модель от OpenAI Medium"
            ),
            (
                "Gpt-image-1-high",
                ImageModel.GPT_HIGH.value,
                "Мультимодульная модель от OpenAI High"
            ),
            (
                "Dall-e-3",
                ImageModel.DALLE.value,
                "Флагманская модель от OpenAI. Обладает высоким качеством интерпретации текста и генерацией с отличной композицией"
            ),
            (
                "Dall-e-3-hd",
                ImageModel.DALLE_HD.value,
                "Продвинутая версия DALL·E 3 с улучшенной детализацией и глубиной изображения. Подходит для иллюстраций и профессиональных задач."
            ),
        ]

    async def generate(
            self,
            prompt: str,
            model: ImageModel,
            mode: ImageMode
    ) -> Union[str, BufferedInputFile, None]:
        """Генерирует изображение и возвращает URL, BufferedInputFile или None"""
        try:
            if model == ImageModel.NEUROIMG:
                return await self._generate_neuroimg(prompt, mode)
            if model in [ImageModel.GPT_LOW, ImageModel.GPT_MEDIUM, ImageModel.GPT_HIGH]:
                quality_param = self._get_gpt_quality(model)
                result = await self._generate_gpt_image(prompt, mode, quality_param)
                if not result:
                    return None
                image_data = base64.b64decode(result)
                return BufferedInputFile(image_data, filename="your_image.png")
            if model in [ImageModel.DALLE, ImageModel.DALLE_HD]:
                quality_param = self._get_dally_quality(model)
                return await self._generate_dalle(prompt, mode, quality_param)
            return None
        except Exception as ex:
            logger.error(ex)

    def _get_gpt_quality(self, model: ImageModel) -> str | None:
        """Определяет качество для GPT-Image моделей"""
        if model == ImageModel.GPT_LOW:
            return ImageQuality.low.value
        if model == ImageModel.GPT_MEDIUM:
            return ImageQuality.medium.value
        if model == ImageModel.GPT_HIGH:
            return ImageQuality.high.value
        logger.debug("Ошибка значения")
        return None

    def _get_dally_quality(self, model: ImageModel) -> str | None:
        """Определяет качество для GPT-Image моделей"""
        if model == ImageModel.DALLE:
            return ImageQuality.standard.value
        if model == ImageModel.DALLE_HD:
            return ImageQuality.hd.value
        logger.debug("Ошибка значения")
        return None

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
                logger.error(f"Neuroimg error (attempt {attempt + 1}): {ex}")
        return None

    async def _generate_dalle(
            self,
            prompt: str,
            mode: ImageMode,
            quality_param: str
    ) -> Optional[str]:
        """Генерация через DALL-E API"""
        size = self.get_image_size_dalle(mode)
        for attempt in range(2):
            try:
                response = await self.openai_client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size=size,
                    n=1,
                    quality=quality_param
                )
                return response.data[0].url
            except Exception as ex:
                # Вытаскиваем тело ответа, если это HTTP-исключение от httpx
                content = getattr(ex, 'response', None)
                if content is not None:
                    try:
                        detail = await content.aread()
                        logger.error(f"DALL-E error (attempt {attempt + 1}): {ex} | Response: {detail.decode('utf-8')}")
                    except Exception as inner_ex:
                        logger.error(
                            f"DALL-E error (attempt {attempt + 1}): {ex} | (Failed to read response body: {inner_ex})")
                else:
                    logger.error(f"DALL-E error (attempt {attempt + 1}): {ex}")
        return None

    async def _generate_gpt_image(
            self,
            prompt: str,
            mode: ImageMode,
            quality: str
    ) -> Optional[str]:
        """Генерация через GPT-Image-1 API"""
        size = self.get_image_size_openai(mode)
        for attempt in range(2):
            try:
                response = await self.openai_client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size=size,
                    n=1,
                    quality=quality
                )
                return response.data[0].b64_json
            except Exception as ex:
                content = getattr(ex, 'response', None)
                if content is not None:
                    try:
                        detail = await content.aread()
                        logger.error(
                            f"GPT-Image error (attempt {attempt + 1}): {ex} | Response: {detail.decode('utf-8')}")
                    except Exception as inner_ex:
                        logger.error(
                            f"GPT-Image error (attempt {attempt + 1}): {ex} | (Failed to read response body: {inner_ex})")
                else:
                    logger.error(f"GPT-Image error (attempt {attempt + 1}): {ex}")
        return None


# Инициализация генератора
image_generator = ImageGenerator(
    neuroimg_api_key=KEY_IMAGE_GEN,
    openai_api_key=KEY_OPENAI
)
