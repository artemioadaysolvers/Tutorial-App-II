"""Despacha cada ID hacia su propia calculadora Python."""
import importlib
import json
import math
from functools import lru_cache
from pathlib import Path
from registry import MODELS

ROOT = Path(__file__).parent
CATALOG = {m['id']: m for m in json.loads((ROOT / 'catalog.json').read_text('utf-8'))}
if set(MODELS) != set(CATALOG):
    raise RuntimeError('El registro y el catálogo deben contener los mismos IDs')

@lru_cache(maxsize=24)
def load(model_id):
    if type(model_id) is not int or not 10_000_000 <= model_id <= 99_999_999 or model_id not in MODELS:
        raise ValueError('ID desconocido')
    module = importlib.import_module(MODELS[model_id])
    if module.MODEL_ID != model_id:
        raise RuntimeError('El ID declarado en el archivo no coincide con el registro')
    return module

def predict(model_id, inputs):
    if type(model_id) is not int or not 10_000_000 <= model_id <= 99_999_999 or model_id not in CATALOG:
        raise ValueError('ID desconocido')
    fields = CATALOG[model_id]['fields']
    if not isinstance(inputs, dict) or set(inputs) != {f['key'] for f in fields}:
        raise ValueError('Campos incorrectos')
    for field in fields:
        value = inputs[field['key']]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('Los inputs deben ser números finitos')
        if not field['min'] <= value <= field['max']:
            raise ValueError('Input fuera de rango')
    total = load(model_id).calcular(inputs)
    if not math.isfinite(total):
        raise ValueError('Resultado no finito')
    return {'modelId': model_id, 'values': [float(total)], 'unit': 'unidades', 'demo': True}
