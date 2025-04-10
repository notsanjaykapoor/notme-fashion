import sqlalchemy
import sqlmodel

from .session import table_names


def truncate_tables(db_session: sqlmodel.Session, table_names: list[str]):
    for table_name in table_names:
        db_session.execute(sqlalchemy.text(f"delete from {table_name}"))
    db_session.commit()


def truncate_all(db_session: sqlmodel.Session, exclude: list[str] = ["credentials", "spatial_ref_sys", "users"]):
    for table_name in table_names():
        if table_name not in exclude:
            truncate_tables(db_session, [table_name])
