from fastapi import FastAPI, HTTPException

app = FastAPI()

UNIT_TO_METER = {
    "meter": 1.0,
    "yard": 0.9144,
    "inch": 0.0254,
    "feet": 0.3048,
}

@app.get("/")
def root():
    return {"message": "Length Unit Converter API"}

@app.get("/convert")
def convert(value: float, from_unit: str, to_unit: str):
    if from_unit not in UNIT_TO_METER or to_unit not in UNIT_TO_METER:
        raise HTTPException(status_code=400, detail="unit must be one of: meter, yard, inch, feet")

    value_in_meter = value * UNIT_TO_METER[from_unit]
    result = value_in_meter / UNIT_TO_METER[to_unit]

    return {
        "input_value": value,
        "from_unit": from_unit,
        "to_unit": to_unit,
        "result": round(result, 6)
    }