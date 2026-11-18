import json
import pytest
from business_report.analyzer import parse_csv_text, analyze_metrics
from business_report.exporter import export_json, export_markdown

CSV = """period,revenue,expenses,orders
Jan,1000,700,10
Feb,1200,800,12
"""

def test_parse_csv_rows():
    assert len(parse_csv_text(CSV)) == 2

def test_missing_column_rejected():
    with pytest.raises(ValueError):
        parse_csv_text("period,revenue\nJan,100")

def test_invalid_numeric_rejected():
    with pytest.raises(ValueError):
        parse_csv_text("period,revenue,expenses,orders\nJan,abc,10,2")

def test_negative_values_rejected():
    with pytest.raises(ValueError):
        parse_csv_text("period,revenue,expenses,orders\nJan,-1,10,2")

def test_aggregate_kpis():
    report = analyze_metrics(parse_csv_text(CSV))
    assert report["kpis"]["total_revenue"] == 2200
    assert report["kpis"]["profit"] == 700
    assert report["kpis"]["total_orders"] == 22

def test_margin_calculation():
    report = analyze_metrics(parse_csv_text(CSV))
    assert report["kpis"]["profit_margin_percent"] == 31.82

def test_first_to_last_growth():
    report = analyze_metrics(parse_csv_text(CSV))
    assert report["kpis"]["revenue_change_percent_first_to_last"] == 20.0

def test_zero_revenue_margin_is_none():
    report = analyze_metrics([{"period": "Jan", "revenue": 0, "expenses": 0, "orders": 0}])
    assert report["kpis"]["profit_margin_percent"] is None
    assert report["kpis"]["average_order_value"] is None

def test_empty_rows_rejected():
    with pytest.raises(ValueError):
        analyze_metrics([])

def test_negative_metric_rejected():
    with pytest.raises(ValueError):
        analyze_metrics([{"period": "Jan", "revenue": 1, "expenses": -2, "orders": 1}])

def test_json_export(tmp_path):
    report = analyze_metrics(parse_csv_text(CSV))
    path = tmp_path / "report.json"
    export_json(report, path)
    assert json.loads(path.read_text())["kpis"]["profit"] == 700

def test_markdown_export(tmp_path):
    report = analyze_metrics(parse_csv_text(CSV))
    path = tmp_path / "report.md"
    export_markdown(report, path)
    assert "Key performance indicators" in path.read_text()
