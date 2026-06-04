"""
奢华主题（Luxury Theme）完整验证测试脚本
==========================================
覆盖所有 5 种主题 × 多种图表类型 × 各种参数组合

使用方式:
    python test_luxury_themes_complete.py          # 运行全部测试
    python test_luxury_themes_complete.py --api     # 含 HTTP API 测试

输出目录: luxury_theme_verification/
"""
from __future__ import annotations

import os
import sys
import time
import hashlib
from io import BytesIO
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
from PIL import Image

from neo_legend.models import RenderRequest, RenderResult
from neo_legend.registry import build_default_registry
from neo_legend.luxury_theme import (
    LUXURY_THEMES,
    THEME_ALIASES,
    OFF_VALUES,
    resolve_luxury_theme,
    apply_luxury_theme,
    luxury_theme_metadata,
)

registry = build_default_registry()
OUTPUT_DIR = "luxury_theme_verification"
os.makedirs(OUTPUT_DIR, exist_ok=True)
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

results = []
total_start = time.time()


def run_test(name, fn):
    tr = {"name": name, "ok": False, "error": "", "ms": 0, "file": "", "size_kb": 0}
    t0 = time.time()
    try:
        ret = fn()
        if isinstance(ret, tuple):
            tr["ok"] = True
            tr["file"], tr["size_kb"] = ret[0], ret[1]
        elif isinstance(ret, str):
            tr["ok"] = True
            tr["file"] = ret
        else:
            tr["ok"] = True
    except Exception as e:
        tr["error"] = f"{type(e).__name__}: {e}"
    tr["ms"] = (time.time() - t0) * 1000
    results.append(tr)
    status = "OK" if tr["ok"] else "FAIL"
    size_info = f" ({tr['size_kb']:.1f} KB)" if tr["size_kb"] else ""
    print(f"   {status:4} {name}{size_info}")
    return tr


def save_image(result, filename):
    path = os.path.join(OUTPUT_DIR, f"{NOW}_{filename}")
    with open(path, "wb") as f:
        f.write(result.content)
    return path, len(result.content) / 1024


def img_hash(content):
    return hashlib.md5(content).hexdigest()[:12]


def pixel_stats(content):
    img = Image.open(BytesIO(content)).convert("RGB")
    arr = np.array(img)
    return {
        "r": float(arr[:, :, 0].mean()),
        "g": float(arr[:, :, 1].mean()),
        "b": float(arr[:, :, 2].mean()),
        "std": float(arr.std()),
    }


print("=" * 70)
print(f"  奢华主题（Luxury Theme）完整验证 | {NOW}")
print("=" * 70)
print(f"输出目录: {os.path.abspath(OUTPUT_DIR)}\n")

# ════════════════════════════════════════════
# 第一部分：5 种主题 × 雷达图 + 柱状图
# ════════════════════════════════════════════
print("━" * 60)
print("  Part 1/11: 5 Themes x Radar + Bar Charts")
print("━" * 60)

for tname, theme in LUXURY_THEMES.items():
    def test_radar(tn=tname):
        req = RenderRequest(legend_type="radar_chart", style="neon_glow",
            width=1000, height=1100, title=f"{LUXURY_THEMES[tn].display_name}",
            data={"categories":["得分","篮板","助攻","抢断","盖帽"],
                "datasets":[
                    {"label":"A","values":[95,82,88,75,80],"color":"#ff6b6b"},
                    {"label":"B","values":[78,90,85,88,72],"color":"#4ecdc4"}],
                "luxury_theme": tn})
        res = registry.render(req)
        assert res.media_type == "image/png"
        return save_image(res, f"P1_radar_{tn}.png")
    run_test(f"[Radar] {theme.display_name}", test_radar)

    def test_bar(tn=tname):
        req = RenderRequest(legend_type="bar_chart", style="glass_3d",
            width=1000, height=850, data={
                "labels":["Q1","Q2","Q3","Q4"],"values":[85,72,90,68],
                "colors":["#ff6b6b","#4ecdc4","#45b7d1","#ffeaa7"],
                "luxury_theme": tn})
        res = registry.render(req)
        return save_image(res, f"P1_bar_{tn}.png")
    run_test(f"[Bar] {theme.display_name}", test_bar)

