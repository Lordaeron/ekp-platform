# EKP企业级知识中台MVP实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 2周完成第一阶段MVP开发，实现完整的文档上传-处理-召回全流程，具备可用的基础功能和管理后台。
**架构：** 前后端分离架构，后端FastAPI+Celery实现异步处理，PostgreSQL存储业务元数据，Neo4j存储知识图谱，复用火山引擎智能知识库作为向量检索引擎，本地文件系统存储原始文档。
**技术栈：** FastAPI + Pydantic + SQLAlchemy + Celery + Redis + PostgreSQL + Neo4j + Vue3 + Element Plus + 火山引擎SDK

---

## 一、项目文件结构
| 文件路径 | 职责说明 |
|---------|---------|
| `pyproject.toml` | Python项目配置、依赖管理 |
| `requirements.txt` | 依赖清单 |
| `.env.example` | 环境变量模板 |
| `docker-compose.yml` | Docker Compose部署配置 |
| `Dockerfile` | 后端服务镜像构建 |
| `src/ekp_platform/__init__.py` | 包初始化、版本信息 |
| `src/ekp_platform/main.py` | FastAPI应用入口、路由注册 |
| `src/ekp_platform/config.py` | 配置管理，读取环境变量 |
| `src/ekp_platform/database.py` | PostgreSQL连接、SQLAlchemy ORM基类 |
| `src/ekp_platform/celery_app.py` | Celery应用初始化、任务配置 |
| `src/ekp_platform/models/*.py` | 数据库ORM模型定义 |
| `src/ekp_platform/schemas/*.py` | Pydantic请求/响应Schema定义 |
| `src/ekp_platform/api/v1/*.py` | V1版本API路由实现 |
| `src/ekp_platform/services/*.py` | 核心业务逻辑层 |
| `src/ekp_platform/clients/volcano_kb_client.py` | 火山向量库SDK封装 |
| `src/ekp_platform/tasks/process_tasks.py` | 文档处理异步任务实现 |
| `src/ekp_platform/utils/*.py` | 工具函数（文件处理、哈希等） |
| `tests/conftest.py` | Pytest测试配置 |
| `tests/test_*.py` | 各模块单元测试 |
| `frontend/` | Vue3前端项目 |

---

## 二、详细开发任务
### 任务 1：项目基础框架搭建
**文件：**
- 创建：`pyproject.toml`
- 创建：`requirements.txt`
- 创建：`.env.example`
- 创建：`src/ekp_platform/__init__.py`
- 创建：`src/ekp_platform/config.py`
- 创建：`src/ekp_platform/main.py`
- 测试：`tests/test_basic.py`

**优先级：最高 | 工作量：1人天 | 依赖：无**

- [ ] **步骤 1：编写pyproject.toml项目配置**
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "ekp-platform"
version = "0.1.0"
authors = [
  { name="Your Name", email="your.email@example.com" }
]
description = "EKP - Enterprise Knowledge Platform, 企业级知识中台"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.100.0",
  "uvicorn>=0.23.2",
  "pydantic>=2.0.0",
  "pydantic-settings>=2.0.0",
  "sqlalchemy>=2.0.20",
  "psycopg2-binary>=2.9.7",
  "celery>=5.3.4",
  "redis>=5.0.0",
  "python-multipart>=0.0.6",
  "python-dotenv>=1.0.0",
  "unstructured>=0.10.19",
  "langchain>=0.0.300",
  "pydantic>=2.0.0",
  "python-jose[cryptography]>=3.3.0",
  "passlib[bcrypt]>=1.7.4",
  "jinja2>=3.1.2"
]

[project.optional-dependencies]
dev = [
  "pytest>=7.4.0",
  "pytest-cov>=4.1.0",
  "black>=23.9.1",
  "flake8>=6.1.0",
  "mypy>=1.5.1",
  "ipython>=8.15.0"
]

[project.scripts]
ekp = "ekp_platform.cli:main"
```

- [ ] **步骤 2：编写requirements.txt**
```txt
fastapi>=0.100.0
uvicorn>=0.23.2
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.20
psycopg2-binary>=2.9.7
celery>=5.3.4
redis>=5.0.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
unstructured>=0.10.19
langchain>=0.0.300
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
jinja2>=3.1.2
pytest>=7.4.0
pytest-cov>=4.1.0
```

- [ ] **步骤 3：编写.env.example环境变量模板**
```env
# 服务配置
SERVICE_NAME=ekp-platform
DEBUG=True
HOST=0.0.0.0
PORT=8000

# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ekp
POSTGRES_USER=ekp
POSTGRES_PASSWORD=ekp123456

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Neo4j配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j123456

# 火山引擎配置
VOLCANO_ACCESS_KEY=your_access_key
VOLCANO_SECRET_KEY=your_secret_key
VOLCANO_REGION=cn-beijing
VOLCANO_KB_ENDPOINT=your_kb_endpoint

# 文件存储配置
FILE_STORAGE_PATH=./data/files
MAX_FILE_SIZE=104857600  # 100MB
```

- [ ] **步骤 4：编写包初始化文件__init__.py**
```python
"""EKP - Enterprise Knowledge Platform, 企业级知识中台"""

__version__ = "0.1.0"
__author__ = "Your Name"
```

- [ ] **步骤 5：编写配置管理文件config.py**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # 服务配置
    SERVICE_NAME: str = "ekp-platform"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "ekp"
    POSTGRES_USER: str = "ekp"
    POSTGRES_PASSWORD: str = "ekp123456"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Neo4j配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j123456"
    
    # 火山引擎配置
    VOLCANO_ACCESS_KEY: str = ""
    VOLCANO_SECRET_KEY: str = ""
    VOLCANO_REGION: str = "cn-beijing"
    VOLCANO_KB_ENDPOINT: str = ""
    
    # 文件存储配置
    FILE_STORAGE_PATH: str = "./data/files"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB

settings = Settings()
```

