from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from duty.database.sqlite import setup_collate_function


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from duty.database.models import Base  # noqa
target_metadata = Base.metadata


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        setup_collate_function(connection)

        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if not context.is_offline_mode():
    run_migrations_online()
else:
    raise Exception('Offline run disabled')