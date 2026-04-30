#!/usr/bin/env python3
"""
Hermes AI Benchmark Intelligence — Chart Generator
Reads data/benchmark-data.yaml, outputs clean SVG charts.
"""

import yaml, os, math
from pathlib import Path

BASE = Path('/opt/data/hermes-ai-benchmark-intel')
DATA_FILE = BASE / 'data' / 'benchmark-data.yaml'

with open(DATA_FILE) as f:
    data = yaml.safe_load(f)

models = data['models']
benchmarks = {b['id']: b for b in data['benchmarks']}

def get_score(m, bench_id):
    for s in m['scores']:
        if s['benchmark'] == bench_id:
            return s['score']
    return None

def fmt(v, is_elo=False):
    if v is None: return '—'
    if is_elo: return str(int(v))
    return f"{v:.1f}"

# ─── CHART 1: Multi-benchmark grouped bars — key models, key benchmarks ───

def chart_1():
    """Grouped horizontal bars — DeepSeek V4 Pro/V4 Flash vs US frontier on 6 key benchmarks."""
    
    key_benches = [
        ('aa-intelligence-index', 'AA Intelligence Index', False),
        ('swe-bench-v', 'SWE-bench Verified', False),
        ('swe-bench-pro', 'SWE-bench Pro', False),
        ('mmlu-pro', 'MMLU-Pro', False),
        ('terminal-bench', 'Terminal-Bench 2.0', False),
        ('livecodebench', 'LiveCodeBench', False),
    ]
    
    show = ['DeepSeek V4 Pro (Max)', 'DeepSeek V4 Flash', 'Kimi K2.6 Thinking',
            'GPT-5.5 (xhigh)', 'Claude Opus 4.7 (max)', 'Gemini 3.1 Pro Preview']
    
    colors = ['#E86A17', '#F4A261', '#2A9D8F', '#264653', '#8338EC', '#3A86FF']
    
    # Layout
    bar_h = 22
    gap = 4
    group_gap = 40
    bar_area = 550
    left_margin = 200
    top_margin = 60
    right_margin = 30
    
    rows = len(key_benches)
    cols = len(show)
    row_h = cols * (bar_h + gap) + group_gap
    total_h = top_margin + rows * row_h + 40
    total_w = left_margin + bar_area + right_margin + 200  # extra for legend
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" style="background:#fff; font-family:Arial,Helvetica,sans-serif;">')
    svg.append(f'<rect width="100%" height="100%" fill="#fff"/>')
    
    # Title
    svg.append(f'<text x="{left_margin}" y="28" fill="#111" font-size="20" font-weight="bold">AI Benchmark Scores — April 30, 2026</text>')
    svg.append(f'<text x="{left_margin}" y="46" fill="#666" font-size="12">DeepSeek V4 lineup vs US frontier. Higher = better. Sources: AA, Vals AI, DeepSeek, VentureBeat.</text>')
    
    y = top_margin
    
    for bench_id, bench_name, is_elo in key_benches:
        scores = []
        for m in models:
            if m['name'] in show:
                s = get_score(m, bench_id)
                if s is not None:
                    scores.append(s)
        
        max_val = max(scores) if scores else 100
        
        # Scale: set max to 110% of actual max for breathing room
        scale_to = max_val * 1.1
        
        # Row label
        svg.append(f'<text x="{left_margin - 12}" y="{y + (cols * (bar_h + gap) - gap)//2 + 6}" text-anchor="end" fill="#333" font-size="14" font-weight="bold">{bench_name}</text>')
        
        for i, mn in enumerate(show):
            by = y + i * (bar_h + gap)
            score = get_score(next(m for m in models if m['name'] == mn), bench_id)
            
            bar_w = (score / scale_to) * bar_area if score else 0
            
            if score:
                svg.append(f'<rect x="{left_margin}" y="{by}" width="{bar_w:.0f}" height="{bar_h}" rx="3" fill="{colors[i]}" opacity="0.9"/>')
                # Score label
                label = fmt(score, is_elo)
                svg.append(f'<text x="{left_margin + bar_w + 6}" y="{by + bar_h//2 + 4}" fill="#333" font-size="12" font-weight="bold">{label}</text>')
            else:
                svg.append(f'<text x="{left_margin + 4}" y="{by + bar_h//2 + 4}" fill="#999" font-size="12">—</text>')
        
        y += cols * (bar_h + gap) + group_gap
    
    # Legend (top right area)
    lx = left_margin + bar_area + 40
    ly = top_margin + 10
    for i, mn in enumerate(show):
        short = mn.replace(' (Max)', '').replace(' (xhigh)', '').replace(' (max)', '').replace(' Preview', '').replace(' Thinking', '')
        svg.append(f'<rect x="{lx}" y="{ly + i*20}" width="14" height="14" rx="2" fill="{colors[i]}"/>')
        svg.append(f'<text x="{lx + 20}" y="{ly + i*20 + 12}" fill="#444" font-size="12">{short}</text>')
    
    svg.append('</svg>')
    
    return '\n'.join(svg)


