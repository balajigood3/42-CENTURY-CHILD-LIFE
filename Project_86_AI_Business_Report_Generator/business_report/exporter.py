import json
from pathlib import Path

def export_json(report, path):
    Path(path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

def export_markdown(report, path):
    k = report["kpis"]
    lines = [f"# {report['report_title']}", "", "## Key performance indicators",
             f"- Total revenue: {k['total_revenue']:,.2f}",
             f"- Total expenses: {k['total_expenses']:,.2f}",
             f"- Profit: {k['profit']:,.2f}",
             f"- Profit margin: {k['profit_margin_percent'] if k['profit_margin_percent'] is not None else 'N/A'}%",
             f"- Total orders: {k['total_orders']}",
             f"- Average order value: {k['average_order_value'] if k['average_order_value'] is not None else 'N/A'}",
             "", "## Period data", "| Period | Revenue | Expenses | Orders |",
             "|---|---:|---:|---:|"]
    lines += [f"| {x['period']} | {x['revenue']:,.2f} | {x['expenses']:,.2f} | {x['orders']} |"
              for x in report["periods"]]
    lines += ["", "## Insights"] + [f"- {x}" for x in report["insights"]]
    lines += ["", "## Recommendations"] + [f"- {x}" for x in report["recommendations"]]
    lines += ["", "## Limitations"] + [f"- {x}" for x in report["limitations"]]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