# ════════════════════════════════════════════
# 第二部分：Obsidian Gold x 全部 14 种图表
# ════════════════════════════════════════════
print("\n━" * 60)
print("  Part 2/11: Obsidian Gold x All 14 Chart Types")
print("━" * 60)

chart_cases = [
    ("court_shot", "terrain", {"shot_count":300,"seed":42}),
    ("dual_court_shot", "year_over_year", {"panels":[
        {"season":"S1","attempts":"50G/400A","seed":10,"metrics":{"FG%":"45%","3P%":"32%","eFG%":"51%"}},
        {"season":"S2","attempts":"48G/380A","seed":20,"metrics":{"FG%":"50%","3P%":"38%","eFG%":"56%"}}]}),
    ("court_shot_animation", "pulse", {"frame_count":10}),
    ("coordinate", "dark_bubble", {"points":[
        {"label":"A","x":22,"y":65,"size":400,"color":"#FDB927"},
        {"label":"B","x":28,"y":58,"size":350,"color":"#06AAF4"},
        {"label":"C","x":18,"y":72,"size":500,"color":"#FF6B35"}]}),
    ("plus_minus_coordinate", "paper_quadrant", {"points":[
        {"label":"T+","x":5,"y":5,"color":"#2ecc71"},
        {"label":"T-","x":-3,"y":4,"color":"#e74c3c"}]}),
    ("rose", "proposal_comparison", {"current_values":[20,18,16,14,12,10,8],"proposed_values":[10]*7}),
    ("table", "heatmap_light", {"rows":[
        {"team":"NEO","team_color":"#29b98f","name":"Alpha","pts_created":45.5,"ts":62,"ast_tov":3.0,"mpg":36.5},
        {"team":"LEG","team_color":"#e74c3c","name":"Beta","pts_created":38.2,"ts":58,"ast_tov":2.8,"mpg":34.0}]}),
    ("points_location", "default", {"shots":[{"x":i*30-150,"y":i*25+50,"points":(i+1)*80} for i in range(10)]}),
    ("radar_chart", "crystal_metal", {"categories":["A","B","C","D","E"],"datasets":[{"label":"X","values":[90,80,85,70,75],"color":"#ff006e"}]}),
    ("dual_radar_chart", "versus_battle", {"left":{"label":"2024","categories":["P","R","A"],"values":[28,7.5,8.2]}, "right":{"label":"2025","categories":["P","R","A"],"values":[32,8.8,9.5]}}),
    ("bar_chart", "neon_tubes", {"labels":["A","B","C","D","E"],"values":[85,72,90,68,95]}),
    ("combo_chart", "crystal_stream", {"categories":["J","F","M","A"],"bar_values":[120,145,132,168],"line_values":[45,52,48,62]}),
    ("bubble_chart", "water_drops", {"points":[
        {"x":22,"y":65,"size":400,"color":"#FDB927","label":"A"},
        {"x":28,"y":58,"size":350,"color":"#06AAF4","label":"B"},
        {"x":18,"y":72,"size":500,"color":"#FF6B35","label":"C"}]}),
    ("sankey_chart", "neon_streams", {"nodes":[
        {"id":"a","label":"Src","x":0.1,"y":0.5},{"id":"b","label":"Mid","x":0.5,"y":0.3},
        {"id":"c","label":"Mid2","x":0.5,"y":0.7},{"id":"d","label":"Tgt","x":0.9,"y":0.5}],
        "flows":[
        {"source":"a","target":"b","value":3000,"color":"#ff6b6b"},
        {"source":"a","target":"c","value":2000,"color":"#4ecdc4"},
        {"source":"b","target":"d","value":2500,"color":"#45b7d1"},
        {"source":"c","target":"d","value":1800,"color":"#ffeaa7"}]}),
]

