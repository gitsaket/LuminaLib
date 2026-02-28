"""Extract plain text from uploaded book files."""

import io

def extract_text(file_bytes: bytes, filename: str) -> str:
    """Return plain text from PDF or text files."""
    lower = filename.lower()

    if lower.endswith(".pdf"):
        return _extract_pdf(file_bytes)

    # Fallback: assume UTF-8 text
    return file_bytes.decode("utf-8", errors="replace")


def _extract_pdf(data: bytes) -> str:
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    except Exception:
        # Fallback to pdfminer
        try:
            from pdfminer.high_level import extract_text_to_fp  # type: ignore
            from pdfminer.layout import LAParams  # type: ignore

            output = io.StringIO()
            extract_text_to_fp(io.BytesIO(data), output, laparams=LAParams())
            return output.getvalue()
        except Exception:
            return ""
