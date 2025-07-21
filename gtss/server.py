
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from .routers import GTSS
from .logger import logger
from .database import init_database_factory
from .exec_hook import ExtractException
from contextlib import asynccontextmanager

@asynccontextmanager
async def gtdb_lifespan(app: FastAPI):
    try:
        logger.debug(f"初始化并启动...")
        await init_database_factory()
        logger.success("初始化成功，程序正式启动!")
        yield
    finally:
        logger.info("服务器关闭...")
        pass

APPLICATION = FastAPI(title="GTSS 幻想乡威胁评估系统", version="1.1", lifespan=gtdb_lifespan)

APPLICATION.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应替换为具体前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@APPLICATION.get("/")
async def echo() -> str:
    """ 测试服务是否正在运行 """
    return "if you see this message, that means the gtss server is running."

@APPLICATION.exception_handler(Exception)
async def exception_handler(req: Request, exc: Exception) -> JSONResponse:
    """ 异常处理器 """
    exc_stack = ExtractException(type(exc), exc, exc.__traceback__)
    for err in exc_stack if exc_stack else []:
        if isinstance(err, str):
            logger.error(err)
        if isinstance(err, list):
            for e in err:
                logger.error(e)
    return JSONResponse(content="哦不，看来我们发生了一些错误，稍等，已经通知管理员！", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

APPLICATION.include_router(GTSS)

def run(host: str = "localhost", port: int = 8000) -> None:
    """ 运行服务 """
    link = fr"http://{host}:{port}"
    logger.debug(f"程序将运行再: {link}")
    uvicorn.run(APPLICATION, host=host, port=port, log_level="critical")

if __name__ == "__main__":
    run()