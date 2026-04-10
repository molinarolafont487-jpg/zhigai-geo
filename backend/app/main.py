from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# ====================== 创建 FastAPI 应用 ======================
app = FastAPI(
 title="智改GEO API",
 description="智改赋能深圳科技有限公司 - 生成式引擎优化平台后端",
 version="0.1.0",
 docs_url="/docs",
 redoc_url="/redoc"
)

# ====================== CORS 配置（允许前端访问） ======================
app.add_middleware(
 CORSMiddleware,
 allow_origins=["*"], # 开发阶段允许所有，生产环境请修改
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

# ====================== 根路由 ======================
@app.get("/")
async def root():
 return {
 "message": "智改GEO API 已成功启动！",
 "company": "智改赋能深圳科技有限公司",
 "product": "智改GEO - 让品牌被AI主动推荐",
 "status": "running",
 "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
 "version": "0.1.0 (Stage 1 - 豆包试点)"
 }

# ====================== 健康检查 ======================
@app.get("/health")
async def health_check():
 return {
 "status": "healthy",
 "timestamp": datetime.now().isoformat(),
 "service": "zhigai-geo-backend"
 }

# ====================== 简单测试接口（后续会扩展） ======================
@app.get("/api/monitoring/status")
async def monitoring_status():
 """返回当前监测系统状态"""
 return {
 "brand": "SAGASAI.cc",
 "platform": "豆包",
 "total_prompts": 50,
 "monitored_today": 42,
 "average_citation_rate": 58.3,
 "last_update": datetime.now().strftime("%Y-%m-%d %H:%M")
 }

# ====================== 启动说明 ======================
if __name__ == "__main__":
 print("🚀 智改GEO Backend 正在启动...")
 print("访问地址: http://127.0.0.1:8000/docs 查看API文档")
 uvicorn.run(app, host="0.0.0.0", port=8000)
