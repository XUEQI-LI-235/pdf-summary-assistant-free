# src/pdf_reader.py

import fitz  # PyMuPDF

def extract_text(pdf_path: str) -> str:
    """
    使用 PyMuPDF 从 PDF 中提取文本。
    对 macOS 生成的 PDF、中文/日文 PDF 的兼容性比 PyPDF2 更好。
    """
    text_parts: list[str] = []

    # 打开 PDF
    with fitz.open(pdf_path) as doc:
        for page in doc:
            # get_text() 会返回这一页的纯文本
            text_parts.append(page.get_text())

    return "\n".join(text_parts)
