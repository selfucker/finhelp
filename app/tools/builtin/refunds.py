# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
# 注：金融域改造 —— submit_refund → submit_dispute（争议申诉）。
from typing import Annotated

from langchain_core.tools import InjectedToolArg, tool
from pydantic import Field

from app.tools import registry
from app.tools.builtin.orders import NOT_OWNED
from app.tools.business import owns_order


@tool
async def submit_dispute(
    txn_id: Annotated[str, Field(description="要发起争议申诉的交易号")],
    user_id: Annotated[str, InjectedToolArg],
    reason: Annotated[str | None, Field(description="申诉原因(可选,最终以前端固定类目下拉为准)")] = None,
) -> dict:
    """判定这一笔交易可以发起争议申诉后,调用本工具发起申诉。实际提交由前端表单确认后落库,
    本工具只表示『这一笔可以申诉,已把提交入口交给用户』。
    发起人身份由系统注入,你不要传 user_id。"""
    # 写操作有二次确认门,但那道门确认的是「要不要申诉」,不是「这笔是不是你的」,归属得单独校验
    if not owns_order(user_id, txn_id):
        return dict(NOT_OWNED)
    return {"status": "待用户确认", "txn_id": txn_id}


registry.register(registry.spec_from_langchain_tool(
    submit_dispute, source="builtin", inject_user_id=True))
