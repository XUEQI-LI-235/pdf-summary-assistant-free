from PyPDF2 import PdfReader

def extract_text(pdf_path: str) -> str:
    """
    从 PDF 文件中提取文本内容。

    :param pdf_path: PDF 文件路径
    :return: 提取出的文本字符串
    """
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text
