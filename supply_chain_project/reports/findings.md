========================================================================
  SUPPLY CHAIN — AUTOMATED KPI REPORT  |  2024
========================================================================

[ EXECUTIVE SUMMARY ]
  Total SKUs                          15
  Stockouts                           2
  Low-stock SKU-warehouses            5
  Overstock SKU-warehouses            24
  On-Time Delivery                    49.6%
  Fill Rate                           79.7%
  Avg Lead Time                       8.7 days
  Total Spend                         $25.88M
  Service Level                       90.5%

[ INVENTORY HEALTH ]
stock_status  STOCKOUT  LOW_STOCK  HEALTHY  OVERSTOCK
category                                             
Cosmetics            0          3        8          9
Haircare             1          2       11          6
Skincare             1          0       10          9

[ STOCKOUT RISK SKUs ]
product_name  category  avg_stock  avg_reorder  stock_ratio
 Moisturizer  Skincare        0.0         56.0        0.000
    Hair Oil  Haircare        0.0        200.0        0.000
 Conditioner  Haircare       37.0        189.0        0.196
       Blush Cosmetics       49.0        187.0        0.262
     Shampoo  Haircare      115.0        193.0        0.596
    Eyeliner Cosmetics      109.0        146.0        0.747
     Mascara Cosmetics      114.0        117.0        0.974

[ SERVICE LEVEL BY CATEGORY ]
           Avg SL%  Min SL%  Max SL%
category                            
Cosmetics     90.0     86.0     95.6
Haircare      90.3     85.6    100.7
Skincare      91.4     83.9     96.9

[ VENDOR SCORECARD ]
 supplier  total_orders  avg_lead_time  avg_fill_rate_pct  otd_rate_pct  total_spend
Vendor_02           185            8.4               80.6          53.0   3224810.31
Vendor_01           170            9.0               81.0          52.9   3262485.55
Vendor_03           186            9.2               79.4          52.2   2913740.16
Vendor_06           192            8.9               80.3          50.5   3306148.94
Vendor_08           194            8.2               79.1          49.0   3405520.28
Vendor_05           187            8.5               78.3          48.7   3050385.48
Vendor_07           214            8.3               80.3          46.3   3514458.95
Vendor_04           172            9.2               78.9          44.8   3202909.75

  Top 3 OTD:
 supplier  otd_rate_pct
Vendor_02          53.0
Vendor_01          52.9
Vendor_03          52.2

  Bottom 3 OTD:
 supplier  otd_rate_pct
Vendor_04          44.8
Vendor_07          46.3
Vendor_05          48.7

[ LOGISTICS KPIs ]
transport_mode  shipments  avg_lead_days  avg_fill_pct  otd_pct  total_value_k
           Air        368            3.6          80.0     51.9         6272.2
          Road        360            6.4          80.3     46.1         6188.7
          Rail        364            8.5          79.9     50.3         6378.7
           Sea        408           15.5          78.8     50.0         7040.9

[ RECOMMENDATIONS ]

  [INVENTORY] 2 stockouts, 5 low-stock. Prioritize reorder for risk-flagged SKUs.

  [OVERSTOCK] 24 positions exceed 90% capacity. Consider transfers or clearance.

  [VENDOR] Network OTD is 49.6%. Vendors below 85% OTD should go on performance review.

  [TRANSPORT] Air=3.6d vs Sea=15.5d. Route urgent replenishments via Air.

  [SEASONALITY] Skincare spikes Apr–Jun; Cosmetics spikes Oct–Dec. Build 6-week pre-season buffer.

  [FILL RATE] Fill rate 79.7%. Align supplier MOQs to demand forecasts.

========================================================================