- [ ] **步骤 6：编写FastAPI入口文件main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .api.v1 import router as v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    yield
    # 关闭时清理

app = FastAPI(
    title=settings.SERVICE_NAME,
    description="EKP - 企业级知识中台API文档",
    version="0.1.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(v1_router, prefix="/api/v1", tags=["v1"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.SERVICE_NAME, "version": "0.1.0"}
```

- [ ] **步骤 7：编写基础测试用例**
```python
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

- [ ] **步骤 8：运行测试验证通过**
运行：`pytest tests/test_basic.py::test_health_check -v`
预期：PASS

- [ ] **步骤 9：Commit**
```bash
git add pyproject.toml requirements.txt .env.example src/ekp_platform/__init__.py src/ekp_platform/config.py src/ekp_platform/main.py tests/test_basic.py
git commit -m "feat: 项目基础框架搭建完成"
```

### 任务 2：数据库ORM层和模型开发
**文件：**
- 创建：`src/ekp_platform/database.py`
- 创建：`src/ekp_platform/models/__init__.py`
- 创建：`src/ekp_platform/models/knowledge_base.py`
- 创建：`src/ekp_platform/models/document.py`
- 创建：`src/ekp_platform/models/process_task.py`
- 创建：`src/ekp_platform/models/knowledge_chunk.py`
- 测试：`tests/test_models.py`

**优先级：最高 | 工作量：1.5人天 | 依赖：任务1**

- [ ] **步骤 1：编写数据库连接基类database.py**
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, UUID

from .config import settings

# 创建数据库引擎
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基类
Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **步骤 2：编写知识库模型knowledge_base.py**
```python
from sqlalchemy import Column, String, Text, SmallInteger, JSON
from ..database import BaseModel

class KnowledgeBase(BaseModel):
    __tablename__ = "knowledge_base"
    
    name = Column(String(100), nullable=False, index=True, comment="知识库名称")
    description = Column(Text, comment="知识库描述")
    default_skill_id = Column(String(36), comment="默认SKILL配置ID")
    vector_model_config = Column(JSON, comment="向量模型配置")
    retrieval_config = Column(JSON, comment="默认召回配置")
    status = Column(SmallInteger, default=0, comment="状态：0-正常 1-禁用")
```

- [ ] **步骤 3：编写文档模型document.py**
```python
from sqlalchemy import Column, String, BigInteger, Text, SmallInteger, TIMESTAMP, UUID
from ..database import BaseModel

class Document(BaseModel):
    __tablename__ = "document"
    
    kb_id = Column(UUID(as_uuid=True), nullable=False, index=True, comment="所属知识库ID")
    name = Column(String(255), nullable=False, comment="文件名")
    file_type = Column(String(50), comment="文件类型")
    size = Column(BigInteger, comment="文件大小（字节）")
    md5 = Column(String(32), index=True, comment="文件MD5哈希")
    storage_path = Column(String(500), nullable=False, comment="本地存储路径")
    version = Column(SmallInteger, default=1, comment="版本号")
    process_status = Column(SmallInteger, default=0, comment="处理状态：0-待处理 1-处理中 2-成功 3-失败")
    error_log = Column(Text, comment="处理错误日志")
    processed_at = Column(TIMESTAMP, comment="处理完成时间")
```

- [ ] **步骤 4：编写处理任务模型process_task.py**
```python
from sqlalchemy import Column, String, SmallInteger, Integer, JSON, TIMESTAMP, ARRAY, UUID
from ..database import BaseModel

class ProcessTask(BaseModel):
    __tablename__ = "process_task"
    
    kb_id = Column(UUID(as_uuid=True), nullable=False, index=True, comment="知识库ID")
    document_ids = Column(ARRAY(UUID(as_uuid=True)), comment="关联的文档ID列表")
    skill_id = Column(UUID(as_uuid=True), comment="使用的SKILL配置ID")
    status = Column(SmallInteger, default=0, comment="任务状态：0-待执行 1-执行中 2-成功 3-失败")
    progress = Column(Integer, default=0, comment="处理进度百分比 0-100")
    result = Column(JSON, comment="处理结果统计")
    finished_at = Column(TIMESTAMP, comment="完成时间")
```

- [ ] **步骤 5：编写知识片段模型knowledge_chunk.py**
```python
from sqlalchemy import Column, String, JSON, SmallInteger, UUID
from ..database import BaseModel

class KnowledgeChunk(BaseModel):
    __tablename__ = "knowledge_chunk"
    
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True, comment="所属文档ID")
    kb_id = Column(UUID(as_uuid=True), nullable=False, index=True, comment="所属知识库ID")
    volcano_chunk_id = Column(String(100), comment="火山向量库中的片段ID")
    content_hash = Column(String(64), index=True, comment="内容哈希")
    location_info = Column(JSON, comment="在原始文档中的位置信息")
    review_status = Column(SmallInteger, default=0, comment="审核状态：0-未审核 1-正常 2-错误 3-已修正")
    error_info = Column(JSON, comment="错误信息")
```

- [ ] **步骤 6：编写模型初始化__init__.py**
```python
from .knowledge_base import KnowledgeBase
from .document import Document
from .process_task import ProcessTask
from .knowledge_chunk import KnowledgeChunk

__all__ = [
    "KnowledgeBase",
    "Document",
    "ProcessTask",
    "KnowledgeChunk"
]
```

- [ ] **步骤 7：编写模型测试用例**
```python
def test_create_knowledge_base(db_session):
    from ekp_platform.models import KnowledgeBase
    
    kb = KnowledgeBase(
        name="测试知识库",
        description="这是一个测试知识库",
        status=0
    )
    db_session.add(kb)
    db_session.commit()
    
    assert kb.id is not None
    assert kb.name == "测试知识库"
    assert kb.created_at is not None

def test_create_document(db_session):
    from ekp_platform.models import Document
    import uuid
    
    doc = Document(
        kb_id=uuid.uuid4(),
        name="测试文档.pdf",
        file_type="pdf",
        size=1024,
        md5="testmd5hash",
        storage_path="/tmp/test.pdf"
    )
    db_session.add(doc)
    db_session.commit()
    
    assert doc.id is not None
    assert doc.name == "测试文档.pdf"
    assert doc.process_status == 0
```

- [ ] **步骤 8：运行测试验证通过**
运行：`pytest tests/test_models.py -v`
预期：全部PASS

- [ ] **步骤 9：Commit**
```bash
git add src/ekp_platform/database.py src/ekp_platform/models/ tests/test_models.py
git commit -m "feat: 数据库ORM层和核心模型开发完成"
```

### 任务 3：火山向量库SDK封装
**文件：**
- 创建：`src/ekp_platform/clients/__init__.py`
- 创建：`src/ekp_platform/clients/volcano_kb_client.py`
- 测试：`tests/test_volcano_client.py`

**优先级：高 | 工作量：1人天 | 依赖：任务1**

- [ ] **步骤 1：编写火山SDK封装类volcano_kb_client.py**
```python
import json
from typing import List, Dict, Any, Optional
from volcengine.vectordb.VectorDBService import VectorDBService

from ..config import settings

class VolcanoKbClient:
    def __init__(self):
        self.client = VectorDBService()
        self.client.set_ak(settings.VOLCANO_ACCESS_KEY)
        self.client.set_sk(settings.VOLCANO_SECRET_KEY)
        self.client.set_host(settings.VOLCANO_KB_ENDPOINT)
        self.region = settings.VOLCANO_REGION
    
    def create_collection(self, collection_name: str, description: str = "") -> Dict[str, Any]:
        """创建集合（对应一个知识库）"""
        params = {
            "CollectionName": collection_name,
            "Description": description,
            "VectorIndex": {
                "MetricType": "cosine",
                "VectorType": "dense_float",
                "Dimension": 1536
            }
        }
        return self.client.create_collection(params)
    
    def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """删除集合"""
        params = {
            "CollectionName": collection_name
        }
        return self.client.delete_collection(params)
    
    def upsert_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量插入文档到向量库"""
        params = {
            "CollectionName": collection_name,
            "Documents": documents
        }
        return self.client.upsert_documents(params)
    
    def search(self, 
               collection_name: str, 
               query_text: str, 
               top_k: int = 10, 
               score_threshold: float = 0.0,
               filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """搜索向量"""
        params = {
            "CollectionName": collection_name,
            "Query": query_text,
            "TopK": top_k,
            "ScoreThreshold": score_threshold
        }
        if filter:
            params["Filter"] = filter
        return self.client.search(params)
    
    def hybrid_search(self,
                      collection_name: str,
                      query_text: str,
                      top_k: int = 10,
                      score_threshold: float = 0.0,
                      vector_weight: float = 0.7,
                      keyword_weight: float = 0.3) -> Dict[str, Any]:
        """混合检索（向量+关键词）"""
        params = {
            "CollectionName": collection_name,
            "Query": query_text,
            "TopK": top_k,
            "ScoreThreshold": score_threshold,
            "SearchStrategy": "hybrid",
            "HybridSearchParam": {
                "VectorWeight": vector_weight,
                "KeywordWeight": keyword_weight
            }
        }
        return self.client.search(params)
    
    def delete_documents(self, collection_name: str, document_ids: List[str]) -> Dict[str, Any]:
        """删除文档"""
        params = {
            "CollectionName": collection_name,
            "DocumentIds": document_ids
        }
        return self.client.delete_documents(params)

# 单例实例
volcano_kb_client = VolcanoKbClient()
```

- [ ] **步骤 2：编写客户端测试用例（Mock模式）**
```python
from unittest.mock import Mock, patch
from ekp_platform.clients.volcano_kb_client import VolcanoKbClient

def test_volcano_client_search():
    client = VolcanoKbClient()
    
    with patch.object(client.client, 'search') as mock_search:
        mock_search.return_value = {
            "Code": 0,
            "Message": "success",
            "Result": {
                "Documents": [
                    {
                        "Id": "doc1",
                        "Score": 0.92,
                        "Content": "测试内容1",
                        "MetaData": {"document_id": "test_doc_id"}
                    }
                ]
            }
        }
        
        result = client.search("test_collection", "测试查询", top_k=5)
        assert result["Code"] == 0
        assert len(result["Result"]["Documents"]) == 1
        assert result["Result"]["Documents"][0]["Score"] == 0.92
```

- [ ] **步骤 3：运行测试验证通过**
运行：`pytest tests/test_volcano_client.py -v`
预期：PASS

- [ ] **步骤 4：Commit**
```bash
git add src/ekp_platform/clients/ tests/test_volcano_client.py
git commit -m "feat: 火山向量库SDK封装完成"
```

### 任务 4：知识库管理模块开发
**文件：**
- 创建：`src/ekp_platform/schemas/__init__.py`
- 创建：`src/ekp_platform/schemas/knowledge_base.py`
- 创建：`src/ekp_platform/services/__init__.py`
- 创建：`src/ekp_platform/services/knowledge_base_service.py`
- 创建：`src/ekp_platform/api/v1/__init__.py`
- 创建：`src/ekp_platform/api/v1/knowledge_base.py`
- 测试：`tests/test_knowledge_base_api.py`

**优先级：高 | 工作量：1.5人天 | 依赖：任务2、任务3**

- [ ] **步骤 1：编写知识库Schema**
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

class KnowledgeBaseBase(BaseModel):
    name: str = Field(..., description="知识库名称", max_length=100)
    description: Optional[str] = Field(None, description="知识库描述")
    default_skill_id: Optional[UUID] = Field(None, description="默认SKILL配置ID")
    vector_model_config: Optional[Dict[str, Any]] = Field(None, description="向量模型配置")
    retrieval_config: Optional[Dict[str, Any]] = Field(None, description="默认召回配置")
    status: Optional[int] = Field(0, description="状态：0-正常 1-禁用")

class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass

class KnowledgeBaseUpdate(KnowledgeBaseBase):
    name: Optional[str] = Field(None, description="知识库名称")

class KnowledgeBaseOut(KnowledgeBaseBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

- [ ] **步骤 2：编写知识库服务层**
```python
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from ..models import KnowledgeBase
from ..schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate
from ..clients.volcano_kb_client import volcano_kb_client

class KnowledgeBaseService:
    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> List[KnowledgeBase]:
        """获取知识库列表"""
        return db.query(KnowledgeBase).offset(skip).limit(limit).all()
    
    @staticmethod
    def get(db: Session, kb_id: UUID) -> Optional[KnowledgeBase]:
        """根据ID获取知识库"""
        return db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    @staticmethod
    def create(db: Session, kb_in: KnowledgeBaseCreate) -> KnowledgeBase:
        """创建知识库"""
        kb = KnowledgeBase(**kb_in.model_dump())
        db.add(kb)
        db.commit()
        db.refresh(kb)
        
        # 在火山创建对应的集合
        try:
            volcano_kb_client.create_collection(
                collection_name=str(kb.id),
                description=kb.description
            )
        except Exception as e:
            # 创建失败回滚
            db.delete(kb)
            db.commit()
            raise e
        
        return kb
    
    @staticmethod
    def update(db: Session, kb_id: UUID, kb_in: KnowledgeBaseUpdate) -> Optional[KnowledgeBase]:
        """更新知识库"""
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
        if not kb:
            return None
        
        update_data = kb_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(kb, key, value)
        
        db.add(kb)
        db.commit()
        db.refresh(kb)
        return kb
    
    @staticmethod
    def delete(db: Session, kb_id: UUID) -> bool:
        """删除知识库"""
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
        if not kb:
            return False
        
        # 删除火山对应的集合
        try:
            volcano_kb_client.delete_collection(collection_name=str(kb.id))
        except Exception as e:
            raise e
        
        db.delete(kb)
        db.commit()
        return True
```

- [ ] **步骤 3：编写知识库API路由**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ...database import get_db
from ...schemas.knowledge_base import KnowledgeBaseOut, KnowledgeBaseCreate, KnowledgeBaseUpdate
from ...services.knowledge_base_service import KnowledgeBaseService

router = APIRouter(prefix="/knowledge-base", tags=["知识库管理"])

@router.get("", response_model=List[KnowledgeBaseOut], summary="获取知识库列表")
def list_knowledge_bases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return KnowledgeBaseService.list(db, skip=skip, limit=limit)

@router.get("/{kb_id}", response_model=KnowledgeBaseOut, summary="获取知识库详情")
def get_knowledge_base(
    kb_id: UUID,
    db: Session = Depends(get_db)
):
    kb = KnowledgeBaseService.get(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return kb

@router.post("", response_model=KnowledgeBaseOut, summary="创建知识库")
def create_knowledge_base(
    kb_in: KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):
    try:
        return KnowledgeBaseService.create(db, kb_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建知识库失败：{str(e)}")

@router.put("/{kb_id}", response_model=KnowledgeBaseOut, summary="更新知识库")
def update_knowledge_base(
    kb_id: UUID,
    kb_in: KnowledgeBaseUpdate,
    db: Session = Depends(get_db)
):
    kb = KnowledgeBaseService.update(db, kb_id, kb_in)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return kb

@router.delete("/{kb_id}", summary="删除知识库")
def delete_knowledge_base(
    kb_id: UUID,
    db: Session = Depends(get_db)
):
    success = KnowledgeBaseService.delete(db, kb_id)
    if not success:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return {"status": "success", "message": "删除成功"}
```

- [ ] **步骤 4：注册API路由到v1/__init__.py**
```python
from fastapi import APIRouter
from .knowledge_base import router as kb_router

router = APIRouter()
router.include_router(kb_router)
```

- [ ] **步骤 5：编写API测试用例**
```python
def test_create_knowledge_base(client):
    response = client.post(
        "/api/v1/knowledge-base",
        json={
            "name": "测试知识库API",
            "description": "API测试知识库"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试知识库API"
    assert "id" in data
    return data["id"]

def test_list_knowledge_bases(client):
    # 先创建一个
    kb_id = test_create_knowledge_base(client)
    
    response = client.get("/api/v1/knowledge-base")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(item["id"] == kb_id for item in data)
```

- [ ] **步骤 6：运行测试验证通过**
运行：`pytest tests/test_knowledge_base_api.py -v`
预期：全部PASS

- [ ] **步骤 7：Commit**
```bash
git add src/ekp_platform/schemas/ src/ekp_platform/services/ src/ekp_platform/api/v1/ tests/test_knowledge_base_api.py
git commit -m "feat: 知识库管理模块开发完成"
```

### 任务 5：文档上传和管理模块开发
**文件：**
- 创建：`src/ekp_platform/utils/__init__.py`
- 创建：`src/ekp_platform/utils/file_utils.py`
- 创建：`src/ekp_platform/utils/hash_utils.py`
- 创建：`src/ekp_platform/schemas/document.py`
- 创建：`src/ekp_platform/services/document_service.py`
- 创建：`src/ekp_platform/api/v1/document.py`
- 测试：`tests/test_document_api.py`

**优先级：高 | 工作量：2人天 | 依赖：任务4**

- [ ] **步骤 1：编写文件工具函数file_utils.py**
```python
import os
import shutil
from pathlib import Path
from uuid import UUID
from typing import Optional

from ..config import settings

def get_storage_path() -> Path:
    """获取文件存储根路径"""
    path = Path(settings.FILE_STORAGE_PATH)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_kb_storage_path(kb_id: UUID) -> Path:
    """获取知识库的存储路径"""
    path = get_storage_path() / str(kb_id)
    path.mkdir(parents=True, exist_ok=True)
    return path

def save_upload_file(file, dest_path: Path) -> None:
    """保存上传的文件到指定路径"""
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

def get_file_size(file_path: Path) -> int:
    """获取文件大小（字节）"""
    return os.path.getsize(file_path)

def delete_file(file_path: Path) -> bool:
    """删除文件"""
    try:
        if file_path.exists():
            os.remove(file_path)
            return True
        return False
    except:
        return False
```

- [ ] **步骤 2：编写哈希工具函数hash_utils.py**
```python
import hashlib
from pathlib import Path

def calculate_md5(file_path: Path, chunk_size: int = 4096) -> str:
    """计算文件MD5哈希"""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            md5.update(chunk)
    return md5.hexdigest()

def calculate_content_md5(content: str) -> str:
    """计算字符串内容的MD5哈希"""
    return hashlib.md5(content.encode("utf-8")).hexdigest()
```

- [ ] **步骤 3：编写文档Schema**
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class DocumentBase(BaseModel):
    name: str = Field(..., description="文件名")
    file_type: Optional[str] = Field(None, description="文件类型")
    size: Optional[int] = Field(None, description="文件大小（字节）")
    process_status: Optional[int] = Field(0, description="处理状态：0-待处理 1-处理中 2-成功 3-失败")

class DocumentOut(DocumentBase):
    id: UUID
    kb_id: UUID
    md5: Optional[str]
    version: int
    error_log: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True

class ProcessTaskCreate(BaseModel):
    document_ids: List[UUID] = Field(..., description="要处理的文档ID列表")
    skill_id: Optional[UUID] = Field(None, description="使用的SKILL配置ID")

class ProcessTaskOut(BaseModel):
    id: UUID
    status: int
    progress: int
    result: Optional[dict]
    created_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True
```

- [ ] **步骤 4：编写文档服务层**
```python
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pathlib import Path
import os

from ..models import Document, ProcessTask
from ..schemas.document import ProcessTaskCreate
from ..utils.file_utils import get_kb_storage_path, save_upload_file, get_file_size
from ..utils.hash_utils import calculate_md5
from ..config import settings
from ..celery_app import celery_app

class DocumentService:
    @staticmethod
    def list(db: Session, kb_id: UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        """获取知识库下的文档列表"""
        return db.query(Document).filter(Document.kb_id == kb_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def get(db: Session, doc_id: UUID) -> Optional[Document]:
        """根据ID获取文档"""
        return db.query(Document).filter(Document.id == doc_id).first()
    
    @staticmethod
    def upload(db: Session, kb_id: UUID, file) -> Document:
        """上传文档"""
        # 检查文件大小
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > settings.MAX_FILE_SIZE:
            raise ValueError(f"文件大小超过限制，最大支持{settings.MAX_FILE_SIZE // 1024 // 1024}MB")
        
        # 保存文件到本地
        kb_path = get_kb_storage_path(kb_id)
        file_path = kb_path / file.filename
        
        # 处理重名文件
        counter = 1
        while file_path.exists():
            name = file.filename.rsplit(".", 1)[0]
            ext = file.filename.rsplit(".", 1)[1] if "." in file.filename else ""
            file_path = kb_path / f"{name}_{counter}.{ext}" if ext else kb_path / f"{name}_{counter}"
            counter += 1
        
        save_upload_file(file, file_path)
        
        # 计算MD5
        md5 = calculate_md5(file_path)
        
        # 检查重复文件
        existing = db.query(Document).filter(
            Document.kb_id == kb_id,
            Document.md5 == md5,
            Document.name == file.filename
        ).first()
        if existing:
            return existing
        
        # 保存文档元数据
        file_type = file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
        doc = Document(
            kb_id=kb_id,
            name=file.filename,
            file_type=file_type,
            size=file_size,
            md5=md5,
            storage_path=str(file_path)
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc
    
    @staticmethod
    def create_process_task(db: Session, kb_id: UUID, task_in: ProcessTaskCreate) -> ProcessTask:
        """创建文档处理任务"""
        # 检查文档都存在
        for doc_id in task_in.document_ids:
            doc = db.query(Document).filter(Document.id == doc_id, Document.kb_id == kb_id).first()
            if not doc:
                raise ValueError(f"文档{doc_id}不存在")
            # 更新文档状态为处理中
            doc.process_status = 1
            db.add(doc)
        
        # 创建任务
        task = ProcessTask(
            kb_id=kb_id,
            document_ids=task_in.document_ids,
            skill_id=task_in.skill_id,
            status=0
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # 提交异步任务
        celery_app.send_task(
            "tasks.process_documents",
            args=[str(task.id)]
        )
        
        return task
    
    @staticmethod
    def get_process_task(db: Session, task_id: UUID) -> Optional[ProcessTask]:
        """获取处理任务状态"""
        return db.query(ProcessTask).filter(ProcessTask.id == task_id).first()
    
    @staticmethod
    def delete(db: Session, doc_id: UUID) -> bool:
        """删除文档"""
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return False
        
        # 删除本地文件
        if doc.storage_path:
            from ..utils.file_utils import delete_file
            delete_file(Path(doc.storage_path))
        
        db.delete(doc)
        db.commit()
        return True
```

- [ ] **步骤 5：编写文档API路由**
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ...database import get_db
from ...schemas.document import DocumentOut, ProcessTaskCreate, ProcessTaskOut
from ...services.document_service import DocumentService
from ...services.knowledge_base_service import KnowledgeBaseService

router = APIRouter(prefix="/document", tags=["文档管理"])

@router.get("/{kb_id}", response_model=List[DocumentOut], summary="获取知识库下的文档列表")
def list_documents(
    kb_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # 检查知识库存在
    kb = KnowledgeBaseService.get(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return DocumentService.list(db, kb_id, skip=skip, limit=limit)

@router.get("/detail/{doc_id}", response_model=DocumentOut, summary="获取文档详情")
def get_document(
    doc_id: UUID,
    db: Session = Depends(get_db)
):
    doc = DocumentService.get(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return doc

@router.post("/upload/{kb_id}", response_model=DocumentOut, summary="上传文档")
def upload_document(
    kb_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 检查知识库存在
    kb = KnowledgeBaseService.get(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    try:
        return DocumentService.upload(db, kb_id, file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败：{str(e)}")

@router.post("/process/{kb_id}", response_model=ProcessTaskOut, summary="创建文档处理任务")
def create_process_task(
    kb_id: UUID,
    task_in: ProcessTaskCreate,
    db: Session = Depends(get_db)
):
    # 检查知识库存在
    kb = KnowledgeBaseService.get(db, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    try:
        return DocumentService.create_process_task(db, kb_id, task_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败：{str(e)}")

@router.get("/process-task/{task_id}", response_model=ProcessTaskOut, summary="获取处理任务状态")
def get_process_task(
    task_id: UUID,
    db: Session = Depends(get_db)
):
    task = DocumentService.get_process_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task

@router.delete("/{doc_id}", summary="删除文档")
def delete_document(
    doc_id: UUID,
    db: Session = Depends(get_db)
):
    success = DocumentService.delete(db, doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {"status": "success", "message": "删除成功"}
```

- [ ] **步骤 6：注册文档路由到v1/__init__.py**
```python
from fastapi import APIRouter
from .knowledge_base import router as kb_router
from .document import router as doc_router

router = APIRouter()
router.include_router(kb_router)
router.include_router(doc_router)
```

- [ ] **步骤 7：编写API测试用例**
```python
import io
def test_upload_document(client, test_kb_id):
    # 创建一个测试文件
    file_content = b"这是测试文件内容"
    file = io.BytesIO(file_content)
    file.name = "test.txt"
    
    response = client.post(
        f"/api/v1/document/upload/{test_kb_id}",
        files={"file": ("test.txt", file, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test.txt"
    assert data["file_type"] == "txt"
    assert data["size"] == len(file_content)
    assert data["process_status"] == 0
    return data["id"]
```

- [ ] **步骤 8：运行测试验证通过**
运行：`pytest tests/test_document_api.py -v`
预期：全部PASS

- [ ] **步骤 9：Commit**
```bash
git add src/ekp_platform/utils/ src/ekp_platform/schemas/document.py src/ekp_platform/services/document_service.py src/ekp_platform/api/v1/document.py tests/test_document_api.py
git commit -m "feat: 文档上传和管理模块开发完成"
```

### 任务 6：Celery配置和基础文档处理任务开发
**文件：**
- 创建：`src/ekp_platform/celery_app.py`
- 创建：`src/ekp_platform/tasks/__init__.py`
- 创建：`src/ekp_platform/tasks/process_tasks.py`
- 创建：`src/ekp_platform/services/process_service.py`
- 测试：`tests/test_process_tasks.py`

**优先级：高 | 工作量：2人天 | 依赖：任务5**

- [ ] **步骤 1：编写Celery应用配置celery_app.py**
```python
from celery import Celery
from celery.schedules import crontab

from .config import settings

celery_app = Celery(
    "ekp",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["ekp_platform.tasks.process_tasks"]
)

# 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 任务超时时间1小时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 定时任务（可选）
celery_app.conf.beat_schedule = {
    # 后续添加清理任务等
}

if __name__ == "__main__":
    celery_app.start()
```

- [ ] **步骤 2：编写文档处理服务process_service.py**
```python
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List
import uuid
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..models import Document, ProcessTask, KnowledgeChunk
from ..clients.volcano_kb_client import volcano_kb_client
from ..config import settings

class ProcessService:
    @staticmethod
    def process_document(db: Session, doc_id: uuid.UUID) -> dict:
        """处理单个文档"""
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return {"status": "failed", "error": "文档不存在"}
        
        try:
            # 1. 加载文档
            loader = UnstructuredFileLoader(doc.storage_path)
            documents = loader.load()
            
            # 2. 文本切块
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            chunks = text_splitter.split_documents(documents)
            
            # 3. 生成向量并存储到火山
            kb_id = str(doc.kb_id)
            volcano_docs = []
            chunk_models = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                # 构造火山文档格式
                volcano_doc = {
                    "Id": chunk_id,
                    "Content": chunk.page_content,
                    "MetaData": {
                        "document_id": str(doc_id),
                        "chunk_index": i,
                        "source": chunk.metadata.get("source", ""),
                        "page_number": chunk.metadata.get("page_number", 0)
                    }
                }
                volcano_docs.append(volcano_doc)
                
                # 保存chunk元数据
                chunk_model = KnowledgeChunk(
                    document_id=doc_id,
                    kb_id=doc.kb_id,
                    volcano_chunk_id=chunk_id,
                    content_hash="",  # 后续可以计算
                    location_info={
                        "chunk_index": i,
                        "page_number": chunk.metadata.get("page_number", 0),
                        "source": chunk.metadata.get("source", "")
                    }
                )
                chunk_models.append(chunk_model)
            
            # 批量插入到火山
            if volcano_docs:
                volcano_kb_client.upsert_documents(kb_id, volcano_docs)
            
            # 批量保存到数据库
            db.bulk_save_objects(chunk_models)
            
            # 更新文档状态
            doc.process_status = 2
            db.add(doc)
            db.commit()
            
            return {
                "status": "success",
                "chunks_count": len(chunks),
                "document_id": str(doc_id)
            }
            
        except Exception as e:
            # 更新文档状态为失败
            doc.process_status = 3
            doc.error_log = str(e)[:1000]  # 只保存前1000字符
            db.add(doc)
            db.commit()
            
            return {"status": "failed", "error": str(e), "document_id": str(doc_id)}
    
    @staticmethod
    def process_documents_task(db: Session, task_id: uuid.UUID) -> None:
        """处理文档任务的核心逻辑"""
        task = db.query(ProcessTask).filter(ProcessTask.id == task_id).first()
        if not task:
            return
        
        # 更新任务状态为执行中
        task.status = 1
        db.add(task)
        db.commit()
        
        total_docs = len(task.document_ids)
        success_count = 0
        failed_count = 0
        results = []
        
        for i, doc_id in enumerate(task.document_ids):
            # 处理文档
            result = ProcessService.process_document(db, doc_id)
            results.append(result)
            
            if result["status"] == "success":
                success_count += 1
            else:
                failed_count += 1
            
            # 更新进度
            task.progress = int((i + 1) / total_docs * 100)
            db.add(task)
            db.commit()
        
        # 更新任务完成
        task.status = 2 if failed_count == 0 else 3
        task.result = {
            "total": total_docs,
            "success": success_count,
            "failed": failed_count,
            "details": results
        }
        db.add(task)
        db.commit()
```

- [ ] **步骤 3：编写Celery任务process_tasks.py**
```python
from celery import shared_task
import uuid
from ..database import SessionLocal
from ..services.process_service import ProcessService

@shared_task(bind=True, name="tasks.process_documents")
def process_documents_task(self, task_id: str):
    """处理文档任务"""
    db = SessionLocal()
    try:
        ProcessService.process_documents_task(db, uuid.UUID(task_id))
    finally:
        db.close()
```

- [ ] **步骤 4：编写任务测试用例**
```python
from unittest.mock import patch
from ekp_platform.tasks.process_tasks import process_documents_task

def test_process_document_task(db_session, test_document):
    with patch.object(ProcessService, 'process_document') as mock_process:
        mock_process.return_value = {"status": "success", "chunks_count": 5}
        
        # 创建处理任务
        from ekp_platform.models import ProcessTask
        import uuid
        
        task = ProcessTask(
            kb_id=test_document.kb_id,
            document_ids=[test_document.id],
            status=0
        )
        db_session.add(task)
        db_session.commit()
        
        # 执行任务
        process_documents_task(str(task.id))
        
        # 验证
        updated_task = db_session.query(ProcessTask).get(task.id)
        assert updated_task.status == 2
        assert updated_task.result["success"] == 1
        assert updated_task.result["total"] == 1
```

- [ ] **步骤 5：运行测试验证通过**
运行：`pytest tests/test_process_tasks.py -v`
预期：PASS

- [ ] **步骤 6：Commit**
```bash
git add src/ekp_platform/celery_app.py src/ekp_platform/tasks/ src/ekp_platform/services/process_service.py tests/test_process_tasks.py
git commit -m "feat: 异步任务和基础文档处理流程开发完成"
```

### 任务 7：知识召回接口开发
**文件：**
- 创建：`src/ekp_platform/schemas/retrieval.py`
- 创建：`src/ekp_platform/services/retrieval_service.py`
- 创建：`src/ekp_platform/api/v1/retrieval.py`
- 测试：`tests/test_retrieval_api.py`

**优先级：高 | 工作量：1.5人天 | 依赖：任务6**

- [ ] **步骤 1：编写召回Schema**
```python
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List, Dict, Any

class RetrievalQuery(BaseModel):
    query: str = Field(..., description="查询文本")
    kb_id: UUID = Field(..., description="知识库ID")
    top_k: int = Field(10, ge=1, le=100, description="返回结果数量")
    similarity_threshold: float = Field(0.0, ge=0.0, le=1.0, description="相似度阈值")
    retrieval_strategy: str = Field("hybrid_parallel", description="检索策略：hybrid_parallel(混合并行)、raw(原始检索)")
    with_entities: bool = Field(False, description="是否返回关联实体")
    vector_weight: float = Field(0.7, ge=0.0, le=1.0, description="向量检索权重")
    keyword_weight: float = Field(0.3, ge=0.0, le=1.0, description="关键词检索权重")

class RetrievalResultItem(BaseModel):
    chunk_id: UUID
    content: str
    similarity: float
    document_id: UUID
    document_name: str
    file_type: Optional[str]
    location_info: Dict[str, Any]
    entities: Optional[List[Dict[str, Any]]] = None

class RetrievalResponse(BaseModel):
    query: str
    total: int
    results: List[RetrievalResultItem]
```

- [ ] **步骤 2：编写召回服务层**
```python
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID

from ..schemas.retrieval import RetrievalQuery, RetrievalResultItem
from ..clients.volcano_kb_client import volcano_kb_client
from ..models import Document, KnowledgeChunk

class RetrievalService:
    @staticmethod
    def hybrid_search(db: Session, query: RetrievalQuery) -> Dict[str, Any]:
        """混合检索：向量+关键词"""
        kb_id = str(query.kb_id)
        
        # 调用火山混合检索
        response = volcano_kb_client.hybrid_search(
            collection_name=kb_id,
            query_text=query.query,
            top_k=query.top_k,
            score_threshold=query.similarity_threshold,
            vector_weight=query.vector_weight,
            keyword_weight=query.keyword_weight
        )
        
        if response.get("Code") != 0:
            raise Exception(f"检索失败：{response.get('Message')}")
        
        volcano_docs = response.get("Result", {}).get("Documents", [])
        
        # 查询对应的元数据
        results = []
        for doc in volcano_docs:
            volcano_chunk_id = doc.get("Id")
            similarity = doc.get("Score")
            content = doc.get("Content", "")
            meta = doc.get("MetaData", {})
            
            # 查询chunk元数据
            chunk = db.query(KnowledgeChunk).filter(
                KnowledgeChunk.volcano_chunk_id == volcano_chunk_id
            ).first()
            
            if not chunk:
                continue
            
            # 查询文档信息
            document = db.query(Document).filter(Document.id == chunk.document_id).first()
            if not document:
                continue
            
            result_item = RetrievalResultItem(
                chunk_id=chunk.id,
                content=content,
                similarity=similarity,
                document_id=document.id,
                document_name=document.name,
                file_type=document.file_type,
                location_info=chunk.location_info or {},
                entities=[] if query.with_entities else None
            )
            results.append(result_item)
        
        return {
            "query": query.query,
            "total": len(results),
            "results": results
        }
    
    @staticmethod
    def raw_search(db: Session, query: RetrievalQuery) -> Dict[str, Any]:
        """原始检索：只返回火山结果，不做额外处理"""
        kb_id = str(query.kb_id)
        
        response = volcano_kb_client.search(
            collection_name=kb_id,
            query_text=query.query,
            top_k=query.top_k,
            score_threshold=query.similarity_threshold
        )
        
        if response.get("Code") != 0:
            raise Exception(f"检索失败：{response.get('Message')}")
        
        return response
    
    @staticmethod
    def search(db: Session, query: RetrievalQuery) -> Dict[str, Any]:
        """统一检索入口"""
        if query.retrieval_strategy == "raw":
            return RetrievalService.raw_search(db, query)
        else:  # 默认 hybrid_parallel
            return RetrievalService.hybrid_search(db, query)
```

- [ ] **步骤 3：编写召回API路由**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas.retrieval import RetrievalQuery, RetrievalResponse
from ...services.retrieval_service import RetrievalService
from ...services.knowledge_base_service import KnowledgeBaseService

router = APIRouter(prefix="/retrieval", tags=["知识检索"])

@router.post("/query", response_model=RetrievalResponse, summary="知识检索接口")
def retrieval_query(
    query: RetrievalQuery,
    db: Session = Depends(get_db)
):
    # 检查知识库存在
    kb = KnowledgeBaseService.get(db, query.kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    try:
        return RetrievalService.search(db, query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败：{str(e)}")

@router.post("/test", summary="检索测试接口（后台使用）")
def retrieval_test(
    query: RetrievalQuery,
    db: Session = Depends(get_db)
):
    # 和query接口逻辑一样，用于后台测试，返回更详细的信息
    return retrieval_query(query, db)
```

- [ ] **步骤 4：注册召回路由到v1/__init__.py**
```python
from fastapi import APIRouter
from .knowledge_base import router as kb_router
from .document import router as doc_router
from .retrieval import router as retrieval_router

router = APIRouter()
router.include_router(kb_router)
router.include_router(doc_router)
router.include_router(retrieval_router)
```

- [ ] **步骤 5：编写API测试用例**
```python
from unittest.mock import patch
def test_retrieval_query(client, test_kb_id):
    with patch.object(volcano_kb_client, 'hybrid_search') as mock_search:
        mock_search.return_value = {
            "Code": 0,
            "Message": "success",
            "Result": {
                "Documents": [
                    {
                        "Id": "test_chunk_id",
                        "Score": 0.92,
                        "Content": "测试内容",
                        "MetaData": {"document_id": "test_doc_id"}
                    }
                ]
            }
        }
        
        response = client.post(
            "/api/v1/retrieval/query",
            json={
                "query": "测试查询",
                "kb_id": str(test_kb_id),
                "top_k": 5,
                "similarity_threshold": 0.6
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "测试查询"
        assert len(data["results"]) >= 0
```

- [ ] **步骤 6：运行测试验证通过**
运行：`pytest tests/test_retrieval_api.py -v`
预期：全部PASS

- [ ] **步骤 7：Commit**
```bash
git add src/ekp_platform/schemas/retrieval.py src/ekp_platform/services/retrieval_service.py src/ekp_platform/api/v1/retrieval.py tests/test_retrieval_api.py
git commit -m "feat: 知识召回接口开发完成"
```

### 任务 8：基础前端页面开发
**文件：**
- 创建：`frontend/` Vue3项目，包含知识库管理、文档管理、检索测试页面
- 更新：`docker-compose.yml` 增加前端服务配置

**优先级：中 | 工作量：2人天 | 依赖：任务7**
（这部分可根据需要调整，前端主要包含三个页面：知识库列表、文档上传管理、检索测试）

### 任务 9：Docker Compose部署脚本开发
**文件：**
- 创建：`Dockerfile` 后端镜像构建
- 创建：`docker-compose.yml` 完整部署配置
- 创建：`.dockerignore` Docker忽略文件

**优先级：中 | 工作量：1人天 | 依赖：任务8**

### 任务 10：整体联调和测试
**优先级：最高 | 工作量：1人天 | 依赖：任务9**
- 全流程测试：上传文档→创建处理任务→等待处理完成→测试检索
- Bug修复和优化
- 文档补充

---

## 三、自检清单
- [ ] 所有第一阶段功能都有对应的实现任务
- [ ] 每个任务都有明确的验收标准和测试用例
- [ ] 所有文件路径、模型字段、API字段都和设计文档一致
- [ ] 任务之间的依赖关系清晰，支持并行开发
- [ ] 没有遗留的TODO或占位符内容
