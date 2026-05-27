# -*- coding: utf-8 -*-
"""
批量生成所有 14 种图表类型的完整示例图片
输出目录: all_charts_showcase/
"""
import os
import sys

# 设置 stdout 编码为 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from neo_legend.models import RenderRequest
from neo_legend.registry import build_default_registry

output_dir = "all_charts_showcase"
os.makedirs(output_dir, exist_ok=True)

registry = build_default_registry()
all_types = registry.list_types()

print("=" * 70)
print("[BATCH GENERATOR] Generating All Chart Examples")
print(f"Total legend types: {len(all_types)}")
print("=" * 70)

total_files = 0
summary = []

for type_meta in all_types:
    legend_type = type_meta.legend_type
    display_name = type_meta.display_name
    styles = type_meta.styles
    
    print(f"\n{'='*60}")
    print(f"[{legend_type}] {display_name}")
    print(f"   Style count: {len(styles)}")
    print("-"*60)
    
    for style_info in styles:
        style_name = style_info.name
        
        safe_filename = f"{legend_type}__{style_name}.png"
        filepath = os.path.join(output_dir, safe_filename)
        
        try:
            request = RenderRequest(
                legend_type=legend_type,
                style=style_name,
                width=1000,
                height=900,
                title=f"{display_name.upper()}",
                subtitle=f"Style: {style_name.replace('_', ' ').title()}"
            )
            
            result = registry.render(request)
            
            with open(filepath, "wb") as f:
                f.write(result.content)
            
            file_size = len(result.content)
            total_files += 1
            
            print(f"   [OK] {style_name:<25} -> {file_size:>10,} bytes")
            
            summary.append({
                "type": legend_type,
                "display": display_name,
                "style": style_name,
                "file": safe_filename,
                "size": file_size
            })
            
        except Exception as e:
            print(f"   [FAIL] {style_name:<25} -> ERROR: {e}")

print("\n" + "=" * 70)
print("[COMPLETE] Batch generation finished!")
print("=" * 70)
print(f"\nOutput directory: {os.path.abspath(output_dir)}")
print(f"Total files generated: {total_files}")
print(f"\nFile list:")
print("-" * 70)

current_type = None
for item in summary:
    if item["type"] != current_type:
        current_type = item["type"]
        print(f"\n[{item['type']}] {item['display']}:")
    
    print(f"   -> {item['file']:<45} {item['size']:,} bytes")

total_size = sum(item["size"] for item in summary)
print(f"\n{'='*70}")
print(f"Total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
print(f"Directory: {os.path.abspath(output_dir)}")
print("=" * 70)
