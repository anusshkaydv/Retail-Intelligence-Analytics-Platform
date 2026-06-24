import csv
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_HTML = PROJECT_ROOT / "docs" / "powerbi_style_dashboard.html"


def money(value):
    if abs(value) >= 10000000:
        return f"₹{value/10000000:.2f}Cr"

    if abs(value) >= 100000:
        return f"₹{value/100000:.2f}L"

    return f"₹{value:,.0f}"


def read_csv(name):
    with (DATA_DIR / name).open(newline="") as file:
        return list(csv.DictReader(file))


def bar_rows(items):
    max_value = max(value for _, value in items)
    colors = ["#2097f3", "#1d2aa4", "#ef6b2f", "#800080", "#dc3fa5"]
    rows = []

    for index, (name, value) in enumerate(items):
        width = value / max_value * 100
        rows.append(
            "<div class='bar-row'>"
            f"<span>{name}</span>"
            "<div class='bar-track'>"
            f"<div class='bar' style='width:{width:.1f}%;background:{colors[index % len(colors)]}'>{money(value)}</div>"
            "</div></div>"
        )

    return "\n".join(rows)


def build_line_chart(monthly_revenue):
    months = sorted(monthly_revenue)
    values = [monthly_revenue[month] for month in months]
    max_value = max(values)
    min_value = min(values)
    width = 640
    height = 220
    points = []

    for index, value in enumerate(values):
        x = 30 + index * ((width - 60) / (len(values) - 1))
        y = 20 + (max_value - value) / (max_value - min_value) * (height - 50)
        points.append(f"{x:.1f},{y:.1f}")

    polyline = " ".join(points)
    area = f"30,{height - 25} {polyline} {width - 30},{height - 25}"

    return f"""
      <svg viewBox='0 0 {width} {height}' preserveAspectRatio='none'>
        <polygon points='{area}' fill='#d8eefe' opacity='.95'></polygon>
        <polyline points='{polyline}' fill='none' stroke='#2097f3' stroke-width='4'></polyline>
        <text x='30' y='20' fill='#555' font-size='14'>{money(max_value)}</text>
        <text x='30' y='{height - 28}' fill='#555' font-size='14'>{money(min_value)}</text>
        <text x='30' y='{height - 5}' fill='#555' font-size='14'>{months[0]}</text>
        <text x='{width - 95}' y='{height - 5}' fill='#555' font-size='14'>{months[-1]}</text>
      </svg>
    """


def build_region_category_chart(region_category):
    category_colors = {
        "Books": "#1d9bf0",
        "Clothing": "#2332a4",
        "Electronics": "#ef7d32",
        "Home": "#7a167c",
        "Sports": "#df3ca6",
        "Toys": "#7a55c7",
    }
    regions = sorted(region_category)
    categories = sorted({category for values in region_category.values() for category in values})
    max_region = max(sum(region_category[region].values()) for region in regions)
    stacks = []

    for region in regions:
        segments = []
        for category in categories:
            value = region_category[region].get(category, 0)
            if value:
                height = value / max_region * 180
                color = category_colors.get(category, "#888")
                segments.append(
                    f"<span title='{category}: {money(value)}' style='height:{height:.1f}px;background:{color}'></span>"
                )
        stacks.append(f"<div class='stack'><div class='stack-bars'>{''.join(segments)}</div><strong>{region}</strong></div>")

    legend = "".join(
        f"<span><i style='background:{category_colors.get(category, '#888')}'></i>{category}</span>"
        for category in categories
    )

    return f"<div class='legend'>{legend}</div><div class='stack-wrap'>{''.join(stacks)}</div>"