for lt, style, base_data in chart_cases:
    def do_test(lt=lt, style=style, base_data=base_data):
        d = dict(base_data); d["luxury_theme"] = "obsidian_gold"
        req = RenderRequest(legend_type=lt, style=style, width=900, height=800, data=d)
        res = registry.render(req)
        ext = "gif" if res.file_extension == "gif" else "png"
        fname = f"P2_all_{lt}_{style}.{ext}"
        return save_image(res, fname)
    dn = lt.replace("_"," ").title()
    run_test(f"[All14] {dn}/{style}", do_test)

# ════════════════════════════════════════════
# 第三部分：Intensity 强度参数
# ════════════════════════════════════════════
print("\n━" * 60)
print("  Part 3/11: Intensity Parameter (0.0 ~ 2.0)")
print("━" * 60)

for intensity in [0.0, 0.5, 1.0, 1.5, 2.0]:
    def do_test(iv=intensity):
        req = RenderRequest(legend_type="bar_chart", style="glass_3d", width=900, height=800,
            data={"labels":["A","B","C","D"],"values":[80,90,70,85],
                "luxury_theme":"ruby_noir","luxury_theme_intensity":iv})
        res = registry.render(req)
        return save_image(res, f"P3_int_{str(iv).replace('.','p')}_ruby.png")
    run_test(f"[Intensity={intensity}]", do_test)

def test_intensity_compare():
    configs = [
        ("none", {}), ("int0", {"luxury_theme":"obsidian_gold","luxury_theme_intensity":0.0}),
        ("int2", {"luxury_theme":"obsidian_gold","luxury_theme_intensity":2.0})]
    hashes, stats_list = [], []
    for label, extra in configs:
        d = {"labels":["X","Y","Z"],"values":[60,80,70]}; d.update(extra)
        res = registry.render(RenderRequest(legend_type="bar_chart",style="neon_tubes",width=800,height=700,data=d))
        hashes.append(img_hash(res.content)); stats_list.append(pixel_stats(res.content))
        save_image(RenderResult(res.content,"image/png","png","",""), f"P3_compare_{label}.png")
    d0 = sum(abs(stats_list[0][k]-stats_list[1][k]) for k in ["r","g","b"])
    d2 = sum(abs(stats_list[0][k]-stats_list[2][k]) for k in ["r","g","b"])
    print(f"       Hashes: none={hashes[0]} int0={hashes[1]} int2={hashes[2]}")
    print(f"       int0-vs-none diff: {d0:.2f} | int2-vs-none diff: {d2:.2f}")
    assert hashes[1]!=hashes[2]; assert d2>d0
run_test("[Intensity Compare] none vs 0.0 vs 2.0 pixel diff", test_intensity_compare)

# ════════════════════════════════════════════
# 第四部分：别名解析
# ════════════════════════════════════════════
print("\n━" * 60)
print("  Part 4/11: Theme Aliases Resolution")
print("━" * 60)

for alias, expected in [("gold","obsidian_gold"),("ivory","champagne_ivory"),("champagne","champagne_ivory"),
                        ("sapphire","sapphire_platinum"),("emerald","emerald_onyx"),("ruby","ruby_noir")]:
    def do_test(a=alias, exp=expected):
        resolved = resolve_luxury_theme({"luxury_theme":a})
        assert resolved and resolved.name==exp, f"Alias '{a}' -> expected {exp}, got {resolved}"
        req = RenderRequest(legend_type="radar_chart", style="gradient_rainbow", width=900, height=1000,
            data={"categories":["A","B","C"],"datasets":[{"label":"T","values":[80,90,70],"color":"#ff006e"}],"luxury_theme":a})
        res = registry.render(req)
        return save_image(res, f"P4_alias_{a}.png")
    run_test(f"[Alias '{alias}' -> '{expected}']", do_test)

