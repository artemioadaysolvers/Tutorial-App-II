import logging
import math
import re
from typing import Annotated
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt
from starlette.concurrency import run_in_threadpool

ModelId = Annotated[StrictInt, Field(ge=10_000_000,le=99_999_999)]

class AccessRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    modelId: ModelId

class Inputs(BaseModel):
    model_config = ConfigDict(extra='forbid')
    inputs: dict[str,StrictFloat|StrictInt]

class BodyLimit:
    def __init__(self, app):
        self.app=app

    async def __call__(self,scope,receive,send):
        if scope['type']!='http':
            return await self.app(scope,receive,send)
        parts=[];size=0
        while True:
            message=await receive()
            if message['type']=='http.disconnect':
                return
            chunk=message.get('body',b'');size+=len(chunk)
            if size>16384:
                return await JSONResponse({'error':'Petición demasiado grande'},status_code=413)(scope,receive,send)
            parts.append(chunk)
            if not message.get('more_body',False):
                break
        replayed=False
        async def replay():
            nonlocal replayed
            if not replayed:
                replayed=True
                return {'type':'http.request','body':b''.join(parts),'more_body':False}
            return await receive()
        await self.app(scope,replay,send)

def allowed(grant,user,model_id):
    return bool(grant and grant.get('enabled') is True and grant.get('email')==user.email
        and (not grant.get('subject') or grant['subject']==user.sub)
        and any(type(value) is int and value==model_id for value in grant.get('modelIds',[])))

def create_app(repo=None,verify=None,predict=None,lifespan=None):
    app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None,lifespan=lifespan)
    app.state.repo=repo;app.state.verify=verify;app.state.predict=predict

    @app.exception_handler(HTTPException)
    async def http_error(_request,error):
        return JSONResponse({'error':error.detail},status_code=error.status_code,headers=error.headers)

    @app.exception_handler(RequestValidationError)
    async def invalid(_request,_error):
        return JSONResponse({'error':'Datos inválidos: usa solo los campos requeridos e IDs numéricos de ocho dígitos'},status_code=400)

    @app.exception_handler(Exception)
    async def internal(_request,error):
        logging.error('Error de API: %s',type(error).__name__)
        return JSONResponse({'error':'Error interno'},status_code=500)

    @app.middleware('http')
    async def authenticate(request,call_next):
        match=re.fullmatch(r'Bearer ([^\s]+)',request.headers.get('authorization',''))
        if not match:
            return JSONResponse({'error':'Debes iniciar sesión con Google'},status_code=401,headers={'Cache-Control':'no-store'})
        try:
            user=await run_in_threadpool(app.state.verify,match[1])
        except Exception:
            return JSONResponse({'error':'Sesión Google inválida o vencida'},status_code=401,headers={'Cache-Control':'no-store'})
        try:
            await run_in_threadpool(app.state.repo.register,user)
        except Exception:
            return JSONResponse({'error':'Error interno'},status_code=500,headers={'Cache-Control':'no-store'})
        request.state.user=user
        response=await call_next(request)
        response.headers['Cache-Control']='no-store'
        return response

    @app.get('/v1/catalog')
    def catalog():
        return {'models':app.state.repo.catalog()}

    @app.get('/v1/me')
    def me(request:Request):
        user=request.state.user;r=app.state.repo
        grant=r.grant(user.email)
        return dict(email=user.email,modelIds=[m['id'] for m in r.catalog() if allowed(grant,user,m['id'])],requested=r.requested(user))

    @app.post('/v1/requests',status_code=202)
    def request_access(body:AccessRequest,request:Request):
        model=app.state.repo.model(body.modelId)
        if not model or not model['active']:
            raise HTTPException(404,'Modelo no disponible')
        app.state.repo.request(request.state.user,body.modelId)
        return dict(status='pending',modelId=body.modelId)

    @app.post('/v1/models/{raw_id}/predict')
    def calculate(raw_id:str,body:Inputs,request:Request):
        if not re.fullmatch(r'[1-9]\d{7}',raw_id):
            raise HTTPException(400,'ID de modelo inválido')
        model_id=int(raw_id);user=request.state.user;r=app.state.repo
        if not allowed(r.grant(user.email),user,model_id):
            raise HTTPException(403,'No tienes acceso a este ID de modelo')
        model=r.model(model_id)
        if not model or not model['active']:
            raise HTTPException(404,'Modelo no disponible')
        values=body.inputs;fields=model['fields']
        if set(values)!={field['key'] for field in fields} or any(
            not math.isfinite(values[f['key']]) or not f['min']<=values[f['key']]<=f['max']
            or f.get('integer') and int(values[f['key']])!=values[f['key']] for f in fields):
            raise HTTPException(400,'Entradas inválidas para este modelo')
        if not r.consume(user):
            raise HTTPException(429,'Límite de 30 cálculos por minuto',headers={'Retry-After':'60'})
        try:
            result=app.state.predict(model_id,values)
        except Exception:
            raise HTTPException(503,'El servicio de calculadoras no está disponible')
        if not allowed(r.grant(user.email),user,model_id):
            raise HTTPException(403,'Acceso revocado')
        return {**result,'modelId':model_id,'demo':model['demo'] or result['demo']}

    app.add_middleware(BodyLimit)
    return app
