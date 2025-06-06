#!/usr/bin/env python3
import re
from pathlib import Path


def parse_settings(js_file: Path):
    text = js_file.read_text(encoding="utf-8")
    # locate the start of the settings array
    settings_start = text.find("settings:")
    settings_start = text.find("[", settings_start)

    # extract each top‑level { … } block within that array
    blocks = []
    depth = 0
    i = settings_start
    while i < len(text):
        c = text[i]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                break
        elif c == "{" and depth == 1:
            # found a setting object
            start = i
            brace = 0
            while i < len(text):
                if text[i] == "{":
                    brace += 1
                elif text[i] == "}":
                    brace -= 1
                    if brace == 0:
                        blocks.append(text[start : i + 1])
                        break
                i += 1
        i += 1

    settings = []
    for blk in blocks:
        # pull out our fields via regex
        id_ = re.search(r'id\s*:\s*"([^"]+)"', blk)
        cats = re.search(r"category\s*:\s*\[([^\]]+)\]", blk, re.DOTALL)
        name = re.search(r'name\s*:\s*"([^"]+)"', blk)
        typ = re.search(r'type\s*:\s*"([^"]+)"', blk)
        default = re.search(r'defaultValue\s*:\s*(?:"([^"]*)"|([^,\n]+))', blk)

        # handle multiline tooltip concatenations
        tooltip_match = re.search(
            r"tooltip\s*:\s*("  # start of tooltip expression
            r'"[^"]*"'  # first quoted part
            r'(?:\s*\+\s*"[^"]*")*'  # optional + "..." parts
            r")",
            blk,
            re.DOTALL,
        )
        tooltip = ""
        if tooltip_match:
            # extract all quoted pieces and join
            parts = re.findall(r'"([^"]*)"', tooltip_match.group(1), re.DOTALL)
            tooltip = "".join(parts)

        attrs = re.search(r"attrs\s*:\s*\{([^}]+)\}", blk, re.DOTALL)

        # cleanup
        cat_list = []
        if cats:
            cat_list = [c.strip().strip("'\"") for c in cats.group(1).split(",")]

        attr_dict = {}
        if attrs:
            for k, v in re.findall(r"(\w+)\s*:\s*([^,\n]+)", attrs.group(1)):
                attr_dict[k] = v.strip()

        settings.append(
            {
                "id": id_.group(1) if id_ else "",
                "category": cat_list,
                "name": name.group(1) if name else "",
                "type": typ.group(1) if typ else "",
                "default": default.group(1) or default.group(2).strip() if default else "",
                "tooltip": tooltip.replace("\\n", " ").strip(),
                "attrs": attr_dict,
            }
        )

    return settings


def write_markdown(settings, out_file: Path):
    with out_file.open("w", encoding="utf-8") as f:
        f.write(
            "# RyuuNoodles 🐲 Settings\n\n"
            "Auto-generated by [/extras/settings_markdown_conv.py](/extras/settings_markdown_conv.py) "
            "from [/js/settings.js](/js/settings.js) using [generate_settings_md.yml](/.github/workflows/generate_settings_md.yml).\n"
            "You can find the settings the custom node pack adds here as well as the defaults and tooltips.\n\n"
        )
        for s in reversed(settings):  # reversed here to match visual settings page
            cats = s["category"]
            # build header: ignore first & last category, use middle + name
            if len(cats) >= 3:
                section = cats[1]
                header = f"## {section} > {s['name']}"
            else:
                header = f"## {s['name']}"

            f.write(f"{header}\n\n")
            f.write(f"- **ID**: `{s['id']}`\n")
            f.write(f"- **Type**: {s['type']}\n")
            if s["attrs"]:
                f.write(f"- **Attributes**:\n")
                for k, v in s["attrs"].items():
                    f.write(f"  - `{k}`: {v}\n")
            f.write(f"- **Default Value**: `{s['default']}`\n")
            f.write(f"- **Tooltip**: {s['tooltip']}\n\n")


if __name__ == "__main__":
    base = Path(__file__).parent
    js = base / ".." / "js" / "settings.js"
    md = base / ".." / "SETTINGS.md"

    if not js.exists():
        print(f"❌ Cannot find {js}")
        exit(1)

    settings = parse_settings(js)
    write_markdown(settings, md)
    print(f"✅ Generated {md}")
