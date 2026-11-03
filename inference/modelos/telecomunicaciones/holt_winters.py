"""ID: 10000011. Calculadora: suma todos los inputs recibidos."""

MODEL_ID = 10000011

def calcular(inputs: dict[str, float]) -> float:
    return sum(inputs.values())
