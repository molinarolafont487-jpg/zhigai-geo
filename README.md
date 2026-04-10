# 智改GEO

智改GEO 是一个面向品牌 GEO 监测的 Streamlit 仪表板原型，当前演示品牌为 **SAGASAI.cc**，已接入火山方舟豆包推理接入点，并支持渐进式批量真实监测。

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

## Streamlit Cloud 部署

1. 将本项目推送到 GitHub 仓库
2. 打开 Streamlit Community Cloud: <https://share.streamlit.io>
3. 选择 GitHub 仓库
4. Main file path 填写：`frontend/dashboard.py`
5. 在 App Secrets 或环境变量中配置：

```toml
ARK_API_KEY="你的火山方舟 API Key"
```

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
