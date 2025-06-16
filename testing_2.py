import aiohttp
import asyncio
import json


async def generate_image_stream(prompt: str, api_key: str):
    async with aiohttp.ClientSession() as session:
        payload = {
            "token": api_key,
            "model": "RealisticVision-V4fp8_e4m3fn",
            "prompt": prompt,
            "steps": 35,
            "stream": True
        }

        async with session.post(
                "https://neuroimg.art/api/v1/generate",
                json=payload,
                timeout=600
        ) as response:
            async for line in response.content:
                if line:
                    status = json.loads(line)
                    with open("result.json", "w", encoding="utf-8") as f:
                        json.dump(status, f, ensure_ascii=False, indent=4)
                    if status["status"] == "WAITING":
                        print(f"В очереди: {status['queue_position']}/{status['queue_total']}")
                    elif status["status"] == "RUNNING":
                        print("Генерация...")
                    elif status["status"] == "SUCCESS":
                        print(f"Готово! URL: {status['image_url']}")
                        return status['image_url']

# promt = """
# Ультрареалистичная сцена: киберпанк-город ночью, дождь, неоновые огни отражаются в лужах, девушка в плаще стоит с зонтом, летающие машины пролетают над улицей, насыщенные цвета, атмосфера загадочности, 4K, cinematic lighting
# """
promt = """
Девушка смотрит на сельский туалет в огороде в деревне"""
async def main():
    result = await generate_image_stream(
        prompt=promt,
        api_key="9c5970dc-7b61-4db0-9bc5-9cc42d57593c"
    )
    print(result)

asyncio.run(main())