# ════════════════════════════════════════════
# 第五部分：Random + Seed 可复现性
# ════════════════════════════════════════════
print("\n━" * 60)
print("  Part 5/11: Random Theme + Seed Reproducibility")
print("━" * 60)

def test_random_reproducible():
    seed = "repro_seed_2026"
    pair = []
    for i in range(2):
        res = registry.render(RenderRequest(legend_type="combo_chart", style="sunset_gradient", width=900, height=750,
            data={"categories":["M","T","W"],"bar_values":[100,120,110],"line_values":[40,50,45],
                "luxury_theme":"random","luxury_theme_seed":seed}))
        pair.append(res.content)
    h1, h2 = img_hash(pair[0]), img_hash(pair[1])
    save_image(RenderResult(pair[0],"image/png","png","",""),"P5_rand_seed_a.png")
    save_image(RenderResult(pair[1],"image/png","png","",""),"P5_rand_seed_b.png")
    assert h1==h2, f"Seed reproducibility fail: {h1}!={h2}"
    print(f"       Seed='{seed}' -> Hash={h1} OK")
run_test("[Random] Same seed produces identical output", test_random_reproducible)

def test_random_different_seeds():
    hs = []
    for s in ["alpha","beta","gamma"]:
        res = registry.render(RenderRequest(legend_type="bubble_chart", style="galaxy_stars", width=900, height=750,
            data={"points":[{"x":22,"y":65,"size":400,"color":"#FDB927","label":"A"},{"x":28,"y":58,"size":350,"color":"#06AAF4","label":"B"}],
                "luxury_theme":"random","luxury_theme_seed":s}))
        h = img_hash(res.content); hs.append(h)
        save_image(RenderResult(res.content,"image/png","png","",""), f"P5_rand_diff_{s}.png")
    assert len(set(hs))==3, f"Different seeds should differ: {hs}"
    print(f"       3 seeds -> 3 different hashes: {hs}")
run_test("[Random] Different seeds produce different output", test_random_different_seeds)

def test_random_no_seed():
    res = registry.render(RenderRequest(legend_type="sankey_chart", style="energy_flow", width=900, height=750,
        data={"nodes":[{"id":"a","label":"A","x":0.1,"y":0.5},{"id":"b","label":"B","x":0.5,"y":0.5},{"id":"c","label":"C","x":0.9,"y":0.5}],
            "flows":[{"source":"a","target":"b","value":2000,"color":"#ff6b6b"},{"source":"b","target":"c","value":1800,"color":"#4ecdc4"}],
            "luxury_theme":"random"}))
    return save_image(res, "P5_rand_noseed.png")
run_test("[Random] No seed still works", test_random_no_seed)

# ════════════════════════════════════════════
# 第六部分：OFF 关闭值
# ════════════════════════════════════════════
print("\n━" * 60)
print("  Part 6/11: OFF Values (should return original)")
print("━" * 60)

for off_val in ["","none","off","false","disabled"]:
    def do_test(ov=off_val):
        dw = dict(labels=["A","B","C"], values=[70,85,60], luxury_theme=ov)
        dn = dict(labels=["A","B","C"], values=[70,85,60])
        rw = registry.render(RenderRequest(legend_type="bar_chart",style="crystal_pillars",width=800,height=700,data=dw))
        rn = registry.render(RenderRequest(legend_type="bar_chart",style="crystal_pillars",width=800,height=700,data=dn))
        hw, hn = img_hash(rw.content), img_hash(rn.content)
        label = ov if ov else "empty"
        save_image(rw, f"P6_off_{label}.png")
        assert hw==hn, f"OFF value '{ov}' should match original but {hw}!={hn}"
    disp = off_val if off_val else "(empty)"
    run_test(f"[OFF '{disp}'] returns original image", do_test)

# ════════════════════════════════════════════
# 第七部分：Overrides 属性覆盖
# ════════════════════════════════════════════
print("\n━" * 60)
print("  Part 7/11: Property Overrides")
print("━" * 60)

