import os
from contextlib import asynccontextmanager
from starlette.concurrency import run_in_threadpool
from .app import create_app
from .auth import GoogleVerifier
from .database import open_database
from .repository import PostgresRepository
from .predictor import PrivatePredictor

@asynccontextmanager
async def lifespan(app):
    verify=GoogleVerifier(os.getenv('GOOGLE_WEB_CLIENT_ID'))
    predict=PrivatePredictor(os.getenv('INFERENCE_URL'))
    engine,close=await run_in_threadpool(open_database)
    app.state.repo=PostgresRepository(engine)
    app.state.verify=verify
    app.state.predict=predict
    try:
        yield
    finally:
        await run_in_threadpool(close)

app=create_app(lifespan=lifespan)