# ─── CHART 2: DeepSeek lineup deep dive ───

def chart_2():
    """DeepSeek V4 Pro vs V4 Flash vs V3.2 vs Kimi K2.6 across all available benchmarks."""
    
    ds_models = ['DeepSeek V4 Pro (Max)', 'DeepSeek V4 Flash', 'DeepSeek V3.2', 'Kimi K2.6 Thinking']
    ds_colors = ['#E86A17', '#F4A261', '#D68C45', '#2A9D8F']
    
    # Collect all benchmarks these models have
    all_benches = set()
    for m in models:
        if m['name'] in ds_models:
            for s in m['scores']:
                all_benches.add(s['benchmark'])
    
    bench_list = []
    for bid in all_benches:
        meta = benchmarks.get(bid)
        if meta:
            # Check at least 3 of 4 models have a score
            count = sum(1 for m in models if m['name'] in ds_models and get_score(m, bid) is not None)
            if count >= 2:
                bench_list.append((bid, meta['name']))
    
    # Sort by coverage
    bench_list.sort(key=lambda x: -sum(1 for m in models if m['name'] in ds_models and get_score(m, x[0]) is not None))
    
    bar_h = 20
    gap = 3
    group_gap = 35
    bar_area = 500
    left_margin = 190
    top_margin = 60
    
    rows = len(bench_list)
    cols = len(ds_models)
    row_h = cols * (bar_h + gap) + group_gap
    total_h = top_margin + rows * row_h + 30
    total_w = left_margin + bar_area + 200
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" style="background:#fff; font-family:Arial,Helvetica,sans-serif;">')
    svg.append(f'<rect width="100%" height="100%" fill="#fff"/>')
    
    svg.append(f'<text x="{left_margin}" y="28" fill="#111" font-size="18" font-weight="bold">DeepSeek Lineup — Full Benchmark Breakdown</text>')
    svg.append(f'<text x="{left_margin}" y="46" fill="#666" font-size="12">V4 Pro vs V4 Flash vs V3.2 vs Kimi K2.6. Higher = better.</text>')
    
    y = top_margin
    
    for bid, bname in bench_list:
        is_elo = bid == 'arena-elo'
        scores_list = []
        for mn in ds_models:
            m = next(x for x in models if x['name'] == mn)
            scores_list.append(get_score(m, bid))
        
        valid = [s for s in scores_list if s is not None]
        max_val = max(valid) if valid else 100
        scale_to = max(max_val * 1.15, 100)
        
        svg.append(f'<text x="{left_margin - 12}" y="{y + (cols * (bar_h + gap) - gap)//2 + 5}" text-anchor="end" fill="#333" font-size="13" font-weight="bold">{bname}</text>')
        
        for i, (mn, score) in enumerate(zip(ds_models, scores_list)):
            by = y + i * (bar_h + gap)
            if score:
                bar_w = (score / scale_to) * bar_area
                svg.append(f'<rect x="{left_margin}" y="{by}" width="{bar_w:.0f}" height="{bar_h}" rx="3" fill="{ds_colors[i]}" opacity="0.9"/>')
                svg.append(f'<text x="{left_margin + bar_w + 5}" y="{by + bar_h//2 + 4}" fill="#333" font-size="11" font-weight="bold">{fmt(score, is_elo)}</text>')
            else:
                svg.append(f'<text x="{left_margin + 4}" y="{by + bar_h//2 + 4}" fill="#999" font-size="11">—</text>')
        
        y += cols * (bar_h + gap) + group_gap
    
    # Legend
    lx = left_margin + bar_area + 30
    ly = top_margin + 10
    for i, mn in enumerate(ds_models):
        short = mn.replace('DeepSeek ', 'DS ').replace(' (Max)', '')
        svg.append(f'<rect x="{lx}" y="{ly + i*20}" width="12" height="12" rx="2" fill="{ds_colors[i]}"/>')
        svg.append(f'<text x="{lx + 18}" y="{ly + i*20 + 10}" fill="#444" font-size="12">{short}</text>')
    
    svg.append('</svg>')
    return '\n'.join(svg)


# ─── CHART 3: Price comparison — simple bar chart ───

