---
name: restaurant-drama
description: 餐馆剧情 skill —— Naturestaurant（NRT）纯 AI 剧情短视频的融合流程，任何题材都适用（恐怖、喜剧、温情、悬疑、科幻、产品广告等）：外壳管流程关口、时长约束、提示词框架格式（Solis 中文逐镜头）、配乐延续/转折判断、品牌名念法和出海匠画布脚本；内功（编剧、光影、镜头、调度、衔接、声音、产品动作、质检）用速查表 + 收录的 DirectorSKILL、seedance-tvc-director 原文和本机小逻 skill。用户说「餐馆剧情」「抓马视频」「做一条 NRT 剧情片 / AI 样片」「按吸血鬼那条的做法」时使用；只出脚本点子也先看第 1 阶段。纯录屏讲解、数字人口播、图文不走这个 skill。
---

# 餐馆剧情（融合版）

**分工**：本 skill 是外壳，只规定「按什么顺序做、每段多长、提示词长什么样、哪些项目规则不能破」；**拍得好不好看的内容规则全部读原文**——`references/routing.md` 列了每个阶段读哪份。冲突时按 routing.md 的优先级：用户 > 外壳 > 外部原文 > 我的默认。

| 文件 | 管什么 |
| --- | --- |
| `references/quick-ref.md` | 通用速查表：光影、镜头、调度表演、衔接、声音、产品动作、出问题时，每条标原文出处；日常先看这份 |
| `references/routing.md` | 阶段 → 外部原文路由表、优先级、已知冲突裁决 |
| `references/prompt-rules.md` | 视频 / 图片提示词框架、时长约束、配乐延续/转折、品牌念法、真实性 |
| `references/canvas-pitfalls.md` | 出海匠画布和开放平台的坑 |
| `vendor/DirectorSKILL/`、`vendor/seedance-tvc-director/` | 收录的原文（MIT） |
| 小逻 | 本机 `~/Downloads/AI视频制作-skill与流程包/3-skills/外部-GitHub/XiaoLuo-AI-Drama-Skill/`（未声明许可，只引用不复制） |
| `scripts/` | 画布搭建 / 生成 / 动线标注 / 审片 / 粗剪 |

样板：P04 吸血鬼叉子（`assets/P04-吸血鬼叉子/project.json`、`timeline_v2.json`，分镜 `content/分镜/P04-吸血鬼叉子-分镜.md`）；光影样板：V07 婚礼（`content/分镜/V07-设定集.md`、`V07-提示词.md`）。复盘：`knowledge/07-AI视频制作复盘.md`。项目规则仍以 `CLAUDE.md` 为准。

## 阶段与关口

每阶段做完、用户确认（或用户说了「自己做完别问我」）才进下一阶段。**改了前面的设定，回头同步所有依赖它的提示词和分镜。** 每阶段先按 routing.md 读对应原文，再动笔。

1. **点子与脚本**——先定题材和语气：查 `genre-playbooks.md` 对应题材那一节；要混合题材或从一种语气转到另一种，看同文件的 Tone dial / Hybrid 两节；时长结构查 tvc `tvc-structure.md`。外壳规定：先出 6–9 个点子池让用户挑；品牌要在剧情里自然露出（台词、道具、场景），商品段只表现真实外观和用法；先确认合同时长口径。
   - **抓马模式**（陈尚宇的偏好，做「抓马」系列时用）：类型片大脑洞，场景不限餐饮，餐具只当剧情道具；角色在关键时刻顺口说出 Naturestaurant（只说品牌名，不说网址）；结构 A 剧情 → B 重来（Take two）→ C 商品写实 → CTA（引导关注主页，不说品牌名）→ 尾板（最好不要，要留只闪一下）。样板 P04（CTA 和尾板是旧做法，按 `prompt-rules.md` 第四节改）。
   - 其他题材照样用本流程，只是第 1 阶段的结构和第 2 阶段的光影、镜头配方换成该题材的。
