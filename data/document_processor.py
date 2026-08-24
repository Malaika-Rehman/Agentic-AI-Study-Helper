"""
document_processor.py
Extracts plain text from virtually any file a student might upload.

Supported formats
─────────────────
Documents : PDF, DOCX, DOC, ODT, RTF, TXT, MD
Slides    : PPTX, PPT, ODP
Spreadsheets: XLSX, XLS, ODS, CSV
Web / Data  : HTML, HTM, JSON, XML
"""

import io
import re
import traceback


# ── public entry point ────────────────────────────────────────────────────────

def extract_text(uploaded_file) -> tuple[str, str]:
    """
    Extract plain text from any uploaded file.

    Returns
    -------
    (text, error_message)
    error_message is '' on success, non-empty on failure.
    """
    filename   = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()

    if not file_bytes:
        return "", "The file is empty — please upload a valid document."

    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""

    dispatch = {
        # Documents
        "pdf":  _pdf,
        "docx": _docx,
        "doc":  _doc,
        "odt":  _odt,
        "rtf":  _rtf,
        "txt":  _txt,
        "md":   _txt,
        # Slides
        "pptx": _pptx,
        "ppt":  _ppt,
        "odp":  _odp,
        # Spreadsheets
        "xlsx": _xlsx,
        "xls":  _xls,
        "ods":  _ods,
        "csv":  _csv,
        # Web / Data
        "html": _html,
        "htm":  _html,
        "json": _json,
        "xml":  _xml,
    }

    handler = dispatch.get(ext)
    if handler:
        return handler(file_bytes)

    # ── Unknown extension: try plain text first ──
    try:
        text = file_bytes.decode("utf-8", errors="ignore").strip()
        if len(text) > 50:
            return text, ""
    except Exception:
        pass

    return (
        "",
        f"Unsupported file type: .{ext.upper() or 'unknown'}. "
        "Try PDF, DOCX, PPTX, TXT, XLSX, CSV, HTML, or JSON."
    )


# ── Documents ─────────────────────────────────────────────────────────────────

def _pdf(b: bytes) -> tuple[str, str]:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(b))
        if not reader.pages:
            return "", "PDF has no pages."
        text = "\n".join(p.extract_text() or "" for p in reader.pages).strip()
        if not text:
            return "", (
                "This PDF appears to be image-based (scanned). "
                "No text could be extracted — please use a text-based PDF."
            )
        return text, ""
    except Exception:
        return "", f"PDF read error:\n{traceback.format_exc()}"


def _docx(b: bytes) -> tuple[str, str]:
    try:
        from docx import Document
        doc   = Document(io.BytesIO(b))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        parts.append(cell.text.strip())
        text = "\n".join(parts).strip()
        if not text:
            return "", "DOCX file appears empty — no readable text found."
        return text, ""
    except Exception:
        return "", f"DOCX read error:\n{traceback.format_exc()}"


def _doc(b: bytes) -> tuple[str, str]:
    """Legacy .doc binary — extract via python-docx (works on most .doc files)
    or fall back to olefile raw stream parsing."""
    # Try python-docx first (sometimes handles .doc)
    try:
        from docx import Document
        doc   = Document(io.BytesIO(b))
        parts = [p.text for p in doc.paragraphs if p.text.strip()]
        text  = "\n".join(parts).strip()
        if text:
            return text, ""
    except Exception:
        pass

    # Fallback: raw OLE word document stream
    try:
        import olefile
        ole = olefile.OleFileIO(io.BytesIO(b))
        if ole.exists("WordDocument"):
            raw  = ole.openstream("WordDocument").read()
            text = raw.decode("latin-1", errors="ignore")
            text = re.sub(r"[^\x20-\x7E\n\t]", " ", text)
            text = re.sub(r" {3,}", " ", text).strip()
            if len(text) > 50:
                return text, ""
    except Exception:
        pass

    return (
        "",
        "Could not read this .doc file. Please open it in Microsoft Word "
        "and Save As → .docx, then re-upload."
    )


