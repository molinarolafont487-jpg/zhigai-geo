from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ====================== 数据库配置 ======================
DATABASE_URL = os.getenv(
 "DATABASE_URL", 
 "postgresql://postgres:your_password@localhost:5432/zhigai_geo"
)

# 创建引擎
engine = create_engine(DATABASE_URL, echo=False)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ====================== 数据库初始化 ======================
def init_db():
 """初始化数据库表"""
 SQLModel.metadata.create_all(bind=engine)
 print("✅ 智改GEO 数据库初始化完成（多租户支持就绪）")

# ====================== 获取数据库会话 ======================
def get_db():
 """FastAPI 依赖注入用"""
 db = SessionLocal()
 try:
 yield db
 finally:
 db.close()

# ====================== 测试连接 ======================
def test_connection():
 """测试数据库是否可以连接"""
 try:
 with Session(engine) as session:
 session.execute("SELECT 1")
 print("✅ 数据库连接测试成功")
 return True
 except Exception as e:
 print(f"❌ 数据库连接失败: {e}")
 return False

if __name__ == "__main__":
 init_db()
 test_connection()
