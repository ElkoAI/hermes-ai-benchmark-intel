#!/usr/bin/env python3
"""
Benchmark Report Generator — April 2026
Pulls from benchmark-data.yaml and generates:
1. Multi-benchmark grouped bar chart (focused: DeepSeek vs US frontier)
2. Cost vs Performance scatter chart
3. Readable markdown summary for email reports

Authoritative sources:
- Artificial Analysis: https://artificialanalysis.ai/leaderboards/models
- Vals AI: https://www.vals.ai/benchmarks
- LM Arena: https://lmarena.ai
- PricePerToken: https://pricepertoken.com
"""

import yaml
import os
from pathlib import Path

BASE_DIR = Path('/opt/data/60632-archer-heights')
DATA_FILE = BASE_DIR / 'data' / 'benchmark-data.yaml'
OUT_DIR = BASE_DIR / 'reports' / 'daily'

with open(DATA_FILE) as f:
    data = yaml.safe_load(f)

models = data['models']
benchmarks = data['benchmarks']

# ─── Color palette ───
COLORS = {
    'GPT-5.5 (xhigh)':        '#10A37F',
    'Claude Opus 4.7 (max)':  '#A362FF',
    'Gemini 3.1 Pro Preview': '#4285F4',
    'GPT-5.4 (xhigh)':        '#7CCF9E',
    'DeepSeek V4 Pro (Max)':  '#FF6B35',
    'DeepSeek V4 Flash':      '#FF9F6E',
    'DeepSeek V3.2':          '#FFB896',
    'Kimi K2.6 Thinking':     '#00B4D8',
    'MiMo V2.5 Pro':          '#90BE6D',
    'Qwen 3.5 27B':           '#F9C74F',
}

def fmt_score(v):
    if isinstance(v, int) and v > 200:
        return str(v)
    return f"{v:.1f}"

