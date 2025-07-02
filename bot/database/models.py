from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, SmallInteger, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship



Base = declarative_base()


class User(Base):
    """Модель пользователя Telegram"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50))
    join_date = Column(DateTime, default=datetime.utcnow) # дата регистрации
    is_admin = Column(Boolean, default=False) # является админом или нет
    tokens = Column(Integer, default=0)  # Количество токенов для генерации

    referral_code = Column(String(20), unique=True, nullable=False) # Реферальный код пользователя
    invited_by_code = Column(String(20), ForeignKey('users.referral_code'), nullable=True) # Реферальный код пригласившего

    inviter = relationship(
        'User',
        back_populates='invited_users',
        foreign_keys=[invited_by_code],
        remote_side=[referral_code],
        primaryjoin='User.invited_by_code == User.referral_code'
    )

    invited_users = relationship(
        'User',
        back_populates='inviter',
        foreign_keys=[invited_by_code],
        primaryjoin='User.invited_by_code == User.referral_code'
    )

    referrals_given = relationship(
        'Referral',
        back_populates='inviter',
        cascade="all, delete-orphan",
        primaryjoin='User.referral_code == Referral.inviter_code'  # Явное указание условия связи
    )

    referral_info = relationship(
        'Referral',
        back_populates='invited_user',
        uselist=False,
        primaryjoin='User.id == Referral.invited_user_id'  # Явное указание условия связи
    )




class Tariff(Base):
    """Модель пакетного тарифа (по количеству генераций)"""
    __tablename__ = 'tariffs'

    id = Column(String, primary_key=True)  # Например, "pack_100"
    title = Column(String, nullable=False)  # Название тарифа (например, "100 токенов")
    price_rub = Column(Integer, nullable=False)  # Цена в рублях
    tokens_amount = Column(Integer, default=0)  # Сколько токенов входит в пакет
    bonus_tokens = Column(Integer, default=0)  # Бонусные токены (например, +10)
    is_active = Column(Boolean, default=True)  # Доступен ли тариф
    sort_order = Column(SmallInteger, default=0)  # Порядок отображения в списке


class Referral(Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True)
    inviter_code = Column(String(20), ForeignKey('users.referral_code'), nullable=False) # Код пригласившего
    invited_user_id = Column(Integer, ForeignKey('users.id'), nullable=False) # id пользователя которого пригласил
    reward_amount_tokens = Column(Integer, default=0)  # сколько бонусов выдали
    created_at = Column(DateTime, default=datetime.utcnow)

    inviter = relationship(
        'User',
        foreign_keys=[inviter_code],
        back_populates='referrals_given'  # Синхронизация с обратной связью
    )

    invited_user = relationship(
        'User',
        foreign_keys=[invited_user_id],
        back_populates='referral_info'  # Синхронизация с обратной связью
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tariff_id = Column(String, ForeignKey("tariffs.id"), nullable=False)

    amount = Column(Integer, nullable=False)  # сумма в рублях или центах/копейках
    currency = Column(String(10), default="RUB")  # RUB / USDT / BTC и т.п.
    status = Column(String(20), default="pending")  # pending / paid / failed / expired
    payment_method = Column(String(30), nullable=True)  # yookassa / crypto / btc и т.д.
    external_id = Column(String, nullable=True) # Индивидуальный идентификатор платежа

    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    user = relationship("User", backref="payments")
    tariff = relationship("Tariff", backref="payments")


class ImageGeneration(Base):
    __tablename__ = 'image_generations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    id_api = Column(String, nullable=True) # Уникальный ключ от API
    model_id = Column(Integer, ForeignKey("generation_models.id"), nullable=True)

    prompt = Column(String, nullable=False)  # Запрос, который использовал пользователь
    filename = Column(String, nullable=False)  # путь до изображения
    url = Column(String, nullable=True)  # ссылка на изображение
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")  # pending / success / error
    
    # Связь с пользователем и модели генерации
    user = relationship("User", backref="image_generations")
    model = relationship("GenerationModel", backref="image_generations")


class GenerationModel(Base):
    __tablename__ = 'generation_models'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # Название модели (gpt-image-1, "neuroimg", "dall-e-3")
    token_cost = Column(Integer, default=0)  # Сколько токенов списывается за 1 генерацию
    is_active = Column(Boolean, default=True)  # Можно ли сейчас использовать модель


