"""
SQLAlchemy utils
"""

from __future__ import annotations
import os
import logging
from typing import List, Optional, Dict, Tuple, Union
import logging.config

import sqlalchemy_utils
from sqlalchemy.orm import sessionmaker, scoped_session, class_mapper
from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.query import Query
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, DateTime
from sqlalchemy import inspect, MetaData
from sqlalchemy import text
from sqlalchemy import func as sql_func
from sqlalchemy_filters import apply_filters, apply_loads, apply_pagination, apply_sort


log = logging.getLogger(__name__)


SQLBaseModel = declarative_base()
sql_engine = None
sql_session = None


class SQLModel(SQLBaseModel):
    """
    SQL model base class
    """

    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_instant = Column(DateTime, default=sql_func.now())
    updated_instant = Column(DateTime, default=sql_func.now(), onupdate=sql_func.now())

    @classmethod
    def query(cls, sql_session: Session) -> Query:
        """
        Query from the model's table
        """

        return sql_session.query(cls)

    @classmethod
    def filtered_query(
        cls,
        sql_session: Session,
        filters: List = None,
        sort: List = None,
        loads: List = None,
        page: int = None,
        per_page: int = None,
        qs=None,
    ) -> Query:
        """
        Filtered query
        """

        pagination = None
        if not qs:
            qs = cls.query(sql_session)
        if filters:
            qs = apply_filters(qs, filters)
        if sort:
            qs = apply_sort(qs, sort)
        if page and per_page:
            qs, pagination = apply_pagination(qs, page_number=page, page_size=per_page)
        if loads:
            qs = apply_loads(qs, loads)

        if pagination:
            return qs.all(), pagination
        else:
            return qs.all()

    @classmethod
    def get_all(
        cls,
        sql_session: Session,
        page: int = None,
        per_page: int = None,
        **kwargs,
    ) -> List[Optional[SQLModel]]:
        """
        Select all matching fields as kwargs
        """

        if page and per_page:
            q = (
                cls.query(sql_session)
                .filter_by(**kwargs)
                .limit(per_page)
                .offset((page - 1) * per_page)
            )
        else:
            q = cls.query(sql_session).filter_by(**kwargs)

        return q.all()

    @classmethod
    def get_all_ids(
        cls,
        sql_session: Session,
        model_ids: List[int],
        page: int = None,
        per_page: int = None,
    ):
        """
        Gets all records from a list of IDs
        """

        if page and per_page:
            q = (
                cls.query(sql_session)
                .filter(cls.id.in_(model_ids))
                .limit(per_page)
                .offset((page - 1) * per_page)
            )
        else:
            q = cls.query(sql_session).filter(cls.id.in_(model_ids))

        return {model.id: model for model in q.all()}

    @classmethod
    def filter(cls, sql_session: Session, *args) -> List[Optional[SQLModel]]:
        """
        Select all matching a SQLAlchemy filter
        """

        return cls.query(sql_session).filter(*args).all()

    @classmethod
    def get(cls, sql_session: Session, **kwargs) -> Optional[SQLModel]:
        """
        Select the first record from the model's table
        """

        return cls.query(sql_session).filter_by(**kwargs).first()

    @classmethod
    def get_or_create(
        cls, sql_session: Session, commit: bool = True, flush: bool = False, **kwargs
    ) -> Tuple[SQLModel, bool]:
        """
        Select for a record based. If none exists, create one
        """

        created = False
        model = cls.get(sql_session, **kwargs)
        if not model:
            model = cls.insert(sql_session, commit, flush, **kwargs)
            created = True

        return model, created

    @classmethod
    def get_fields(cls) -> List[str]:
        """
        Gets the model's field names
        """

        return class_mapper(cls).c.keys()

    @classmethod
    def insert(
        cls, sql_session: Session, commit: bool = True, flush: bool = False, **kwargs
    ) -> SQLModel:
        """
        Inserts a record
        """

        model = cls(**kwargs)
        sql_session.add(model)
        if flush:
            sql_session.flush()

        if commit:
            commit_transaction(sql_session)

        return model

    def update(
        self, sql_session: Session, commit: bool = True, flush: bool = False
    ) -> None:
        """
        Updates itself in the database
        """

        sql_session.add(self)
        if flush:
            sql_session.flush()

        if commit:
            commit_transaction(sql_session)

    def delete(
        self, sql_session: Session, commit: bool = True, flush: bool = False
    ) -> None:
        """
        Deletes itself from the database
        """

        sql_session.delete(self)
        if flush:
            sql_session.flush()

        if commit:
            commit_transaction(sql_session)

    @classmethod
    def exist(
        cls, sql_session: Session, values: List[int], field: str = "id"
    ) -> Union[bool, List[int]]:
        """
        Validates a list of values exists. Returns True if they all exist, or a list
        of non-existent values.
        """

        query = text(
            f"""
                SELECT array_agg({field})
                FROM unnest(:values) {field}
                WHERE {field} NOT IN (
                    SELECT
                        {field}
                    FROM
                        {cls.__tablename__}
                )
            """
        )

        return sql_session.execute(query, {"values": values}).scalar()


def sql_connection_string():
    """
    Gets the SQL connection string from env vars
    """

    return f"postgresql+pg8000://{os.environ['SQL_USER']}:{os.environ['SQL_PASSWORD']}@{os.environ['SQL_HOST']}:{os.environ['SQL_PORT']}/{os.environ['SQL_DATABASE']}"


def get_sql_engine(reset=False) -> Engine:
    """
    Connects to a SQL database
    """

    global sql_engine
    if not sql_engine or reset:
        sql_engine = create_engine(sql_connection_string())

    return sql_engine


def get_sql_session(reset=False) -> Session:
    """
    Returns a SQL session
    """

    global sql_session
    if not sql_session or reset:
        sql_session = scoped_session(sessionmaker(bind=get_sql_engine()))

    return sql_session


def truncate_sql_db():
    """
    Truncates SQL database tables
    """

    sql_engine = get_sql_engine()
    sql_session = get_sql_session()
    inspector = inspect(sql_engine)
    statement = "TRUNCATE TABLE "
    for table in inspector.get_table_names():
        statement += f"{table},"

    statement = f"{statement[:-1]} RESTART IDENTITY CASCADE"
    sql_session.execute(statement)
    commit_transaction(sql_session)
    log.info("Truncated the SQL database")


def commit_transaction(sql_session: Session):
    """
    Commits a SQL transaction
    """

    try:
        sql_session.commit()
        log.debug("Committed SQL transaction")
    except Exception as e:
        sql_session.rollback()
        log.debug("Failed to commit SQL transaction")
        raise e


def drop_sqldb():
    """
    Drop a SQL database
    """

    sqlalchemy_utils.drop_database(get_sql_engine().url)
    log.info("Dropped SQL database")


def create_sqldb():
    """
    Creates a SQL database
    """

    sqlalchemy_utils.create_database(get_sql_engine().url)
    log.info("Created SQL database")


def schema_diagram():
    """
    Builds a schema diagram
    """
    # flake8: noqa: C901
    from sqlalchemy_schemadisplay import create_schema_graph

    graph = create_schema_graph(
        metadata=MetaData(sql_connection_string()),
        show_datatypes=False,
        show_indexes=False,
        rankdir="LR",
        concentrate=False,
    )
    graph.write_png("schema.png")