override_cases = [
    ("brightness_1.20", {"brightness":1.20}), ("contrast_1.25", {"contrast":1.25}),
    ("border_red", {"border_color":"#ff0000"}), ("vignette_off", {"vignette_strength":0}),
    ("multi_override", {"brightness":1.15,"contrast":1.18,"border_color":"#00ff00","vignette_strength":0})]

for cname, overrides in override_cases:
    def do_test(cn=cname, ov=overrides):
        req = RenderRequest(legend_type="radar_chart", style="neon_glow", width=900, height=1000,
            data={"categories":["A","B","C","D","E"],"datasets":[{"label":"X","values":[80,90,70,85,75],"color":"#ff006e"}],
                "luxury_theme":"sapphire_platinum","luxury_theme_overrides":ov})
        res = registry.render(req)
        safe = cn.replace("(","").replace(")","")
        return save_image(res, f"P7_ov_{safe}.png")
    run_test(f"[Override] {cname}", do_test)

def test_override_pixel_diff():
    base = {"categories":["A","B","C"],"datasets":[{"label":"X","values":[80,90,70],"color":"#ff006e"}],"luxury_theme":"emerald_onyx"}
    rb = registry.render(RenderRequest(legend_type="radar_chart",style="crystal_metal",width=800,height=900,data=dict(base)))
    ovd = dict(base); ovd["luxury_theme_overrides"] = {"brightness":1.25,"contrast":1.30}
    ro = registry.render(RenderRequest(legend_type="radar_chart",style="crystal_metal",width=800,height=900,data=ovd))
    sb, so = pixel_stats(rb.content), pixel_stats(ro.content)
    save_image(rb, "P7_ov_cmp_base.png"); save_image(ro, "P7_ov_cmp_mod.png")
    delta = sum(abs(sb[k]-so[k]) for k in ["r","g","b"])
    print(f"       Base RGB: ({sb['r']:.1f},{sb['g']:.1f},{sb['b']:.1f}) Override: ({so['r']:.1f},{so['g']:.1f},{so['b']:.1f}) delta={delta:.2f}")
    assert delta > 0
run_test("[Override] Pixel difference confirmed", test_override_pixel_diff)

# ════════════════════════════════════════════
# 第八部分：GIF 动图 + 奢华主题
# ════════════════════════════════════════════
print("\n━" * 60)
print("  Part 8/11: GIF Animation + Luxury Theme")
print("━" * 60)

for tn in ["obsidian_gold","ruby_noir"]:
    def do_test(tn=tn):
        res = registry.render(RenderRequest(legend_type="court_shot_animation", style="pulse",
            data={"frame_count":10,"luxury_theme":tn,"luxury_theme_intensity":1.2}))
        assert res.media_type=="image/gif", f"Expected GIF got {res.media_type}"
        img = Image.open(BytesIO(res.content))
        frames = getattr(img,'n_frames',1)
        print(f"       GIF frames: {frames}")
        assert frames >= 8
        return save_image(res, f"P8_gif_{tn}.gif")
    run_test(f"[GIF+{tn}] pulse animation", do_test)

# ════════════════════════════════════════════
# 第九部分：有/无主题对比
# ════════════════════════════════════════════
print("\n━" * 60)
print("  Part 9/11: With/Without Theme Comparison")
print("━" * 60)

