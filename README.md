# AI 信息雷达

> 每天自动从 30+ 信息源抓取 AI 内容，AI 智能评分筛选，生成 Obsidian 日报。

关注方向：**OPC/AI 赚钱案例 · AI+电商 · AI 工具实操 · AI 新技术 · 投融资动态**

---

## 致谢

本项目基于 [AI 信息雷达](https://github.com/hustcc/ai-info-aggregator)（作者：hustcc）进行二次开发，原项目采用 MIT 协议。

**原项目特性：**
- GitHub Actions 定时运行，全自动抓取 + AI 评分 + 日报生成
- 43 个中英文信息源（RSS/Atom）
- Claude Haiku 评分 + Claude Sonnet 摘要（via OpenRouter）
- Obsidian 原生格式，支持 Dataview 查询

**本次修改：**
- **API 适配**：支持任意 OpenAI 兼容 API（DeepSeek / 小米 MiMo / OpenRouter 等），通过环境变量 `API_KEY` + `API_BASE_URL` + `MODEL_NAME` 配置
- **dotenv 支持**：本地开发时自动加载 `.env` 文件
- **钉钉通知**：每日生成完成后自动推送钉钉机器人消息
- **兼容性**：保留对原 `DEEPSEEK_API_KEY` / `OPENROUTER_API_KEY` 环境变量的兼容

---

## 效果预览

每天早上自动生成，推送到 GitHub，钉钉机器人同步通知。

```markdown
## OPC/AI赚钱案例

### [40 installs per day to 130. 34 USD per day to 130.](https://reddit.com/...)
- **来源**：Reddit r/SideProject
- **评分**：8/10
- **标签**：`#ASO实战` `#一人公司` `#增长黑客`
- **摘要**：开发者通过5个ASO优化调整，将应用从每天40次自然安装、34美元收入提升至
  130次安装、130美元收入...
```

→ 查看完整示例：[examples/AI Daily - 2026-04-03.md](examples/AI%20Daily%20-%202026-04-03.md)

---

## 快速开始

### 第一步：Fork 仓库

点击右上角 **Fork**，fork 到你的 GitHub 账户。

### 第二步：配置 Secrets

在你 fork 的仓库中：**Settings → Secrets and variables → Actions → New repository secret**

| Name | Value | 说明 |
|------|-------|------|
| `API_KEY` | 你的 API Key | 支持 DeepSeek / 小米 MiMo / OpenRouter |
| `API_BASE_URL` | `https://api.deepseek.com` | API 接口地址 |
| `MODEL_NAME` | `deepseek-v4-flash` | 模型名称 |
| `DINGTALK_WEBHOOK` | `https://oapi.dingtalk.com/robot/send?access_token=xxx` | 钉钉机器人 Webhook（可选） |

**小米 MiMo 配置示例：**
- `API_BASE_URL`：`https://token-plan-cn.xiaomimimo.com/v1`
- `MODEL_NAME`：`mimo-v2.5-pro`

### 第三步：启用 Actions

进入 **Actions** 标签页，点击 **"I understand my workflows, go ahead and enable them"**。

**完成。** 每天北京时间 07:00 自动运行，结果写入 `output/` 目录，钉钉收到通知。

---

## 钉钉机器人配置

1. 在钉钉群中添加自定义机器人（Webhook 方式）
2. 复制 Webhook URL
3. 在 GitHub repo 的 Secrets 中添加 `DINGTALK_WEBHOOK`
4. 机器人会收到每日摘要通知，包含文章数量和 top 文章标题

---

## 本地运行

```bash
# 克隆仓库
git clone https://github.com/your-username/ai-info-aggregator.git
cd ai-info-aggregator

# 安装依赖
pip install -r requirements.txt

# 配置 API（编辑 .env 文件）
cp .env.example .env
# 编辑 .env，填入 API_KEY / API_BASE_URL / MODEL_NAME

# 运行
python main.py

# 或指定回溯天数
LOOKBACK_DAYS=3 python main.py
```

---

## 信息源（43个）

覆盖中英文，按方向分类：

| 方向 | 来源 |
|------|------|
| OPC/创业案例 | Indie Hackers · Reddit r/SideProject · Reddit r/Entrepreneur |
| AI Newsletter | Ben's Bites · The Rundown AI · One Useful Thing · Zara's Newsletter · TLDR AI · The Batch · Latent Space · Lenny's Newsletter |
| AI 技术 | Simon Willison · Hugging Face Blog · Hacker News Show HN · Reddit r/LocalLLaMA · GitHub Trending |
| 科技媒体（英文） | VentureBeat AI · TechCrunch AI · MIT Technology Review |
| 商业趋势 | Trends.vc · Product Hunt |
| AI + 电商 | Practical Ecommerce · Shopify Blog · Marketing AI Institute · SEJ Ecommerce · eCommerceFuel · eCommerceBytes |
| 中文媒体 | 量子位 · 机器之心 · 36氪 · 少数派 · 爱范儿 · 极客公园 · 晚点 LatePost |
| 微信公众号 | 数字生命卡兹克 · 卡尔的AI沃茨 · 饼干哥哥AGI · 刘小排r · 沃垠AI · AGI Hunt · 一泽Eze · 赛博禅心 · 第二曲线增长 |

---

## 项目结构

```
ai-info-aggregator/
├── main.py              # 入口（dotenv + 通用 API 配置）
├── feeds.toml           # 信息源配置
├── requirements.txt
├── .env.example         # 环境变量模板
├── src/
│   ├── feeds.py         # RSS 抓取
│   ├── scorer.py        # AI 评分 / 去重 / 摘要
│   ├── history.py       # 历史去重
│   └── writer.py        # Markdown 生成
├── output/              # 生成的日报（Git 追踪）
└── .github/workflows/
    ├── daily.yml        # 定时任务 + 钉钉通知
    └── keepalive.yml    # 防止 Actions 休眠
```

---

## License

MIT（原项目：[hustcc/ai-info-aggregator](https://github.com/hustcc/ai-info-aggregator)）
