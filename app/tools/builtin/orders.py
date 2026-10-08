# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
# 注：金融域改造 —— query_order → query_transaction，query_product → query_rate_policy。
import random
from typing import Annotated

from langchain_core.tools import InjectedToolArg, tool
from pydantic import Field

from app.tools import registry
from app.tools.business import order_snapshot, owns_order

# 查不到和不是本人的交易回同一句话。分开回就成了枚举 oracle:攻击者靠回答差异
# 就能挨个试出哪些交易号真实存在。
NOT_OWNED = {"error": "没有找到您的这笔交易", "code": "order_not_owned"}


@tool
async def query_transaction(
    txn_id: Annotated[str, Field(description="交易号,例如 1001")],
    user_id: Annotated[str, InjectedToolArg],
) -> dict:
    """查询某笔交易的状态、金额、发生时间、商户和账单参考号(bill_ref)。用于用户询问某笔交易情况时。
    要查账单状态/争议进度,需先用本工具拿到交易号对应的 bill_ref,再把它传给 query_bill_status。
    发起人身份由系统注入,你不要传 user_id。"""
    if not owns_order(user_id, txn_id):
        return dict(NOT_OWNED)
    return order_snapshot(txn_id)


@tool
async def query_rate_policy(
    policy_key: Annotated[str, Field(description="费率/规则关键词,例如 分期手续费")],
) -> dict:
    """查询费率、年费、积分等规则细节。用于用户咨询某类费用怎么算、有什么规则时。"""
    rng = random.Random(f"policy:{policy_key}")
    return {
        "policy_key": policy_key,
        "rate": f"{rng.uniform(0.05, 24.0):.2f}%",
        "basis": rng.choice(["按笔", "按期", "按年", "按日"]),
        "note": "具体以银行官方口径为准",
    }


registry.register(registry.spec_from_langchain_tool(
    query_transaction, source="builtin", inject_user_id=True))
registry.register(registry.spec_from_langchain_tool(query_rate_policy, source="builtin"))
