# 餐馆剧情（restaurant-drama）

给 Naturestaurant 做 AI 剧情短视频的 skill：从出点子、写分镜、出参考图，到生成视频、审片、粗剪，按固定流程一步步带着做。恐怖、喜剧、悬疑、科幻、温情都能用。

适用于 Codex 和 Claude Code。

## 安装

```bash
git clone https://github.com/skylar-33/restaurant-drama.git ~/.agents/skills/restaurant-drama
```

然后新建一个空文件夹（比如 `NRT视频`），在里面打开 Codex，输入 `/skills`，列表里出现 `restaurant-drama` 就装好了。

更新：`cd ~/.agents/skills/restaurant-drama && git pull`

## 怎么用

```
$restaurant-drama 做一条恐怖题材的抓马视频，道具用官网的纸杯
```

Codex 会按这个顺序推进，每一步做完等你点头再往下走：

1. 出 6–9 个点子让你挑
2. 写分镜（角色、道具、每段几秒、配乐怎么接）
3. 出角色、道具、场景参考图
4. 每段出首帧
5. 生成视频并自动审片
6. 粗剪出片

## 四条铁律

- 视频里不出现网址，口播也不说
- 结尾不说品牌名，改成引导关注主页
- 只拍官网在售的商品，规格照官网
- 不提定制 logo、城市合伙人、佣金，不写配送时效

完整规则和发布前检查在 [`data/内容规则.md`](data/内容规则.md)。

## 需要准备

- 出海匠 API Key（找项目负责人要，交给 Codex 帮你配）
- `python3`、`ffmpeg`（审片和粗剪要用，没装的话让 Codex 装）

## 里面有什么

| 位置 | 内容 |
| --- | --- |
| `SKILL.md` | 流程主文件，Codex 读这个 |
| `references/` | 速查表、提示词格式、画布踩坑记录 |
| `scripts/` | 出海匠画布搭建、批量生成、动线标注、审片、粗剪 |
| `data/` | 内容规则、官网商品目录和数据、6 个数字人模特三视图 |
| `vendor/` | 收录的两份第三方导演 skill 原文（MIT，保留原许可） |