def chart_3():
    """Price comparison — output token cost per model, ordered by performance."""
    
    show = ['GPT-5.5 (xhigh)', 'Claude Opus 4.7 (max)', 'Gemini 3.1 Pro Preview',
            'GPT-5.4 (xhigh)', 'Kimi K2.6 Thinking', 'DeepSeek V4 Pro (Max)',
            'DeepSeek V3.2', 'MiMo V2.5 Pro', 'DeepSeek V4 Flash']
    
    bar_h = 24
    gap = 4
    left_margin = 220
    bar_area = 400
    top_margin = 60
    
    total_h = top_margin + len(show) * (bar_h + gap) + 60
    total_w = left_margin + bar_area + 250
    
    # Find max cost for scaling
    max_cost = 0
    for mn in show:
        m = next(x for x in models if x['name'] == mn)
        cost = m['pricing']['output_per_m'] + m['pricing']['input_per_m'] / 3
        max_cost = max(max_cost, cost)
    
    scale_to = max_cost * 1.15
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {total_h}" style="background:#fff; font-family:Arial,Helvetica,sans-serif;">')
    svg.append(f'<rect width="100%" height="100%" fill="#fff"/>')
    
    svg.append(f'<text x="{left_margin}" y="28" fill="#111" font-size="18" font-weight="bold">API Cost per Million Tokens — April 2026</text>')
    svg.append(f'<text x="{left_margin}" y="46" fill="#666" font-size="12">Blended cost: output + (input ÷ 3). Lower = cheaper.</text>')
    
    # Grid lines
    for v in range(0, int(max_cost) + 5, 5):
        x = left_margin + (v / scale_to) * bar_area
        svg.append(f'<line x1="{x:.0f}" y1="{top_margin - 10}" x2="{x:.0f}" y2="{top_margin + len(show)*(bar_h+gap)}" stroke="#eee" stroke-width="1"/>')
        svg.append(f'<text x="{x:.0f}" y="{top_margin - 16}" text-anchor="middle" fill="#999" font-size="10">${v}</text>')
    
    for i, mn in enumerate(show):
        m = next(x for x in models if x['name'] == mn)
        by = top_margin + i * (bar_h + gap)
        cost = m['pricing']['output_per_m'] + m['pricing']['input_per_m'] / 3
        
        bar_w = (cost / scale_to) * bar_area
        
        color = '#E86A17' if m['country'] == 'China' else '#264653'
        
        # Model label
        short = mn.replace(' (Max)', '').replace(' (xhigh)', '').replace(' Preview', '').replace(' (max)', '').replace(' Thinking', '')
        svg.append(f'<text x="{left_margin - 8}" y="{by + bar_h//2 + 4}" text-anchor="end" fill="#333" font-size="12" font-weight="bold">{short}</text>')
        
        # Bar
        svg.append(f'<rect x="{left_margin}" y="{by}" width="{bar_w:.0f}" height="{bar_h}" rx="3" fill="{color}" opacity="0.85"/>')
        
        # Cost label
        svg.append(f'<text x="{left_margin + bar_w + 6}" y="{by + bar_h//2 + 4}" fill="#333" font-size="12" font-weight="bold">${cost:.2f}/M</text>')
        
        # Flag
        flag = '🇨🇳' if m['country'] == 'China' else '🇺🇸'
        svg.append(f'<text x="{total_w - 20}" y="{by + bar_h//2 + 4}" text-anchor="end" fill="#999" font-size="11">{flag}</text>')
    
    svg.append(f'<text x="{left_margin}" y="{top_margin + len(show)*(bar_h+gap) + 20}" fill="#888" font-size="11">Light bars = Chinese open-weight. Dark bars = US closed frontier.</text>')
    svg.append('</svg>')
    
    return '\n'.join(svg)


# ─── Generate all ───
out_dir = BASE / 'reports' / 'daily'
out_dir.mkdir(parents=True, exist_ok=True)

# Chart 1
svg1 = chart_1()
html1 = f'<html><body style="margin:20px;background:#fff">{svg1}</body></html>'
with open(out_dir / 'chart-1-benchmarks.svg', 'w') as f:
    f.write(svg1)
with open(out_dir / 'chart-1-benchmarks.html', 'w') as f:
    f.write(html1)
print(f"✅ Chart 1: {out_dir / 'chart-1-benchmarks.html'}")

# Chart 2
svg2 = chart_2()
html2 = f'<html><body style="margin:20px;background:#fff">{svg2}</body></html>'
with open(out_dir / 'chart-2-deepseek-deep-dive.svg', 'w') as f:
    f.write(svg2)
with open(out_dir / 'chart-2-deepseek-deep-dive.html', 'w') as f:
    f.write(html2)
print(f"✅ Chart 2: {out_dir / 'chart-2-deepseek-deep-dive.html'}")

# Chart 3
svg3 = chart_3()
html3 = f'<html><body style="margin:20px;background:#fff">{svg3}</body></html>'
with open(out_dir / 'chart-3-pricing.svg', 'w') as f:
    f.write(svg3)
with open(out_dir / 'chart-3-pricing.html', 'w') as f:
    f.write(html3)
print(f"✅ Chart 3: {out_dir / 'chart-3-pricing.html'}")

print("\nDone — 3 clean SVG charts generated.")
