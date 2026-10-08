# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
import logging

from app.tools import mcp_client, registry
from app.tools.registry import ToolSpec


class _FakeTool:
    def __init__(self, name):
        self.name = name
        self.description = f"{name} 描述"
        self.args_schema = {"type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"]}


async def test_fetch_mcp_specs_marks_source_and_permission(monkeypatch):
    async def fake_get_tools(*, server_name=None):
        return [_FakeTool("query_bill_status")] if server_name == "billing" else [_FakeTool("query_risk_level")]
    monkeypatch.setattr(mcp_client, "_get_tools_of", fake_get_tools)
    specs = await mcp_client.fetch_mcp_specs()
    by = {s.name: s for s in specs}
    assert set(by) == {"query_bill_status", "query_risk_level"}
    assert by["query_bill_status"].source == "mcp" and by["query_bill_status"].mcp_server == "billing"
    assert all(s.permission == "read" for s in specs)          # 我们侧规则:MCP 不在写清单→只读
    assert by["query_bill_status"].format_result is mcp_client.FORMATTERS["query_bill_status"]


async def test_one_server_down_degrades_gracefully(monkeypatch, caplog):
    async def fake_get_tools(*, server_name=None):
        if server_name == "billing":
            raise ConnectionError("拒绝连接")
        return [_FakeTool("query_risk_level")]
    monkeypatch.setattr(mcp_client, "_get_tools_of", fake_get_tools)
    with caplog.at_level(logging.WARNING):
        specs = await mcp_client.fetch_mcp_specs()
    assert {s.name for s in specs} == {"query_risk_level"}       # 单台挂了跳过,不拖垮
    assert any("不可达" in r.message for r in caplog.records)


async def test_get_all_specs_merges_builtin_wins(monkeypatch):
    async def fake_fetch():
        return [ToolSpec(name="query_transaction", description="MCP 冒名",
                         json_schema={"type": "object", "properties": {}},
                         tool=_FakeTool("query_transaction"), permission="read", source="mcp", mcp_server="x"),
                ToolSpec(name="query_bill_status", description="账单",
                         json_schema={"type": "object", "properties": {}},
                         tool=_FakeTool("query_bill_status"), permission="read", source="mcp",
                         mcp_server="billing")]
    monkeypatch.setattr(mcp_client, "fetch_mcp_specs", fake_fetch)
    specs = await registry.get_all_specs()
    by = {s.name: s for s in specs}
    assert by["query_transaction"].source == "builtin"               # 重名 builtin 优先,后到 MCP 丢弃
    assert by["query_bill_status"].source == "mcp"               # 账单由 MCP 接管
    assert {"query_faq", "create_ticket", "submit_dispute", "query_rate_policy"} <= set(by)


def test_bill_status_formatter_translates_codes():
    out = mcp_client.FORMATTERS["query_bill_status"](
        {"bill_ref": "TX1", "status_code": "BILL_OVERDUE", "amount_due": 1000,
         "min_payment": 100, "due_date": "2026-08-05", "policy_ref": "BILL-POLICY-01"})
    assert out == {"bill_ref": "TX1", "status": "已逾期", "amount_due": 1000,
                   "min_payment": 100, "due_date": "2026-08-05"}            # 挑字段 + 枚举翻人话,内部编码剔除
