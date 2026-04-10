# 智改GEO

智改GEO 是一个面向品牌 GEO 监测的 Streamlit 仪表板原型，当前演示品牌为 **SAGASAI.cc**，已接入火山方舟豆包推理接入点，并支持渐进式批量真实监测。

GitHub 仓库：<https://github.com/molinarolafont487-jpg/zhigai-geo>

## 主入口

- Streamlit 主入口：`frontend/dashboard.py`

## 项目结构

```bash
zhigai-geo/
├── frontend/
│   └── dashboard.py
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── services/
│   │       └── doubao_service.py
│   └── requirements.txt
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 本地运行

```bash
cd zhigai-geo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run frontend/dashboard.py
```

默认访问地址：`http://localhost:8501`

## Streamlit Community Cloud 部署

### 1. 登录 Streamlit Cloud

打开：<https://share.streamlit.io>

使用 GitHub 账号登录，并授权读取仓库。

### 2. 创建新 App

登录后点击：
- **New app**

按下面配置填写：
- **Repository**: `molinarolafont487-jpg/zhigai-geo`
- **Branch**: `main`
- **Main file path**: `frontend/dashboard.py`
- **App URL**: 可自定义一个子域名前缀

### 3. 配置 Secrets

在 App 的 **Advanced settings** 或部署后的 **Settings → Secrets** 中添加：

```toml
ARK_API_KEY="你的火山方舟 API Key"
```

### 4. 点击 Deploy

部署完成后会得到一个：
- `https://xxx.streamlit.app`

的临时访问地址。

## 依赖说明

根目录 `requirements.txt` 已整理为 Streamlit Cloud 可直接安装的版本，包含：
- streamlit
- pandas
- python-dotenv
- openai
- fastapi
- uvicorn
- sqlmodel
- pydantic

## 当前功能

- 深黑专业风格仪表板
- 渐进式批量真实豆包监测
- 实时进度条
- 逐条追加结果表格
- 可见度分数、情感、理由、优化建议展示

## 注意事项

- 不要把真实 `.env` 或密钥提交到 GitHub
- 当前真正可用的是 Ark 的**推理接入点 ID**，不是控制台展示名
- 若部署到 Streamlit Cloud，建议把敏感配置放在 Secrets 中
- 如果 Streamlit Cloud 首次部署失败，优先检查：
  - `Main file path` 是否为 `frontend/dashboard.py`
  - Secrets 中是否已填写 `ARK_API_KEY`
  - 根目录 `requirements.txt` 是否被正确识别
