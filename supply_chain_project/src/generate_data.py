"""
Simulates a real-world supply chain dataset modeled after the
"Supply Chain Analysis" dataset on Kaggle (Fashion/FMCG domain).
"""

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
np.random.seed(42)
random.seed(42)

CATEGORIES = ["Skincare", "Haircare", "Cosmetics"]
PRODUCTS = {
    "Skincare":  ["Moisturizer", "Sunscreen", "Face Wash", "Serum", "Toner"],
    "Haircare":  ["Shampoo", "Conditioner", "Hair Oil", "Hair Mask", "Dry Shampoo"],
    "Cosmetics": ["Foundation", "Lipstick", "Mascara", "Blush", "Eyeliner"],
}
SUPPLIERS  = [f"Vendor_{i:02d}" for i in range(1, 9)]
WAREHOUSES = ["WH_Delhi", "WH_Mumbai", "WH_Bangalore", "WH_Chennai"]
TRANSPORT  = ["Road", "Rail", "Air", "Sea"]
N_ORDERS   = 1500

def random_date(start="2023-01-01", end="2024-12-31"):
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt   = datetime.strptime(end,   "%Y-%m-%d")
    delta    = (end_dt - start_dt).days
    return start_dt + timedelta(days=random.randint(0, delta))

def build_products():
    rows, sku_id = [], 1000
    for cat, names in PRODUCTS.items():
        for name in names:
            rows.append({"sku_id": f"SKU{sku_id}", "product_name": name,
                         "category": cat, "unit_cost": round(random.uniform(8, 120), 2),
                         "reorder_point": random.randint(50, 200),
                         "max_stock": random.randint(800, 2000)})
            sku_id += 1
    return pd.DataFrame(rows)

def build_inventory(products_df):
    rows = []
    for _, p in products_df.iterrows():
        for wh in WAREHOUSES:
            opening = random.randint(100, 1800)
            rows.append({"sku_id": p["sku_id"], "warehouse": wh,
                         "opening_stock": opening,
                         "current_stock": max(0, opening + random.randint(-600, 400)),
                         "reorder_point": p["reorder_point"],
                         "max_stock": p["max_stock"],
                         "last_restock_dt": random_date("2024-01-01", "2024-12-31")})
    return pd.DataFrame(rows)

def build_orders(products_df):
    rows = []
    skus = products_df["sku_id"].tolist()
    for i in range(N_ORDERS):
        sku   = random.choice(skus)
        cat   = products_df.loc[products_df["sku_id"] == sku, "category"].values[0]
        cost  = products_df.loc[products_df["sku_id"] == sku, "unit_cost"].values[0]
        qty   = random.randint(10, 500)
        sup   = random.choice(SUPPLIERS)
        trans = random.choice(TRANSPORT)
        base_lead = {"Road": 5, "Rail": 7, "Air": 2, "Sea": 14}[trans]
        lead_time  = max(1, base_lead + random.randint(-1, 4))
        order_dt   = random_date()
        delivery_dt = order_dt + timedelta(days=lead_time + random.randint(0, 3))
        on_time = delivery_dt <= order_dt + timedelta(days=lead_time + 1)
        fill_rt = round(random.uniform(0.6, 1.0), 3)
        rows.append({"order_id": f"ORD{10000+i}", "sku_id": sku, "category": cat,
                     "supplier": sup, "warehouse": random.choice(WAREHOUSES),
                     "transport_mode": trans, "order_qty": qty,
                     "fulfilled_qty": int(qty * fill_rt), "unit_cost": cost,
                     "order_date": order_dt.strftime("%Y-%m-%d"),
                     "delivery_date": delivery_dt.strftime("%Y-%m-%d"),
                     "lead_time_days": lead_time, "on_time_delivery": int(on_time),
                     "fill_rate": fill_rt, "order_value": round(qty * cost, 2)})
    return pd.DataFrame(rows)

def build_demand(products_df):
    rows = []
    for _, p in products_df.iterrows():
        for month in range(1, 13):
            base = random.randint(200, 1500)
            if p["category"] == "Skincare"  and month in [4, 5, 6]:  base = int(base * 1.4)
            if p["category"] == "Cosmetics" and month in [10, 11, 12]: base = int(base * 1.6)
            rows.append({"sku_id": p["sku_id"], "category": p["category"],
                         "year": 2024, "month": month, "demand_units": base,
                         "actual_sales": int(base * random.uniform(0.75, 1.05))})
    return pd.DataFrame(rows)
