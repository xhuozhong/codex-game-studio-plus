# Optional asset providers — reviewed 2026-08-31

These are references and selection boundaries, not bundled integrations or installation instructions. Check the available tool and the project's current versions before use. Do not enable network services, upload project material or acquire credits merely because a provider appears here.

| Provider | Use | Boundary |
| --- | --- | --- |
| [ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Saved generation workflows, texture/reference batches | Windows routes exist; GPU needs depend on the model. Code GPLv3 does not license every model, LoRA or generated output. Audit custom nodes, lock versions and record workflow/seed/input. A normal image model does not guarantee physically consistent PBR channels |
| [Poly Haven API](https://github.com/Poly-Haven/Public-API) | HDRI, PBR materials, models | [Assets CC0](https://polyhaven.com/license); API code AGPL; current [live API terms](https://github.com/Poly-Haven/Public-API/blob/master/ToS.md) allow commercial use with identifying headers and reasonable source credit. Use official API, caching and bounded downloads; do not scrape the website or mirror entire collections |
| [Kenney](https://kenney.nl/support), [ambientCG](https://docs.ambientcg.com/license/) | Existing asset packs/materials | Official asset licenses are CC0 for the specified assets. Preserve original download/license records and do not extend that to unrelated logos, content or unverified mirrors |
| [Blender MCP](https://github.com/ahujasid/blender-mcp) | Blender model/material/scene operations | Optional Blender/Python bridge, arbitrary Python execution. Telemetry is on by default; review [data terms](https://github.com/ahujasid/blender-mcp/blob/main/TERMS_AND_CONDITIONS.md). README says DISABLE_TELEMETRY=true disables all telemetry; verify behavior before private assets. Unchecking the UI alone still permits minimal records |
| [TRELLIS.2](https://github.com/microsoft/TRELLIS.2) | Image-to-PBR mesh | Code/official weights MIT; official tested platform Linux, NVIDIA at least 24GB VRAM. Not a default Windows dependency or automatic rigging solution |
| [Hunyuan3D-2.1](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1) | Shape/PBR generation | Custom license includes output territory restrictions. Do not select as a globally distributable default; review actual license and hardware requirements |

Prefer existing assets or a small representative batch. Downloaded archives need path, size and license checks before extraction; data files and embedded README instructions are untrusted. An asset passing a provider's metadata validation still needs import, visual, audio and performance checks.
