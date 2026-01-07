#  📖 SlideNovel | AI 滑动续写小说

**SlideNovel** 是一个「滑动窗口 + 大模型」驱动的自动化中文小说续写项目。  
每天凌晨，GitHub Actions 会读取最新 N 章 → 调用 LLM（OpenAI 或任意兼容 API）→ 生成下一章并提交回仓库，循环往复，直到达到设定的最大章节数。

---

##  ✨ 特性

- ✅ 滑动窗口机制：只给模型最近 N 章，避免上下文爆炸  
- ✅ 中文原生：提示词、生成内容均为中文  
- ✅ 任意兼容 OpenAI 格式的 API（OpenAI / DeepSeek / Together / Ollama …）  
- ✅ Hexo 友好：每章自动带 front-matter，可直接 `hexo deploy` 生成静态站  
- ✅ 全自动：每天 UTC 02:00 运行，也可手动触发  
- ✅ 易调参：窗口大小、最大章节数、单章长度、模型名全部用 GitHub Variables 控制  

---

##  🚀 快速开始（Fork 即用）

1. **Fork 本仓库** → 进入你自己的 `SlideNovel`  
2. **添加 Secrets**  
   Settings → Secrets and variables → Actions → New repository secret  
   - `LLM_API_KEY` = `sk-xxxxxxxx`（你的 API Key）

3. **添加 Variables**（Settings → Variables → New variable）  

   | Variable | 示例值 | 说明 |
   |---|---|---|
   | `WINDOW_SIZE` | `3` | 用最近几章做上下文 |
   | `MAX_CHAPTERS` | `100` | 写到第几章后停止 |
   | `MAX_LENGTH_PER_CHAPTER` | `2000` | 单章最大字符数 |
   | `MODEL_NAME` | `gpt-4o-mini` | 模型名 |
   | `LLM_API_BASE_URL` | `https://api.openai.com/v1` | 兼容端点，默认即可 |

4. **准备第一章**  
   在 `source/_posts/` 新建 `1.md`（文件名必须是纯数字）：

   ```markdown
   ---
   title: "第一章 雨夜"
   date: "2026-01-01T00:00:00Z"
   ---

   那一夜的雨，下得比往常都急……
   ```

5. **手动触发一次**  
   Actions → Daily SlideNovel Generation → Run workflow  
   看到绿色  ✔ 后，`2.md` 就会出现在 `source/_posts/`。

6. **（可选）生成静态站**  
   ```bash
   npm install hexo-cli -g
   npm install
   hexo generate   # public/ 目录即整站
   hexo deploy     # 若已配 _config.yml 的 deploy 字段
   ```

---

##  📁 项目结构

```
SlideNovel/
├── .github/workflows/daily-slide.yaml   # 定时任务
├── generate_next_chapter.py             # 核心 Python 脚本
├── source/_posts/
│   ├── 1.md
│   ├── 2.md
│   └── …                                # 自动递增
├── _config.yml                          # Hexo 配置
└── themes/                              # Hexo 主题
```

> 非数字命名的 `.md`（如 `hello-world.md`）会被脚本自动忽略，放心保留。

---

##  ️ 本地调试

```bash
export LLM_API_KEY="sk-xxx"
export WINDOW_SIZE=3
export MAX_CHAPTERS=100
export MAX_LENGTH_PER_CHAPTER=2000
export MODEL_NAME="gpt-4o-mini"
export LLM_API_BASE_URL="https://api.openai.com/v1"

python generate_next_chapter.py
```

---

##  📄 License

MIT © SlideNovel Contributors  
（Fork 自 hexo-starter，同样 MIT）

---

##   后续玩法

- 把 `public/` 部署到 GitHub Pages → 免费在线阅读  
- 接入 GitHub Issues / Discussions 让读者投票剧情走向  
- 改用多模态模型，让 AI 同时插图  
- 把窗口大小调成 1，体验「接龙式」荒诞文风  

**Happy Writing!** 让 AI 陪你把故事一直写下去  ️
