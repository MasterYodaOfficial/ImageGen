# from openai import OpenAI
#
# client = OpenAI(
#     api_key="sk-rzE0V7pRVABFfWdl68qAgMKNvzCEs2Pf",
#     base_url="https://api.proxyapi.ru/openai/v1",
# )
#
# prompt = """
# Стеклянная бутылка, внутри которой плывет корабль посреди шторма
# """
#
# result = client.images.generate(
#     model="dall-e-3",
#     prompt=prompt
# )
#
# image_url = result.data[0].url
# print(image_url)

from openai import OpenAI
import base64

client = OpenAI(
    api_key="sk-rzE0V7pRVABFfWdl68qAgMKNvzCEs2Pf",
    base_url="https://api.proxyapi.ru/openai/v1",
)

# prompt = """
# Стеклянная бутылка, внутри которой плывет корабль посреди шторма
# """
prompt = """
Энакин Скайуокер в повреждённом костюме Дарта Вейдера стоит на коленях перед простым каменным надгробием на пустынной планете Татуин. Его шлем снят — обгоревшее лицо с механическими имплантами искажено болью, жёлтые глаза ситха полны слёз. Стиль: фотореализм 8K, детализированные текстуры кожи, металла и камня, драматическое освещение. Настроение: глубокая скорбь и раскаяние"""

result = client.images.generate(
    model="gpt-image-1",
    quality="high",
    prompt=prompt
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

with open("image.png", "wb") as f:
    f.write(image_bytes)