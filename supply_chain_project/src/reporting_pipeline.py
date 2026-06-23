import sys
sys.path.insert(0, "supply_chain/src")
import pandas as pd
from pathlib import Path
from analysis import (executive_summary, vendor_scorecard, logistics_kpis,
                      stock_status_summary, stockout_risk_skus,
                      demand_vs_supply, best_worst_vendors)

def run_pipeline():
    lines = []
    def out(text=""):
        print(text); lines.append(text)

    out("="*72)
    out("  SUPPLY CHAIN — AUTOMATED KPI REPORT  |  2024")
    out("="*72)

    kpis = executive_summary()
    out("\n[ EXECUTIVE SUMMARY ]")
    for label, val in [
        ("Total SKUs", kpis["total_skus"]),
        ("Stockouts", kpis["stockout_count"]),
        ("Low-stock SKU-warehouses", kpis["low_stock_count"]),
        ("Overstock SKU-warehouses", kpis["overstock_count"]),
        ("On-Time Delivery", f"{kpis['otd_rate_pct']}%"),
        ("Fill Rate", f"{kpis['fill_rate_pct']}%"),
        ("Avg Lead Time", f"{kpis['avg_lead_days']} days"),
        ("Total Spend", f"${kpis['total_spend_m']}M"),
        ("Service Level", f"{kpis['service_level']}%"),
    ]: out(f"  {label:<35} {val}")

    out("\n[ INVENTORY HEALTH ]")
    out(stock_status_summary().to_string())

    out("\n[ STOCKOUT RISK SKUs ]")
    risk = stockout_risk_skus(8)
    out(risk[["product_name","category","avg_stock","avg_reorder","stock_ratio"]].to_string(index=False))

    out("\n[ SERVICE LEVEL BY CATEGORY ]")
    dvs = demand_vs_supply()
    monthly_avg = dvs.groupby("category")["service_level_pct"].agg(["mean","min","max"]).round(1)
    monthly_avg.columns = ["Avg SL%","Min SL%","Max SL%"]
    out(monthly_avg.to_string())

    out("\n[ VENDOR SCORECARD ]")
    out(vendor_scorecard().to_string(index=False))

    bw = best_worst_vendors()
    out("\n  Top 3 OTD:"); out(bw["best_otd"].to_string(index=False))
    out("\n  Bottom 3 OTD:"); out(bw["worst_otd"].to_string(index=False))

    out("\n[ LOGISTICS KPIs ]")
    out(logistics_kpis().to_string(index=False))

    out("\n[ RECOMMENDATIONS ]")
    logi = logistics_kpis()
    air_days = logi[logi["transport_mode"]=="Air"]["avg_lead_days"].values[0]
    sea_days = logi[logi["transport_mode"]=="Sea"]["avg_lead_days"].values[0]
    for tag, msg in [
        ("INVENTORY",   f"{kpis['stockout_count']} stockouts, {kpis['low_stock_count']} low-stock. Prioritize reorder for risk-flagged SKUs."),
        ("OVERSTOCK",   f"{kpis['overstock_count']} positions exceed 90% capacity. Consider transfers or clearance."),
        ("VENDOR",      f"Network OTD is {kpis['otd_rate_pct']}%. Vendors below 85% OTD should go on performance review."),
        ("TRANSPORT",   f"Air={air_days}d vs Sea={sea_days}d. Route urgent replenishments via Air."),
        ("SEASONALITY", "Skincare spikes Apr–Jun; Cosmetics spikes Oct–Dec. Build 6-week pre-season buffer."),
        ("FILL RATE",   f"Fill rate {kpis['fill_rate_pct']}%. Align supplier MOQs to demand forecasts."),
    ]: out(f"\n  [{tag}] {msg}")

    out("\n" + "="*72)
    Path("supply_chain/reports").mkdir(exist_ok=True)
    Path("supply_chain/reports/findings.md").write_text("\n".join(lines))
    print("\n✓ Report saved → supply_chain/reports/findings.md")
