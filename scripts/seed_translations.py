"""Seed translation tables for community plugins.

Only display text is translated. Entry names, command ids, slots and JSON keys are
never touched. Run once; later edits should be made directly in translations/*.json.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKLOG = ROOT / ".work" / "translation-backlog.json"

SEED = {
    "gridfinity": {
        "name": "Gridfinity 收纳系统",
        "description": "Gridfinity 收纳盒（空心、省料或实心）、底板，以及按打印机尺寸或指定抽屉底板拆分的抽屉底板，支持整格、半格或自定义网格。Edit bin 可修改已生成的收纳盒，未改动的设置保持为 Keep。",
    },
    "woodwork": {
        "name": "木工柜体",
        "description": "用板材制作柜体与家具：柜体生成器与切割清单。",
    },
    "solidinserts": {
        "name": "热熔螺母座",
        "description": "在已有孔的圆形边缘生成热熔螺纹螺母的座孔。",
        "extra": {
            "entries.applica.input_schema.hole_picks.title": "孔边缘",
            "entries.applica.input_schema.hole_picks.description": "选择螺母要装入一侧的圆形孔边缘。",
            "entries.applica.input_schema.serie.title": "类型",
            "entries.applica.input_schema.serie.description": "M3、M4、M5 使用短版；M3 可用 VORON M3 × 5 × 4。",
            "entries.applica.input_schema.filettatura.title": "螺纹规格",
            "entries.applica.input_schema.filettatura.description": "自动模式会在 ±0.05 mm 内匹配孔的公称直径。间隙孔请选择螺钉尺寸。",
            "entries.applica.input_schema.compensazione_mm.title": "直径补偿",
            "entries.applica.input_schema.compensazione_mm.description": "座孔直径的调整量。使用 0 表示目录标准尺寸。",
        },
    },
    "techsquid-bearings": {
        "name": "轴承",
        "description": "放置深沟球轴承与 CSK 单向离合器。",
    },
    "techsquid-extrusions": {
        "name": "型材导轨",
        "description": "MISUMI 5 系列 T 型槽与 OpenBuilds V 型槽导轨，含槽螺母。可在点上放置定长构件，或沿草图直线生成独立导轨。",
    },
    "techsquid-inserts": {
        "name": "热熔螺母",
        "description": "基于 CNC Kitchen 的热熔螺母规格。选择草图点或圆：每处生成螺母底孔及螺母本体。",
        "extra": {
            "entries.make-insert.input_schema.create.title": "创建内容",
            "entries.make-insert.input_schema.create.description": "孔和螺母：在每个选定点下方的零件上钻孔，并将螺母作为独立组件放置到每个点。仅孔：只钻孔，不添加螺母。两者都需要选择点或圆。仅螺母可在有或没有选择时使用：未选择时螺母位于原点。",
            "entries.make-insert.input_schema.custom_diameter.title": "自定义直径",
            "entries.make-insert.input_schema.custom_diameter.description": "可选。滚花点之间的外径。留空则使用所选尺寸的外径。",
            "entries.make-insert.input_schema.custom_length.title": "自定义长度",
            "entries.make-insert.input_schema.custom_length.description": "可选。螺母的总长。留空则使用所选尺寸的长度。",
            "entries.make-insert.input_schema.custom_thread.title": "自定义螺纹",
            "entries.make-insert.input_schema.custom_thread.description": "可选。用螺钉规格替代所选尺寸的孔螺纹，例如 M8x1。螺母必须大于该螺纹。",
            "entries.make-insert.input_schema.hole_adjust.title": "孔径调整",
            "entries.make-insert.input_schema.hole_adjust.description": "加到孔直径上的补偿量。打印出的孔通常偏小：以 0.1 mm 为步长增大，直到适合你的打印机。",
            "entries.make-insert.input_schema.hole_depth.title": "孔深",
            "entries.make-insert.input_schema.hole_depth.description": "盲孔为螺母长度加 1 mm。通孔会钻穿零件；使用时请将草图放在零件表面上。",
            "entries.make-insert.input_schema.hole_type.title": "孔类型",
            "entries.make-insert.input_schema.hole_type.description": "热熔：用于将螺母熔入打印件的直孔。胶粘：用于树脂打印件的台阶孔，列出 M2.5 到 1/4-20 共 8 种规格。",
            "entries.make-insert.input_schema.placement.title": "放置位置",
            "entries.make-insert.input_schema.placement.description": "在视图中选择要放置螺母的草图点或圆。点击圆或圆内部可取圆心。每处生成螺母底孔，若创建内容允许则同时放置螺母。未选择任何对象时，在原点放置一个独立螺母。",
            "entries.make-insert.input_schema.size.title": "尺寸",
            "entries.make-insert.input_schema.size.description": "CNC Kitchen 螺母规格：螺纹与螺母长度。直径、长度和螺纹由所选规格一并确定。",
            "entries.make-insert.input_schema.thread_modeled.title": "建模螺纹",
            "entries.make-insert.input_schema.thread_modeled.description": "切削内螺纹。关闭时保留装饰螺纹，重建更快。统一螺纹和管螺纹必须关闭此项。",
        },
    },
    "techsquid-nuts": {
        "name": "六角螺母",
        "description": "放置普通六角螺母或尼龙锁紧螺母，可选配防转沉孔与螺栓孔。选择草图点或圆，也可在原点放置一个独立螺母。",
        "extra": {
            "entries.make-nut.input_schema.create.title": "创建内容",
            "entries.make-nut.input_schema.create.description": "仅螺母：只生成螺母，未选择对象时在原点。螺母和沉孔：在每个选定点下方的零件上切削六角沉孔及螺栓间隙孔，并将螺母齐平嵌入。仅沉孔：只切削沉孔，不生成螺母。",
            "entries.make-nut.input_schema.custom_size.title": "自定义规格",
            "entries.make-nut.input_schema.custom_size.description": "可选的公制螺纹，包括 M8x1 这样的细牙。锁紧螺母需要选用列表中已有的公称直径。",
            "entries.make-nut.input_schema.custom_thickness.title": "自定义厚度",
            "entries.make-nut.input_schema.custom_thickness.description": "可选的总高度，包括锁紧螺母的尼龙圈。留空则使用所选标准。",
            "entries.make-nut.input_schema.custom_width.title": "自定义宽度",
            "entries.make-nut.input_schema.custom_width.description": "可选的对边宽度。留空则使用所选标准。",
            "entries.make-nut.input_schema.placement.title": "放置位置",
            "entries.make-nut.input_schema.placement.description": "在视图中选择要放置螺母的草图点或圆。点击圆或圆内部可取圆心。每处生成一个螺母，若创建内容为螺母和沉孔则同时生成沉孔。未选择任何对象时，在原点放置一个螺母。",
            "entries.make-nut.input_schema.pocket_adjust.title": "沉孔调整",
            "entries.make-nut.input_schema.pocket_adjust.description": "在创建内容切削沉孔时使用。螺母每个平面与沉孔之间的间隙。打印出的沉孔通常偏小：增大此值直到螺母能放入。",
            "entries.make-nut.input_schema.size.title": "尺寸",
            "entries.make-nut.input_schema.size.description": "选择粗牙公制螺纹。标注“仅普通六角”的尺寸只适用于该样式；其他尺寸也适用于尼龙锁紧螺母。",
            "entries.make-nut.input_schema.style.title": "螺母样式",
            "entries.make-nut.input_schema.style.description": "普通 ISO 4032 六角螺母，或薄型 DIN 985 尼龙锁紧螺母。尼龙圈朝向远离贴合面的方向。",
            "entries.make-nut.input_schema.thread_modeled.title": "建模螺纹",
            "entries.make-nut.input_schema.thread_modeled.description": "切削内螺纹。关闭时保留装饰螺纹，重建更快。",
        },
    },
    "techsquid-screws": {
        "name": "螺钉",
        "description": "基于 ISO 公制螺钉标准。选择已有孔位来安装螺钉，或选择草图点和圆生成螺钉及可选底孔。未选择任何对象时，在原点放置一枚螺钉。",
        "extra": {
            "entries.make-screw.input_schema.create.title": "创建内容",
            "entries.make-screw.input_schema.create.description": "仅螺钉：只生成螺钉，未选择对象时在原点。螺钉和孔：在每个选定点下方的零件上钻孔。仅孔：只钻孔，不生成螺钉。",
            "entries.make-screw.input_schema.custom_size.title": "自定义规格",
            "entries.make-screw.input_schema.custom_size.description": "可选。替代尺寸字段的公制规格，例如 M8x1 或 M3.5x0.6。若所选头部没有该规格的标准，请同时填写自定义头部直径和自定义头部高度。",
            "entries.make-screw.input_schema.drive.title": "驱动槽",
            "entries.make-screw.input_schema.drive.description": "标准模式按所选头部切削常见驱动槽：内六角用于内六角圆柱头、半圆头和沉头螺钉及紧定螺钉；十字槽用于盘头和 M3 以下沉头；一字槽用于圆柱头；六角头无槽。除填写驱动槽尺寸外，均按标准确定尺寸。",
            "entries.make-screw.input_schema.drive_size.title": "驱动槽尺寸",
            "entries.make-screw.input_schema.drive_size.description": "可选。留空则使用所选驱动槽的标准尺寸。内六角：扳手尺寸，或扳手尺寸和深度，例如 2.5 或 2.5x1.3。Torx：T10。十字：PH2 或 PH2x2.1。一字：宽度和深度，例如 0.8x0.7。若头部高度不足，Torx 凹槽会切削较浅，底部保留 0.3 mm；回复中会给出实际切削深度。",
            "entries.make-screw.input_schema.flip.title": "翻转方向",
            "entries.make-screw.input_schema.flip.description": "仅用于仅螺钉模式。在放置点处翻转每枚螺钉。选择孔位时，头部默认朝外。",
            "entries.make-screw.input_schema.head.title": "头部",
            "entries.make-screw.input_schema.head.description": "头部尺寸依据所选尺寸和驱动槽的标准确定：一字或十字盘头/沉头与内六角头尺寸不同。紧定螺钉和螺柱无头部。若某尺寸没有头部标准，请填写两项自定义头部尺寸。",
            "entries.make-screw.input_schema.head_diameter.title": "自定义头部直径",
            "entries.make-screw.input_schema.head_diameter.description": "可选。留空则使用标准头部。六角头指对边宽度。单独填写时保留标准高度。沉头或没有标准头部的尺寸还需要填写自定义头部高度。",
            "entries.make-screw.input_schema.head_height.title": "自定义头部高度",
            "entries.make-screw.input_schema.head_height.description": "可选。留空则使用标准头部。单独填写时保留标准直径。沉头或没有标准头部的尺寸还需要填写自定义头部直径。",
            "entries.make-screw.input_schema.hole_type.title": "孔类型",
            "entries.make-screw.input_schema.hole_type.description": "在创建内容钻孔时使用。间隙孔为 ISO 273 标准通孔。沉头孔增加沉孔，沉头螺钉则增加锥形沉孔，使螺钉头部齐平。攻丝孔切削螺钉自身的螺纹。深度均与螺钉伸入深度一致。",
            "entries.make-screw.input_schema.length.title": "长度",
            "entries.make-screw.input_schema.length.description": "按标准列出的长度：头下长度；沉头螺钉为总长（ISO 10642、ISO 2009 和 ISO 7046-1 含头部）；紧定螺钉和螺柱为总长。",
            "entries.make-screw.input_schema.placement.title": "放置位置",
            "entries.make-screw.input_schema.placement.description": "仅用于仅螺钉模式：点击孔边缘或孔壁，以刚性接头安装螺钉。草图点和圆用于放置独立螺钉或定位新孔。未选择任何对象时，在原点放置一枚独立螺钉。",
            "entries.make-screw.input_schema.size.title": "尺寸",
            "entries.make-screw.input_schema.size.description": "常见机螺钉尺寸，粗牙。其他公制尺寸（如细牙）请填写自定义规格。",
            "entries.make-screw.input_schema.thread_length.title": "螺纹长度",
            "entries.make-screw.input_schema.thread_length.description": "可选。从尖端起算的螺纹长度，不包含尖端。留空则使用标准：短螺钉为整个杆部，足够长的螺钉为标准螺纹长度。输入完整长度可将全部杆部车螺纹。",
            "entries.make-screw.input_schema.thread_modeled.title": "建模螺纹",
            "entries.make-screw.input_schema.thread_modeled.description": "在杆部切削螺纹轮廓。关闭时保留装饰螺纹，重建更快。",
            "entries.make-screw.input_schema.tip.title": "尖端",
            "entries.make-screw.input_schema.tip.description": "平端为方形端面；紧定螺钉上为 ISO 4026 平端：45° 倒角至较小平面。尖端为自攻螺旋端，计入长度。杯端为端面 120° 凹坑；紧定螺钉上为 ISO 4029 杯端，外侧倒角至边缘。",
        },
    },
    "techsquid-v-wheels": {
        "name": "V 型轮",
        "description": "OpenBuilds V 型轮。选择草图点或圆：每处生成一个滚轮，可包含轴承与垫片。未选择任何对象时，在原点放置一个滚轮。",
        "extra": {
            "entries.make-v-wheel.input_schema.assembled.title": "包含轴承与内垫片",
            "entries.make-v-wheel.input_schema.assembled.description": "开启时添加两个轴承及其间的垫片，作为滚轮的一个组件；关闭时仅生成裸轮。",
            "entries.make-v-wheel.input_schema.placement.title": "放置位置",
            "entries.make-v-wheel.input_schema.placement.description": "在视图中选择要放置滚轮的草图点或圆。点击圆或圆内部可取圆心。未选择任何对象时，在原点放置一个滚轮。",
            "entries.make-v-wheel.input_schema.size.title": "零件",
            "entries.make-v-wheel.input_schema.size.description": "要放置的 OpenBuilds 滚轮型号。",
        },
    },
    "gen-design-engine": {
        "name": "生成式设计引擎",
        "description": "工程材料库（含来源卡片）、材料报告、带安全系数的平板件二维应力校核、板材优化器，以及圆杆支架（桁架）设计器。第三方插件，与 SolidCraft 官方无关。",
    },
    "custom-threads": {
        "name": "自定义螺纹",
        "description": "为 3D 打印生成光滑 B-rep 自定义螺纹，支持预设、间隙、多线导程与实时参数。",
    },
    "wood-joinery": {
        "name": "木工榫卯",
        "description": "板材之间的木工接合：榫卯、开槽、半搭接、木榫、指接、活动榫、嵌槽、斜接、企口、斜接榫、燕尾榫、螺钉与饼干榫。",
    },
    "gear-generator": {
        "name": "齿轮生成器",
        "description": "在原点生成渐开线圆柱齿轮：使用普通草图与拉伸，设计文件无需插件即可打开。",
    },
    "solidcraft-honeycomb": {
        "name": "蜂窝与六边形生成器",
        "description": "在选定的草图区域内填充最多 250 个单元。按 Esc 结束当前工具，再按住 Shift 点击区域后打开蜂窝工具。",
    },
    "iso-sheet": {
        "name": "等轴测制造图",
        "description": "将当前设计中的每个实体投影为真实等轴测视图，用深度缓冲消除隐藏线，并输出带尺寸的 ANSI B 制造图 SVG：标题栏、物料清单、参数表与注释。",
    },
    "mould-maker": {
        "name": "模具生成器",
        "description": "按打印机尺寸生成可打印模具。圆形：碗、花盆。方形：平面零件的模具。硅胶套：芯模、对开外套与底座。大型圆模需运行两次：若只生成外壳，请再次运行。",
    },
    "solidcraft-3d-printing-holes": {
        "name": "3D 打印孔",
        "description": "专为 3D 打印设计的孔。水滴形：选择草图圆后运行，每个孔上方会生成直径百分之几的小尖顶，防止水平孔顶部下垂。未选择对象时会绘制一个示例孔。",
    },
    "solidcraft-aprilcube": {
        "name": "AprilCube",
        "description": "生成带 AprilTag 或 ArUco 标记、边缘倒角、镶嵌凹槽及检测器 JSON 的可打印立方体与体素靶标。",
    },
    "filament-swatch": {
        "name": "耗材色卡",
        "description": "耗材样品片：以文字标注品牌、材料、颜色与温度，并通过薄台阶展示耗材的透光程度。",
    },
    "mesh-solidify": {
        "name": "网格实体化",
        "description": "将破损的网格实体（孔洞、开放壳体、重叠）重建为单一水密、可打印的实体，并作为新实体添加。",
    },
    "thread-generator": {
        "name": "螺纹生成器",
        "description": "在选定面上切削带打印间隙的螺纹，或生成螺栓、螺母与螺柱的 STL。",
    },
    "makeorbit-cnc-studio": {
        "name": "发送到 MakeOrbit CNC Studio",
        "description": "将设计以 STEP 格式发送到 MakeOrbit CNC Studio（在对方程序中确认接收）。",
    },
    "makeorbit": {
        "name": "发送到 MakeOrbit",
        "description": "将设计连同源文件以 STEP/STL/3MF 格式发送到 MakeOrbit（在对方程序中确认归档）。",
    },
    "solidcraft-laserjoints": {
        "name": "激光切割接合",
        "description": "在激光切割板材的边缘生成指接榫与开槽。切缝与过盈保持为参数，特征位于时间轴中。",
    },
    "sw2sc": {
        "name": "SolidWorks 零件 (sw2sc)",
        "description": "打开 SolidWorks 零件并保留其特征树：草图、尺寸、约束与特征，并依据零件自身实体进行校验。",
    },
    "timber": {
        "name": "木材型材",
        "description": "标准木方截面（4x2、3x2、2x2、CLS、搁栅、立柱、木条），长度任意，可放置在原点，或与选定木方平行或垂直。",
    },
}


def main() -> int:
    backlog = json.loads(BACKLOG.read_text(encoding="utf-8"))
    written = []

    for pid, payload in SEED.items():
        info = backlog.get(pid, {})
        repo = info.get("repo", "")
        strings = {"name": payload["name"], "description": payload["description"]}
        strings.update(payload.get("extra", {}))

        output = {
            "_meta": {"locale": "zh-CN", "revision": 1, "upstream": repo},
            "strings": strings,
        }
        target = ROOT / "translations" / f"{pid}.zh-CN.json"
        target.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append({"id": pid, "strings": len(strings)})

    print(json.dumps({"written": len(written), "total_strings": sum(x["strings"] for x in written),
                      "plugins": written}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