def _odt(b: bytes) -> tuple[str, str]:
    """OpenDocument Text (.odt) — unzip and parse content.xml."""
    try:
        import zipfile
        from xml.etree import ElementTree as ET
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            xml = z.read("content.xml")
        tree = ET.fromstring(xml)
        ns   = {"text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
        parts = [el.text or "" for el in tree.iter() if el.text]
        text  = "\n".join(p.strip() for p in parts if p.strip())
        if not text:
            return "", "ODT file appears empty."
        return text, ""
    except Exception:
        return "", f"ODT read error:\n{traceback.format_exc()}"


def _rtf(b: bytes) -> tuple[str, str]:
    try:
        from striprtf.striprtf import rtf_to_text
        text = rtf_to_text(b.decode("latin-1", errors="ignore")).strip()
        if not text:
            return "", "RTF file appears empty."
        return text, ""
    except Exception:
        return "", f"RTF read error:\n{traceback.format_exc()}"


def _txt(b: bytes) -> tuple[str, str]:
    for enc in ("utf-8", "utf-16", "latin-1", "cp1252"):
        try:
            text = b.decode(enc).strip()
            if text:
                return text, ""
        except Exception:
            continue
    return "", "Could not decode text file — unknown encoding."


# ── Slides ────────────────────────────────────────────────────────────────────

def _pptx(b: bytes) -> tuple[str, str]:
    try:
        from pptx import Presentation
        prs   = Presentation(io.BytesIO(b))
        parts = []
        for i, slide in enumerate(prs.slides, 1):
            parts.append(f"\n--- Slide {i} ---")
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    parts.append(shape.text.strip())
        text = "\n".join(parts).strip()
        if not text:
            return "", "PPTX file appears empty — no readable text in slides."
        return text, ""
    except Exception:
        # Some files saved with .pptx extension are actually .ppt
        result, _ = _ppt(b)
        if result:
            return result, ""
        return "", f"PPTX read error:\n{traceback.format_exc()}"


def _ppt(b: bytes) -> tuple[str, str]:
    """
    Legacy .ppt binary — parse OLE PowerPoint Document stream.

    MS-PPT RecordHeader (8 bytes total):
      [0-1] verAndInstance  (NOT the record type)
      [2-3] recType         <- TextCharsAtom=0x0FA0, TextBytesAtom=0x0FA8
      [4-7] recLen

    The original code had the bug of reading bytes [0-1] as recType.
    """
    try:
        import olefile

        ole = olefile.OleFileIO(io.BytesIO(b))

        # Find the PowerPoint stream — name may vary slightly across PPT versions
        ppt_stream = None
        for entry in ole.listdir():
            name = entry[-1].lower()
            if "powerpoint" in name:
                try:
                    ppt_stream = ole.openstream(entry).read()
                    break
                except Exception:
                    pass

        if ppt_stream is None and ole.exists("PowerPoint Document"):
            ppt_stream = ole.openstream("PowerPoint Document").read()

        # -- Method 1: Correct record parsing --
        texts = []
        if ppt_stream:
            i = 0
            while i + 8 <= len(ppt_stream):
                try:
                    # FIXED: recType is at bytes [2-3], verAndInstance is at [0-1]
                    rec_type = int.from_bytes(ppt_stream[i+2:i+4], "little")
                    rec_len  = int.from_bytes(ppt_stream[i+4:i+8], "little")

                    # Sanity check to skip corrupted records
                    if rec_len < 0 or rec_len > 10_000_000:
                        i += 1
                        continue

                    data = ppt_stream[i+8: i+8+rec_len]

                    if rec_type == 0x0FA0:      # TextCharsAtom -- UTF-16LE
                        t = data.decode("utf-16-le", errors="ignore").strip()
                        if t:
                            texts.append(t)
                    elif rec_type == 0x0FA8:    # TextBytesAtom -- Latin-1
                        t = data.decode("latin-1", errors="ignore").strip()
                        if t:
                            texts.append(t)

                    i += 8 + rec_len
                except Exception:
                    i += 1  # skip one byte and retry on corrupt data

        text = "\n".join(t for t in texts if len(t) > 1)

        # -- Method 2: Brute-force UTF-16 scan fallback --
        if not text:
            raw    = ppt_stream or b
            chunks = re.findall(rb"(?:[ -~]){4,}", raw)
            text   = "\n".join(
                c.decode("utf-16-le", errors="ignore").strip()
                for c in chunks
                if len(c) > 6
            )

        # -- Method 3: Latin-1 printable lines fallback --
        if not text:
            raw   = ppt_stream or b
            lines = [
                ln.strip()
                for ln in raw.decode("latin-1", errors="ignore").splitlines()
                if len(ln.strip()) > 4
                and all(32 <= ord(c) < 127 for c in ln.strip())
            ]
            text = "\n".join(lines)

        if not text or len(text) < 20:
            return "", (
                "Could not extract readable text from this .ppt file. "
                "It may use image-only slides. "
                "Try opening in PowerPoint and Save As .pptx, then re-upload."
            )

        return text.strip(), ""

    except Exception:
        return "", f"PPT read error: {traceback.format_exc()}"


def _odp(b: bytes) -> tuple[str, str]:
    """OpenDocument Presentation (.odp)."""
    try:
        import zipfile
        from xml.etree import ElementTree as ET
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            xml = z.read("content.xml")
        tree  = ET.fromstring(xml)
        parts = [el.text or "" for el in tree.iter() if el.text]
        text  = "\n".join(p.strip() for p in parts if p.strip())
        if not text:
            return "", "ODP file appears empty."
        return text, ""
    except Exception:
        return "", f"ODP read error:\n{traceback.format_exc()}"


# ── Spreadsheets ──────────────────────────────────────────────────────────────

def _xlsx(b: bytes) -> tuple[str, str]:
    try:
        import openpyxl
        wb    = openpyxl.load_workbook(io.BytesIO(b), read_only=True, data_only=True)
        parts = []
        for sheet in wb.worksheets:
            parts.append(f"\n=== Sheet: {sheet.title} ===")
            for row in sheet.iter_rows(values_only=True):
                row_text = " | ".join(str(c) for c in row if c is not None)
                if row_text.strip():
                    parts.append(row_text)
        text = "\n".join(parts).strip()
        if not text:
            return "", "XLSX file appears empty."
        return text, ""
    except Exception:
        return "", f"XLSX read error:\n{traceback.format_exc()}"


def _xls(b: bytes) -> tuple[str, str]:
    try:
        import xlrd
        wb    = xlrd.open_workbook(file_contents=b)
        parts = []
        for sheet in wb.sheets():
            parts.append(f"\n=== Sheet: {sheet.name} ===")
            for r in range(sheet.nrows):
                row_text = " | ".join(str(sheet.cell_value(r, c)) for c in range(sheet.ncols))
                if row_text.strip():
                    parts.append(row_text)
        text = "\n".join(parts).strip()
        if not text:
            return "", "XLS file appears empty."
        return text, ""
    except Exception:
        return "", f"XLS read error:\n{traceback.format_exc()}"


def _ods(b: bytes) -> tuple[str, str]:
    """OpenDocument Spreadsheet (.ods)."""
    try:
        import zipfile
        from xml.etree import ElementTree as ET
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            xml = z.read("content.xml")
        tree  = ET.fromstring(xml)
        parts = [el.text or "" for el in tree.iter() if el.text]
        text  = "\n".join(p.strip() for p in parts if p.strip())
        if not text:
            return "", "ODS file appears empty."
        return text, ""
    except Exception:
        return "", f"ODS read error:\n{traceback.format_exc()}"


def _csv(b: bytes) -> tuple[str, str]:
    try:
        import csv
        for enc in ("utf-8", "latin-1", "cp1252"):
            try:
                reader = csv.reader(io.StringIO(b.decode(enc)))
                rows   = [" | ".join(row) for row in reader if any(row)]
                text   = "\n".join(rows).strip()
                if text:
                    return text, ""
            except Exception:
                continue
        return "", "Could not parse CSV file."
    except Exception:
        return "", f"CSV read error:\n{traceback.format_exc()}"


# ── Web / Data ────────────────────────────────────────────────────────────────

def _html(b: bytes) -> tuple[str, str]:
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(b, "html.parser")
        # Remove script and style tags
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator="\n").strip()
        text = re.sub(r"\n{3,}", "\n\n", text)
        if not text:
            return "", "HTML file appears empty."
        return text, ""
    except Exception:
        return "", f"HTML read error:\n{traceback.format_exc()}"


