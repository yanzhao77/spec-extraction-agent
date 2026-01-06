"""
ModelScope创空间启动文件
用于在ModelScope平台上部署和运行工程规范文档结构化抽取Agent API服务
"""

import os
import uvicorn

# 导入FastAPI应用
from src.api_server import app

if __name__ == "__main__":
    # 获取端口配置，ModelScope默认使用7860端口
    port = int(os.getenv("PORT", 7860))
    
    # 启动FastAPI服务
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
