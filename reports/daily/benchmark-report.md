# 🤖 AI Benchmark Intelligence — April 30, 2026

*Weekly snapshot from authoritative sources. Data as of Apr 28-30.*

---

## 🏆 Current Landscape

| Model | AA Index | SWE-bench V | SWE-Pro | Price/M (in+out/3) | Type |
|-------|----------|-------------|---------|-------------------|------|
| 🔒 GPT-5.5 (xhigh)                |   60 |  82.6 |  58.6 | $$15.00 | frontier-closed |
| 🔒 Claude Opus 4.7 (max)          |   57 |  82.0 |  64.3 | $$13.33 | frontier-closed |
| 🔒 Gemini 3.1 Pro Preview         |   57 |  78.8 |     — | $ $5.83 | frontier-closed |
| 🔒 GPT-5.4 (xhigh)                |   57 |  78.2 |     — | $$13.33 | frontier-closed |
| 🔓 DeepSeek V4 Pro (Max)          |   52 |  80.6 |  55.4 | $ $2.32 | open-weight |
| 🔓 DeepSeek V4 Flash              |   47 |  79.0 |     — | $ $0.23 | open-weight |
| 🔓 DeepSeek V3.2                  |    — |  73.0 |  48.0 | $ $0.43 | open-weight |
| 🔓 Kimi K2.6 Thinking             |   54 |  74.5 |  58.6 | $ $1.43 | open-weight |
| 🔓 MiMo V2.5 Pro                  |   54 |  78.0 |     — | $ $0.50 | open-weight |
| 🔓 Qwen 3.5 27B                   |    — |     — |     — | $ $0.25 | open-weight |

*Legend: 🔒 = US Closed, 🔓 = Open-Weight / Chinese*

---

## 🎯 Key Takeaways

1. **GPT-5.5 takes the lead** on AA Intelligence Index (60) — first time any model crosses 60. But Claude Opus 4.7 matches it on human preference (1504 Elo).
2. **DeepSeek V4 Pro** scores 52 AA Index, 87.5% MMLU-Pro — matches GPT-5.4 on knowledge tasks. SWE-bench Pro at 55.4% trails Opus 4.7 (64.3%) but costs **1/6th**.
3. **DeepSeek V4 Flash** is the sleeper hit: 79.0% SWE-bench Verified at **$0.14/$0.28 per million tokens**. That's 1/35th the cost of GPT-5.5. With 90% cache-hit discounts, effective cost drops to ~$0.014/M for input.
4. **Kimi K2.6** is the top open-weight model on AA Index (54) and Vals Index (63.9%). SWE-bench Pro 58.6% matches GPT-5.4 on the harder benchmark at 1/42nd the output cost.
5. **Cost gap is widening, not narrowing.** Chinese open-weight models now deliver 85-98% of frontier performance at 5-40× less cost. The value frontier has shifted dramatically.

---

## 📚 Authoritative Sources

- [artificial_analysis](https://artificialanalysis.ai/leaderboards/models)
- [vals_ai](https://www.vals.ai/benchmarks)
- [lm_arena](https://lmarena.ai)
- [price_per_token](https://pricepertoken.com)
- [deepseek_official](https://api-docs.deepseek.com/quick_start/pricing)
- [hf_deepseek_v4](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro)
- [datacamp](https://www.datacamp.com/blog/deepseek-v4)
- [officechai](https://officechai.com/ai/deepseek-v4-pro-deepseek-v4-flash-benchmarks-pricing/)
- [venturebeat](https://venturebeat.com/technology/deepseek-v4-arrives-with-near-state-of-the-art-intelligence-at-1-6th-the-cost-of-opus-4-7-gpt-5-5)
- [ofox](https://ofox.ai/blog/llm-leaderboard-best-ai-models-ranked-2026/)
- [buildfastwithai](https://www.buildfastwithai.com/blogs/best-ai-models-leaderboard-april-2026-updated)
- [codersera](https://codersera.com/blog/deepseek-v4-flash-deep-dive/)
- [felloai](https://felloai.com/deepseek-pricing/)
- [swebench_official](https://www.swebench.com/)
- [hf_lmarena](https://huggingface.co/spaces/lmarena-ai/arena-leaderboard)
- [marc0dev](https://www.marc0.dev/en/leaderboard)
- [llm_stats](https://llm-stats.com)

---

## 🗓 Weekly Refresh

Next pull: Monday, May 4, 2026 via cron
*Charts regenerated from: `data/benchmark-data.yaml` → `scripts/generate-benchmark-report.py`*