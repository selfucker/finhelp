# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
from app.tools import business
from app.tools.builtin.orders import query_transaction, query_rate_policy

USER = "u-mock"
MINE = business.list_user_orders(USER)[0]["order_id"]   # 这个用户名下真实存在的一笔交易

# ch08:query_bill_status 内置版下线,账单查询由账务 MCP Server 接管(见 tests/tools/test_mcp_servers.py)


async def test_query_transaction_deterministic_and_shaped():
    # ch08:身份由执行引擎注入,查自己的交易才有数据(归属校验见 tests/tools/test_order_ownership.py)
    r1 = await query_transaction.ainvoke({"txn_id": MINE, "user_id": USER})
    r2 = await query_transaction.ainvoke({"txn_id": MINE, "user_id": USER})
    assert r1 == r2                                  # 同种子可复现
    assert r1["order_id"] == MINE
    assert r1["status"] in {"已入账", "待入账", "已撤销", "争议中"}
    assert r1["bill_ref"].startswith("TX")           # 账单参考号,查账单需先拿它


async def test_query_rate_policy_names_and_determinism():
    assert query_transaction.name == "query_transaction"
    assert query_rate_policy.name == "query_rate_policy"
    p1 = await query_rate_policy.ainvoke({"policy_key": "分期手续费"})
    p2 = await query_rate_policy.ainvoke({"policy_key": "分期手续费"})
    assert p1 == p2                                   # 同种子可复现
    assert p1["policy_key"] == "分期手续费" and "rate" in p1
