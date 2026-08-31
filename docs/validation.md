# 3.0.0 验证记录

日期：2026-08-31。对象为本仓库交付的 Skill 和辅助工具，不是某个游戏的完整生产验收。

## 静态与元数据

- 15 个 Skill 与 `studio-manifest.json` 清单一致。
- 使用 Codex skill-creator 的 `quick_validate.py` 和 PyYAML 6.0.3 解析全部 Skill frontmatter；UI YAML 同时解析。
- 修复了旧版 multiplayer-game、game-developer、game-ui-ux 的 description 未引用冒号问题，含义与指令正文不变。
- 检查 UTF-8、相对链接、Python 语法、PowerShell 语法、来源哈希和明显凭据/个人路径泄漏。
- 离线安装校验器只检查本包采用的 frontmatter 子集，不冒充完整 YAML 解析器。

## 实际行为测试

- 数值工具：`python tests/test_balance.py`，12 项 unittest 通过。涵盖确定性配对、重复事件/计分、冷却边界、分母为零或负数、数值溢出、无效遥测、工具失败和退出码。
- 素材工具：`python tests/test_assets.py --scratch-parent <仓库外现有目录>`，6 组检查通过。使用合成图片检查 4 帧切分、共同缩放、底部居中、透明度、图集、GIF、原件保护和坏输入拒绝；使用合成 GLB 检查结构清单、哈希、损坏文件拒绝及外部 URI 不读取。
- 测试环境使用 Python 3.12.13、Pillow 12.3.0；用户运行辅助工具的依赖要求见各 Skill。
- Phaser 参考中的 5 段 JavaScript 通过 Node 语法检查；未启动 Phaser。

Windows 安装测试在 `tests/test_installer.ps1` 中，使用 Windows PowerShell 5.1，**13 组全部通过**。仅对新建的隔离项目执行，不安装到测试者的用户 Skill 目录。测试证据保留在调用者指定的 ScratchParent 下。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\test_installer.ps1 -ScratchParent 'D:\TestScratch'
```

测试目录必须已存在且在仓库外。测试包含默认冲突不改文件、强制更新备份自定义文件、卸载保留其他 Skill、标记保护、坏清单、未知来源目录和目录联接保护。Windows PowerShell 5.1 对普通复制/哈希路径仍有限制；安装器在写入前检查目标长度，备份移动使用经过路径校验的 Windows 长路径形式。

## 未执行或未包含

- 未对真实游戏做自动试玩、截图回归或玩家体验测试；遥测/资源工具测试不能替代这些工作。
- 未执行图像生成服务、Blender/glTF Transform 转换、真实 3D 渲染或解码性能测试。
- 未执行 macOS/Linux 安装测试、网络共享路径测试、付费服务调用或云部署。
- 未注入文件复制/移动中途故障，未测试并发文件系统竞争；错误恢复不能替代独立备份。
- 不以语法校验宣称所有 Phaser API 示例已在真实游戏中运行。
- 没有为旧版材料完成独立版权审计；许可限制见 NOTICE。
