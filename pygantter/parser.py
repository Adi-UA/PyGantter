import json
import os
from datetime import datetime
from typing import Any, Dict, List, Union

import pandas as pd

DATE_FORMATS = ["%m/%d/%Y"]


def parse_date(date_str: str) -> datetime:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}")


def read_input(file_path: str) -> List[Dict[str, Any]]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".csv", ".tsv"]:
        sep = "," if ext == ".csv" else "\t"
        df = pd.read_csv(file_path, sep=sep)
        records = df.to_dict(orient="records")
    elif ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            records = json.load(f)
    else:
        raise ValueError("Unsupported file format. Use CSV, TSV, or JSON.")
    return [normalize_record(r) for r in records]


from .enums import TaskField


def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(record)
    if TaskField.START in result:
        result[TaskField.START] = parse_date(str(result[TaskField.START]))
    if TaskField.END in result and result[TaskField.END]:
        result[TaskField.END] = parse_date(str(result[TaskField.END]))
    if TaskField.EFFORT in result and result[TaskField.EFFORT]:
        result[TaskField.EFFORT] = int(result[TaskField.EFFORT])
    if TaskField.DEPENDENCIES in result and isinstance(
        result[TaskField.DEPENDENCIES], str
    ):
        result[TaskField.DEPENDENCIES] = [
            d.strip() for d in result[TaskField.DEPENDENCIES].split(",") if d.strip()
        ]
    if TaskField.GROUP in result and isinstance(result[TaskField.GROUP], str):
        result[TaskField.GROUP] = result[TaskField.GROUP].strip()
    return result
