# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
# 注：金融域改造 —— 订单→交易/账单，product→merchant，tracking_no→bill_ref。
"""mock 数据源(纯函数,随机种子固定 → 同键稳定)。
ch08 起工具实现迁至 app/tools/builtin/(注册即定义),本模块只留被 graph 节点
(fetch_order)与 builtin 工具共用的快照函数,不再定义任何 @tool。"""
import random


def order_snapshot(order_id: str) -> dict:
    """交易快照(纯函数,随机种子固定 → 同 order_id 稳定)。query_transaction 工具与 fetch_order 节点同源。"""
    rng = random.Random(f"order:{order_id}")
    return {
        "order_id": order_id,
        "status": rng.choice(["已入账", "待入账", "已撤销", "争议中"]),
        "amount": rng.randint(50, 5000),
        "created_at": f"2026-07-{rng.randint(1, 12):02d} 10:00",
        "merchant": rng.choice(["商超消费", "餐饮消费", "加油消费", "线上订阅"]),
        "bill_ref": f"TX{rng.randint(10**11, 10**12 - 1)}",
    }


def owns_order(user_id: str, order_id: str) -> bool:
    """这一笔交易是不是这个人的。归属判断只有这一处,工具和节点都调它,不各判各的。

    空 user_id 一律不放行:身份是注入进来的,注入没接上就是空串,那种情况下放行等于没做校验。"""
    if not user_id or not order_id:
        return False
    return any(o["order_id"] == order_id for o in list_user_orders(user_id))


# 课程演示单。文档、curl 例子、各章验收脚本里到处写着 1001 和 2002,让每个账号名下都有
# 这两笔,例子拿来即跑。想看归属校验拦人,随便报一个别的号(如 9999)就会被挡下。
DEMO_ORDER_IDS = ("1001", "2002")


def list_user_orders(user_id: str) -> list[dict]:
    """按 user_id 稳定列出该用户的交易(mock,不落库):两笔演示单 + 2-4 笔随机单。
    每笔用 order_snapshot 同源,前端选中后回填 order_id 即可 query_transaction。"""
    rng = random.Random(f"user_orders:{user_id}")
    ids = list(DEMO_ORDER_IDS)
    for _ in range(rng.randint(2, 4)):
        oid = str(rng.randint(1000, 9999))
        if oid not in ids:
            ids.append(oid)
    out = []
    for oid in ids:
        s = order_snapshot(oid)
        out.append({"order_id": oid, "merchant": s["merchant"],
                    "status": s["status"], "amount": s["amount"]})
    return out
