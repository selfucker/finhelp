# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
from typing import Literal

from pydantic import BaseModel, Field


class CreateTicketRequest(BaseModel):
    conversation_id: int
    description: str = Field(min_length=1)
    ticket_type: Literal["账务", "投诉", "咨询"]


class CreateTicketResponse(BaseModel):
    ticket_no: str
    status: str = "已转人工"


class CreateRefundRequest(BaseModel):
    conversation_id: int
    txn_id: str = Field(min_length=1)
    reason: Literal["重复扣款", "非本人交易", "金额不符", "商户争议", "其他"]


class CreateRefundResponse(BaseModel):
    ticket_no: str
    status: str = "争议申诉已提交"


class ResumeRequest(BaseModel):
    conversation_id: int
    order_id: str | None = Field(default=None, min_length=1)   # ch06 交易选择器点选
    confirmed: bool | None = None                              # ch08 工单预览 确认/取消
