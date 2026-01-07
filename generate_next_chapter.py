import os
import re
import glob
from pathlib import Path
from openai import OpenAI
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 从环境变量读取配置
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", "3"))
MAX_CHAPTERS = int(os.getenv("MAX_CHAPTERS", "100"))
MAX_LENGTH_PER_CHAPTER = int(os.getenv("MAX_LENGTH_PER_CHAPTER", "2000"))  # 字符数上限（可按需改为 token）
API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_API_BASE_URL", "https://api.openai.com/v1")  # 支持兼容 API（如 Ollama, vLLM, etc.）
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

POSTS_DIR = Path("source/_posts")
POSTS_DIR.mkdir(parents=True, exist_ok=True)

def extract_number(filename: str) -> int:
    """从文件名提取序号，如 '3.md' → 3"""
    stem = Path(filename).stem
    match = re.match(r"(\d+)", stem)
    return int(match.group(1)) if match else -1

def get_latest_chapters(window_size: int):
    """获取最新的 window_size 个章节内容（按序号排序）"""
    md_files = glob.glob(str(POSTS_DIR / "*.md"))
    md_files.sort(key=extract_number, reverse=True)
    latest_files = sorted(md_files[:window_size], key=extract_number)
    chapters = []
    for f in latest_files:
        with open(f, "r", encoding="utf-8") as file:
            content = file.read()
            # 去掉 Hexo 的 front-matter（如果存在）
            if content.startswith("---"):
                end = content.find("---", 3)
                if end != -1:
                    content = content[end + 3:].lstrip()
            chapters.append(content.strip())
    return chapters

def get_next_chapter_number():
    """计算下一个章节序号"""
    md_files = glob.glob(str(POSTS_DIR / "*.md"))
    numbers = [extract_number(f) for f in md_files if extract_number(f) >= 0]
    return max(numbers) + 1 if numbers else 1

def generate_continuation(chapters: list[str]) -> str:
    """调用 LLM 生成续写（中文提示）"""
    # 把最近 WINDOW_SIZE 章拼接成上下文
    context = "\n\n---\n\n".join(chapters[-WINDOW_SIZE:])

    system_msg = "你是一位擅长中文长篇小说的作家，语言流畅、富有画面感。"
    user_msg = (
        f"以下是小说的最后 {len(chapters[-WINDOW_SIZE:])} 章内容：\n\n"
        f"{context}\n\n"
        "请续写下一章，只返回小说正文，不要任何解释、标题或注释。"
    )

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=MAX_LENGTH_PER_CHAPTER // 4,
            temperature=0.7,
        )
        text = response.choices[0].message.content.strip()
        return text
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise

def save_chapter(number: int, content: str):
    """保存为 Hexo 格式的 .md 文件"""
    filename = POSTS_DIR / f"{number}.md"
    # 简单 front-matter
    front_matter = f"""---
title: "Chapter {number}"
date: "{os.popen('date -u +"%Y-%m-%dT%H:%M:%SZ"').read().strip()}"
---

"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + content)
    logger.info(f"Saved chapter {number} to {filename}")

def main():
    current_count = len(glob.glob(str(POSTS_DIR / "*.md")))
    if current_count >= MAX_CHAPTERS:
        logger.info("Reached maximum chapter count. Exiting.")
        return

    if current_count == 0:
        logger.info("No existing chapters. Please add at least one (e.g., source/_posts/1.md).")
        return

    chapters = get_latest_chapters(WINDOW_SIZE)
    if not chapters:
        logger.error("No valid chapters found.")
        return

    logger.info(f"Using {len(chapters)} latest chapters for context.")
    new_content = generate_continuation(chapters)
    next_num = get_next_chapter_number()
    save_chapter(next_num, new_content)

if __name__ == "__main__":
    main()
