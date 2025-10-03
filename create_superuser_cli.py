import asyncio

import click
from sqlalchemy import select

from src.core.db import get_async_session_cm
from src.core.logger import logger
from src.models.user import User
from src.schemas.validators import (
    email_validator,
    password_validator,
    phone_validator,
    telegram_id_validator,
    username_validator,
)
from src.services.auth import PasswordService


async def init_db_and_superuser(
    username: str,
    email: str,
    password: str,
    phone: str,
    telegram_id: str | None,
) -> None:
    """Инициализация базы данных и создание супер-юзера с валидацией данных."""
    try:
        validated_username = username_validator(username)
        validated_email = email_validator(email)
        validated_password = password_validator(password)
        validated_phone = phone_validator(phone)
        validated_telegram_id = (
            telegram_id_validator(telegram_id) if telegram_id else None
        )
    except Exception as error:
        logger.error(f'Ошибка валидации: {error}')
        return

    try:
        async with get_async_session_cm() as session:
            result = await session.execute(
                select(User).where(
                    User.email == validated_email,
                ),
            )
            user: User | None = result.scalar_one_or_none()

            if not user:
                password_hashed: str = PasswordService.hash_password(
                    validated_password,
                )
                superuser = User(
                    username=validated_username,
                    email=validated_email,
                    password=password_hashed,
                    phone=validated_phone,
                    tg_id=validated_telegram_id,
                    is_superuser=True,
                    role='admin',
                )
                session.add(superuser)
                await session.commit()
                await session.refresh(superuser)

                logger.info(
                    f'Суперпользователь {validated_email} создан',
                    user=superuser,
                )
            else:
                logger.info(
                    f'Суперпользователь {validated_email} уже существует',
                    user=user,
                )
    except Exception as error:
        logger.error(f'Ошибка при создании суперпользователя: {error}')


@click.group()
def cli() -> None:
    """Основная команда для управления приложением."""
    pass


@cli.command()
def create_superuser() -> None:
    """Команда для создания суперпользователя."""
    try:
        # Показываем описание формата полей
        click.echo('Введите данные для создания суперпользователя:')
        click.echo(
            '1. Username должен быть от 3 до 50 символов, '
            'только латинские буквы, цифры и _',
        )
        click.echo(
            '2. Email должен быть в формате user@example.com '
            'и длиной от 5 до 100 символов',
        )
        click.echo(
            '3. Пароль должен содержать минимум 8 символов, '
            'строчные и заглавные буквы, цифры и спецсимволы',
        )
        click.echo('4. Телефон должен быть в формате +79998887766')
        click.echo(
            '5. Telegram ID должен быть числовым, '
            'например, 123456789 (необязательно)',
        )

        username = click.prompt('Введите имя пользователя', type=str)
        email = click.prompt('Введите email', type=str)
        password = click.prompt('Введите пароль', hide_input=True, type=str)
        phone = click.prompt('Введите номер телефона', type=str)
        tg_id = click.prompt(
            'Введите Telegram ID (необязательно)',
            type=str,
            default='',
        )

        tg_id = None if tg_id.strip() == '' else tg_id

        asyncio.run(
            init_db_and_superuser(username, email, password, phone, tg_id),
        )
        logger.info(
            'Команда для создания суперпользователя выполнена успешно.',
        )
    except Exception as error:
        logger.error(f'Ошибка при выполнении команды: {error}')


if __name__ == '__main__':
    cli()