def build_multi_bench_chart():
    """Grouped bar chart: DeepSeek lineup vs US frontier on key benchmarks."""
    
    # Benchmarks to show (ones with good cross-model coverage)
    target_benches = [
        'aa-intelligence-index', 'arena-elo', 'swe-bench-v',
        'swe-bench-pro', 'terminal-bench', 'mmlu-pro', 'gpqa-diamond', 'livecodebench'
    ]
    
    # Filter to benchmarks we actually have data for
    bench_configs = []
    for b in target_benches:
        meta = next((x for x in benchmarks if x['id'] == b), None)
        if meta:
            # Check if at least 3 models have this score
            count = sum(1 for m in models if any(s['benchmark'] == b for s in m['scores']))
            if count >= 3:
                bench_configs.append((b, meta['name']))
    
    # Models to show (key players)
    show_models = [
        'GPT-5.5 (xhigh)', 'Claude Opus 4.7 (max)', 'Gemini 3.1 Pro Preview',
        'DeepSeek V4 Pro (Max)', 'DeepSeek V4 Flash', 'Kimi K2.6 Thinking',
        'DeepSeek V3.2'
    ]
    
    def get_score(model_name, bench_id):
        m = next((x for x in models if x['name'] == model_name), None)
        if not m:
            return None
        for s in m['scores']:
            if s['benchmark'] == bench_id:
                return s['score']
        return None
    
    # Build data matrix: rows=benchmarks, cols=models
    matrix = []
    for bid, bname in bench_configs:
        row = [bname, bid]
        for mn in show_models:
            row.append(get_score(mn, bid))
        matrix.append(row)
    
    # ─── SVG Generation ───
    bar_h = 28
    gap = 6
    margin_left = 180
    margin_right = 50
    margin_top = 50
    margin_bottom = 30
    col_w = len(show_models) * (bar_h + gap)
    row_gap = 60
    
    total_h = margin_top + margin_bottom + len(matrix) * (col_w + row_gap)
    
    # Find max score for scaling
    all_scores = [v for row in matrix for v in row[2:] if v is not None]
    max_score = max(all_scores)
    
    # Scale: some are Elo (1400-1510) and some are percentages (0-100)
    # Need to normalize. AA Index is 0-60. SWE-bench is 0-100. Elo is 1300-1550.
    # We'll use linear scale per row
    bar_area_w = 700
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {margin_left + bar_area_w + margin_right} {total_h}"')
    svg.append('     style="background:#0D1117; font-family:system-ui,-apple-system,sans-serif;">')
    svg.append(f'<rect width="100%" height="100%" fill="#0D1117"/>')
    
    # Title
    svg.append(f'<text x="{margin_left + bar_area_w//2}" y="28" text-anchor="middle" fill="#E6EDF3" font-size="18" font-weight="bold">')
    svg.append('  AI Model Benchmarks — April 2026 (DeepSeek V4 vs US Frontier)')
    svg.append('</text>')
    svg.append(f'<text x="{margin_left + bar_area_w//2}" y="44" text-anchor="middle" fill="#8B949E" font-size="11">')
    svg.append('  Sources: Artificial Analysis · Vals AI · LM Arena · DeepSeek Official · VentureBeat')
    svg.append('</text>')
    
    y = margin_top
    
    for row_idx, row in enumerate(matrix):
        bname, bid = row[0], row[1]
        scores = row[2:]
        
        is_elo = bid == 'arena-elo'
        if is_elo:
            # Elo: shift to 0-based from 1350
            baseline = 1350
            ceiling = 1520
            range_ = ceiling - baseline
            col_scale = lambda v: ((v - baseline) / range_) * bar_area_w if v else 0
        else:
            max_row = max(v for v in scores if v is not None)
            col_scale = lambda v: (v / 120) * bar_area_w if v else 0
        
        # Row label
        svg.append(f'<text x="{margin_left - 10}" y="{y + col_w//2 + 5}" text-anchor="end" fill="#E6EDF3" font-size="13" font-weight="bold">')
        svg.append(f'  {bname}')
        svg.append('</text>')
        
        for mi, (mn, score) in enumerate(zip(show_models, scores)):
            bx = margin_left
            by = y + mi * (bar_h + gap)
            
            color = COLORS.get(mn, '#888')
            
            if score is not None:
                if is_elo:
                    bw = col_scale(score)
                else:
                    bw = col_scale(score)
                
                # Bar
                svg.append(f'<rect x="{bx}" y="{by}" width="{bw:.0f}" height="{bar_h}" rx="4" fill="{color}" opacity="0.85"/>')
                
                # Label inside bar or after
                label = fmt_score(score) if not is_elo else str(int(score))
                if bw > 50:
                    svg.append(f'<text x="{bx + bw - 4}" y="{by + bar_h//2 + 1}" text-anchor="end" fill="#fff" font-size="10" font-weight="bold">{label}</text>')
                else:
                    svg.append(f'<text x="{bx + bw + 4}" y="{by + bar_h//2 + 1}" text-anchor="start" fill="#E6EDF3" font-size="10">{label}</text>')
            else:
                # No data
                svg.append(f'<text x="{bx + 4}" y="{by + bar_h//2 + 1}" fill="#8B949E" font-size="10">—</text>')
        
        # Model legend for this row (on the right)
        for mi, mn in enumerate(show_models):
            lx = margin_left + bar_area_w + 15
            ly = y + mi * (bar_h + gap) + bar_h//2 + 1
            color = COLORS.get(mn, '#888')
            svg.append(f'<circle cx="{lx}" cy="{ly - 5}" r="5" fill="{color}"/>')
        
        y += col_w + row_gap
    
    # Footer legend
    y += 10
    svg.append(f'<text x="{margin_left}" y="{y}" fill="#8B949E" font-size="10">')
    svg.append('  ● US Closed Frontier    ● Chinese Open-Weight')
    svg.append('</text>')
    
    # Source links
    y += 20
    svg.append(f'<text x="{margin_left}" y="{y}" fill="#8B949E" font-size="9" font-style="italic">')
    svg.append('  Data as of April 28-30, 2026. Scores from Artificial Analysis, Vals AI, LM Arena, and vendor reports.')
    svg.append('</text>')
    
    svg.append('</svg>')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="theme-color" content="#0D1117">
