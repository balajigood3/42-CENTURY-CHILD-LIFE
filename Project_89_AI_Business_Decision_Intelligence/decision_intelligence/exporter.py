import json
from pathlib import Path

def export_json(result, path):
    Path(path).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

def export_markdown(result, path):
    lines = ["# Business Decision Analysis", "",
             f"**Recommended option:** {result['recommended_option']}",
             f"**Score gap to runner-up:** {result['score_gap_to_runner_up']}", "",
             "## Ranking", "| Rank | Option | Weighted score |", "|---:|---|---:|"]
    lines += [f"| {i} | {x['name']} | {x['total_score']:.4f} |"
              for i, x in enumerate(result["ranking"], 1)]
    lines += ["", "## Normalized weights"]
    lines += [f"- {k}: {v:.2%} ({result['criterion_directions'][k]})"
              for k, v in result["normalized_weights"].items()]
    lines += ["", "## Weighted contributions"]
    for item in result["ranking"]:
        lines += [f"### {item['name']}"]
        lines += [f"- {k}: {v:.4f}" for k, v in item["weighted_contributions"].items()]
    lines += ["", "## Method", result["method"], "", "## Caveats"]
    lines += [f"- {x}" for x in result["caveats"]]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
