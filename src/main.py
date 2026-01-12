from __future__ import annotations

import argparse
import sys
from pathlib import Path
import re
from collections import Counter

from pdf_reader import extract_text


EXIT_OK = 0
EXIT_USAGE = 2
EXIT_RUNTIME = 1


def split_sentences(text: str) -> list[str]:
    """按中英文标点把文本切成句子。"""
    sentences = re.split(r"[。！？!?\n]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    return sentences


def summarize(text: str, max_sentences: int = 5) -> str:
    """简单的本地“伪摘要”算法（保持你现有逻辑不变）。"""
    sentences = split_sentences(text)
    if not sentences:
        return "没有可用的句子，可能 PDF 中主要是图片或空白。"

    words = []
    for s in sentences:
        cleaned = re.sub(r"[，,。．・、：:；;（）()\[\]\"'「」『』…]", " ", s)
        parts = cleaned.split()
        words.extend(parts)

    if not words:
        return "。\n".join(sentences[:max_sentences])

    freq = Counter(words)

    sentence_scores: list[tuple[float, str]] = []
    for s in sentences:
        cleaned = re.sub(r"[，,。．・、：:；;（）()\[\]\"'「」『』…]", " ", s)
        parts = cleaned.split()
        if not parts:
            continue
        score = sum(freq.get(w, 0) for w in parts) / len(parts)
        sentence_scores.append((score, s))

    sentence_scores.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s for _, s in sentence_scores[:max_sentences]]
    ordered = [s for s in sentences if s in top_sentences]
    return "。\n".join(ordered)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdf-demo",
        description="PDF demo v1.0 (engineering): extract text and write summary to a file.",
    )
    p.add_argument("-i", "--input", required=True, help="Input PDF path")
    p.add_argument("-o", "--output", required=False, help="Output file path (default: output/<input>.txt)")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose logs")
    return p


def default_output_path(input_path: Path) -> Path:
    return Path("output") / f"{input_path.stem}.txt"


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    in_path = Path(args.input)
    if not in_path.exists() or not in_path.is_file():
        print(f"[ERROR] Input file not found: {in_path}", file=sys.stderr)
        return EXIT_USAGE
    if in_path.suffix.lower() != ".pdf":
        print(f"[ERROR] Input is not a .pdf file: {in_path}", file=sys.stderr)
        return EXIT_USAGE

    out_path = Path(args.output) if args.output else default_output_path(in_path)

    # 确保输出目录存在
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Cannot create output directory: {out_path.parent}\n{type(e).__name__}: {e}", file=sys.stderr)
        return EXIT_USAGE

    try:
        if args.verbose:
            print(f"[INFO] Extracting text from: {in_path}")

        text = extract_text(str(in_path))

        if not text or not text.strip():
            print("[ERROR] No text extracted (maybe image-only PDF).", file=sys.stderr)
            return EXIT_RUNTIME

        summary = summarize(text)

        payload = (
            "=== 原文前 200 字 ===\n"
            f"{text[:200]}\n\n"
            "=== 本地摘要（伪 AI，免费，无需网络） ===\n"
            f"{summary}\n"
        )

        if args.verbose:
            print(f"[INFO] Writing output to: {out_path}")

        out_path.write_text(payload, encoding="utf-8")

        if args.verbose:
            print("[INFO] Done.")
        return EXIT_OK

    except Exception as e:
        print(f"[ERROR] Failed to process PDF: {in_path}\n{type(e).__name__}: {e}", file=sys.stderr)
        return EXIT_RUNTIME


if __name__ == "__main__":
    raise SystemExit(main())
