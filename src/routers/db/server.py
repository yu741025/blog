import subprocess
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from src.dependencies.auth import get_super_admin_user
from src.dependencies.basic import get_db
from src.schemas.basic import TextOnly

router = APIRouter()


@router.post("/renew")
async def renew_database():
    from src.database.database import engine, drop_all_tables
    from src.database.database import create_all_tables
    from src.database.utils import add_test_data

    drop_all_tables(engine)
    create_all_tables(engine)
    add_test_data()
    return TextOnly(text="Database Renewed")


@router.post('/alembic')
async def alembic(
        db: Annotated[Session, Depends(get_db)]
):
    from src.database.database import TRIAL_URL, DB_NAME
    from src.database.database import create_database_if_not_exists

    create_database_if_not_exists(TRIAL_URL, DB_NAME)

    # remove alembic_version table
    db.execute(text("DROP TABLE IF EXISTS alembic_version"))
    db.commit()

    # execute `bash /run/run_alembic.sh` and return the output
    process = subprocess.Popen(['/bin/bash', '/run/run_alembic.sh'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = process.communicate()

    return {
        "output": output.decode('utf-8').split('\n'),
        "error": error.decode('utf-8').split('\n')
    }
