# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ExtractRequest(BaseModel):
    text: str = Field(min_length=1, description="用户的争议/账务描述原文")


class RequestType(str, Enum):
    DISPUTE_REFUND = "争议退款"
    BILL_ADJUST = "账务调整"
    COMPLAINT = "投诉"
    OTHER = "其他"


class DisputeTicket(BaseModel):
    """从用户争议/账务描述中提取的结构化工单。"""

    txn_id: str | None = Field(
        default=None, description="交易号,原文未出现则为 null,禁止编造"
    )
    request_type: RequestType = Field(description="用户诉求类型")
    expected_solution: str = Field(description="用户期望的处理方案,一句话概括")

    @field_validator("txn_id", mode="before")
    @classmethod
    def _normalize_missing_txn_id(cls, v: object) -> object:
        # 模型偶尔把"没有交易号"表达成占位字符串而非省略参数,统一归一为 None
        if isinstance(v, str) and v.strip().lower() in {"", "null", "none", "n/a", "无"}:
            return None
        return v
