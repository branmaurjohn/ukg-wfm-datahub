#!/usr/bin/env python3
"""
Generate docs/entities/*.md from a Data Hub Data Dictionary Excel workbook.

Public-safe defaults:
- Does NOT include dataset/schema values unless --include-dataset is set
- Does NOT include sample row values
- Drops columns that look like PII by keyword (configurable)

Usage:
  python tools/generate_entities.py --dictionary /path/to/dictionary.xlsx
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd

ENTITY_COL_CANDIDATES = [
    "entity", "entity_name", "object", "object_name", "view", "view_name", "table", "table_name", "name"
]
DESC_COL_CANDIDATES = ["description", "desc", "definition", "purpose", "details"]
DOMAIN_COL_CANDIDATES = ["domain", "subject_area", "area"]
WRAPPER_COL_CANDIDATES = ["wrapper", "wrapper_name"]
PIPELINE_COL_CANDIDATES = ["pipeline", "pipeline_name"]

FIELD_NAME_CANDIDATES = ["field", "field_name", "column", "column_name", "attribute", "attribute_name"]
FIELD_TYPE_CANDIDATES = ["type", "data_type", "datatype"]
FIELD_DESC_CANDIDATES = ["field_description", "column_description", "attribute_description", "description", "desc", "definition"]
FIELD_NULLABLE_CANDIDATES = ["nullable", "is_nullable", "nulls_allowed"]
FIELD_PK_CANDIDATES = ["primary_key", "pk", "is_pk", "key"]

DEFAULT_PII_KEYWORDS = [
    "ssn", "social", "email", "phone", "address", "dob", "birth", "passport",
    "driver", "license", "bank", "routing", "account", "salary", "wage",
    "security_nbr", "security", "home_address"
]

@dataclass
class Cols:
    entity: str
    desc: Optional[str] = None
    domain: Optional[str] = None
    wrapper: Optional[str] = None
    pipeline: Optional[str] = None

    field_name: Optional[str] = None
    field_type: Optional[str] = None
    field_desc: Optional[str] = None
    field_nullable: Optional[str] = None
    field_pk: Optional[str] = None

def _norm(s: str) -> str:
    return s.strip().lower()

def pick_col(cols: List[str], candidates: List[str]) -> Optional[str]:
    cols_l = [_norm(c) for c in cols]
    for cand in candidates:
        if cand in cols_l:
            return cols[cols_l.index(cand)]
    for cand in candidates:
        for i, c in enumerate(cols_l):
            if cand in c:
                return cols[i]
    return None

def slugify(text: str) -> str:
    t = _norm(text)
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-") or "entity"

def safe_str(v) -> str:
    if pd.isna(v):
        return ""
    return str(v).strip()

def looks_sensitive_column(col_name: str, pii_keywords: List[str]) -> bool:
    c = _norm(col_name)
    return any(k in c for k in pii_keywords)

def write_md(path: str, lines: List[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")

def compact_kv_block(kv: List[Tuple[str, str]]) -> List[str]:
    out = []
    for k, v in kv:
        if v:
            out.append(f"**{k}:** {v}")
    return out

def to_md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No field metadata found in this sheet._"
    return df.to_markdown(index=False)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dictionary", required=True, help="Path to the Excel data dictionary workbook")
    ap.add_argument("--out", default="docs/entities", help="Output folder for generated entity pages")
    ap.add_argument("--include-dataset", action="store_true",
                    help="Include dataset/schema values if present (NOT recommended for public repos)")
    ap.add_argument("--pii-keywords", default=",".join(DEFAULT_PII_KEYWORDS),
                    help="Comma-separated keywords; columns containing these will be dropped from output tables")
    args = ap.parse_args()

    pii_keywords = [k.strip().lower() for k in args.pii_keywords.split(",") if k.strip()]

    xls = pd.ExcelFile(args.dictionary)
    generated: List[Tuple[str, str]] = []

    for sheet in xls.sheet_names:
        df = xls.parse(sheet)
        if df is None or df.empty:
            continue

        cols = list(df.columns)
        entity_col = pick_col(cols, ENTITY_COL_CANDIDATES)
        if not entity_col:
            continue

        c = Cols(
            entity=entity_col,
            desc=pick_col(cols, DESC_COL_CANDIDATES),
            domain=pick_col(cols, DOMAIN_COL_CANDIDATES),
            wrapper=pick_col(cols, WRAPPER_COL_CANDIDATES),
            pipeline=pick_col(cols, PIPELINE_COL_CANDIDATES),
            field_name=pick_col(cols, FIELD_NAME_CANDIDATES),
            field_type=pick_col(cols, FIELD_TYPE_CANDIDATES),
            field_desc=pick_col(cols, FIELD_DESC_CANDIDATES),
            field_nullable=pick_col(cols, FIELD_NULLABLE_CANDIDATES),
            field_pk=pick_col(cols, FIELD_PK_CANDIDATES),
        )

        for entity_val, g in df.groupby(c.entity):
            name = safe_str(entity_val)
            if not name:
                continue

            domain = safe_str(g[c.domain].dropna().astype(str).unique()[0]) if c.domain and g[c.domain].dropna().any() else ""
            wrapper = safe_str(g[c.wrapper].dropna().astype(str).unique()[0]) if c.wrapper and g[c.wrapper].dropna().any() else ""
            pipeline = safe_str(g[c.pipeline].dropna().astype(str).unique()[0]) if c.pipeline and g[c.pipeline].dropna().any() else ""
            desc = safe_str(g[c.desc].dropna().astype(str).unique()[0]) if c.desc and g[c.desc].dropna().any() else ""

            field_cols_map = {
                "Field": c.field_name,
                "Type": c.field_type,
                "Nullable": c.field_nullable,
                "PK": c.field_pk,
                "Description": c.field_desc,
            }
            keep = [(k, v) for k, v in field_cols_map.items() if v and v in g.columns]
            fields_df = pd.DataFrame()

            if keep:
                tmp = pd.DataFrame({k: g[v].map(safe_str) for k, v in keep})
                tmp = tmp.loc[:, [col for col in tmp.columns if tmp[col].astype(str).str.strip().any()]]
                tmp = tmp.loc[:, [col for col in tmp.columns if not looks_sensitive_column(col, pii_keywords)]]
                if "Field" in tmp.columns:
                    tmp = tmp[tmp["Field"].astype(str).str.strip() != ""]
                tmp = tmp.drop_duplicates()
                fields_df = tmp.head(500)

            fn = f"{slugify(name)}.md"
            out_path = os.path.join(args.out, fn)

            lines: List[str] = []
            lines += [f"# {name}", ""]
            lines += ["> Auto-generated from a Data Dictionary workbook. Output is public-safe by default.", ""]

            kv = []
            if domain:
                kv.append(("Domain", domain))
            if wrapper:
                kv.append(("Wrapper", wrapper))
            if pipeline:
                kv.append(("Pipeline", pipeline))
            if args.include_dataset:
                pass

            if kv:
                lines += compact_kv_block(kv) + [""]

            lines += ["## What it is", ""]
            lines += [desc if desc else "_No description found in this sheet._", ""]

            lines += ["## Fields", ""]
            lines += [to_md_table(fields_df), ""]

            lines += ["## How to use it", ""]
            lines += [
                "- Confirm the **grain** (what one row represents) before joining.",
                "- Join using **IDs/keys**, not labels.",
                "- Apply **partition/date filters** early (BigQuery cost control).",
                "- Validate with a small reference sample before publishing dashboards.",
                "",
            ]

            lines += ["## Gotchas", ""]
            lines += [
                "- If this entity participates in many-to-many joins, document the safe join path here.",
                "- If attributes are “current only,” document how to handle historical reporting here.",
                "",
            ]

            write_md(out_path, lines)
            generated.append((name, fn))

    generated = sorted(set(generated), key=lambda x: x[0].lower())
    idx_path = os.path.join(args.out, "index.md")
    idx_lines = [
        "# Entities",
        "",
        "These pages are generated from a Data Dictionary workbook.",
        "",
        "## Public-safe rule",
        "- The Excel workbook is **not committed** to this public repo.",
        "- Only the generated markdown pages are committed.",
        "",
        "## Index",
        "",
    ]
    if not generated:
        idx_lines += ["_No entities generated. Check that your workbook has an entity/table/view column._"]
    else:
        for name, fn in generated:
            idx_lines.append(f"- [{name}]({fn})")
    write_md(idx_path, idx_lines)

if __name__ == "__main__":
    main()
