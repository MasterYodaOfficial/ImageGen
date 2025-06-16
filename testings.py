from openai import OpenAI
import base64

client = OpenAI(
    api_key="sk-IRZvEZAKzr1f8MtgQ7PMkS7xjgVKof6o",
    base_url="https://api.proxyapi.ru/openai/v1",
)

prompt = """
Программист сидит за ноутбуком на столе, в космическом корабле на орбите земли. Из окна красивый вид на землю. Реалистично.
"""

result = client.images.generate(
    model="gpt-image-1",
    prompt=prompt,
    quality="medium",
    output_format="jpeg",


)

# result2 = client.images.generate(
#     model="dall-e-2",
#     prompt=prompt
# )

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# image_url = result2.data[0].url
# print(image_url)

with open("image_low_.jpeg", "wb") as f:
    f.write(image_bytes)