def test_theme_comparison():
    base_data = {"nodes":[
        {"id":"src","label":"Source","x":0.1,"y":0.5},{"id":"mid","label":"Mid","x":0.5,"y":0.35},
        {"id":"mid2","label":"Mid2","x":0.5,"y":0.65},{"id":"tgt","label":"Target","x":0.9,"y":0.5}],
        "flows":[
        {"source":"src","target":"mid","value":2500,"color":"#ff6b6b"},
        {"source":"src","target":"mid2","value":1800,"color":"#4ecdc4"},
        {"source":"mid","target":"tgt","value":2200,"color":"#45b7d1"},
        {"source":"mid2","target":"tgt","value":1600,"color":"#ffeaa7"}]}
    rn = registry.render(RenderRequest(legend_type="sankey_chart",style="golden_paths",width=1000,height=850,data=dict(base_data)))
    sn = pixel_stats(rn.content)
    save_image(rn, "P9_cmp_none.png")
    print(f"       {'Theme':<22} {'MeanR':>8} {'MeanG':>8} {'MeanB':>8} {'Std':>8} {'Delta':>10}")
    print(f"       {'(no theme)':<22} {sn['r']:8.1f} {sn['g']:8.1f} {sn['b']:8.1f} {sn['std']:8.1f} {'--':>10}")
    for tname, theme in LUXURY_THEMES.items():
        d = dict(base_data); d["luxury_theme"]=tname
        res = registry.render(RenderRequest(legend_type="sankey_chart",style="golden_paths",width=1000,height=850,data=d))
        st = pixel_stats(res.content)
        delta = sum(abs(sn[k]-st[k]) for k in ["r","g","b"])
        save_image(res, f"P9_cmp_{tname}.png")
        print(f"       {theme.display_name:<22} {st['r']:8.1f} {st['g']:8.1f} {st['b']:8.1f} {st['std']:8.1f} {delta:10.2f}")
run_test("[Compare] All 5 themes vs no-theme pixel stats", test_theme_comparison)

# ════════════════════════════════════════════
# 第十部分：HTTP API 接口测试
# ════════════════════════════════════════════
print("\n━" * 60)
print("  Part 10/11: HTTP POST /render API Tests")
print("━" * 60)

try:
    import httpx
    has_httpx = True
except ImportError:
    has_httpx = False; print("   [SKIP] httpx not installed, skipping API tests")

if has_httpx:
    def test_api_basic():
        with httpx.Client(timeout=120) as c:
            r = c.post("http://127.0.0.1:9001/render", json={"legend_type":"bar_chart","style":"glass_3d","width":800,"height":700,"data":{"labels":["A","B"],"values":[50,80]}})
            assert r.status_code==200
            return save_image(RenderResult(r.content,r.headers["content-type"],"png","",""), "P10_api_basic.png")
    run_test("[API] POST /render (no theme)", test_api_basic)

    for tn in ["obsidian_gold","champagne_ivory","ruby_noir"]:
        def do_test(tn=tn):
            with httpx.Client(timeout=120) as c:
                r = c.post("http://127.0.0.1:9001/render", json={"legend_type":"radar_chart","style":"neon_glow","width":900,"height":1000,
                    "data":{"categories":["A","B","C"],"datasets":[{"label":"T","values":[70,85,60],"color":"#ff006e"}],"luxury_theme":tn,"luxury_theme_intensity":1.3}})
                if r.status_code!=200: raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
                return save_image(RenderResult(r.content,r.headers["content-type"],"png","",""), f"P10_api_{tn}.png")
        run_test(f"[API] POST + {tn}", do_test)

    def test_api_themes_endpoint():
        with httpx.Client(timeout=30) as c:
            r = c.get("http://127.0.0.1:9001/luxury-themes")
            assert r.status_code==200
            themes = r.json(); assert len(themes)==5
            import json
            with open(os.path.join(OUTPUT_DIR,f"{NOW}_P10_themes.json"),"w",encoding="utf-8") as f: json.dump(themes,f,ensure_ascii=False,indent=2)
            print(f"       /luxury-themes returned {len(themes)} themes")
    run_test("[API] GET /luxury-themes endpoint", test_api_themes_endpoint)

    def test_api_get_query():
        with httpx.Client(timeout=120) as c:
            r = c.get("http://127.0.0.1:9001/render", params={"legend_type":"combo_chart","style":"ocean_depths","width":900,"height":750,"luxury_theme":"gold","luxury_theme_intensity":1.4})
            if r.status_code!=200: raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
            return save_image(RenderResult(r.content,r.headers["content-type"],"png","",""), "P10_api_get_query.png")
    run_test("[API] GET ?luxury_theme=gold query param", test_api_get_query)

    def test_api_unknown_theme():
        with httpx.Client(timeout=120) as c:
            r = c.post("http://127.0.0.1:9001/render", json={"legend_type":"bar_chart","style":"glass_3d","data":{"labels":["X"],"values":[42],"luxury_theme":"nonexistent_xyz"}})
            assert r.status_code==200, f"Unknown theme should gracefully degrade, got HTTP {r.status_code}"
    run_test("[API] Unknown theme name degrades gracefully", test_api_unknown_theme)

