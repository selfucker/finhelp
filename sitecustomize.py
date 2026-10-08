# Python 启动即执行的环境清理钩子（sitecustomize，仅本项目目录在 sys.path 上时加载）。
#
# 背景：这台机器的进程环境里 NO_PROXY 含非法值 "[::1]"（且大小写重复），httpx
# 0.28+ 会把 no_proxy 列表里的每一项解析成 URLPattern，"[::1]" 被当成 host:port →
# 端口 ":1]" 非法 → langchain-openai/openai SDK 初始化时抛
#   httpx.InvalidURL: Invalid port: ':1]'
#
# 上游（DeepSeek / 硅基流动）都是国内服务、本就不需要代理。这里在解释器启动时把
# NO_PROXY 改成 "*"（httpx 语义：不经过任何代理，直连），一劳永逸。
# 项目各 make 目标均设 PYTHONPATH=.，故本项目运行任何 python 时都会自动生效。
import os

try:
    os.environ["NO_PROXY"] = "*"
except Exception:  # noqa: BLE001 —— 环境清理失败不应阻断启动
    pass
