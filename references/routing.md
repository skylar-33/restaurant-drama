# 内功路由：每个阶段读哪份原文

日常先看 `quick-ref.md`（通用规则 + 出处）；题材专属配方和拿不准的细节再按下表读原文。

「餐馆剧情」只管外壳：流程关口、时长约束、提示词框架格式、配乐延续/转折判断、品牌念法、项目规则、画布机制（`prompt-rules.md`、`canvas-pitfalls.md`）。**怎么拍得好看（编剧、表演、光影、镜头、调度、衔接、声音、产品动作、质检）一律读下面的原文**，按原文的规则把内容填进我们的框架。只读当前阶段要用的那几份，不要一次全读。

路径：`V=` 本 skill 的 `vendor/`（MIT，原样收录，见各自 LICENSE）；`X=` `~/Downloads/AI视频制作-skill与流程包/3-skills/外部-GitHub/XiaoLuo-AI-Drama-Skill/`（未声明许可，只在本机引用，不复制、不外发）。

## 优先级（冲突时从上往下）

1. 用户当下的话。
2. 餐馆剧情外壳：提示词格式（Solis 中文逐镜头、图片N = 连线顺序）、分段方式、时长约束、配乐延续/转折、品牌念法、项目规则（模特库、真实性、业务数据、内部信息）、画布机制。
3. 外部原文的内容规则；同一问题以更贴近本次工具的为准：Seedance 2.5 的行为听 seedance-tvc-director，通用电影语言听 DirectorSKILL，分镜资产与表演写法听小逻。
4. 我的默认做法。

## 阶段 → 原文

| 阶段 | 要解决的事 | 读哪份 |
| --- | --- | --- |
| 1 点子与脚本 | 题材结构、钩子、反转、节奏 | `V/DirectorSKILL/references/genre-playbooks.md`（按当次题材读对应一节；混合或转换语气读 Tone dial / Hybrid 两节）；`V/seedance-tvc-director/references/ad-hook.md`、`tvc-structure.md`；`X/小逻-影视编剧创作.md`（需要完整剧本时） |
| 1 | 剧情拆节拍、潜台词 | `V/DirectorSKILL/SKILL.md` Pipeline 第 2–3 步；`V/DirectorSKILL/assets/beat-sheet-template.md` |
| 2 分镜 | 镜头数量和节奏密度 | `V/seedance-tvc-director/references/pacing-and-shot-density.md` |
| 2 | 分镜脚本写法、资产编号、时间轴、表演写法（不写情绪词） | `X/小逻-剧本分镜脚本.md`、`X/xiaoluo-90s-script-to-video.md`；`V/DirectorSKILL/assets/shot-plan-template.md` |
| 2 | 调度、走位、正反打、180 度轴线 | `V/DirectorSKILL/references/blocking-and-staging.md` |
| 2 | 景别、机位高度、焦段、运镜与情绪 | `V/DirectorSKILL/references/cinematic-language.md` |
| 2 | 影调弧线、光比、光向、轮廓光、色彩 | `V/DirectorSKILL/references/lighting-and-color.md`（V07 光影好就是这套做法） |
| 2 | 场景推进、镜头和段之间怎么接、声音桥 | `V/seedance-tvc-director/references/scene-progression.md`、`shot-handoffs-and-sound-bridges.md` |
| 2 | 声音分层、配乐功能写法、对白字数上限和口型 | `V/DirectorSKILL/references/sound-and-dialogue.md`；有旁白时 `V/seedance-tvc-director/references/voiceover.md` |
| 2 | 俯视布局、机位编号、视野锥 | `X/小逻-场景俯视布局.md`、`X/小逻-AI短剧场景布局设计.md` |
| 2 | 连续性圣经（服装、道具、光、伤妆跨镜一致） | `V/DirectorSKILL/references/continuity-bible.md`；多人同框 `V/seedance-tvc-director/references/ensemble-continuity.md` |
| 2 | 导演风格（想要某种质感时才用） | `V/DirectorSKILL/references/director_styles/`（先看 README） |
| 3 参考图 | 角色三视图、服装、道具、表情 | `X/小逻-角色三视图.md`、`X/小逻-角色服装设定.md`、`X/小逻-角色道具设定.md`、`X/小逻-角色表情设定.md`；选角与外形 `V/seedance-tvc-director/references/casting-and-beauty-direction.md` |
| 3 | 场景图、多视角场景 | `X/小逻-场景四视图.md` |
| 3–4 | 关键帧 / 首帧提示词内容 | `V/DirectorSKILL/assets/keyframe-prompt-template.md`、`V/DirectorSKILL/references/image-model-adapters.md`（GPT-Image 部分）、`prompt-lexicon.md` |
| 5 视频 | Seedance 2.5 的写法、素材职责、负面词、生成模式 | `V/seedance-tvc-director/references/seedance-2-5-prompting.md`、`generation-modes.md`；`V/DirectorSKILL/assets/video-prompt-template.md`、`references/ai-video-tool-adapters.md`（Seedance 节） |
| 5 | 商品展示、食物、产品微距 | `V/seedance-tvc-director/references/product-actions.md`、`food-flavor-direction.md`；`V/DirectorSKILL/references/product-and-macro.md` |
| 5 审片 | 失败类型诊断、修法 | `V/DirectorSKILL/references/failure-modes.md`、`assets/qc-checklist.md`；`V/seedance-tvc-director/references/delivery-and-qc.md` |
| 6 粗剪 | 剪辑节奏、时间线 | `V/DirectorSKILL/references/editing-and-assembly.md`、`assets/edit-timeline-template.md` |

## 已知冲突与裁决

| 冲突 | 外部原文 | 我们的做法（外壳说了算） |
| --- | --- | --- |
| 分段 | tvc：30 秒优先一次原生生成（见 `model-and-segmentation-routing.md`） | 按节奏段分 3–5 段：要换参考组合、做悲剧/重来、商品写实转折时必须分段；同一情绪、同一场景、≤30 秒的连续戏可以并成一段 |
| 视频提示词格式 | DirectorSKILL 模板是英文或中文散文式，建议 40–80 词 | Solis 中文逐镜头，一段 2–7 个镜头；只采纳「不重复首帧已有的静态描述」 |
| 镜头编号 | 小逻时间轴行不写镜头编号，只写「起止秒（景别、距离、方位角度、运镜）」 | 保留 Solis 的「镜头N（运镜，景别，起止秒）」，括号里补上小逻要求的距离、方位角度；小逻的「不用代词、写名字或资产标签」采纳 |
| 背景音乐 | 小逻分镜末行默认「无字幕，无背景音乐」 | 音乐随视频生成，按延续/转折写（`prompt-rules.md` 第三节）；「无字幕」保留 |
| 旁白机制 | tvc 的 VO-ID、repeat_count | 只在用了旁白时才用 |
| 品牌名 | 原文没有专门规则 | 台词原文写拼读，生成后单独切词核对 |
| 俯视图用途 | 小逻俯视图是美术规划资产，带机位和视野锥 | 采纳机位编号和视野锥，画进动线图；动线图只给人看，不挂给生成节点；生成用俯视图出的两向场景图 |
| 时长取舍 | tvc 按 15/30 秒档位压镜头密度 | 先保必须表现的情节点（每个 ≥1 秒），不够就加长，超出合同口径再出精简版 |

## 不用的

- `prompt-expert`（内部，基于 Seedance 2.0，和 2.5 实测冲突）。
- `chj-short-drama-video`（出海匠自有连续剧 IP 用，规则过重；接入脚本默认预发环境）。