def _json(b: bytes) -> tuple[str, str]:
    try:
        import json

        def _flatten(obj, prefix=""):
            lines = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    lines.extend(_flatten(v, f"{prefix}{k}: "))
            elif isinstance(obj, list):
                for item in obj:
                    lines.extend(_flatten(item, prefix))
            else:
                lines.append(f"{prefix}{obj}")
            return lines

        data  = json.loads(b.decode("utf-8", errors="ignore"))
        text  = "\n".join(_flatten(data)).strip()
        if not text:
            return "", "JSON file appears empty."
        return text, ""
    except Exception:
        return "", f"JSON read error:\n{traceback.format_exc()}"


def _xml(b: bytes) -> tuple[str, str]:
    try:
        from xml.etree import ElementTree as ET
        tree  = ET.fromstring(b)
        parts = [el.text or "" for el in tree.iter() if el.text]
        text  = "\n".join(p.strip() for p in parts if p.strip())
        if not text:
            return "", "XML file appears empty."
        return text, ""
    except Exception:
        # Fallback: strip tags with regex
        try:
            raw  = b.decode("utf-8", errors="ignore")
            text = re.sub(r"<[^>]+>", " ", raw)
            text = re.sub(r"\s{2,}", " ", text).strip()
            if text:
                return text, ""
        except Exception:
            pass
        return "", f"XML read error:\n{traceback.format_exc()}"