"""ID: 10000016. Calculadora: suma todos los inputs recibidos."""

MODEL_ID = 10000016

def calcular(inputs: dict[str, float]) -> float:
    return sum(inputs.values())
