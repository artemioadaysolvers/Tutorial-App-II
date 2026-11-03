"""ID: 10000003. Calculadora: suma todos los inputs recibidos."""

MODEL_ID = 10000003

def calcular(inputs: dict[str, float]) -> float:
    return sum(inputs.values())