2. **分镜**（`content/分镜/<编号>-分镜.md`）——外壳规定必须有：
   - 设定表：角色模特库编号与服装（`assets/数字人三视图/` 6 人，优先深肤色；非人类角色可例外）、**每件道具在哪几段出现**、资产编号、影调弧线、场景级光源句；
   - 必须表现的情节点清单和秒数分配（`prompt-rules.md` 第二节）；
   - 每段配乐（和光色）标「延续」或「转折」（第三节）；
   - 空间复杂时规划俯视布局、动线、机位编号。
3. **参考图**（GPT-Image-2，每个 1 张，不出候选；不满意再单独重出）：角色三视图 → 道具 → 俯视图 → 两个方向的场景图。俯视图用 `plan_annotate.py` 标动线给用户看。某段不带的道具，从定稿图编辑出去掉道具的版本。
4. **首帧**（每段 1 张，2 候选）：构图对得上俯视图；首帧定稿才生成视频。
5. **视频**（Seedance 2.5 官方版，全能参考，每段 2 候选）：按 `prompt-rules.md` 第一节框架写；延续段挂上一段选定视频，转折段不挂；品牌台词写拼读。`review.py --brand natur` 审片，逐条核对情节点、左右朝向、台词归属；漏掉的情节点单独补拍短段。
6. **粗剪与交付**：写 `timeline.json`，`assemble.py` 出片（-14 LUFS）；去掉 AI 片段首尾自带黑帧；粗剪上画布；分镜末尾写选用理由和已知问题；更新待办、工作记录；新教训同时写进本 skill 和 `knowledge/07`。

## 配乐和光色：每段先判断延续还是转折（必做）

写每个视频段的「声音」之前问：**这段的情绪和上一段一样吗？** 在 `project.json` 的视频 job 里填 `"music"`，`canvas_gen.py` 提交前会检查，不合规则拒绝提交。

| music | 什么时候 | 怎么写 | 参考挂法 |
| --- | --- | --- | --- |
| `start` | 全片第一段 | 写全新的音乐设定（BPM、乐器、走向、must_not），可以开头几秒故意不放 | 不挂视频 |
| `continue` | 同一场景、同一情绪往下走（悲剧 → 重来、同一场追逐） | 「音乐延续视频1 的同一主题……」；光沿用同一场景光句 | **必须**挂上一段选定的视频作视频1 |
| `turn` | 情绪翻面（恐怖 → 商品、危机 → 获救、搞笑 → 温情） | 提示词**开头**写全新音乐，列出不要的上一段乐器和音效；光色整套换 | **不能**挂上一段视频，要接画面只挂尾帧图片 |
| `none` | 不要配乐的段（插入镜头、只要音效的补拍） | 写「没有音乐」 | 随意 |

详细说明和踩坑案例见 `references/prompt-rules.md` 第三节。

## 项目目录与命令

```
assets/<编号>-<名>/
  project.json   画布 ID、refs、jobs（kind/label/ratio|duration/refs/prompt）、plans
  state.json     已提交 / 失败任务、快照（脚本维护）
  参考素材/  参考图/  视频/  视频/审片/  timeline.json
```

```bash
S=.claude/skills/restaurant-drama/scripts
python3 -I $S/canvas_setup.py assets/<项目> [--sync-prompts]   # 建/补画布节点，打印每段图片编号核对
python3 -I $S/canvas_gen.py   assets/<项目> R1 R2                 # 默认参考图 1 张、视频 2 候选；首帧加 --n 2；一次最多 3 个视频候选
python3 -I $S/plan_annotate.py assets/<项目> [--grid]             # 俯视图坐标网格 / 动线标注
python3    $S/review.py --brand natur assets/<项目>/视频/*.mp4     # 联系表 + 转写 + 品牌词单独转写
python3 -I $S/assemble.py assets/<项目>/timeline.json             # 粗剪
```
- job 名不含 `_v`；改提示词后 `canvas_setup.py --sync-prompts` 再生成。视频生成走后台，等通知。
- 规格、价格取官网并注明取价日期；AI 不画产品性能测试。
