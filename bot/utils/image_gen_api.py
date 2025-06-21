import aiohttp
import asyncio
import json
from enum import Enum

import loguru

from bot.utils.keys import KEY_IMAGE_GEN


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


async def generate_image_stream(prompt: str, mode: ImageMode = ImageMode.square, api_key: str = KEY_IMAGE_GEN):
    timeout = aiohttp.ClientTimeout(total=360)
    width, height = get_image_size(mode)
    payload = {
        "token": api_key,
        "model": "epiCRealismXL-VXVI-LastFAME",
        "prompt": prompt,
        "width": width,
        "height": height,
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


# async def generate_image_stream(prompt: str, mode: ImageMode = ImageMode.square, api_key: str = KEY_IMAGE_GEN):
#     timeout = aiohttp.ClientTimeout(total=360)
#     width, height = get_image_size(mode)
#     payload = {
#         "token": api_key,
#         "model": "CyberRealisticXL-v5.3",
#         "prompt": prompt,
#         "width": width,
#         "height": height,
#         "steps": 35,
#         "stream": True
#     }
#
#     async with aiohttp.ClientSession(timeout=timeout) as session:
#         for attempt in range(2):
#             try:
#                 async with session.post(
#                         "https://neuroimg.art/api/v1/generate",
#                         json=payload
#                 ) as response:
#                     # Проверка HTTP-статуса
#                     if response.status != 200:
#                         error_body = await response.text()
#                         loguru.logger.error(
#                             f"API error [attempt {attempt + 1}]: "
#                             f"Status={response.status}, Response={error_body}"
#                         )
#                         continue  # Переход к следующей попытке
#
#                     # Обработка потокового ответа
#                     error_message = None
#                     async for line in response.content:
#                         if line:
#                             try:
#                                 status = json.loads(line)
#                                 if status["status"] == "SUCCESS":
#                                     return status['image_url']
#                                 elif status["status"] == "ERROR":
#                                     error_message = status.get('message', 'Unknown error')
#                             except json.JSONDecodeError:
#                                 loguru.logger.error(f"Invalid JSON: {line}")
#
#                     # Если дошли до конца потока без успеха
#                     if error_message:
#                         loguru.logger.error(
#                             f"Generation failed [attempt {attempt + 1}]: "
#                             f"{error_message}"
#                         )
#
#             except aiohttp.ClientError as e:
#                 loguru.logger.error(f"Network error [attempt {attempt + 1}]: {str(e)}")
#             except Exception as ex:
#                 loguru.logger.error(f"Unexpected error [attempt {attempt + 1}]: {str(ex)}")
#
#     return None
# async def generate_image_stream(prompt: str, mode: ImageMode = ImageMode.square, api_key: str = KEY_IMAGE_GEN):
#     timeout = aiohttp.ClientTimeout(total=360)
#     width, height = get_image_size(mode)
#     payload = {
#         "token": api_key,
#         "model": "CyberRealisticXL-v5.3",
#         "prompt": prompt,
#         "width": width,
#         "height": height,
#         "steps": 35,
#         "stream": True
#     }
#
#     start_time = asyncio.get_event_loop().time()
#     loguru.logger.info(f"Starting generation for prompt: {prompt[:50]}...")
#
#     async with aiohttp.ClientSession(timeout=timeout) as session:
#         for attempt in range(2):
#             try:
#                 attempt_start = asyncio.get_event_loop().time()
#                 async with session.post(
#                         "https://neuroimg.art/api/v1/generate",
#                         json=payload
#                 ) as response:
#
#                     # Логируем статус и время ответа
#                     response_time = asyncio.get_event_loop().time() - attempt_start
#                     loguru.logger.debug(
#                         f"Attempt {attempt + 1} response time: {response_time:.2f}s, status: {response.status}")
#
#                     if response.status != 200:
#                         error_body = await response.text()
#                         loguru.logger.error(
#                             f"API error [attempt {attempt + 1}]: "
#                             f"Status={response.status}, Response={error_body}"
#                         )
#                         continue
#
#                     # Собираем все ответы для анализа
#                     full_response = []
#                     error_message = None
#                     success_url = None
#
#                     async for line in response.content:
#                         if line:
#                             full_response.append(line)
#                             try:
#                                 status = json.loads(line)
#                                 loguru.logger.trace(f"Stream data: {status}")
#
#                                 if status["status"] == "SUCCESS":
#                                     success_url = status.get('image_url')
#                                 elif status["status"] == "ERROR":
#                                     error_message = status.get('message', 'Unknown error')
#                             except json.JSONDecodeError:
#                                 loguru.logger.warning(f"Invalid JSON: {line}")
#
#                     # Анализируем результаты
#                     if success_url:
#                         loguru.logger.info(f"Generation success on attempt {attempt + 1}")
#                         return success_url
#
#                     if error_message:
#                         loguru.logger.error(
#                             f"Generation failed [attempt {attempt + 1}]: {error_message}\n"
#                             f"Full response: {b''.join(full_response).decode()[:500]}"
#                         )
#                     else:
#                         loguru.logger.error(
#                             f"Generation failed [attempt {attempt + 1}]: No success or error status received\n"
#                             f"Full response: {b''.join(full_response).decode()[:500]}"
#                         )
#
#             except aiohttp.ClientError as e:
#                 loguru.logger.error(f"Network error [attempt {attempt + 1}]: {str(e)}")
#             except Exception as ex:
#                 loguru.logger.exception(f"Unexpected error [attempt {attempt + 1}]: {str(ex)}")
#             finally:
#                 # Пауза между попытками
#                 await asyncio.sleep(1)
#
#     total_time = asyncio.get_event_loop().time() - start_time
#     loguru.logger.error(f"Generation failed after 2 attempts. Total time: {total_time:.2f}s")
#     return None

# async def main():
#     result = await generate_image_stream(
#         "Розовый кит в очках пьет мартини"
#     )
#     print(result)
#
# asyncio.run(main())