# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
# 注：金融域改造 —— 物流 Server → 账务核心 Server；query_logistics → query_bill_status。
"""账务核心 MCP Server(ch08 自建,mock 数据,不接真实系统、不建表)。
独立进程:uv run python mcp_servers/logistics_server.py
工具:query_bill_status(查账单状态/应还/最低还款/到期日)。
实装 mcp==1.28.1:FastMCP(name, host=, port=) + run(transport="streamable-http"),路径默认 /mcp。"""
import asyncio
import os
import random
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("billing",
              host="127.0.0.1", port=int(os.environ.get("PORT", "8101")))

_DELAY = float(os.environ.get("MOCK_DELAY_SECONDS", "0"))
_STATUS_CODES = ["BILL_UNPAID", "BILL_PARTIAL", "BILL_PAID", "BILL_OVERDUE"]  # 内部枚举码,client 侧翻人话


@mcp.tool()
async def query_bill_status(
    bill_ref: Annotated[str, Field(description="账单参考号(形如 TX 开头),需先用 query_transaction 查交易拿到该参考号")],
) -> dict:
    """用账单参考号(bill_ref)查询账单状态、应还金额、最低还款和到期日。用于用户询问账单/还款情况时。
    账单参考号不是交易号,需先用 query_transaction 查交易拿到 bill_ref,再调用本工具。"""
    if _DELAY > 0:
        await asyncio.sleep(_DELAY)
    rng = random.Random(f"bill:{bill_ref}")      # 种子固定 → 同参考号稳定
    code = rng.choice(_STATUS_CODES)
    return {
        "bill_ref": bill_ref,
        "status_code": code,                              # 内部枚举码,Server 侧不翻译,交 client 侧治理
        "amount_due": rng.randint(50, 30000),
        "min_payment": rng.randint(50, 3000),
        "due_date": f"2026-{rng.randint(8, 12):02d}-{rng.randint(1, 28):02d}",
        "policy_ref": "BILL-POLICY-01",                   # 内部政策编号(回答用不上,client 侧应剔除)
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
