import json
from pathlib import Path
from bot.database.models import Tariff, GenerationModel
from bot.database.session import get_session
from bot.logger import logger
from sqlalchemy import select



async def load_tariffs(file_path: str | Path):
    with open(file_path, 'r') as f:
        tariffs_data = json.load(f)
    async with get_session() as session:
        result = await session.execute(select(Tariff))
        existing_tariffs = {tariff.id: tariff for tariff in result.scalars()}

        seen_ids = set()

        for item in tariffs_data:
            tariff_id = item["id"]
            seen_ids.add(tariff_id)

            if tariff_id in existing_tariffs:
                tariff = existing_tariffs[tariff_id]
                tariff.title = item["title"]
                tariff.price_rub = item["price_rub"]
                tariff.tokens_amount = item["tokens_amount"]
                tariff.bonus_tokens = item["bonus_tokens"]
                tariff.sort_order = item["sort_order"]
                tariff.is_active = True
            else:
                tariff = Tariff(
                    id=tariff_id,
                    title=item["title"],
                    price_rub=item["price_rub"],
                    tokens_amount=item["tokens_amount"],
                    bonus_tokens=item["bonus_tokens"],
                    sort_order=item["sort_order"],
                    is_active=True
                )
                session.add(tariff)
        # Деактивируем отсутствующие тарифы
        for tariff_id, tariff in existing_tariffs.items():
            if tariff_id not in seen_ids:
                tariff.is_active = False

        await session.commit()
        logger.info(f"Обновлено {len(tariffs_data)} тарифов")


async def load_generation_models(file_path: str | Path):
    with open(file_path, 'r') as f:
        models_data = json.load(f)
    async with get_session() as session:
        result = await session.execute(select(GenerationModel))
        existing_models = {model.name: model for model in result.scalars()}

        seen_names = set()

        for item in models_data:
            model_name = item["name"]
            seen_names.add(model_name)

            if model_name in existing_models:
                model = existing_models[model_name]
                model.token_cost = item["token_cost"]
                model.is_active = True
            else:
                model = GenerationModel(
                    name=model_name,
                    token_cost=item["token_cost"],
                    is_active=True
                )
                session.add(model)

        # Деактивируем отсутствующие модели
        for model_name, model in existing_models.items():
            if model_name not in seen_names:
                model.is_active = False

        await session.commit()
        logger.info(f"Обновлено {len(models_data)} моделей генерации")