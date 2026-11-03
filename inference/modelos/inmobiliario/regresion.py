"""ID: 10000004. Calculadora: suma todos los inputs recibidos."""

MODEL_ID = 10000004

def calcular(inputs: dict[str, float]) -> float:
    return sum(inputs.values())
