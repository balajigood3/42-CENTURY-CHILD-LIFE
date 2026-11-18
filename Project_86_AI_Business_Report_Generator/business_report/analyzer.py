"""Local business metrics analysis and narrative report generation."""
from __future__ import annotations
import csv
from pathlib import Path

REQUIRED = {"period", "revenue", "expenses", "orders"}

def parse_csv_text(text):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("CSV content is empty.")
    reader = csv.DictReader(text.splitlines())
    if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
        raise ValueError("CSV must include period, revenue, expenses and orders columns.")
    rows = []
    for line_no, row in enumerate(reader, 2):
        try:
            period = row["period"].strip()
            revenue = float(row["revenue"])
            expenses = float(row["expenses"])
            orders = int(row["orders"])
        except (ValueError, TypeError, AttributeError) as exc:
            raise ValueError(f"Invalid numeric value or period on CSV line {line_no}.") from exc
        if not period or revenue < 0 or expenses < 0 or orders < 0:
            raise ValueError(f"Invalid negative or empty value on CSV line {line_no}.")
        rows.append({"period": period, "revenue": revenue, "expenses": expenses, "orders": orders})
    if not rows:
        raise ValueError("CSV must contain at least one data row.")
    return rows

def _pct_change(current, previous):
    if previous == 0:
        return None
    return round((current - previous) / abs(previous) * 100, 2)

def analyze_metrics(rows, report_title="Business Performance Report"):
    if not isinstance(rows, list) or not rows:
        raise ValueError("At least one metrics row is required.")
    normalized = []
    for row in rows:
        if not isinstance(row, dict) or not {"period", "revenue", "expenses", "orders"} <= row.keys():
            raise ValueError("Each row requires period, revenue, expenses and orders.")
        revenue, expenses, orders = float(row["revenue"]), float(row["expenses"]), int(row["orders"])
        if revenue < 0 or expenses < 0 or orders < 0:
            raise ValueError("Metrics cannot be negative.")
        normalized.append({"period": str(row["period"]), "revenue": revenue,
                           "expenses": expenses, "orders": orders})
    total_revenue = sum(x["revenue"] for x in normalized)
    total_expenses = sum(x["expenses"] for x in normalized)
    total_orders = sum(x["orders"] for x in normalized)
    profit = total_revenue - total_expenses
    margin = round(profit / total_revenue * 100, 2) if total_revenue else None
    first, last = normalized[0], normalized[-1]
    revenue_change = _pct_change(last["revenue"], first["revenue"]) if len(normalized) > 1 else None
    expense_change = _pct_change(last["expenses"], first["expenses"]) if len(normalized) > 1 else None
    order_change = _pct_change(last["orders"], first["orders"]) if len(normalized) > 1 else None
    avg_order_value = round(total_revenue / total_orders, 2) if total_orders else None
    insights = []
    if profit < 0:
        insights.append("Reported expenses exceed revenue across the selected periods.")
    else:
        insights.append("Reported revenue exceeds expenses across the selected periods.")
    if margin is not None:
        insights.append(f"Aggregate profit margin is {margin:.2f}%.")
    if revenue_change is not None:
        insights.append(f"Revenue changed by {revenue_change:.2f}% from {first['period']} to {last['period']}.")
    if expense_change is not None:
        insights.append(f"Expenses changed by {expense_change:.2f}% from {first['period']} to {last['period']}.")
    if order_change is not None:
        insights.append(f"Order volume changed by {order_change:.2f}% from {first['period']} to {last['period']}.")
    if not total_orders:
        insights.append("Average order value is unavailable because total orders are zero.")
    return {
        "report_title": report_title.strip() or "Business Performance Report",
        "periods": normalized,
        "kpis": {
            "total_revenue": round(total_revenue, 2),
            "total_expenses": round(total_expenses, 2),
            "profit": round(profit, 2),
            "profit_margin_percent": margin,
            "total_orders": total_orders,
            "average_order_value": avg_order_value,
            "revenue_change_percent_first_to_last": revenue_change,
            "expense_change_percent_first_to_last": expense_change,
            "order_change_percent_first_to_last": order_change
        },
        "insights": insights,
        "recommendations": [
            "Compare period-level trends with the approved budget and forecast.",
            "Investigate material changes in revenue, expenses and order volume.",
            "Segment performance by product, region and customer cohort before making decisions.",
            "Validate source data, accounting definitions and reporting periods."
        ],
        "limitations": [
            "This report describes only the supplied aggregate data.",
            "No causal explanation, forecast or financial assurance is produced.",
            "Currency and accounting basis are not inferred; label them before sharing."
        ]
    }
