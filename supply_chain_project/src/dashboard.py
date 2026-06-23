import sys
sys.path.insert(0, "supply_chain/src")
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path
from analysis import (load_tables_to_db, inventory_health, stock_status_summary,
                      demand_vs_supply, demand_seasonality, vendor_scorecard,
                      logistics_kpis, monthly_order_trend, stockout_risk_skus,
                      executive_summary)

BG    = "#0F1117"; PANEL  = "#1A1D27"; ACCENT = "#4F8EF7"
GREEN = "#2DD4BF"; AMBER  = "#F59E0B"; RED    = "#EF4444"
MUTED = "#94A3B8"; WHITE  = "#F1F5F9"
CAT_COLORS = {"Skincare": ACCENT, "Haircare": GREEN, "Cosmetics": AMBER}

def styled_ax(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.xaxis.label.set_color(MUTED); ax.yaxis.label.set_color(MUTED)
    for sp in ax.spines.values(): sp.set_edgecolor("#2A2D3A")
    if title:   ax.set_title(title, color=WHITE, fontsize=10, fontweight="bold", pad=8)
    if xlabel:  ax.set_xlabel(xlabel, fontsize=8)
    if ylabel:  ax.set_ylabel(ylabel, fontsize=8)

def kpi_box(ax, value, label, color=ACCENT):
    ax.set_facecolor(PANEL)
    for sp in ax.spines.values(): sp.set_edgecolor(color); sp.set_linewidth(1.5)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5,0.58,str(value),transform=ax.transAxes,ha="center",va="center",
            fontsize=22,fontweight="bold",color=color)
    ax.text(0.5,0.22,label,transform=ax.transAxes,ha="center",va="center",
            fontsize=8,color=MUTED)

