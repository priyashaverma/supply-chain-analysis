Supply Chain Inventory & Logistics Analysis


Python · Pandas · SQLite · Matplotlib · Seaborn

End-to-end analytics pipeline for inventory health, demand forecasting gaps, vendor performance, and logistics KPI tracking across a simulated FMCG supply chain.




Project Overview

This project analyzes inventory movement and demand patterns across a simulated supply chain dataset — modeled after the Kaggle Supply Chain Analysis dataset — covering 3 product categories (Skincare, Haircare, Cosmetics) across 4 warehouses and 8 vendors.

Key Deliverables

OutputDescriptionreports/supply_chain_dashboard.png9-panel KPI dashboardreports/findings.mdStructured automated findings reportdata/supply_chain.dbSQLite database with 4 normalized tables


Key Findings

1. Inventory Health


Identified stockout, low-stock, and overstock positions across 80 SKU-warehouse combinations
Built a risk scoring model (stock ratio = current stock / reorder point) to prioritize replenishment
Cosmetics category shows highest overstock risk in Q4 post-holiday


2. Demand & Service Level


Detected seasonal demand spikes: Skincare (+40%) in Apr–Jun, Cosmetics (+60%) in Oct–Dec
Network-wide service level tracked monthly; months dipping below 90% flagged automatically
Unmet demand quantified per SKU for procurement planning


3. Vendor Performance


Scored all 8 vendors on: On-Time Delivery %, Fill Rate %, Avg Lead Time, Total Spend
Vendors below 85% OTD threshold flagged for review
Scatter plot reveals fill rate vs OTD trade-offs across the supplier base


4. Logistics KPIs


Compared 4 transport modes: Air (fastest, ~2 days), Road, Rail, Sea (14 days)
Air freight recommended for stockout-risk replenishments despite higher cost
Monthly order value trends tracked by category to identify procurement seasonality



Project Structure

supply_chain_project/
├── main.py                      # One-command pipeline runner
├── requirements.txt
├── data/
│   ├── products.csv             # 15 SKUs across 3 categories
│   ├── inventory.csv            # 60 SKU-warehouse positions
│   ├── orders.csv               # 1,500 purchase orders
│   ├── demand.csv               # Monthly demand vs actual sales
│   └── supply_chain.db          # SQLite (auto-generated)
├── sql/
│   └── schema_and_queries.sql   # Schema + 7 analytical SQL queries
├── src/
│   ├── generate_data.py         # Simulated dataset generator (Faker + NumPy)
│   ├── analysis.py              # Core KPI functions (SQL + Pandas)
│   ├── reporting_pipeline.py    # Automated KPI report generator
│   └── dashboard.py             # Multi-panel visualization (Matplotlib + Seaborn)
└── reports/
    ├── supply_chain_dashboard.png
    └── findings.md


Setup & Run

bash# 1. Clone and install
git clone https://github.com/yourusername/supply-chain-analysis.git
cd supply-chain-analysis
pip install -r requirements.txt

# 2. Run the full pipeline
python main.py

This single command:


Generates the simulated dataset (CSVs)
Loads data into a local SQLite database
Runs the automated KPI reporting pipeline → reports/findings.md
Renders the 9-panel dashboard → reports/supply_chain_dashboard.png



SQL Queries Included

QueryPurposeinventory_healthClassifies each SKU-warehouse as STOCKOUT / LOW_STOCK / HEALTHY / OVERSTOCKdemand_vs_supplyMonthly service level % per categoryvendor_scorecardOTD rate, fill rate, lead time, spend per vendorlogistics_kpisLead time and OTD by transport modestockout_risk_skusTop 10 SKUs most at risk of stockoutmonthly_order_trendOrder value and fill rate trends by monthdemand_gapUnmet demand quantification by category


Tech Stack


Python 3.10+ — core language
Pandas — data wrangling, aggregations, pivot tables
SQLite + sql queries — structured storage and analytical queries
Matplotlib + Seaborn — dashboard visualization
Faker + NumPy — realistic synthetic data generation



Dataset

Data is synthetically generated to mirror the structure of the Kaggle Supply Chain Analysis dataset, incorporating:


Product categories, SKUs, unit costs
Warehouse-level inventory positions with reorder points
Purchase orders with lead times, fill rates, OTD flags
Monthly demand vs actual sales (with seasonal patterns)



Author

Built as a portfolio project demonstrating end-to-end supply chain analytics using Python, Pandas, and SQL.
Share(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.nonce='SojYkdAyjvAwV3U+0vimAQ==';d.innerHTML="window.__CF$cv$params={r:'a10224d3696a5c15',t:'MTc4MjIwMzU2NA=='};var a=document.createElement('script');a.nonce='SojYkdAyjvAwV3U+0vimAQ==';a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'loading'!==document.readyState&&(document.onreadystatechange=e,c())}}}})();
