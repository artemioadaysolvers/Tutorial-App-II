"""ID: 10000014. Calculadora: suma todos los inputs recibidos."""

MODEL_ID = 10000014

def calcular(inputs: dict[str, float]) -> float:
    return sum(inputs.values())