# ════════════════════════════════════════════
# 第十一部分：元数据完整性
# ════════════════════════════════════════════
print("\n━" * 60)
print("  Part 11/11: Metadata & Registry Integrity")
print("━" * 60)

def test_metadata():
    meta = luxury_theme_metadata()
    assert len(meta)==5
    required = {"name","display_name","description","brightness","contrast","saturation","sharpness","shadow_tint","highlight_tint","shadow_strength","highlight_strength","vignette_strength","border_color","border_width_ratio"}
    for m in meta:
        miss = required - set(m.keys())
        assert not miss, f"Missing fields in {m.get('name')}: {miss}"
    import json
    with open(os.path.join(OUTPUT_DIR,f"{NOW}_P11_metadata.json"),"w",encoding="utf-8") as f: json.dump(meta,f,ensure_ascii=False,indent=2)
    print(f"       5 themes x 14 fields all present")
run_test("[Meta] luxury_theme_metadata() complete", test_metadata)

def test_registry():
    types = registry.list_types()
    names = {t.legend_type for t in types}
    expected = {"court_shot","dual_court_shot","court_shot_animation","coordinate","plus_minus_coordinate","rose","table","points_location","radar_chart","dual_radar_chart","bar_chart","combo_chart","bubble_chart","sankey_chart"}
    assert not (expected-names); assert not (names-expected)
    total_styles = sum(len(t.styles) for t in types)
    print(f"       {len(types)} types registered, {total_styles} styles total")
run_test("[Registry] All 14 types registered", test_registry)

def test_aliases():
    assert len(THEME_ALIASES)==6
    for alias, full in THEME_ALIASES.items(): assert full in LUXURY_THEMES
    print(f"       Aliases: {dict(THEME_ALIASES)}")
run_test("[Aliases] All 6 aliases valid", test_aliases)

def test_off_values():
    assert len(OFF_VALUES)==6
    for v in OFF_VALUES: assert resolve_luxury_theme({"luxury_theme":v}) is None
    print(f"       OFF_VALUES: {set(OFF_VALUES)} all return None")
run_test("[OFF Values] All 6 OFF values return None", test_off_values)


# ════════════════════════════════════════════
# 最终报告
# ════════════════════════════════════════════
elapsed = time.time() - total_start
passed = sum(1 for r in results if r["ok"])
failed = len(results) - passed
total_kb = sum(r["size_kb"] for r in results if r["ok"])

print("\n" + "=" * 70)
print(f"  RESULT: {passed}/{len(results)} passed ({passed/len(results)*100:.0f}%) | {failed} failed | {total_kb:.0f} KB | {elapsed:.1f}s")
print("=" * 70)

if failed:
    print("\n  FAILED:")
    for r in results:
        if not r["ok"]: print(f"    X {r['name']}: {r['error']}")
else:
    print("\n  ALL TESTS PASSED!")

files = sorted(os.listdir(OUTPUT_DIR))
png_f = sum(1 for f in files if f.endswith(".png"))
gif_f = sum(1 for f in files if f.endswith(".gif"))
json_f = sum(1 for f in files if f.endswith(".json"))
print(f"\n  Output: {os.path.abspath(OUTPUT_DIR)}")
print(f"  Files: {len(files)} ({png_f} PNG + {gif_f} GIF + {json_f} JSON)")
print("=" * 70)
