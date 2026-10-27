# 出海匠画布 / 开放平台的坑（2026-10-21～22 实测）

脚本 `scripts/chj.py` 已封装大部分处理；手写调用时照这里做。

| 现象 | 处理 |
| --- | --- |
| 画布网页开着时，API 写入被网页覆盖（新建的节点消失、删掉的被写回、状态被改成 submit_interrupted） | 每次 apply 后等 15 秒读回核对，不对就重写（`Canvas.apply(build_ops, check)`）；生成前确认节点还在 |
| apply 返回 409 | 版本冲突：重读画布、按最新内容重算操作再写 |
| 网络偶发 `SSL EOF` | 重试；失败发生在读取时不会有副作用 |
| 视频任务完成但节点一直 running、不挂素材 | batch-detail 取 `result.data[0]` 的 os_bucket / os_key，`attach_asset`（origin generation，source kind task + sourceTaskId）补挂；网页打开后状态会自己刷新 |
| 对失败（超时）的节点再调 generate | 服务端会另建一个 `gen_X-attempt-…` 节点并返回旧任务号，不会真重出 → 不在原节点重提，新建下一个编号的候选节点 |
| 被用户打断 / 被拒的工具调用 | 可能已在服务端执行：先读画布和 state.json，已有 taskId 就认领，不重复提交 |
| 并发 | Seedance 2.5 上限 4，服务端计数有延迟，一次最多交 3 个视频候选；图片限流 10 次/分钟，间隔 ≥7 秒 |
| 参考图编号 | `generation.inputs` 顺序 = 连线添加顺序；先连的是图片1 |
| 下载地址 | 图片、视频都在 batch-detail 的 `result.data[0].url` |
| GPT-Image-2 比例 | 只认 1:1 / 9:16 / 16:9；传别的比例不报错但出 1024 方图并照扣费 |
| 删除节点 | 先 `share_snapshot()`（分享快照可克隆恢复），本地文件移到 `_不用/`，不真删；用户没说删就不删 |
| 费用 | 公司承担，不报费用、不为省钱串行；每段 2 个候选并行（2026-10-23 起不再出 3 个） |
| 后台任务 | 长轮询用 run_in_background；不要在前台命令里用 `&` 挂起（命令结束进程可能被杀，也收不到完成通知） |
