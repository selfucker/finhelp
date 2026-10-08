-- =============================================================
-- ch03 · 合成历史客服对话(喂挖知识 job)。三段式 + SET NAMES utf8mb4 + 幂等。
-- =============================================================
SET NAMES utf8mb4;

-- 段1 查询:执行前 seed 会话数
SELECT COUNT(*) AS before_conv FROM conversations WHERE user_id LIKE 'seed-%';

-- 段2 写入:先幂等清理 seed-% 会话及其消息,再插入
DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id LIKE 'seed-%');
DELETE FROM conversations WHERE user_id LIKE 'seed-%';

INSERT INTO conversations (user_id, status) VALUES ('seed-u1', '已结束'), ('seed-u2', '已结束');
SET @c1 = (SELECT id FROM conversations WHERE user_id = 'seed-u1' ORDER BY id DESC LIMIT 1);
SET @c2 = (SELECT id FROM conversations WHERE user_id = 'seed-u2' ORDER BY id DESC LIMIT 1);

INSERT INTO messages (conversation_id, role, content) VALUES
  (@c1, 'user',      '你们还款一般多久到账啊'),
  (@c1, 'assistant', '本行 App 与借记卡还款一般实时到账,跨行转账与第三方渠道到账时间以渠道为准,建议还款日前 1-2 个工作日操作。'),
  (@c2, 'user',      '分期手续费怎么算'),
  (@c2, 'assistant', '账单分期每期手续费率 0.6%,消费分期每期 0.75%,费率与期数以申请页面为准。');

-- 段3 验证:seed 会话应为 2,消息应为 4
SELECT COUNT(*) AS after_conv FROM conversations WHERE user_id LIKE 'seed-%';
SELECT COUNT(*) AS after_msg FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id LIKE 'seed-%');
