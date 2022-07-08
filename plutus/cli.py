"""
CLI
"""

import click
import logging
from dotenv import load_dotenv
import subprocess
import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from plutus import util
from plutus.db import util as db_util
from plutus.aws_ecs_task import process_price_channel as process_ticker_channel_ecs_task


util.configure_logging()
log = logging.getLogger(__name__)


@click.group()
def command_group():
    """
    Click command group
    """


@click.command()
def create_sqldb():
    """
    Creates the SQL database
    """

    db_util.create_sqldb()


@click.command()
def drop_sqldb():
    """
    Drops the SQL database
    """

    db_util.drop_sqldb()


@click.command()
def truncate_sqldb():
    """
    Truncates the SQL tables
    """

    db_util.truncate_sql_db()


@click.command()
def sqldb_migration():
    """
    Makes an Alembic SQL migraiton
    """

    subprocess.run(
        "alembic -c plutus/db/alembic/alembic.ini revision --autogenerate",
        shell=True,
        check=True,
    )


@click.command()
def upgrade_sqldb():
    """
    Upgrades the SQL DB's Alembic verion
    """

    subprocess.run(
        "alembic -c plutus/db/alembic/alembic.ini upgrade head",
        shell=True,
        check=True,
    )


@click.command()
def downgrade_sqldb():
    """
    Downgrades the SQL DB's Alembic verion
    """

    subprocess.run(
        "alembic -c plutus/db/alembic/alembic.ini downgrade base",
        shell=True,
        check=True,
    )


@click.command()
def flake8():
    """
    Runs the Flake8 lint check
    """

    try:
        subprocess.run(
            "flake8 plutus --count --max-complexity=10 --max-line-length=162 --statistics",
            shell=True,
            check=True,
        )
    except:
        pass


@click.command()
def lint():
    """
    Runs the black linter
    """

    try:
        subprocess.run(
            "black plutus",
            shell=True,
            check=True,
        )
    except:
        pass


@click.command()
@click.option("-e", "--exchange", required=True, type=str)
@click.option("-s", "--symbol", required=True, type=str)
def process_ticker_channel(exchange, symbol):
    """
    Processes an exchange price feed
    """

    asyncio.run(process_ticker_channel_ecs_task.handler(exchange, symbol))


# @click.command()
# def price_cache_sql_etl():
#     """
#     ETL price data from Redis to SQL
#     """

#     asyncio.run(channel_util.price_cache_sql_etl())


def main():
    """
    Run the cli
    """

    for command in [
        sqldb_migration,
        upgrade_sqldb,
        downgrade_sqldb,
        create_sqldb,
        drop_sqldb,
        flake8,
        truncate_sqldb,
        lint,
        process_ticker_channel,
        # price_cache_sql_etl
    ]:
        command_group.add_command(command)

    command_group()


if __name__ == "__main__":
    main()
