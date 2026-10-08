# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
# 注：本文件已按「FinHelp 银行/信用卡客服」改造，类目体系为金融域 17 类。
"""ch10 权威归并术语表:全系统唯一一份,17 类主题类目(金融域)。
数据处理、预标、训练、推理、评测、前端全部 import 这里,不许各自抄一份。
类目名与边界说明采用 FinHelp 归并术语表;元组顺序即 label id,训练/推理共用。
severity 是容错档位:归错会带偏补知识优先级的类目从严。"""
from dataclasses import dataclass


@dataclass(frozen=True)
class TopicClass:
    name: str
    boundary: str                 # 一句边界说明:什么算这一类,近邻类目靠它划开
    examples: tuple[str, ...]     # 用户的说法示例
    severity: str                 # 容错档位:严 / 中 / 宽


TOPIC_CLASSES: tuple[TopicClass, ...] = (
    TopicClass("账单查询", "账单金额、账单日、应还明细;还款动作归还款",
               ("这期账单怎么这么多", "账单日是哪天", "应还多少", "明细在哪看"), "严"),
    TopicClass("还款", "还款方式、到账时间、最低还款、逾期处理",
               ("还款没到账", "最低还款是多少", "晚还会怎样", "能提前还款吗"), "严"),
    TopicClass("分期", "账单分期、消费分期、手续费",
               ("想分12期", "分期手续费多少", "能提前结清吗", "分期怎么取消"), "严"),
    TopicClass("额度", "固定额度、临时额度、调额",
               ("想提额", "临时额度怎么申请", "额度不够用", "额度被降了"), "严"),
    TopicClass("费率利率", "循环利息、取现费、违约金怎么算",
               ("利息怎么算的", "取现手续费多少", "违约金怎么收", "日息是多少"), "严"),
    TopicClass("年费", "年费收取与减免规则",
               ("年费能免吗", "为什么扣了年费", "首年免年费吗"), "严"),
    TopicClass("争议拒付", "盗刷、重复扣款、商户争议、拒付申诉",
               ("有笔不是我刷的", "重复扣款了", "要申诉这笔交易", "能拒付吗"), "严"),
    TopicClass("反诈安全", "诈骗识别、止付冻结、信息保护",
               ("接到自称客服的电话", "卡被盗刷怎么办", "能冻结账户吗", "验证码能说吗"), "严"),
    TopicClass("卡片挂失", "挂失、补卡、邮寄、激活",
               ("卡丢了怎么挂失", "补卡要多久", "新卡怎么激活", "挂失能撤销吗"), "严"),
    TopicClass("积分权益", "积分累计与兑换、权益等级",
               ("积分怎么换", "权益在哪看", "积分会过期吗", "积分能抵年费吗"), "中"),
    TopicClass("优惠活动", "满减、立减金、活动规则",
               ("立减金怎么用", "活动能叠加吗", "满减规则是什么", "活动什么时候结束"), "中"),
    TopicClass("开卡销卡", "申请、进度、销户",
               ("卡怎么销", "申请进度查不到", "能办第二张吗", "销户影响征信吗"), "中"),
    TopicClass("征信记录", "征信上报、异议、征信报告",
               ("逾期会上征信吗", "征信怎么查", "记录能改吗", "征信有异议怎么办"), "中"),
    TopicClass("转账汇款", "转账限额、到账时间、失败处理",
               ("转账限额多少", "转错了怎么办", "什么时候到账", "跨境能转吗"), "中"),
    TopicClass("理财基金", "产品咨询、申赎、风险等级",
               ("这个产品保本吗", "赎回几天到账", "风险等级怎么看", "能定投吗"), "中"),
    TopicClass("账户信息", "手机号/地址变更、账户状态",
               ("换手机号了", "账户被冻结", "怎么改地址", "密码忘了"), "宽"),
    TopicClass("其他", "上面都对不上的,先兜底",
               ("闲聊", "转人工", "客服几点上班"), "宽"),
)

TOPIC_NAMES: tuple[str, ...] = tuple(c.name for c in TOPIC_CLASSES)
LABEL2ID: dict[str, int] = {name: i for i, name in enumerate(TOPIC_NAMES)}
ID2LABEL: dict[int, str] = {i: name for i, name in enumerate(TOPIC_NAMES)}
NUM_CLASSES = len(TOPIC_CLASSES)
SEVERITY: dict[str, str] = {c.name: c.severity for c in TOPIC_CLASSES}


def terminology_table() -> str:
    """预标/造数 prompt 用的术语表文本:类目:边界说明(示例)。"""
    return "\n".join(
        f"- {c.name}:{c.boundary}(示例:{'、'.join(c.examples)})" for c in TOPIC_CLASSES
    )
