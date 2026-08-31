# Codex Game Studio Plus

**1 个总导演 + 14 个专家，为浏览器游戏开发组织一套可复用的 Codex 工作流。**

从游戏设计 → 引擎与玩法 → UI/UX → 手感 → 资源处理 → 多人联机 → 自动试玩回归 → 经授权部署。

这是 [codex-game-studio](https://github.com/xhuozhong/codex-game-studio) 的独立升级仓库，版本 **3.0.0**。原版保持 1 + 10；Plus 新增 4 位专家、来源记录和可运行的资源/遥测辅助工具。无需逐个召唤专家，总导演按当前任务选择 **1 位主专家 + 通常最多 3 位辅助专家**。

> Skill 是给 Codex 的工作指令与资源，不是十四个后台常驻进程。安装包不附带游戏引擎、浏览器自动化运行时、图片/音频生成服务或云部署账号。是否能执行相关工作取决于当前项目和可用工具。**本集合尚无统一开源许可证**，请先阅读 [NOTICE](NOTICE.md)。

## Plus 增加了什么

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

## Windows 安装

### 首次安装

1. 从 [Releases](https://github.com/xhuozhong/codex-game-studio-plus/releases) 下载 **Source code (zip)**，或在仓库的 Code 菜单选择 Download ZIP。
2. 完整解压，在包含 `skills/` 和 `scripts/` 的目录中运行 `INSTALL_WINDOWS.cmd`。
3. 安装成功后，若 Codex 尚未显示新 Skill，完全退出并重新打开 Codex。

默认装入用户目录下的 `.agents/skills/`。安装过程只复制本地资源，不下载 GitHub 文件，不需要 Git、GitHub CLI 或管理员权限。系统执行策略仍以你所在环境的管理规则为准。

### 从旧版升级

Plus 与旧版有 11 个同名 Skill，**不能在同一安装目录中并排存放这 11 个版本**。默认安装遇到任意同名目录会停止，不覆盖文件。确认要切换时运行 `REPAIR_WINDOWS.cmd`：先备份整个旧目录（包含本地修改），再安装 Plus。

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

更多可复制的任务模板见 [examples/prompts.md](examples/prompts.md)。

## 典型工作流

1. **读项目**：确认引擎、运行命令、已有功能、存档和测试入口。
2. **定一个可玩的切片**：明确玩家目标、输入、反馈、失败条件与验收标准。
3. **选专家并实现**：只加载相关资源；保护现有功能，不为使用专家而换引擎。
4. **处理资源**：需要时生成素材，再拆帧/对齐或检查 3D 资源；保留原文件。
5. **运行和验证**：真正启动游戏，试玩关键流程，检查截图、状态与错误；数值改动加可复现遥测验证。
6. **交付与部署**：记录实际测试结果；只有部署工具可用且已获用户授权时才发布，给出真实地址。

适合浏览器游戏原型、Phaser/Three.js 项目迭代、UI 与手感改善、精灵素材交付、网页 3D 资源检查，以及需要明确验收标准的小游戏开发。不默认承诺 Unity/Unreal/Godot 编辑器控制、付费资产生成或一键上线。

## 目录与验证

```text
skills/                 15 个 Skill，按需含 references、scripts、tests、许可
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
