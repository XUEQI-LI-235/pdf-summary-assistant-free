from pdf_reader import extract_text
import re
from collections import Counter


def split_sentences(text: str) -> list[str]:
    """
    按中英文标点把文本切成句子。
    """
    # 按句号、问号、感叹号等切
    sentences = re.split(r"[。！？!?\n]+", text)
    # 去掉太短的空句子
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    return sentences


def summarize(text: str, max_sentences: int = 5) -> str:
    """
    简单的本地“伪摘要”：
    - 统计每个词出现频率
    - 给每个句子打分（句子里词频之和）
    - 选出分数最高的若干句子
    """
    sentences = split_sentences(text)
    if not sentences:
        return "没有可用的句子，可能 PDF 中主要是图片或空白。"

    # 简单按空格和中文字符切词（非常粗糙，不过够用来玩）
    words = []
    for s in sentences:
        # 去掉一些标点
        cleaned = re.sub(r"[，,。．・、：:；;（）()\[\]\"'「」『』…]", " ", s)
        parts = cleaned.split()
        words.extend(parts)

    if not words:
        # 如果没切出词，就退而求其次：返回前几句
        return "。\n".join(sentences[:max_sentences])

    freq = Counter(words)

    # 句子打分：句子中每个词的频率之和
    sentence_scores: list[tuple[float, str]] = []
    for s in sentences:
        cleaned = re.sub(r"[，,。．・、：:；;（）()\[\]\"'「」『』…]", " ", s)
        parts = cleaned.split()
        if not parts:
            continue
        score = sum(freq.get(w, 0) for w in parts) / len(parts)
        sentence_scores.append((score, s))

    # 按分数从高到低排序，取前 max_sentences 句
    sentence_scores.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s for _, s in sentence_scores[:max_sentences]]

    # 保留原始出现顺序
    ordered = [s for s in sentences if s in top_sentences]
    return "。\n".join(ordered)


def main():
    pdf_path = "sample2.pdf"  # 确保项目根目录有这个文件
    text = extract_text(pdf_path)

    if not text.strip():
        print("PDF 中没有提取到文本（可能是纯图片 PDF）")
        return

    print("=== 原文前 200 字 ===")
    print(text[:200])

    print("\n=== 本地摘要（伪 AI，免费，无需网络） ===")
    summary = summarize(text)
    print(summary)


if __name__ == "__main__":
    main()
