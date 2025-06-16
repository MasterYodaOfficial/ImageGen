import aiohttp
import json
import asyncio


async def free_generate(prompt: str, api_key: str):
    async with aiohttp.ClientSession() as session:
        payload = {
            "token": api_key,
            "prompt": prompt,
            "stream": True
        }

        async with session.post(
                "https://neuroimg.art/api/v1/free-generate",
                json=payload
        ) as response:
            print(response.status)
            print(response.content)
            async for line in response.content:
                if line:
                    data = json.loads(line)
                    if data["status"] == "SUCCESS":
                        print(data["image_url"])
                        return data["image_url"]
                    print(f"Статус: {data['status']}")

promt = """
Космический корабль в космосе на орбите планеты. Очень реалистично. Как будто это живая фотография."""

async def main():
    result = await free_generate(
        prompt=promt,
        api_key="9c5970dc-7b61-4db0-9bc5-9cc42d57593c"
    )
    print(result)

asyncio.run(main())