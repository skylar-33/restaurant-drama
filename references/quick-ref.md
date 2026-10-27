# 速查表（通用，不分题材）

每条摘自原文并标出处，2026-10-22 对原文逐条核对过。拿不准或要细节时按出处查原文；**题材专属的配方（恐怖用几比几光比、喜剧用什么景深……）不在这里，按当次题材查 `DirectorSKILL/references/genre-playbooks.md` 对应一节**（19 种题材 + 调旋钮换题材 + 混合题材）。

`D=` `vendor/DirectorSKILL/references/`　`T=` `vendor/seedance-tvc-director/references/`　`X=` 本机小逻目录（见 routing.md）

## 光影
- 写光源不写情绪词：「single desk lamp camera-left, hard, shadow side about two stops under, tungsten warm」，不写 "moody"。〔D/lighting-and-color §The core rule〕
- 每个场景一句世界坐标的光源句，逐字粘进该场景所有提示词；每镜另写一句相对镜头的方向和一个可见后果（哪边脸亮、鼻影落哪）。反打只改这一句。〔D/lighting-and-color §Lighting continuity for AI video〕
- 光比用文字写：1:1「两侧一样亮」、2:1「暗侧低一档」、4:1「暗侧明显暗但有细节」、8:1「暗侧几乎全黑，只有颊边有光」、16:1「只亮一条」。近景光源出画，模型会回到柔和，每个特写都重写。〔D/lighting-and-color §Lighting ratios、§Lighting continuity〕
- 轮廓光（漏写是画面发糊的头号原因）和眼神光（不写眼睛发死）要写出来。〔D/lighting-and-color §Setup vocabulary〕
- 分级词一镜最多 2 个，多了会糊成米色；"flicker" 要局部化，否则整帧曝光抖。〔D/lighting-and-color §Grading language、§Lighting continuity〕
- 色彩用光源名和材质名（tungsten warm、fluorescent green-white），不用 hex。〔D/lighting-and-color §Naming color for models〕

## 镜头
- 模型在中景到特写最稳；大远景出远处脸变形和多余路人，大特写崩牙、眼、手指。〔D/cinematic-language §Shot sizes〕
- 同一主体连续两镜，角度差 ≥30 度或景别跳两档，最好都变；新角度写成画面内容（「窗户换到她左肩后」）。〔D/cinematic-language §The 30-degree rule〕
- 机位高度写后果不写数字：「camera low, the table edge cuts across the bottom of frame」。〔D/cinematic-language §Camera height〕
- 守 180 度轴线、视线匹配、出入画方向一致。〔D/cinematic-language §Continuity geometry〕
- 相邻镜头景别要有对冲，不连续同景别；括号里写景别、距离、方位角度、运镜。〔X/小逻-剧本分镜脚本〕

## 调度与表演
- 高可靠动作：呼吸起伏（每镜都写，防止像定格）、衣料头发随风、转头 ≤45 度、低头抬头配视线变化、单方向移动 ≤0.9 米、正面慢走 2–3 步。〔D/blocking-and-staging §Blocking for AI video〕
- 低可靠动作要先想替代：**跟拍奔跑**（改固定广角人物横穿画面，或脸部近景加身体颠簸）、递物（拆成伸手和已拿到两镜）、两人各走各的路线（选一人动、另一人定住）、出画再入画、180 度转身、细手部操作、坐下、摔倒。〔D/blocking-and-staging §Blocking for AI video〕
- 表演不写「难过、愤怒」这类情绪名词，用微表情、生理反应、体态、未完成动作来写；提示词里不用代词，写名字或资产标签。〔X/小逻-剧本分镜脚本 §五维物理表演〕
- 角色身份描述 30–50 词，每个提示词逐字复制，不改写；服装放最后。〔D/continuity-bible §The identity string contract〕

## 时间轴与衔接
- 每段动作按「开始状态 → 触发动作 → 决定性变化 → 反馈 → 结束状态」写；人物、产品、相机、环境的运动分开写。〔T/seedance-2-5-prompting §4〕
- 关键动作写切镜许可点：完成态保留约 0.15–0.35 秒才切；只有下一镜同主体、同方向、同阶段接上才可在中段切。〔T/shot-handoffs §写镜头交接契约〕
- 每镜四项：继承项 / 本镜动作 / 结束态 / 下一镜接口。〔T/shot-handoffs §写镜头交接契约〕
- 没有叙事价值的推、递、摆、等待压到 0.6–1.2 秒，不连成节奏谷。〔T/seedance-2-5-prompting §4〕

## 参考素材与负面词
- 每个参考写「只负责什么、不负责什么」，同一维度只有一个最高优先级来源。〔T/seedance-2-5-prompting §2〕
- 负面词只写当前镜头的高风险项（不换脸、不瞬移、不加未提供的文字、不重复已完成动作），不堆通用词。〔T/seedance-2-5-prompting §7〕

## 声音与对白
- 分层：环境声床（段内不重启）/ 动作声 / 音乐弧线（进入、展开、峰值、收束、归静）/ 旁白。音乐由一个可见事件触发进入，开头几秒可以故意不放。〔T/shot-handoffs §建立声音契约〕
- 配乐按功能写（压迫、保留、释放、反讽、粘合……），写 BPM、乐器、走向，**必写 must_not**。〔D/sound-and-dialogue §Music brief〕
- 对白估时：0.6 秒前摇 + 词数 ÷ 2.5 + 0.8 秒；中文约 4.5 字/秒。看得见嘴的台词 ≤6 个英文词、近景以内、片段约 4 秒；一镜一人开口。〔D/sound-and-dialogue §Duration budgeting、§The one-speaker-per-clip rule〕
- 好对口型：双唇音、开元音、短句；难：辅音丛、悄声、大喊、抢话、数字和专有名词。〔D/sound-and-dialogue §Lines that lip-sync well〕

## 产品动作
- 五段受力链：初始结构 → 锚定点 → 施力点和方向 → 看得见的材料反馈 → 明确结束状态。〔T/product-actions §五段受力链〕
- 容器里的小物件先确认在该机位真看得见，看不见就改高角度插入或浅容器。〔T/seedance-2-5-prompting §4、T/product-actions §容器里的最后一件产品〕

## 出问题时
- 先诊断失败类型（F1 人物漂移、F2 像 PPT、F5 没有结束态、F12 光色漂移、F15 口型不对……），从最低成本的修法开始。〔D/failure-modes §Order of operations〕
- 同一镜头设计失败三次，改镜头不改提示词：缩短、推近、简化、拆镜、首尾帧、换成反应镜头或插入镜头、让动作出画只拍后果。〔D/failure-modes §The three-strike rule〕
- 片里有两辆相似的车（或两件相似道具）时，模型会在交接镜头里换成另一辆：该镜写清外形区别并加「这一镜里不出现 X」。〔V07B 2026-10-23 实测〕
- 单个词的台词容易只做口型：改近景，写「清楚说出声」；核对转写时不加 initial_prompt，否则会把提示词本身转写出来。〔V07B 2026-10-23 实测〕
- 参考图里出现的东西比提示词里的「不要」更有分量：某镜反复出现不该有的物体，先查挂的参考图里有没有它，换掉参考图，再挂一帧正确画面作参考。〔V07B 2026-10-26 实测〕
