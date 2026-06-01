#!/usr/bin/env python3
import json
import sys
from pathlib import Path

MAX_ITEMS = 7
LIST_FIELDS = [
    "concepts",
    "frames",
    "metaphors",
    "value_oppositions",
    "subject_roles",
    "cultural_references",
    "literary_references",
    "world_model_dimension",
    "temporality",
]

REQUIRED_TOP = [
    "text_id",
    "title",
    "source",
    "publication_date",
    "url",
    "access_date",
    "segment",
    "genre",
    "speed_layer",
    "topics",
    "selection_reason",
    "legal",
    "annotation",
]


def validate_record(path: Path) -> list[str]:
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"Cannot read JSON: {exc}"]

    for field in REQUIRED_TOP:
        if field not in data:
            errors.append(f"Missing field: {field}")

    ann = data.get("annotation", {})
    for field in LIST_FIELDS:
        value = ann.get(field)
        if value is None:
            errors.append(f"Missing annotation field: {field}")
            continue
        if isinstance(value, list) and len(value) > MAX_ITEMS:
            errors.append(f"Too many items in {field}: {len(value)} > {MAX_ITEMS}")

    legal = data.get("legal", {})
    if legal.get("full_text_stored") is True and legal.get("license_status") not in {"open_license_text", "public_domain_fragment"}:
        errors.append("Full text is stored but license_status is not open_license_text or public_domain_fragment")

    if not data.get("selection_reason") or len(data.get("selection_reason", "")) < 20:
        errors.append("selection_reason is too short")

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: validate_record.py path/to/record.json")
        return 2
    path = Path(sys.argv[1])
    errors = validate_record(path)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
