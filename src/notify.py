"""钉钉机器人通知模块。
将每日摘要中的每篇文章作为独立消息发送到钉钉群。
"""
import os
import re
import time
import json
import urllib.request


def _parse_articles(md_content: str) -> list[dict]:
    """从 markdown 日报中解析出每篇文章。"""
    articles = []
    current_topic = ""

    for line in md_content.split("\n"):
        # 一级主题
        if line.startswith("## "):
            current_topic = line[3:].strip()
        # 文章标题
        elif line.startswith("### ["):
            m = re.match(r"### \[(.+?)\]\((.+?)\)", line)
            if m:
                articles.append({
                    "topic": current_topic,
                    "title": m.group(1),
                    "url": m.group(2),
                    "source": "",
                    "score": "",
                    "tags": [],
                    "summary": "",
                })
        # 文章属性
        elif articles and line.startswith("- **"):
            a = articles[-1]
            if "来源" in line:
                a["source"] = line.split("：", 1)[-1].strip()
            elif "评分" in line:
                a["score"] = line.split("：", 1)[-1].strip()
            elif "标签" in line:
                a["tags"] = re.findall(r"`#(.+?)`", line)
            elif "摘要" in line:
                a["summary"] = line.split("：", 1)[-1].strip()

    return articles


def _send_dingtalk(webhook: str, title: str, text: str, retries: int = 3) -> bool:
    """发送一条钉钉 markdown 消息，带重试（应对限流）。"""
    payload = json.dumps({
        "msgtype": "markdown",
        "markdown": {"title": title, "text": text}
    }).encode("utf-8")

    for attempt in range(retries):
        req = urllib.request.Request(
            webhook,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            resp = urllib.request.urlopen(req, timeout=10)
            result = json.loads(resp.read())
            if result.get("errcode") == 0:
                return True
            # 限流：等待后重试
            if result.get("errcode") in (130001, 300001):
                wait = 5 * (attempt + 1)
                time.sleep(wait)
                continue
            print(f"  [WARN] DingTalk error: {result}")
            return False
        except Exception as e:
            print(f"  [WARN] DingTalk send failed: {e}")
            if attempt < retries - 1:
                time.sleep(3)
    return False


def notify_dingtalk(webhook: str, md_path: str, delay: float = 1.0) -> None:
    """读取日报 markdown，逐篇发送到钉钉。

    Args:
        webhook: 钉钉机器人 Webhook URL
        md_path: 日报 markdown 文件路径
        delay: 每条消息间隔秒数（防限流）
    """
    if not webhook:
        print("[DingTalk] webhook not set, skipping")
        return

    if not os.path.exists(md_path):
        print(f"[DingTalk] file not found: {md_path}")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    articles = _parse_articles(content)
    if not articles:
        print("[DingTalk] no articles found in digest")
        return

    # 提取日期
    date_match = re.search(r"date:\s*(\d{4}-\d{2}-\d{2})", content)
    date = date_match.group(1) if date_match else "today"

    print(f"[DingTalk] sending {len(articles)} articles...")

    # 发送汇总消息
    summary = f"## 🤖 AI 日报 {date}\n\n共 **{len(articles)}** 篇文章入选\n\n"
    for i, a in enumerate(articles, 1):
        summary += f"{i}. [{a['title'][:40]}]({a['url']})\n"
    _send_dingtalk(webhook, f"AI 日报 {date}", summary)
    time.sleep(delay)

    # 逐篇发送
    total = len(articles)
    for i, a in enumerate(articles, 1):
        tags_str = " ".join(f"`#{t}`" for t in a["tags"])

        # 主题 emoji 映射
        topic_emoji = {
            "OPC/AI赚钱案例": "💰",
            "AI+电商": "🛒",
            "AI工具实操/Agent工作流": "🔧",
            "AI新技术/新模型": "🔬",
            "AI投融资动态": "📈",
            "AI对行业的冲击": "🌍",
        }
        emoji = topic_emoji.get(a["topic"], "📌")

        text = (
            f"### {emoji} [{a['title']}]({a['url']})\n\n"
            f"> **{a['topic']}** | 第 {i}/{total} 篇\n\n"
            f"- **来源**：{a['source']}\n"
            f"- **评分**：{a['score']}\n"
        )
        if tags_str:
            text += f"- **标签**：{tags_str}\n"
        if a["summary"]:
            text += f"\n{a['summary']}\n"

        ok = _send_dingtalk(webhook, f"{emoji} {a['title'][:20]}", text)
        status = "✅" if ok else "❌"
        print(f"  {status} [{i}/{total}] {a['title'][:50]}")
        if i < total:
            time.sleep(delay)

    print(f"[DingTalk] done, {len(articles)} messages sent")
