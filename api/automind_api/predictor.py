import re
import requests
from google.oauth2 import id_token
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, StrictBool, StrictInt
from .auth import GoogleRequest

class Result(BaseModel):
    model_config = ConfigDict(extra='forbid')
    modelId: StrictInt
    values: list[FiniteFloat] = Field(min_length=1,max_length=90)
    unit: str
    demo: StrictBool

class PrivatePredictor:
    def __init__(self, url):
        if not url or not re.fullmatch(r'https://[a-z0-9-]+\.[a-z0-9.-]+',url):
            raise ValueError('Configura INFERENCE_URL HTTPS sin barra final')
        self.url = url
        self.request = GoogleRequest()

    def __call__(self, model_id, inputs):
        token = id_token.fetch_id_token(self.request,self.url)
        response = requests.post(self.url+'/predict',headers={'Authorization':f'Bearer {token}'},
            json=dict(modelId=model_id,inputs=inputs),timeout=(10,55))
        response.raise_for_status()
        result = Result.model_validate(response.json())
        if result.modelId != model_id:
            raise ValueError('El motor devolvió otro ID')
        return result.model_dump()
