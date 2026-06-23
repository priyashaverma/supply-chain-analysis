import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH  = Path("supply_chain/data/supply_chain.db")
DATA_DIR = Path("supply_chain/data")

def get_conn():
    return sqlite3.connect(DB_PATH)

def load_tables_to_db():
    conn = get_conn()
    for name in ["products", "inventory", "orders", "demand"]:
        df = pd.read_csv(DATA_DIR / f"{name}.csv")
        df.to_sql(name, conn, if_exists="replace", index=False)
    conn.close()
    print("✓ All tables loaded into SQLite")

def run_sql(query):
    conn = get_conn()
    df   = pd.read_sql_query(query, conn)
    conn.close()
    return df

def inventory_health():
    return run_sql("""
        SELECT i.sku_id, p.product_name, p.category, i.warehouse,
               i.current_stock, i.reorder_point, i.max_stock,
               CASE WHEN i.current_stock = 0                  THEN 'STOCKOUT'
                    WHEN i.current_stock < i.reorder_point    THEN 'LOW_STOCK'
                    WHEN i.current_stock > i.max_stock * 0.90 THEN 'OVERSTOCK'
                    ELSE 'HEALTHY' END AS stock_status,
               ROUND(CAST(i.current_stock AS REAL)/i.max_stock*100,1) AS utilisation_pct
        FROM inventory i JOIN products p USING (sku_id)""")

def stock_status_summary():
    df = inventory_health()
    summary = (df.groupby(["category","stock_status"]).size()
                 .reset_index(name="count")
                 .pivot(index="category", columns="stock_status", values="count")
                 .fillna(0).astype(int))
    for col in ["STOCKOUT","LOW_STOCK","OVERSTOCK","HEALTHY"]:
        if col not in summary.columns: summary[col] = 0
    return summary[["STOCKOUT","LOW_STOCK","HEALTHY","OVERSTOCK"]]

def demand_vs_supply():
    return run_sql("""
        SELECT category, month,
               SUM(demand_units) AS total_demand, SUM(actual_sales) AS total_sales,
               SUM(demand_units - actual_sales) AS unmet_demand,
               ROUND(SUM(actual_sales)*100.0/SUM(demand_units),1) AS service_level_pct
        FROM demand GROUP BY category, month ORDER BY category, month""")

def demand_seasonality():
    df = demand_vs_supply()
    return df.pivot(index="category", columns="month", values="service_level_pct")

def stockout_risk_skus(top_n=10):
    return run_sql(f"""
        SELECT i.sku_id, p.product_name, p.category,
               ROUND(AVG(i.current_stock),0) AS avg_stock,
               ROUND(AVG(i.reorder_point),0) AS avg_reorder,
               SUM(d.demand_units-d.actual_sales) AS cumulative_unmet,
               ROUND(AVG(CAST(i.current_stock AS REAL)/i.reorder_point),3) AS stock_ratio
        FROM inventory i JOIN products p USING (sku_id) JOIN demand d USING (sku_id)
        WHERE i.current_stock < i.reorder_point
        GROUP BY i.sku_id ORDER BY stock_ratio ASC LIMIT {top_n}""")

def vendor_scorecard():
    return run_sql("""
        SELECT supplier, COUNT(order_id) AS total_orders,
               ROUND(AVG(lead_time_days),1) AS avg_lead_time,
               ROUND(AVG(fill_rate)*100,1) AS avg_fill_rate_pct,
               ROUND(SUM(on_time_delivery)*100.0/COUNT(*),1) AS otd_rate_pct,
               ROUND(SUM(order_value),2) AS total_spend
        FROM orders GROUP BY supplier ORDER BY otd_rate_pct DESC""")

def best_worst_vendors():
    df = vendor_scorecard()
    return {"best_otd":    df.nlargest(3,"otd_rate_pct")[["supplier","otd_rate_pct"]],
            "worst_otd":   df.nsmallest(3,"otd_rate_pct")[["supplier","otd_rate_pct"]],
            "best_fill":   df.nlargest(3,"avg_fill_rate_pct")[["supplier","avg_fill_rate_pct"]],
            "lowest_lead": df.nsmallest(3,"avg_lead_time")[["supplier","avg_lead_time"]]}

def logistics_kpis():
    return run_sql("""
        SELECT transport_mode, COUNT(*) AS shipments,
               ROUND(AVG(lead_time_days),1) AS avg_lead_days,
               ROUND(AVG(fill_rate)*100,1) AS avg_fill_pct,
               ROUND(SUM(on_time_delivery)*100.0/COUNT(*),1) AS otd_pct,
               ROUND(SUM(order_value)/1000,1) AS total_value_k
        FROM orders GROUP BY transport_mode ORDER BY avg_lead_days""")

def monthly_order_trend():
    return run_sql("""
        SELECT SUBSTR(order_date,1,7) AS year_month, category,
               COUNT(order_id) AS orders, ROUND(SUM(order_value),2) AS total_value,
               ROUND(AVG(fill_rate)*100,1) AS avg_fill_pct
        FROM orders GROUP BY year_month, category ORDER BY year_month, category""")

def executive_summary():
    inv  = inventory_health()
    ords = run_sql("SELECT * FROM orders")
    dem  = run_sql("SELECT * FROM demand")
    return {
        "total_skus":      inv["sku_id"].nunique(),
        "stockout_count":  int((inv["stock_status"]=="STOCKOUT").sum()),
        "overstock_count": int((inv["stock_status"]=="OVERSTOCK").sum()),
        "low_stock_count": int((inv["stock_status"]=="LOW_STOCK").sum()),
        "otd_rate_pct":    round(ords["on_time_delivery"].mean()*100, 1),
        "fill_rate_pct":   round(ords["fill_rate"].mean()*100, 1),
        "avg_lead_days":   round(ords["lead_time_days"].mean(), 1),
        "total_spend_m":   round(ords["order_value"].sum()/1_000_000, 2),
        "service_level":   round(dem["actual_sales"].sum()/dem["demand_units"].sum()*100, 1),
    }
