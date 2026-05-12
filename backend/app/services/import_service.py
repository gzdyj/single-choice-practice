import csv
import json
from io import StringIO, BytesIO
from typing import Any

import openpyxl
from sqlalchemy.orm import Session

from ..models.question import Question


class ImportResult:
    def __init__(self):
        self.success_count: int = 0
        self.fail_count: int = 0
        self.errors: list[str] = []
        self.questions: list[Question] = []


def _validate_row(row: dict, line: int) -> list[str]:
    """Validate a single question row."""
    errors: list[str] = []
    if not row.get("question_text", "").strip():
        errors.append(f"第{line}行：题目内容不能为空")

    for opt in ["option_a", "option_b", "option_c", "option_d"]:
        if not row.get(opt, "").strip():
            errors.append(f"第{line}行：选项 {opt[-1].upper()} 不能为空")

    answer = row.get("correct_answer", "").strip().upper()
    if answer not in ("A", "B", "C", "D"):
        errors.append(f"第{line}行：正确答案必须是 A/B/C/D 之一，当前值: {answer}")

    return errors


def _row_to_question(row: dict, created_by: int) -> dict:
    """Convert a parsed row dict to question model attributes."""
    return {
        "subject": row.get("subject", "").strip(),
        "difficulty": row.get("difficulty", "medium").strip().lower() or "medium",
        "question_text": row.get("question_text", "").strip(),
        "option_a": row.get("option_a", "").strip(),
        "option_b": row.get("option_b", "").strip(),
        "option_c": row.get("option_c", "").strip(),
        "option_d": row.get("option_d", "").strip(),
        "correct_answer": row.get("correct_answer", "").strip().upper(),
        "explanation": row.get("explanation", "").strip(),
        "created_by": created_by,
    }


def _bulk_insert(db: Session, data_list: list[dict]) -> ImportResult:
    """Insert validated questions into DB."""
    result = ImportResult()
    for idx, data in enumerate(data_list):
        try:
            errors = _validate_row(data, idx + 1)
            if errors:
                result.fail_count += 1
                result.errors.extend(errors)
                continue
            question = Question(**data)
            db.add(question)
            db.flush()
            result.success_count += 1
            result.questions.append(question)
        except Exception as e:
            result.fail_count += 1
            result.errors.append(f"第{idx + 1}行导入失败: {str(e)}")
    db.commit()
    return result


# ── Parsers ──────────────────────────────────────────────────────────────────


def _parse_excel(file_bytes: bytes) -> list[dict]:
    """Parse .xlsx file content into a list of dicts."""
    wb = openpyxl.load_workbook(BytesIO(file_bytes), read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(h).strip().lower().replace(" ", "_") if h else "" for h in rows[0]]
    data: list[dict] = []
    for row in rows[1:]:
        row_data = {}
        for i, val in enumerate(row):
            if i < len(headers):
                row_data[headers[i]] = str(val) if val is not None else ""
        data.append(row_data)
    return data


def _parse_csv(file_bytes: bytes) -> list[dict]:
    """Parse .csv content into a list of dicts."""
    content = file_bytes.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(content))
    return [row for row in reader]


def _parse_json(file_bytes: bytes) -> list[dict]:
    """Parse .json content into a list of dicts.
    Supports both list of dicts and dict with a 'questions' key.
    """
    content = json.loads(file_bytes.decode("utf-8-sig"))
    if isinstance(content, list):
        return content
    if isinstance(content, dict) and "questions" in content:
        return content["questions"]
    return []


PARSERS = {
    ".xlsx": _parse_excel,
    ".xls": _parse_excel,
    ".csv": _parse_csv,
    ".json": _parse_json,
}


def get_supported_extensions() -> list[str]:
    return list(PARSERS.keys())


def import_questions(
    db: Session,
    file_bytes: bytes,
    filename: str,
    created_by: int,
) -> ImportResult:
    """Detect file format, parse, validate, and bulk insert questions."""
    ext = filename.lower().rsplit(".", 1)[-1]
    ext = f".{ext}"
    parser = PARSERS.get(ext)
    if not parser:
        result = ImportResult()
        result.fail_count = 1
        result.errors.append(f"不支持的文件格式: {ext}，支持格式: {', '.join(PARSERS.keys())}")
        return result

    try:
        rows = parser(file_bytes)
    except Exception as e:
        result = ImportResult()
        result.fail_count = 1
        result.errors.append(f"文件解析失败: {str(e)}")
        return result

    if not rows:
        result = ImportResult()
        result.fail_count = 1
        result.errors.append("文件为空或表头不匹配")
        return result

    question_data_list = [_row_to_question(r, created_by) for r in rows]
    return _bulk_insert(db, question_data_list)
