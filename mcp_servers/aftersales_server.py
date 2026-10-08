# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
# 注：金融域改造 —— 售后 Server → 风控与争议 Server；query_warranty/query_return_status → query_risk_level/query_dispute_status。
"""风控与争议 MCP Server(ch08 自建,mock 数据,不接真实系统、不建表)。
独立进程:uv run python mcp_servers/aftersales_server.py
工具:query_risk_level(查风险等级与止付建议)、query_dispute_status(查争议进度)。
MOCK_DELAY_SECONDS 同账务 Server,可注入延迟演示超时。"""
import asyncio
import os
import random
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("riskcontrol",
              host="127.0.0.1", port=int(os.environ.get("PORT", "8102")))

_DELAY = float(os.environ.get("MOCK_DELAY_SECONDS", "0"))


@mcp.tool()
async def query_risk_level(
    customer_id: Annotated[str, Field(description="客户标识,例如 u1")],
) -> dict:
    """查询某客户账户的风险等级与是否需止付。用于用户问盗刷、账户风险、能否冻结时。"""
    if _DELAY > 0:
        await asyncio.sleep(_DELAY)
    rng = random.Random(f"risk:{customer_id}")
    code = rng.choice(["RISK_LOW", "RISK_HIGH"])          # 内部枚举码,client 侧翻人话
    return {"customer_id": customer_id, "risk_code": code,
            "need_freeze": code == "RISK_HIGH",
            "advice_ref": "RISK-ADVICE-01"}                # 内部建议编号(回答用不上,client 侧应剔除)


@mcp.tool()
async def query_dispute_status(
    dispute_no: Annotated[str, Field(description="争议单号,例如 1001")],
) -> dict:
    """查询某笔争议的处理进度(受理中/调查中/已退款/已驳回/无争议记录)。用于用户问申诉到哪一步了。"""
    if _DELAY > 0:
        await asyncio.sleep(_DELAY)
    rng = random.Random(f"dispute:{dispute_no}")
    code = rng.choice(["INVESTIGATING", "RESOLVED_REFUNDED", "REJECTED", "NONE"])
    return {"dispute_no": dispute_no, "dispute_code": code,
            "updated_at": f"2026-07-{rng.randint(1, 16):02d} 10:00"}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
