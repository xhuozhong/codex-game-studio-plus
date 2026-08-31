# NOTICE — Codex Game Studio Plus

由 xhuozhong 发布，独立升级仓库，版本 4.0.0。旧仓库 codex-game-studio 保持不变。

## 旧版材料

本版以 [codex-game-studio@f222fffffceba66158a3662376bdcf4c101bd683](https://github.com/xhuozhong/codex-game-studio/tree/f222fffffceba66158a3662376bdcf4c101bd683) 为基础。11 个原有 Skill 来自 `codex-game-studio-2.0.0-offline.zip`。原 ZIP CRC 已验证，SHA-256 为 `4c2fbd331da3eed73fb3f6d9c9f83bb9da59d87aaf6448805cca8ed6de17144b`；原包没有 LICENSE / NOTICE。

Plus 修改了总导演的专家路由、边界与验证说明；4.0 另增强素材生成专家，其余 9 个原有 Skill 的指令正文保持不变。完整 YAML 解析发现旧版部分 description 含未加引号的冒号，Plus 为这些 frontmatter 描述补上引号；这不改变其描述含义，具体项目在来源清单中标记。安装器、校验器、元数据及发布文档按升级版调整。逐项来源与哈希见 [docs/source-manifest.json](docs/source-manifest.json)。原制作说明称旧版是独立编写集合；本次保留该说明，但它不构成独立版权审计或第三方授权证明。

## 新增专家

| 目录 | 来源与许可范围 |
| --- | --- |
| `skills/phaser-specialist/` | 基于 Phaser 官方固定提交的聚焦改编；完整 MIT 原文与版权署名见目录内 LICENSE.txt，改动和原文件哈希见 source-provenance.json |
| `skills/gameplay-balance-validator/` | 基于 abagames/agentic-gamedev-skills 中两项方法的改编；保留 MIT，工具实现及来源详见该目录 |
| `skills/sprite-animation-pipeline/` | 参考 OpenAI game-studio 工作流后独立编写；未复制上游工具源码。许可及来源见该目录 |
| `skills/web-3d-asset-optimizer/` | 参考 OpenAI game-studio 工作流后独立编写；附只读 GLB 检查工具，非上游优化器的打包。许可及来源见该目录 |

每个子目录的许可仅覆盖其明确标识的材料，**不为旧版 Skill 或整个仓库重新授权**。新材料的许可不得被推断为给外部生成资产、付费服务或游戏项目授权。

## 整体许可状态

本集合目前没有统一开源许可证，根目录不放置一份会误覆盖第三方/旧版材料的 MIT LICENSE。公开可见不等于所有权利均获许可。未明确许可的材料，复制、修改、再分发或商用前应向相应权利人确认授权。本 NOTICE 本身不是额外许可。

发布者补齐旧版授权范围后，可再考虑给可授权部分添加明确的许可证。不得以本次整理为理由覆盖上游署名。

## 名称与依赖

Codex、OpenAI、Phaser、Higgsfield、Three.js 及相关名称属于各自权利人；本项目不暗示其赞助、背书或官方关联。旧版 `develop-web-game` 不是 OpenAI 官方完整工具包；`higgsfield-game-generation` 不附带服务账号、CLI 或资产许可。

安装器只处理本地文件。实际开发可能需要 Python/Pillow、浏览器自动化、引擎、Blender、glTF 转换工具或生成/部署服务。这些依赖未随本包提供，遵循各自许可和服务条款。

## 4.0 新材料

本版新增 asset-production-director、game-level-builder、character-animation-integrator、game-audio-director、narrative-localization-engineer、game-vfx-engineer 六个职责与独立编写的检查工具，各目录附 MIT。既有 3D 专家增加独立编写的 CLI 调用助手，适用该目录许可。examples/asset-slice 为本次独立编写的验证样例，许可见该目录。

未复制或打包 ComfyUI、Blender MCP、Spine、Tiled、LDtk、Howler、Tone、ink、Yarn、postprocessing、Rapier、glTF Transform、KTX 或模型权重。它们的引用不授予使用权或安装权限；编辑器/工具代码、模型权重、输入资源、输出素材和在线服务条款须分别核对。尤其 Spine 采用专用许可、部分模型有地域条款，Blender MCP 默认遥测须审查。
