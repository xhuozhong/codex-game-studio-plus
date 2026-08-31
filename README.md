# Codex Game Studio Plus

**1 个总导演 + 20 个专家，为浏览器游戏开发组织一套可复用的 Codex 工作流。**

从游戏设计 → 引擎与玩法 → UI/UX → 手感 → 资源处理 → 多人联机 → 自动试玩回归 → 经授权部署。

这是 [codex-game-studio](https://github.com/xhuozhong/codex-game-studio) 的独立升级仓库，版本 **4.0.0**。原版保持 1 + 10；Plus 3.0 扩为 1 + 14，4.0 再加入素材统筹、关卡、角色动画、音频、叙事本地化与特效六项职责。无需逐个召唤专家，总导演按当前任务选择 **1 位主专家 + 通常最多 3 位辅助专家**。

> Skill 是给 Codex 的工作指令与资源，不是二十个后台常驻进程。安装包不附带游戏引擎、浏览器自动化运行时、图片/音频生成服务或云部署账号。是否能执行相关工作取决于当前项目和可用工具。**本集合尚无统一开源许可证**，请先阅读 [NOTICE](NOTICE.md)。

## 4.0：从单项素材到可玩交付

目标是让角色、场景、动画、UI、音效、对白与特效按照统一规格进入同一个游戏。先定美术参考和素材清单，再处理来源许可、导入、状态/事件、实际试玩与发布检查。

| 新专家 | 交付重点 | 本包实际提供 |
| --- | --- | --- |
| `asset-production-director` | 风格、素材来源、版本和交接 | 素材台账生成/审计工具；发布模式检查许可声明、哈希和本地验收证据 |
| `game-level-builder` | 地图、实体、碰撞和关卡切换 | Tiled/LDtk 结构检查；有限 Tiled 地图点状出生点检查 |
| `character-animation-integrator` | 骨骼、动画混合、挂点与事件 | 2D/3D 集成流程与版本/授权边界；不附骨骼编辑器或自动绑定器 |
| `game-audio-director` | 音乐、音效、配音与混音 | PCM WAV 峰值/RMS、静音和循环区间检查；实际听检仍需进行 |
| `narrative-localization-engineer` | 剧情、存档、多语言和字幕 | 文本 ID、缺译、空字符串与 `{name}` 占位符检查 |
| `game-vfx-engineer` | 粒子、着色器、后期与性能档位 | 按实际引擎实现和验收的流程，不自动换渲染器 |

既有 `web-3d-asset-optimizer` 新增实际调用 glTF Transform 的助手：生成新候选、保留源文件、拒绝覆盖、记录尺寸与哈希并调用格式验证。第三方 CLI 必须事先可用；“已转换”不等于“已在游戏中验证”或“体积一定缩小”。

[多素材验证样例](examples/asset-slice/README.md) 提供原创 SVG 角色/场景、JSON 地图/中英文、可生成的原声音效、攻击特效和存档。它验证接入流程，不代表商业美术品质、骨骼系统或完整 3D 渲染已获验收。

可选 ComfyUI、素材 API、Blender、Spine、Unity/Godot 桥接的边界见 [4.0 升级说明](docs/upgrade-v4.md)。安装只复制 Skill，不下载引擎、模型或付费服务，不自动上传工程、启用遥测或取得素材授权。

## 3.0 已有增强（继续保留）

| 新专家 | 补上的能力 | 实现边界 |
| --- | --- | --- |
| `phaser-specialist` | Phaser 场景生命周期、加载错误、物理与地图 | 参考固定版本的官方材料；先识别 Phaser 3/4，不自动迁移 |
| `gameplay-balance-validator` | 固定种子、可比策略、分数/冷却不变量、遥测验证 | 检查实际事件；不把几次试玩当作“已证明好玩” |
| `sprite-animation-pipeline` | 透明动画条带拆帧、按透明通道裁剪、底部居中锚点与动画导出 | 附 Python 工具；处理已有图片，运行需 Pillow |
| `web-3d-asset-optimizer` | GLB 检查、网页资源预算、转换与视觉复核流程 | 附只读检查工具；实际优化需项目已有的 3D 工具 |

新增来源及固定提交见 [来源清单](docs/source-manifest.json)。Phaser 与数值平衡改编保留原 MIT 许可；精灵和 3D 辅助实现独立编写，分别声明许可。没有整体复制一个庞大的上游插件目录。

## 团队职责

| Skill | 负责什么 |
| --- | --- |
| **`game-studio-director`** | 读取项目、选择专家、约束范围、组织验证、汇报真实证据 |
| `game-design-theory` | 核心循环、关卡、成长、奖励、难度与玩家动机 |
| `game-engine` | 游戏循环、场景、实体、输入、碰撞、摄像机与性能 |
| `game-developer` | 玩法逻辑、状态机、AI、数据、存档和系统集成 |
| `game-ui-design` | HUD、菜单、物品栏、面板、图标、排版和视觉语言 |
| `game-ui-ux` | 信息层级、响应式布局、触屏/键鼠/手柄与无障碍 |
| `game-feel` | 操作响应、动画节奏、粒子、命中停顿、镜头和音效反馈 |
| `threejs-game-ui-designer` | Three.js 游戏的 HUD、覆盖层与触控 UI |
| `multiplayer-game` | 房间、服务器权威状态、同步、断线重连；仅在明确需要联机时启用 |
| `higgsfield-game-generation` | 原型及图像/音频资源生成流程；须有相应外部工具 |
| `develop-web-game` | 实际运行、自动试玩、截图/状态、控制台错误和回归 |
| `phaser-specialist` | Phaser 专项实现与版本边界 |
| `gameplay-balance-validator` | 可复现的玩法与数值验证 |
| `sprite-animation-pipeline` | 从精灵表到可交付的帧与动画资源 |
| `web-3d-asset-optimizer` | 网页 3D 资源检查与优化流程 |
| `asset-production-director` | 美术规范、素材来源、台账、交接与发布预检 |
| `game-level-builder` | 地图、场景、实体、碰撞、出生点与关卡导入 |
| `character-animation-integrator` | 骨骼与动画、换装挂点、状态切换和事件绑定 |
| `game-audio-director` | 音乐、音效、配音、混音与音频生命周期 |
| `narrative-localization-engineer` | 剧情、对白状态、存档、多语言与字幕映射 |
| `game-vfx-engineer` | 粒子、着色器、后期效果与渲染性能验收 |

## Windows 安装

### 首次安装

1. 从 [Releases](https://github.com/xhuozhong/codex-game-studio-plus/releases) 下载 **Source code (zip)**，或在仓库的 Code 菜单选择 Download ZIP。
2. 完整解压，在包含 `skills/` 和 `scripts/` 的目录中运行 `INSTALL_WINDOWS.cmd`。
3. 安装成功后可在下一轮使用；若界面未刷新，再完全退出并重新打开 Codex。

默认装入用户目录下的 `.agents/skills/`。安装过程只复制本地资源，不下载 GitHub 文件，不需要 Git、GitHub CLI 或管理员权限。系统执行策略仍以你所在环境的管理规则为准。

### 从旧版升级

从原版升级涉及 11 个同名 Skill，从 Plus 3.0 升级涉及 15 个；**同名 Skill 的两个版本不能在同一安装目录并排存放**。默认安装遇到任意同名目录会停止，不覆盖文件。确认要切换时运行 `REPAIR_WINDOWS.cmd`：先备份整个旧目录（包含本地修改），再安装 Plus。

备份位于同一作用域的 `.agents/skill-backups/codex-game-studio-plus/<时间与随机标识>/`，不会作为 Skill 被扫描。卸载使用 `UNINSTALL_WINDOWS.cmd`，仅把标记属于 Plus 的 Skill 移到备份，不永久删除。遇到无标记或其他包标记会先停止，不擅自移动它们。

**先在独立项目试用**，可避免替换用户级旧版。在解压目录打开 PowerShell：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Scope Project -ProjectRoot 'D:\Games\MyGame'
```

`ProjectRoot` 必须是已存在的游戏项目目录。需要更新时在同一命令末尾加 `-Force`。卸载同一作用域：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\uninstall.ps1 -Scope Project -ProjectRoot 'D:\Games\MyGame'
```

先检查实际加载来源；如果同时存在项目级、用户级或旧 `.codex/skills/` 下的同名 Skill，请按当前 Codex 客户端的来源显示整理，避免误以为调用的是另一版本。安装器不会修改旧 `.codex/skills/` 目录。

macOS/Linux 用户可在确认无同名冲突并自行备份后，将所需的整个 Skill 子目录复制到适用的 `.agents/skills/` 中。本版不附 Unix 安装器，也未做这些平台的安装实测。

## 在 Codex 中调用

在支持该命令的 Codex 输入界面输入 `/skills`，检查已发现的 Skill；如果当前界面没有该命令，使用其 Skill 选择入口。然后在游戏项目中输入：

```text
$game-studio-director
接管当前游戏项目。先读取项目说明，识别引擎版本、玩法、UI、存档和测试方式。
列出当前阶段与主要风险，选择一个最有价值、能试玩验证的小功能，完成实现与回归。
保留现有架构，不增加未要求的多人联机或服务。
```

也可单独调用专家，例如 `$phaser-specialist`。Skill 没有加载时，先修复安装或说明缺失，不要假装已经执行专家资源。

新版多素材任务示例：

```text
$game-studio-director
接管当前游戏项目，保留现有引擎。
围绕一个可玩关卡，整理角色、场景、动画、UI、特效、音乐音效和对白需求。
先统一美术规格并建立素材台账，复用已授权资源，按需调用专家完成实际导入。
交付可以试玩的小关卡、来源许可、检查报告与真实运行证据；缺失工具和未验收项单列。
```

更多可复制的任务模板见 [examples/prompts.md](examples/prompts.md)。

## 典型工作流

1. **读项目**：确认引擎、运行命令、已有功能、存档和测试入口。
2. **定一个可玩的切片**：明确玩家目标、输入、反馈、失败条件与验收标准。
3. **选专家并实现**：只加载相关资源；保护现有功能，不为使用专家而换引擎。
4. **处理资源**：统一美术规范，建立素材台账，按需生成、整理、导入和检查；保留原件与来源，区分处理完成和运行验收。
5. **运行和验证**：真正启动游戏，试玩关键流程，检查截图、状态与错误；数值改动加可复现遥测验证。
6. **交付与部署**：记录实际测试结果；只有部署工具可用且已获用户授权时才发布，给出真实地址。

适合浏览器游戏原型、Phaser/Three.js 项目迭代、UI 与手感改善、精灵素材交付、网页 3D 资源检查，以及需要明确验收标准的小游戏开发。不默认承诺 Unity/Unreal/Godot 编辑器控制、付费资产生成或一键上线。

## 目录与验证

```text
skills/                 21 个 Skill，按需含 references、scripts、tests、许可
scripts/                本地安装、备份卸载、结构验证、诊断
tests/                  隔离项目的安装回归测试
examples/               调用模板与发布检查表
docs/                   来源、升级说明、验证记录与推广文案
studio-manifest.json    包名、版本、入口与唯一 Skill 清单
NOTICE.md               许可范围和第三方声明
```

安装检查不依赖 Python：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\validate.ps1
```

可选结构检查：`python scripts/validate_bundle.py`。精灵工具另需 Pillow；数值遥测与 GLB 检查工具使用 Python 标准库。辅助工具的输入格式、命令和限制见各 Skill 的说明。验证记录与未执行项目见 [docs/validation.md](docs/validation.md)。

## 来源与许可

请阅读 [NOTICE.md](NOTICE.md) 和新增专家子目录中的许可/来源文件。旧版 11 个 Skill 未取得统一许可声明；公开仓库不代表所有内容均可按 MIT 再分发。本仓库不宣称是 OpenAI、Phaser、Higgsfield 或 Three.js 的官方产品。
