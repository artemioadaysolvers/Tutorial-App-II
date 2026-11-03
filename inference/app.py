"""Servicio privado. Cloud Run IAM autentica al llamador antes del contenedor."""
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,ConfigDict,StrictFloat,StrictInt,Field
from engine import predict
app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
class Payload(BaseModel):
    model_config=ConfigDict(extra='forbid')
    modelId:StrictInt=Field(ge=10_000_000,le=99_999_999)
    inputs:dict[str,StrictFloat|StrictInt]
@app.post('/predict')
def infer(body:Payload):
    try:return predict(body.modelId,body.inputs)
    except ValueError as e:raise HTTPException(400,str(e))
    except (OSError,KeyError,ImportError):raise HTTPException(503,'Calculadora no disponible')