def build_dashboard():
    kpis  = executive_summary()
    inv_df= inventory_health()
    seas  = demand_seasonality()
    vend  = vendor_scorecard()
    logi  = logistics_kpis()
    trend = monthly_order_trend()
    risk  = stockout_risk_skus(8)

    fig = plt.figure(figsize=(22,16), facecolor=BG)
    fig.suptitle("Supply Chain Inventory & Logistics — KPI Dashboard  |  2024",
                 color=WHITE, fontsize=16, fontweight="bold", y=0.98)
    gs = gridspec.GridSpec(5,4,figure=fig,hspace=0.55,wspace=0.38,
                           left=0.04,right=0.97,top=0.94,bottom=0.04)

    # KPI tiles
    kpi_data = [
        (f"{kpis['total_skus']}",       "Total SKUs",       ACCENT),
        (f"{kpis['stockout_count']}",   "Stockouts",        RED),
        (f"{kpis['low_stock_count']}",  "Low Stock",        AMBER),
        (f"{kpis['overstock_count']}",  "Overstocks",       "#A78BFA"),
        (f"{kpis['otd_rate_pct']}%",    "On-Time Delivery", GREEN),
        (f"{kpis['fill_rate_pct']}%",   "Avg Fill Rate",    ACCENT),
        (f"{kpis['avg_lead_days']}d",   "Avg Lead Time",    AMBER),
        (f"${kpis['total_spend_m']}M",  "Total Spend",      GREEN),
        (f"{kpis['service_level']}%",   "Service Level",    ACCENT),
    ]
    gs0 = gridspec.GridSpecFromSubplotSpec(1,9,subplot_spec=gs[0,:],wspace=0.15)
    for i,(val,lbl,col) in enumerate(kpi_data):
        kpi_box(fig.add_subplot(gs0[0,i]), val, lbl, col)

    # Inventory status bars
    ax1 = fig.add_subplot(gs[1:3,0:2])
    styled_ax(ax1, "Inventory Status by Category", "Units")
    status_data = inv_df.groupby(["category","stock_status"]).size().unstack(fill_value=0)
    for c in ["STOCKOUT","LOW_STOCK","HEALTHY","OVERSTOCK"]:
        if c not in status_data.columns: status_data[c] = 0
    status_data = status_data[["STOCKOUT","LOW_STOCK","HEALTHY","OVERSTOCK"]]
    cmap = {"STOCKOUT":RED,"LOW_STOCK":AMBER,"HEALTHY":GREEN,"OVERSTOCK":"#A78BFA"}
    bot = np.zeros(len(status_data))
    for col in status_data.columns:
        vals = status_data[col].values
        ax1.bar(status_data.index, vals, bottom=bot, color=cmap[col], label=col, width=0.5)
        for j,(v,b) in enumerate(zip(vals,bot)):
            if v>3: ax1.text(j,b+v/2,str(v),ha="center",va="center",fontsize=7,color=WHITE,fontweight="bold")
        bot += vals
    ax1.legend(fontsize=7,labelcolor=MUTED,facecolor=PANEL,edgecolor="#2A2D3A",loc="upper right")
    ax1.set_xticks(range(len(status_data.index))); ax1.set_xticklabels(status_data.index,rotation=0,color=MUTED)

    # Heatmap
    ax2 = fig.add_subplot(gs[1:3,2:4])
    styled_ax(ax2, "Service Level % — Category × Month")
    month_abbr=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    seas.columns=[month_abbr[m-1] for m in seas.columns]
    sns.heatmap(seas,ax=ax2,cmap="RdYlGn",annot=True,fmt=".0f",linewidths=0.4,
                linecolor="#0F1117",cbar_kws={"shrink":0.7},annot_kws={"size":8,"weight":"bold"})
    ax2.tick_params(colors=MUTED,labelsize=8)
    ax2.collections[0].colorbar.ax.tick_params(colors=MUTED,labelsize=7)

    # Monthly trend
    ax3 = fig.add_subplot(gs[3,0:2])
    styled_ax(ax3,"Monthly Order Value by Category","Month","Value (₹)")
    trend_p=trend.pivot(index="year_month",columns="category",values="total_value").fillna(0)
    for cat in trend_p.columns:
        ax3.plot(range(len(trend_p)),trend_p[cat].values,color=CAT_COLORS.get(cat,ACCENT),
                 linewidth=2,marker="o",markersize=3,label=cat)
    step=max(1,len(trend_p)//8)
    ax3.set_xticks(range(0,len(trend_p),step))
    ax3.set_xticklabels(trend_p.index[::step],rotation=35,ha="right",fontsize=7)
    ax3.legend(fontsize=7,labelcolor=MUTED,facecolor=PANEL,edgecolor="#2A2D3A")
    ax3.grid(axis="y",color="#2A2D3A",linestyle="--",linewidth=0.5)

    # Lead time
    ax4=fig.add_subplot(gs[3,2]); styled_ax(ax4,"Avg Lead Time\nby Transport","Days")
    logi_s=logi.sort_values("avg_lead_days"); bc=["#4F8EF7","#2DD4BF","#F59E0B","#EF4444"]
    bars=ax4.barh(logi_s["transport_mode"],logi_s["avg_lead_days"],color=bc[:len(logi_s)],height=0.5)
    for bar,v in zip(bars,logi_s["avg_lead_days"]):
        ax4.text(bar.get_width()+0.1,bar.get_y()+bar.get_height()/2,f"{v}d",va="center",fontsize=8,color=WHITE)
    ax4.set_xlim(0,logi_s["avg_lead_days"].max()*1.25); ax4.tick_params(axis="y",colors=WHITE,labelsize=8)

    # OTD by transport
    ax5=fig.add_subplot(gs[3,3]); styled_ax(ax5,"On-Time Delivery %\nby Transport","%")
    bars2=ax5.barh(logi_s["transport_mode"],logi_s["otd_pct"],color=bc[:len(logi_s)],height=0.5)
    for bar,v in zip(bars2,logi_s["otd_pct"]):
        ax5.text(bar.get_width()+0.3,bar.get_y()+bar.get_height()/2,f"{v}%",va="center",fontsize=8,color=WHITE)
    ax5.set_xlim(0,115); ax5.tick_params(axis="y",colors=WHITE,labelsize=8)

    # Vendor scatter
    ax6=fig.add_subplot(gs[4,0:2]); styled_ax(ax6,"Vendor Scorecard — Fill Rate vs OTD","OTD %","Fill Rate %")
    sc=ax6.scatter(vend["otd_rate_pct"],vend["avg_fill_rate_pct"],
                   s=vend["total_orders"]*1.5,c=vend["avg_lead_time"],cmap="RdYlGn_r",
                   alpha=0.85,edgecolors=WHITE,linewidths=0.5)
    for _,row in vend.iterrows():
        ax6.annotate(row["supplier"],(row["otd_rate_pct"],row["avg_fill_rate_pct"]),
                     textcoords="offset points",xytext=(4,4),fontsize=6.5,color=MUTED)
    cbar=fig.colorbar(sc,ax=ax6,shrink=0.8); cbar.set_label("Avg Lead Time",color=MUTED,fontsize=7)
    cbar.ax.tick_params(colors=MUTED,labelsize=7)
    ax6.axvline(90,color=AMBER,linestyle="--",linewidth=0.8,alpha=0.7,label="90% OTD target")
    ax6.axhline(90,color=RED,linestyle="--",linewidth=0.8,alpha=0.7,label="90% Fill target")
    ax6.legend(fontsize=7,labelcolor=MUTED,facecolor=PANEL,edgecolor="#2A2D3A")

    # Risk table
    ax7=fig.add_subplot(gs[4,2:4]); ax7.set_facecolor(PANEL); ax7.axis("off")
    ax7.set_title("Top SKUs at Stockout Risk",color=WHITE,fontsize=10,fontweight="bold",pad=8)
    rd=risk[["product_name","category","avg_stock","avg_reorder","stock_ratio"]].copy()
    rd.columns=["Product","Category","Avg Stock","Reorder Pt","Stock Ratio"]
    rd["Stock Ratio"]=rd["Stock Ratio"].apply(lambda x:f"{x:.2f}")
    rd["Avg Stock"]=rd["Avg Stock"].apply(lambda x:f"{int(x):,}")
    rd["Reorder Pt"]=rd["Reorder Pt"].apply(lambda x:f"{int(x):,}")
    tbl=ax7.table(cellText=rd.values.tolist(),colLabels=rd.columns.tolist(),
                  cellLoc="center",loc="center",bbox=[0,0,1,1])
    tbl.auto_set_font_size(False); tbl.set_fontsize(7.5)
    for (r,c),cell in tbl.get_celld().items():
        cell.set_facecolor(PANEL if r%2==0 else "#20243A"); cell.set_edgecolor("#2A2D3A")
        if r==0: cell.set_facecolor("#252942"); cell.set_text_props(color=WHITE,fontweight="bold")
        else:
            ratio_val=float(rd.iloc[r-1]["Stock Ratio"]) if r<=len(rd) else 1
            cell.set_text_props(color=RED if (c==4 and ratio_val<0.5) else AMBER if (c==4) else MUTED)

    Path("supply_chain/reports").mkdir(exist_ok=True)
    out="supply_chain/reports/supply_chain_dashboard.png"
    plt.savefig(out,dpi=160,bbox_inches="tight",facecolor=BG)
    print(f"✓ Dashboard saved → {out}")
    return out
