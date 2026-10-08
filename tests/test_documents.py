# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
from app.kb.documents import Chunk, build_chunks


def test_policy_maps_heading_and_parent_path():
    md = "# 费率政策\n\n## 分期手续费\n\n账单分期每期手续费率0.6%,消费分期每期0.75%,费率以申请页面为准。"
    chunks = build_chunks(md, content_type="policy")
    c = [c for c in chunks if c.questions == "分期手续费"][0]
    assert c.category == "费率政策"
    assert c.section_path == "费率政策 / 分期手续费"
    assert "0.6%" in c.answer
    assert c.content_type == "policy"
    assert c.is_key_clause == 1  # 含「手续费」关键条款


def test_table_section_splits_by_rows_with_header():
    rows = "\n".join(f"| 卡种{i} | {i} |" for i in range(1, 15))
    md = f"# 卡种年费表\n\n## 价目\n\n| 卡种 | 年费 |\n| --- | --- |\n{rows}"
    chunks = build_chunks(md, content_type="manual", table_max_rows=5)
    price = [c for c in chunks if c.questions == "价目"]
    assert len(price) >= 2  # 14 行按 5 切成 >=3 块
    for c in price:
        assert c.answer.startswith("| 卡种 | 年费 |")  # 每块复制表头


def test_returns_chunk_dataclass():
    chunks = build_chunks("# A\n\n## B\n\n正文。", content_type="faq")
    assert isinstance(chunks[0], Chunk)
