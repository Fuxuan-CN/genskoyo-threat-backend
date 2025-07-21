""" exception hook """

import traceback
import multiprocessing
import threading
import inspect
import sys
from .logger import logger

def format_stack_trace(exctype, value, tb, max_depth=30, nested=False) -> list[str]:
    tb_list = traceback.extract_tb(tb)
    exception_info = []

    if nested:
        exception_info.append(f"{exctype.__name__}: {value}\n")
    else:
        # 获取当前进程和线程名称
        process_name = multiprocessing.current_process().name
        thread_name = threading.current_thread().name
        exception_info.append(
            f"Exception in process: {process_name}, thread: {thread_name}; {exctype.__name__}: {value}",
        )
        exception_info.append("Traceback (most recent call last):")

    # 限制堆栈跟踪的深度
    limited_tb_list = tb_list[:max_depth]
    more_frames = len(tb_list) - max_depth

    for i, (filename, lineno, funcname, line) in enumerate(limited_tb_list):
        # 获取函数所在的模块名
        module_name = inspect.getmodulename(filename)
        exception_info.append(
            f"  at {module_name}.{funcname} in ({filename}:{lineno})",
        )

    if more_frames > 0:
        exception_info.append(f"  ... {more_frames} more ...")

    # 检查是否有原因和其他信息
    cause = getattr(value, '__cause__', None)
    context = getattr(value, '__context__', None)
    
    if cause:
        exception_info.append("Caused by: ")
        exception_info.append(format_stack_trace(type(cause), cause, cause.__traceback__, nested=True))
    if context and not cause:
        exception_info.append("Original exception: ")
        exception_info.append(format_stack_trace(type(context), context, context.__traceback__, nested=True))
    
    return exception_info

def ExtractException(exctype, value, tb) -> list[str] | None:
    # 获取回溯信息并格式化为字符串
    if all(x is None for x in (exctype, value, tb)):
        return None
    
    tb_str = format_stack_trace(exctype, value, tb)

    return tb_str

def sys_excepthook(exctype, value, tb):
    # 获取异常信息并打印到控制台
    exception_info = ExtractException(exctype, value, tb)
    if exception_info:
        logger.error("发生了致命错误：")
        for exception_element in exception_info:
            logger.critical(exception_element)

def set_exechook():
    """
    设置全局异常处理函数
    """
    logger.debug("异常钩子设置完成")
    sys.excepthook = sys_excepthook

def GetStackTrace(vokedepth: int = 1) -> str:
    """
    获取堆栈跟踪信息
    """
    # 获取当前调用栈信息的前两层
    stack = traceback.extract_stack(limit=vokedepth)
    stack_info = "Stack Trace:\n"
    for frame in stack[:-vokedepth+1]:
        filename = frame.filename
        line = frame.lineno
        funcname = frame.name
        stack_info += f"  at {funcname} in ({filename}:{line})\n"
    return stack_info

if __name__ == '__main__':
    
    set_exechook()
