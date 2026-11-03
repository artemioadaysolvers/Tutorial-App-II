"""ID: 10000018. Calculadora: suma todos los inputs recibidos."""

MODEL_ID = 10000018

def calcular(inputs: dict[str, float]) -> float:
    return sum(inputs.values())
