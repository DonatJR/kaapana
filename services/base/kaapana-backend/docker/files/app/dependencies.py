import os
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from minio import Minio
from .monitoring.services import MonitoringService
from .users.services import UserService
from .workflows.services import WorkflowService
from .experiments.models import KaapanaInstance
from .config import settings
from .database import SessionMaker


async def get_db():
    async with SessionMaker() as session:
        yield session

def get_monitoring_service() -> MonitoringService:
    yield MonitoringService(prometheus_url=settings.prometheus_url)

def get_user_service() -> UserService:
    yield UserService(settings.keycloak_url, settings.keycloak_admin_username, settings.keycloak_admin_password)

def get_minio() -> Minio:
    yield  Minio(settings.minio_url, access_key=settings.minio_username, secret_key=settings.minio_password, secure=False)

def get_workflow_service() -> WorkflowService:
    yield WorkflowService(airflow_api=settings.airflow_url)

async def get_token_header(FederatedAuthorization: str = Header(...), db: Session = Depends(get_db)):
    if FederatedAuthorization:
        db_client_kaapana_instance = (await db.execute(select(KaapanaInstance).where(KaapanaInstance.token == FederatedAuthorization))).first()
        #db_client_kaapana_instance = db.query(KaapanaInstance).filter_by(token=FederatedAuthorization).first()
        if db_client_kaapana_instance:
            return db_client_kaapana_instance
        else:
            raise HTTPException(status_code=400, detail="FederatedAuthorization header invalid")

async def get_query_token(token: str):
    if token != "jessica":
        raise HTTPException(status_code=400, detail="No Jessica token provided")

