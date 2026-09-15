# -*- coding: utf-8 -*-
"""生成模拟广告投放CSV数据 - 动态广告组名称"""
import random
import csv
import io

AD_PLATFORMS = ["TikTok", "Meta", "Google Shopping", "Google Search"]

AD_FORMATS = {
    "TikTok": ["视频广告", "Spark广告", "达人合作", "直播广告"],
    "Meta": ["轮播广告", "故事广告", "再营销广告", "商城广告"],
    "Google Shopping": ["购物广告", "展示广告", "再营销广告", "视频广告"],
    "Google Search": ["品牌词", "品类词", "竞品词", "长尾词"],
}

KEYWORDS = [
    "wireless", "portable", "best", "premium", "mini",
    "waterproof", "smart", "rechargeable", "USB", "LED",
]


def generate_mock_csv(product="产品", market="美国", budget=5000, service_name="TikTok Ads"):
    """生成逼真的广告投放CSV数据，广告组名称根据产品动态生成。
    service_name 可以是字符串或列表（多平台投流）。"""
    svc_platform_map = {
        "TikTok Ads": "TikTok",
        "Meta Ads": "Meta",
        "Google Ads": "Google Shopping",
    }
    if isinstance(service_name, list):
        selected = [svc_platform_map.get(s, "TikTok") for s in service_name]
    else:
        selected = [svc_platform_map.get(service_name, "TikTok")]
    # 补足未选平台，确保广告组覆盖多渠道
    for p in AD_PLATFORMS:
        if p not in selected:
            selected.append(p)
    platforms = selected
    formats_pool = []
    for p in platforms[:4]:
        for f in AD_FORMATS.get(p, ["广告"]):
            formats_pool.append((p, f))
    while len(formats_pool) < 8:
        formats_pool.append((random.choice(AD_PLATFORMS), "通用广告"))
    formats_pool = formats_pool[:8]

    rows = []
    remaining = budget
    for i, (platform, ad_format) in enumerate(formats_pool):
        group_name = "%s-%s-%s-%s" % (platform, market, product[:6], ad_format)
        if i == len(formats_pool) - 1:
            spend = round(remaining, 2)
        else:
            spend = round(random.uniform(300, 900), 2)
            remaining -= spend
            if remaining < 0:
                spend = round(budget / len(formats_pool), 2)
                remaining = budget - spend * (i + 1)

        impressions = int(spend / random.uniform(0.005, 0.02) * 1000)
        clicks = int(impressions * random.uniform(0.008, 0.035))
        cpc = round(spend / max(clicks, 1), 2)
        conversions = int(clicks * random.uniform(0.01, 0.08))
        revenue = round(conversions * random.uniform(25, 60), 2)
        roas = round(revenue / max(spend, 0.01), 2)
        ctr = round(clicks / max(impressions, 1) * 100, 2)
        cvr = round(conversions / max(clicks, 1) * 100, 2)
        cpa = round(spend / max(conversions, 1), 2) if conversions else 0
        keyword = (random.choice(KEYWORDS) + " " + product[:4].lower()).strip()

        rows.append({
            "ad_group": group_name,
            "platform": platform,
            "keyword": keyword,
            "spend": spend,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "roas": roas,
            "ctr": ctr,
            "cvr": cvr,
            "cpc": cpc,
            "cpa": cpa,
            "status": "active" if roas > 1.5 else "underperforming",
        })

    for r in rows[3:6]:
        r["roas"] = round(random.uniform(0.3, 1.2), 2)
        r["conversions"] = max(1, int(r["clicks"] * 0.005))
        r["revenue"] = round(r["conversions"] * 30, 2)
        r["status"] = "underperforming"

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "ad_group", "platform", "keyword", "spend", "impressions",
        "clicks", "conversions", "revenue", "roas", "ctr", "cvr",
        "cpc", "cpa", "status"
    ])
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


if __name__ == "__main__":
    print(generate_mock_csv("智能手表", "英国", 5000, "TikTok Ads"))