<title>AI Benchmark Report — April 2026</title>
<style>
  body {{ margin: 0; background: #0D1117; display: flex; justify-content: center; padding: 20px; }}
  svg {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>
{''.join(svg)}
</body>
</html>'''
    
    out_path = OUT_DIR / 'chart-benchmark-report.html'
    with open(out_path, 'w') as f:
        f.write(html)
    print(f"✅ Chart written: {out_path}")


def build_cost_perf_chart():
    """Cost vs Performance scatter chart."""
    
    # Only models with sufficient benchmark coverage
    target_models = [
        'GPT-5.5 (xhigh)', 'Claude Opus 4.7 (max)', 'Gemini 3.1 Pro Preview',
        'GPT-5.4 (xhigh)', 'DeepSeek V4 Pro (Max)', 'DeepSeek V4 Flash',
        'DeepSeek V3.2', 'Kimi K2.6 Thinking', 'MiMo V2.5 Pro'
    ]
    
    # Compute average SWE-bench score for each model
    model_data = []
    for mn in target_models:
        m = next((x for x in models if x['name'] == mn), None)
        if not m:
            continue
        
        # Get AA Index (best single performance metric)
        aa = None
        for s in m['scores']:
            if s['benchmark'] == 'aa-intelligence-index':
                aa = s['score']
        
        # Get avg coding score
        swe_scores = []
        for s in m['scores']:
            if s['benchmark'] in ('swe-bench-v', 'swe-bench-pro'):
                swe_scores.append(s['score'])
        avg_swe = sum(swe_scores) / len(swe_scores) if swe_scores else None
        
        # Combined cost (input + output, 3:1 ratio typical)
        cost = m['pricing']['input_per_m'] + m['pricing']['output_per_m'] / 3
        
        model_data.append({
            'name': mn.replace(' (Max)', '').replace(' (xhigh)', '').replace(' Preview', '').replace(' (max)', '').replace(' Thinking', ''),
            'name_full': mn,
            'aa': aa,
            'avg_swe': avg_swe,
            'cost': cost,
            'color': COLORS.get(mn, '#888'),
            'provider': m['provider'],
            'country': m['country']
        })
    
    # Scatter plot SVG
    w, h = 800, 650
    pad_left, pad_right = 80, 40
    pad_top, pad_bot = 60, 60
    plot_w = w - pad_left - pad_right
    plot_h = h - pad_top - pad_bot
    
    # Filter to models with AA score
    chart_data = [d for d in model_data if d['aa'] is not None]
    
    if not chart_data:
        print("⚠ No models with AA scores for scatter chart")
        return
    
    min_aa = min(d['aa'] for d in chart_data) - 1
    max_aa = max(d['aa'] for d in chart_data) + 1
    min_cost = 0
    max_cost = max(d['cost'] for d in chart_data) * 1.1
    
    def x_pos(v):
        return pad_left + ((v - min_aa) / (max_aa - min_aa)) * plot_w
    
    def y_pos(v):
        return pad_top + (1 - v / max_cost) * plot_h
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"')
    svg.append('     style="background:#0D1117; font-family:system-ui,-apple-system,sans-serif;">')
    svg.append(f'<rect width="100%" height="100%" fill="#0D1117"/>')
    
    # Title
    svg.append(f'<text x="{w//2}" y="25" text-anchor="middle" fill="#E6EDF3" font-size="18" font-weight="bold">')
    svg.append('  Performance vs Cost — April 2026')
    svg.append('</text>')
    svg.append(f'<text x="{w//2}" y="42" text-anchor="middle" fill="#8B949E" font-size="11">')
    svg.append('  X: AA Intelligence Index (higher = smarter) · Y: API Cost per 1M tokens (lower = cheaper)')
    svg.append('</text>')
    
    # Grid lines
    nx, ny = 5, 5
    for i in range(nx + 1):
        x = pad_left + i * plot_w / nx
        val = min_aa + i * (max_aa - min_aa) / nx
        svg.append(f'<line x1="{x:.0f}" y1="{pad_top}" x2="{x:.0f}" y2="{pad_top + plot_h}" stroke="#1E2433" stroke-width="1"/>')
        svg.append(f'<text x="{x:.0f}" y="{pad_top + plot_h + 18}" text-anchor="middle" fill="#8B949E" font-size="10">{val:.0f}</text>')
    
    for i in range(ny + 1):
        y = pad_top + i * plot_h / ny
        val = max_cost - i * max_cost / ny
        svg.append(f'<line x1="{pad_left}" y1="{y:.0f}" x2="{pad_left + plot_w}" y2="{y:.0f}" stroke="#1E2433" stroke-width="1"/>')
        svg.append(f'<text x="{pad_left - 8}" y="{y + 4:.0f}" text-anchor="end" fill="#8B949E" font-size="10">${val:.1f}</text>')
    
    # Axis labels
    svg.append(f'<text x="{pad_left + plot_w//2}" y="{pad_top + plot_h + 42}" text-anchor="middle" fill="#8B949E" font-size="12">AA Intelligence Index →</text>')
    
    # Data points
    for d in chart_data:
        cx = x_pos(d['aa'])
        cy = y_pos(d['cost'])
        r = 8
        is_china = d['country'] == 'China'
        
        # Circle
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{d["color"]}" opacity="0.85" stroke="#fff" stroke-width="1.5"/>')
        
        # Label
        lx = cx + r + 6
        ly = cy + 4
        svg.append(f'<text x="{lx:.0f}" y="{ly:.0f}" fill="#E6EDF3" font-size="11" font-weight="bold">{d["name"]}</text>')
        
        # Sub-label: AA score and cost
        svg.append(f'<text x="{lx:.0f}" y="{ly + 14}" fill="#8B949E" font-size="9">AA {d["aa"]} · ${d["cost"]:.2f}/M</text>')
    
    svg.append('</svg>')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="theme-color" content="#0D1117">
<title>AI Cost vs Performance — April 2026</title>
<style>
  body {{ margin: 0; background: #0D1117; display: flex; justify-content: center; padding: 20px; }}
  svg {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>
{''.join(svg)}
</body>
</html>'''
    
    out_path = OUT_DIR / 'chart-cost-vs-performance.html'
    with open(out_path, 'w') as f:
        f.write(html)
    print(f"✅ Cost-vs-perf chart written: {out_path}")


def build_deepseek_deep_dive():
    """DeepSeek-only deep dive: V4 Pro vs V4 Flash vs V3.2 across all available benchmarks."""
    
    ds_models = [
        'DeepSeek V4 Pro (Max)', 'DeepSeek V4 Flash', 'DeepSeek V3.2', 'Kimi K2.6 Thinking'
    ]
    
    # Collect all unique benchmarks
    all_benches = set()
    for m in models:
        if m['name'] in ds_models:
            for s in m['scores']:
                all_benches.add(s['benchmark'])
    
    bench_list = []
    for bid in all_benches:
        meta = next((x for x in benchmarks if x['id'] == bid), None)
        if meta:
            bench_list.append((bid, meta['name']))
    
    bench_list.sort(key=lambda x: len(
        [m for m in models if m['name'] in ds_models and any(s['benchmark'] == x[0] for s in m['scores'])]
    ), reverse=True)
    
    w, h = 900, 400
    bar_h = 24
    gap = 5
    margin_l = 160
    
    def get_score(mn, bid):
        m = next((x for x in models if x['name'] == mn), None)
        if not m:
            return None
        for s in m['scores']:
            if s['benchmark'] == bid:
                return s['score']
        return None
    
    rows = []
    for bid, bname in bench_list:
        scores = [get_score(mn, bid) for mn in ds_models]
        if any(s is not None for s in scores):
            rows.append((bname, bid, scores))
    
    col_w = (bar_h + gap) * len(ds_models)
    chart_h = 60 + len(rows) * (col_w + 50)
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {chart_h}"')
    svg.append('     style="background:#0D1117; font-family:system-ui,-apple-system,sans-serif;">')
    svg.append(f'<rect width="100%" height="100%" fill="#0D1117"/>')
    
    svg.append(f'<text x="{w//2}" y="25" text-anchor="middle" fill="#E6EDF3" font-size="16" font-weight="bold">')
    svg.append('  DeepSeek Lineup Deep Dive — April 2026')
    svg.append('</text>')
    
    y = 50
    bar_area = w - margin_l - 20
    
    for bname, bid, scores in rows:
        # Skip Elo for this view
        if bid == 'arena-elo':
            continue
        
        is_elo = bid == 'arena-elo'
        
        max_row = max(v for v in scores if v is not None)
        col_scale = lambda v: (v / 110) * bar_area if v else 0
        
        svg.append(f'<text x="{margin_l - 10}" y="{y + col_w//2 + 5}" text-anchor="end" fill="#E6EDF3" font-size="12" font-weight="bold">{bname}</text>')
        
        for mi, (mn, score) in enumerate(zip(ds_models, scores)):
            bx = margin_l
            by = y + mi * (bar_h + gap)
            color = COLORS.get(mn, '#888')
            
            if score is not None:
                bw = col_scale(score)
                svg.append(f'<rect x="{bx}" y="{by}" width="{bw:.0f}" height="{bar_h}" rx="4" fill="{color}" opacity="0.85"/>')
                label = fmt_score(score)
                if bw > 40:
                    svg.append(f'<text x="{bx + bw - 4}" y="{by + bar_h//2 + 1}" text-anchor="end" fill="#fff" font-size="10" font-weight="bold">{label}</text>')
                else:
                    svg.append(f'<text x="{bx + bw + 4}" y="{by + bar_h//2 + 1}" text-anchor="start" fill="#E6EDF3" font-size="10">{label}</text>')
        
        # Right labels
        for mi, mn in enumerate(ds_models):
            lx = margin_l + bar_area + 8
            ly = y + mi * (bar_h + gap) + bar_h//2 + 1
            color = COLORS.get(mn, '#888')
            svg.append(f'<circle cx="{lx}" cy="{ly - 4}" r="4" fill="{color}"/>')
            svg.append(f'<text x="{lx + 10}" y="{ly}" fill="#8B949E" font-size="10">{mn.replace("DeepSeek ", "DS ")}</text>')
        
        y += col_w + 50
    
    svg.append('</svg>')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="theme-color" content="#0D1117">
<title>DeepSeek Deep Dive — April 2026</title>
<style>
  body {{ margin: 0; background: #0D1117; display: flex; justify-content: center; padding: 20px; }}
  svg {{ max-width: 100%; height: auto; }}
</style>
</head>
<body>
{''.join(svg)}
</body>
</html>'''
    
    out_path = OUT_DIR / 'chart-deepseek-deep-dive.html'
    with open(out_path, 'w') as f:
        f.write(html)
    print(f"✅ DeepSeek deep dive written: {out_path}")


def generate_markdown_summary():
    """Markdown summary for email/Telegram reports."""
    
    lines = []
    lines.append("# 🤖 AI Benchmark Intelligence — April 30, 2026\n")
    lines.append("*Weekly snapshot from authoritative sources. Data as of Apr 28-30.*\n")
    lines.append("---\n")
    
    # ── Top line ──
    lines.append("## 🏆 Current Landscape\n")
    
    gpt55 = next(m for m in models if m['name'] == 'GPT-5.5 (xhigh)')
    opus47 = next(m for m in models if m['name'] == 'Claude Opus 4.7 (max)')
    ds_v4 = next(m for m in models if m['name'] == 'DeepSeek V4 Pro (Max)')
    kimi = next(m for m in models if m['name'] == 'Kimi K2.6 Thinking')
    ds_flash = next(m for m in models if m['name'] == 'DeepSeek V4 Flash')
    
    lines.append(f"| Model | AA Index | SWE-bench V | SWE-Pro | Price/M (in+out/3) | Type |")
    lines.append(f"|-------|----------|-------------|---------|-------------------|------|")
    
    def get_score_val(m, bid):
        for s in m['scores']:
            if s['benchmark'] == bid:
                return s['score']
        return '—'
    
    def cost_line(m):
        combined = m['pricing']['input_per_m'] + m['pricing']['output_per_m'] / 3
        return f"${combined:.2f}"
    
    for m in models:
        aa = get_score_val(m, 'aa-intelligence-index')
        swe_v = get_score_val(m, 'swe-bench-v')
        swe_p = get_score_val(m, 'swe-bench-pro')
        c = cost_line(m)
        t = m['type']
        src_emoji = '🔒' if m['country'] == 'US' else '🔓'
        def fmt_bench(val):
            return str(val) if val != '—' else '—'
        aa_str = fmt_bench(aa)
        swe_v_str = fmt_bench(swe_v)
        swe_p_str = fmt_bench(swe_p)
        lines.append(f"| {src_emoji} {m['name']:30s} | {aa_str:>4s} | {swe_v_str:>5s} | {swe_p_str:>5s} | ${c:>6s} | {t} |")
    
    lines.append("")
    lines.append("*Legend: 🔒 = US Closed, 🔓 = Open-Weight / Chinese*\n")
    lines.append("---\n")
    
    # ── Key takeaways ──
    lines.append("## 🎯 Key Takeaways\n")
    lines.append("1. **GPT-5.5 takes the lead** on AA Intelligence Index (60) — first time any model crosses 60. But Claude Opus 4.7 matches it on human preference (1504 Elo).")
    lines.append(f"2. **DeepSeek V4 Pro** scores {get_score_val(ds_v4, 'aa-intelligence-index')} AA Index, {get_score_val(ds_v4, 'mmlu-pro')}% MMLU-Pro — matches GPT-5.4 on knowledge tasks. SWE-bench Pro at {get_score_val(ds_v4, 'swe-bench-pro')}% trails Opus 4.7 ({get_score_val(opus47, 'swe-bench-pro')}%) but costs **1/6th**.")
    lines.append(f"3. **DeepSeek V4 Flash** is the sleeper hit: {get_score_val(ds_flash, 'swe-bench-v')}% SWE-bench Verified at **$0.14/$0.28 per million tokens**. That's 1/35th the cost of GPT-5.5. With 90% cache-hit discounts, effective cost drops to ~$0.014/M for input.")
    lines.append(f"4. **Kimi K2.6** is the top open-weight model on AA Index (54) and Vals Index (63.9%). SWE-bench Pro {get_score_val(kimi, 'swe-bench-pro')}% matches GPT-5.4 on the harder benchmark at 1/42nd the output cost.")
    lines.append(f"5. **Cost gap is widening, not narrowing.** Chinese open-weight models now deliver 85-98% of frontier performance at 5-40× less cost. The value frontier has shifted dramatically.")
    lines.append("")
    lines.append("---\n")
    lines.append("## 📚 Authoritative Sources\n")
    
    for src_name, src_url in data['meta']['sources'].items():
        lines.append(f"- [{src_name}]({src_url})")
    
    lines.append("")
    lines.append("---\n")
    lines.append("## 🗓 Weekly Refresh\n")
    lines.append("Next pull: Monday, May 4, 2026 via cron")
    lines.append("*Charts regenerated from: `data/benchmark-data.yaml` → `scripts/generate-benchmark-report.py`*")
    
    return '\n'.join(lines)


# ─── Run all ───
OUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("BENCHMARK REPORT GENERATOR — April 2026")
print("=" * 60)

build_multi_bench_chart()
build_cost_perf_chart()
build_deepseek_deep_dive()

md = generate_markdown_summary()
md_path = OUT_DIR / 'benchmark-report.md'
with open(md_path, 'w') as f:
    f.write(md)
print(f"✅ Markdown summary written: {md_path}")

print()
print("All outputs generated. Open in browser:")
for f in sorted(OUT_DIR.glob('chart-*.html')):
    print(f"  📊 {f.name}")
