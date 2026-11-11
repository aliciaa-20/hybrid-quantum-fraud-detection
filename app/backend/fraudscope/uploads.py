"""CSV upload validation. Every failure is an UploadError with a message the user can act on."""

import csv
import io

import numpy as np
import pandas as pd

from fraudscope import config


class UploadError(ValueError):
    def __init__(self, message: str, status_code: int = 422):
        super().__init__(message)
        self.status_code = status_code


def parse_upload(raw: bytes, ranges: dict[str, list[float]] | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Return (rows with exactly config.FEATURES as float columns, one warning string per row; '' if none)."""
    if len(raw) > config.MAX_UPLOAD_BYTES:
        raise UploadError(f"File is larger than {config.MAX_UPLOAD_BYTES // 1_000_000} MB.", 413)
    try:
        text = raw.decode("utf-8-sig")  # also strips a BOM
    except UnicodeDecodeError:
        raise UploadError("File is not valid UTF-8 text. Please upload a plain CSV.")
    if not text.strip():
        raise UploadError("The file is empty.")

    header = [h.strip() for h in next(csv.reader(io.StringIO(text)))]
    for f in config.FEATURES:
        if header.count(f) > 1:
            raise UploadError(f"Column {f} appears more than once.")
    missing = [f for f in config.FEATURES if f not in header]
    if missing:
        raise UploadError(f"Missing column{'s' if len(missing) > 1 else ''} {', '.join(missing)}. "
                          f"Found: {', '.join(h for h in header if h) or 'no columns'}. "
                          f"Required: {', '.join(config.FEATURES)}.")
    try:
        df = pd.read_csv(io.StringIO(text), skipinitialspace=True)
    except Exception as e:
        raise UploadError(f"Could not read this file as a CSV: {e}")
    df.columns = [str(c).strip() for c in df.columns]
    if len(df) == 0:
        raise UploadError("The file has a header but no data rows.")
    if len(df) > config.RF_MAX_ROWS:
        raise UploadError(f"Too many rows ({len(df):,}); the limit is {config.RF_MAX_ROWS:,}.", 413)

    out = pd.DataFrame(index=df.index)
    for f in config.FEATURES:
        col = pd.to_numeric(df[f], errors="coerce")
        bad = col.isna() | ~np.isfinite(col.fillna(0))
        if bad.any():
            i = int(np.flatnonzero(bad.values)[0])
            cell = df[f].iloc[i]
            shown = "blank" if pd.isna(cell) else str(cell)
            raise UploadError(f"Column {f} has a missing or non-numeric value at data row {i + 1} "
                              f"({shown}). All values must be finite numbers.")
        out[f] = col.astype(float)

    warnings = [""] * len(out)
    if ranges:
        for f in config.FEATURES:
            lo, hi = ranges[f]
            for i in np.flatnonzero(((out[f] < lo) | (out[f] > hi)).values):
                msg = f"{f} outside training range"
                warnings[i] = f"{warnings[i]}; {msg}" if warnings[i] else msg
    return out.reset_index(drop=True), warnings
