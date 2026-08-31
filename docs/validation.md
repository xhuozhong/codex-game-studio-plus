# 4.0.0 验证记录

日期：2026-08-31。对象为交付的 Skill、辅助工具和原创多素材验收样例。历史 3.0 记录见 [validation-v3.md](validation-v3.md)。

## 已执行

- 21 个 Skill 与安装清单一致；官方 skill-creator quick_validate 和 PyYAML 6.0.3 完整检查 frontmatter/UI YAML。检查 UTF-8、Python 语法、相对链接、来源哈希和明显秘密/个人路径泄漏。Windows 上官方校验以 UTF-8 模式运行。
- 新增 production 测试 15 组通过：来源哈希与证据、未审核许可/草稿拒绝发布、路径逃逸/ADS/Windows 路径拒绝、重复记录/缺依赖/体积预算；地图引用/GID/翻转标志/稀疏图片图块/出生点/LDtk 外置层及不支持格式；PCM 样本/循环区间；中英文本与占位符数量。
- 原数值遥测 12 项测试、精灵/GLB 6 组回归测试通过。Python 3.12.13、Pillow 12.3.0。
- Windows PowerShell 5.1 安装回归 13 组通过：对完整 21-Skill 包执行隔离项目安装、冲突拒绝、备份更新、卸载、标记保护、非法清单、符号链接/目录联接及长路径预检。未永久删除旧 Skill。
- 实际 glTF Transform 4.4.2：原创双材质三角形 GLB 的 dedup 与 meshopt 转换成功，验证源文件不变、重复输出拒绝，dedup 后材质数从 2 到 1。测试输入 608 字节，dedup 输出 632 字节，meshopt 输出 1088 字节；这说明小素材不能假定压缩会变小。校验器对 EXT_meshopt_compression 报告不支持的扩展，不能因此宣称完整解码正确。
- 原创浏览器样例的 JavaScript 语法检查、SVG/地图/中英文资源加载与实际按钮操作。运行中的 DOM 显示移动、任务、命中次数、WAV 解码/AudioContext running、声音调度事件以及保存/重置/读取结果；随后实际到达出口通关，切换英文，查看画面并检查当前浏览器日志，无 error/warn。画面为原创几何素材，不代表最终商业美术。

## 验证命令

```text
python scripts/validate_bundle.py
python tests/test_production.py
python tests/test_balance.py
python tests/test_assets.py --scratch-parent <仓库外的现有目录>
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tests/test_installer.ps1 -ScratchParent <仓库外的现有目录>
```

Windows 安装回归入口实际为 `tests/test_installer.ps1 -ScratchParent <仓库外现有目录>`。GLB 转换助手命令见其 SKILL.md；测试依赖安装在独立临时工作目录，未加入发行包。

## 未覆盖/不作承诺

- 未启动真实 Phaser/Three/Unity/Godot 项目、未验证骨骼/重定向、复杂 PBR 或 3D 运行态解码。原创 Canvas 样例不能替代这些测试。
- 未运行 resize 纹理变换、KTX 转码、ComfyUI、Blender、Spine、云生成或付费服务；未获取模型权重。没有宣称自动产生商业美术。
- 音频检查与浏览器调度状态不等于实际听检。本次未验证扬声器输出、混音质量或循环可听接缝；未做手机、手柄与完整无障碍矩阵。
- 未测 macOS/Linux 安装、网络共享路径、并发文件竞争或复制/移动中途故障注入。未完成历史材料独立版权审计。
- 新专家是独立编写的工作流程。未进行独立代理前向评估，不以结构检查代替真实项目中的技能表现评估。
