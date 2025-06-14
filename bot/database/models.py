from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, SmallInteger, ForeignKey
from sqlalchemy.orm import declarative_base
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
    counter = Column(Integer, default=3)  # Остаток генераций

    referral_code = Column(String(20), unique=True, nullable=False) # Реферальный код пользователя
    invited_by_code = Column(String(20), ForeignKey('users.referral_code'), nullable=True) # Реферальный код пригласившего

    # ✅ [ИСПРАВЛЕНО] Указан `foreign_keys`, чтобы избежать амбигуити
    inviter = relationship(
        'User',
        back_populates='invited_users',
        foreign_keys=[invited_by_code],
        remote_side=[referral_code],
        primaryjoin='User.invited_by_code == User.referral_code'
    )

    # ✅ [ИСПРАВЛЕНО] Явно указан `foreign_keys`
    invited_users = relationship(
        'User',
        back_populates='inviter',
        foreign_keys=[invited_by_code],
        primaryjoin='User.invited_by_code == User.referral_code'
    )

    # ✅ [ИСПРАВЛЕНО] Добавлен явный primaryjoin
    referrals_given = relationship(
        'Referral',
        back_populates='inviter',
        cascade="all, delete-orphan",
        primaryjoin='User.referral_code == Referral.inviter_code'  # Явное указание условия связи
    )

    # ✅ [ИСПРАВЛЕНО] Добавлен явный primaryjoin
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
    title = Column(String, nullable=False)  # Название тарифа (например, "100 генераций")
    price_rub = Column(Integer, nullable=False)  # Цена в рублях
    generation_amount = Column(Integer, nullable=False)  # Сколько генераций входит в пакет
    bonus_generations = Column(Integer, default=0)  # Бонусные генерации (например, +10)
    is_active = Column(Boolean, default=True)  # Доступен ли тариф
    sort_order = Column(SmallInteger, default=0)  # Порядок отображения в списке


class Referral(Base):
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True)
    inviter_code = Column(String(20), ForeignKey('users.referral_code'), nullable=False) # Код пригласившего
    invited_user_id = Column(Integer, ForeignKey('users.id'), nullable=False) # id пользователя которого пригласил
    reward_amount = Column(Integer, default=0)  # сколько бонусов выдали
    created_at = Column(DateTime, default=datetime.utcnow)

    # ✅ [ИСПРАВЛЕНО] Упрощено определение связи
    inviter = relationship(
        'User',
        foreign_keys=[inviter_code],
        back_populates='referrals_given'  # Синхронизация с обратной связью
    )

    # ✅ [ИСПРАВЛЕНО] Упрощено определение связи
    invited_user = relationship(
        'User',
        foreign_keys=[invited_user_id],
        back_populates='referral_info'  # Синхронизация с обратной связью
    )