def main():
    customers = read_csv("customers.csv")
    products = {row["product_id"]: row for row in read_csv("products.csv")}
    stores = {row["store_id"]: row for row in read_csv("stores.csv")}

    monthly_revenue = defaultdict(float)
    store_profit = defaultdict(float)
    product_revenue = defaultdict(float)
    region_category = defaultdict(lambda: defaultdict(float))
    total_revenue = 0.0
    rows = 0

    for sale in read_csv("sales_transactions.csv"):
        rows += 1
        product = products[sale["product_id"]]
        store = stores[sale["store_id"]]
        revenue = float(sale["total_amount"])
        profit = revenue - int(sale["quantity"]) * float(product["unit_cost"])

        total_revenue += revenue
        monthly_revenue[sale["date"][:7]] += revenue
        store_profit[store["store_name"]] += profit
        product_revenue[product["product_name"]] += revenue
        region_category[store["region"]][product["category"]] += revenue

    top_products = sorted(product_revenue.items(), key=lambda item: item[1], reverse=True)[:5]
    top_stores = sorted(store_profit.items(), key=lambda item: item[1], reverse=True)[:5]

    html = f"""<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<style>
  body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; color: #0d2570; background: white; }}
  .page {{ width: 1600px; height: 1050px; padding: 28px 34px; box-sizing: border-box; }}
  .title {{ background:#f3e59b; border:2px solid #2a85b6; border-radius:24px 24px 0 0; text-align:center; padding:20px; font-size:54px; font-weight:800; color:#7944c1; }}
  .subtitle {{ text-align:center; color:#555; font-size:18px; margin-top:8px; }}
  .cards {{ display:grid; grid-template-columns: repeat(4, 1fr); gap:28px; border:2px solid #7b49c7; border-radius:8px; padding:18px; margin:22px 20px 36px; }}
  .card {{ background:white; box-shadow:0 5px 13px rgba(80,60,160,.25); border-left:7px solid #7b49c7; padding:16px 24px; text-align:center; }}
  .card strong {{ display:block; font-size:48px; color:#112ca4; margin-bottom:8px; }}
  .card span {{ font-size:22px; color:#111; font-weight:700; }}
  .grid {{ display:grid; grid-template-columns: 2fr 1fr; gap:20px; }}
  .grid2 {{ display:grid; grid-template-columns: 1.15fr 1fr; gap:20px; margin-top:20px; }}
  .panel {{ border:2px solid #7b49c7; padding:14px 18px; background:#fff; min-height:250px; }}
  .panel h2 {{ text-align:center; margin:0 0 10px; font-size:22px; color:#122d98; }}
  svg {{ width:100%; height:230px; background:#f1f1f1; }}
  .bar-row {{ display:grid; grid-template-columns:140px 1fr; align-items:center; gap:12px; margin:11px 0; color:#555; font-size:18px; }}
  .bar-track {{ height:30px; background:#f0f0f0; }}
  .bar {{ height:30px; color:white; text-align:right; padding-right:10px; line-height:30px; box-sizing:border-box; font-weight:700; }}
  table {{ width:100%; border-collapse:collapse; font-size:18px; color:#333; }}
  th {{ text-align:left; color:#555; border-bottom:2px solid #2c9fd8; padding:8px; }}
  td {{ padding:8px; border-bottom:1px solid #ddd; }}
  td.num {{ text-align:right; }}
  .stack-wrap {{ display:flex; align-items:flex-end; justify-content:space-around; height:220px; padding-top:10px; }}
  .stack {{ display:flex; flex-direction:column; align-items:center; gap:8px; width:110px; }}
  .stack-bars {{ height:190px; width:80px; display:flex; align-items:flex-end; }}
  .stack-bars span {{ width:80px; display:block; }}
  .legend {{ display:flex; flex-wrap:wrap; gap:12px; justify-content:center; color:#555; margin-bottom:4px; }}
  .legend i {{ display:inline-block; width:12px; height:12px; border-radius:50%; margin-right:4px; }}
</style>
</head>
<body>
<div class='page'>
  <div class='title'>RETAIL ANALYTICS DASHBOARD</div>
  <div class='subtitle'>Power BI-style static dashboard mockup generated from the corrected CSV dataset</div>
  <div class='cards'>
    <div class='card'><strong>{money(total_revenue)}</strong><span>Total Revenue</span></div>
    <div class='card'><strong>{len(customers)}</strong><span>Total Customers</span></div>
    <div class='card'><strong>{len(products)}</strong><span>Total Products</span></div>
    <div class='card'><strong>{money(total_revenue / rows)}</strong><span>Average Order Value</span></div>
  </div>
  <div class='grid'>
    <div class='panel'><h2>Monthly Revenue Trend</h2>{build_line_chart(monthly_revenue)}</div>
    <div class='panel'><h2>Top 5 Stores by Profit</h2><table><thead><tr><th>store_name</th><th class='num'>profit</th></tr></thead><tbody>{''.join(f'<tr><td>{store}</td><td class="num">{money(value)}</td></tr>' for store, value in top_stores)}</tbody></table></div>
  </div>
  <div class='grid2'>
    <div class='panel'><h2>Top 5 Products by Revenue</h2>{bar_rows(top_products)}</div>
    <div class='panel'><h2>Sales by Region & Category</h2>{build_region_category_chart(region_category)}</div>
  </div>
</div>
</body>
</html>"""

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
