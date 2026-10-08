# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
# 注：金融域改造 —— 九类意图与样例换成 FinHelp 语义。
"""意图四件套标注评估:九类判对率 + confidence 可解析 + 怪问题落其他 + 多轮漂移。需聊天上游可调通。
用法:.venv/bin/python -m scripts.eval_intent"""
import asyncio

from app.core.intent import classify

SAMPLES = [
    ("这笔2002的交易现在什么状态", "账务查询"), ("我上个月消费了多少钱来着", "账务查询"),
    ("分期手续费怎么算", "业务咨询"), ("年费能减免吗", "业务咨询"),
    ("我要对这笔交易发起申诉", "争议申诉"), ("这笔重复扣款能退款吗", "争议申诉"),
    ("账单多扣了一笔帮我改", "账务调整"), ("这笔金额不对要冲正", "账务调整"),
    ("我的卡丢了怎么挂失", "卡片与安全"), ("账户能冻结吗", "卡片与安全"),
    ("你们这什么破服务,我要投诉", "投诉"), ("太差了给我个说法", "投诉"),
    ("帮我建个工单", "人工"), ("账户被盗刷了,帮我建个工单跟进", "人工"),
    ("你好呀", "闲聊"), ("今天天气不错", "闲聊"),
    ("帮我写一段 Python 代码", "其他"), ("阿斯顿发发", "其他"),
]

_FIN_INTENTS = ("账务查询", "业务咨询", "争议申诉", "账务调整", "卡片与安全",
                "投诉", "人工", "闲聊", "其他")


async def main():
    passed = bad_json = 0
    for q, expect in SAMPLES:
        r = await classify(q)
        got = r.get("intent")
        conf = r.get("confidence")
        ok = got == expect
        json_ok = got in _FIN_INTENTS and isinstance(conf, float) and 0.0 <= conf <= 1.0
        bad_json += not json_ok
        passed += ok
        print(f"{'✅' if ok else '❌'} {q!r} -> {got}(conf={conf}) 期望={expect}")

    # 多轮漂移:账务查询→争议申诉,当前句意图应随上下文
    hist = "用户:交易1001现在什么状态\n客服:已入账,商户为商超消费\n用户:那我想申诉这笔\n客服:好的,帮您看下争议规则\n"
    r = await classify("那需要我提供什么", hist)
    print(f"多轮漂移『那需要我提供什么』(争议后)-> {r['intent']}(期望 争议申诉)")

    print(f"\n判对 {passed}/{len(SAMPLES)};JSON 越界 {bad_json} 条(非确定性,抖动如实重跑记录)")


if __name__ == "__main__":
    asyncio.run(main())
