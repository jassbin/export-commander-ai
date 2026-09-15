# -*- coding: utf-8 -*-
"""模拟模式（Mock Mode）：不调用真实大模型，返回预置高质量演示数据。
用于 Token Plan 额度耗尽期间 / 不想消耗额度时的演示。"""
import base64
import csv
import io


def _safe(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _en(s):
    words = {
        "蓝牙音箱": "Bluetooth Speaker", "瑜伽": "Yoga Wear", "宠物": "Pet", "硅胶": "Silicone Kit",
        "化妆镜": "Makeup Mirror", "榨汁杯": "Juice Cup", "积木": "Building Blocks",
        "手机支架": "Car Phone Holder", "运动手表": "Smart Watch", "饮水机": "Water Fountain",
        "露营帐篷": "Camping Tent", "登山背包": "Hiking Backpack", "LED": "LED",
    }
    for k, v in words.items():
        if k in str(s):
            return v
    return "Premium Product"


def mock_image_data_uri(product_name, market="US"):
    """离线可用的 SVG 占位主图（data URI），避免真实调用图片模型"""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="480">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#02153a"/><stop offset="1" stop-color="#0a6fd6"/>'
        '</linearGradient></defs>'
        '<rect width="640" height="480" fill="url(#g)"/>'
        '<circle cx="540" cy="90" r="110" fill="#00d4ff" opacity="0.15"/>'
        '<text x="320" y="200" font-family="Arial" font-size="34" font-weight="bold" fill="#fff" text-anchor="middle">'
        + _safe(product_name) + '</text>'
        '<text x="320" y="240" font-family="Arial" font-size="16" fill="#bfe0ff" text-anchor="middle">AI Ad Creative (Mock)</text>'
        '<text x="320" y="270" font-family="Arial" font-size="13" fill="#7fa8cf" text-anchor="middle">Market: '
        + _safe(market) + ' | no token consumed</text>'
        '</svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


def mock_strategy(product, budget, market, extra=""):
    p = str(product).strip() or "跨境商品"
    e = str(extra).strip() or "差异化功能与高品质体验"
    return {
        "market_positioning": "以「" + e + "」为核心卖点，锁定" + market + "市场25-40岁注重品质生活的消费人群，定位中高端性价比品牌，主打差异化与口碑传播。",
        "target_audience": market + "市场对" + p + "有明确需求、习惯社媒种草并信任达人测评的25-40岁用户，注重品质、颜值与实用性，决策周期短。",
        "channel_strategy": [
            {"channel": "TikTok", "reason": "短视频种草适合情景化展示使用场景，传播速度快", "budget_pct": 40, "content_type": "15-30s创意短视频/开箱测评"},
            {"channel": "Instagram", "reason": "图文+Reels覆盖高购买力人群，强化品牌调性", "budget_pct": 30, "content_type": "高清图文 / Reels"},
            {"channel": "YouTube", "reason": "长视频测评建立信任，沉淀长期搜索流量", "budget_pct": 30, "content_type": "5-10分钟深度测评"},
        ],
        "content_plan": ["达人开箱+多场景演示", "痛点对比型短视频", "限时优惠+稀缺感文案"],
        "budget_allocation": {"ads": 45, "content": 20, "kol": 25, "tools": 10},
        "kol_suggestion": "TikTok中腰部达人(2-20万粉)为主，搭配Instagram生活方式博主与YouTube测评Up主",
        "key_metrics": ["ROAS", "CTR", "CPA", "内容互动率"],
        "timeline": "第1周达人种草启动；第2周广告放量；第3-4周数据优化与滚量",
        "mock_note": "模拟数据（不消耗Token额度）",
    }


def mock_content(product, market):
    p = str(product).strip() or "跨境商品"
    return {
        "product_title": p + " · 限定款",
        "product_title_en": "Premium " + _en(p) + " — Best Seller",
        "slogan": "点亮生活每一刻，品质看得见",
        "ad_copy_tiktok": "开箱实测「" + p[:8] + "」！颜值在线+实用满分，关注我解锁更多宝藏好物~ #好物分享 #开箱",
        "ad_copy_instagram": p[:8] + " ✨ 让日常更有质感\\n细节满分，出片神器\\n#lifestyle #instagramfinds .. 点击了解更多",
        "ad_copy_meta": "【" + p[:8] + "】限时特惠！品质之选，今日下单立享专属优惠。立即抢购 >>",
        "image_prompt": "professional e-commerce hero image of " + _en(p) + ", clean studio background, soft lighting, premium feel, 4k",
        "selling_points": ["核心卖点1：设计感与实用性并重", "核心卖点2：品质稳定、耐用可靠", "核心卖点3：适配" + market + "本地化使用习惯"],
        "cultural_tips": "避免夸张与绝对化表述，多用真实使用场景与用户评价背书",
        "image_url": mock_image_data_uri(p, market),
        "mock_note": "模拟数据（不消耗额度）",
    }


def mock_kol(name, market, strategy=None):
    return {
        "kol_matches": [
            {"name": "Luna Tech", "platform": "TikTok", "followers": "128K", "engagement_rate": "5.2%",
             "fit_score": 92, "collaboration_type": "开箱测评+种草短视频", "estimated_cost": "$800",
             "reason": "数码/生活方式赛道，粉丝画像与目标人群高度重合"},
            {"name": "Sophia Lee", "platform": "Instagram", "followers": "86K", "engagement_rate": "4.1%",
             "fit_score": 86, "collaboration_type": "图文种草+Reels", "estimated_cost": "$650",
             "reason": "高质感图文风格，擅长传递生活方式卖点"},
            {"name": "Max Reviews", "platform": "YouTube", "followers": "215K", "engagement_rate": "3.4%",
             "fit_score": 81, "collaboration_type": "深度视频测评", "estimated_cost": "$1200",
             "reason": "测评类Up主，长视频建立信任、沉淀搜索流量"},
            {"name": "Emma Daily", "platform": "TikTok", "followers": "45K", "engagement_rate": "6.8%",
             "fit_score": 78, "collaboration_type": "场景化使用短视频", "estimated_cost": "$450",
             "reason": "腰部KOL成本低、互动率高，适合批量铺量"},
        ],
        "outreach_script": "Hi Creator! We loved your content and would love to send you a free sample of "
                           + str(name)[:8] + " for an honest review. 期待合作！",
        "collaboration_plan": "第1周：TikTok 3位KOL开箱/场景视频；第2周：Instagram图文种草+Reels；第3周：YouTube长测评上线；全程提供统一素材包与优惠码",
        "budget_split": "TikTok 40% / Instagram 30% / YouTube 30%；KOL预算建议占总营销预算25%",
        "mock_note": "模拟数据（不消耗额度）",
    }


def mock_diagnosis(csv_text, product="产品", market="美国"):
    """基于CSV数据做统计（零API），ROAS用合理模拟分布，方便演示诊断价值"""
    total_spend = 0.0
    rows = []
    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        for r in reader:
            spend = float(r.get("spend", 0) or 0)
            total_spend += spend
            rows.append({"ad_group": r.get("ad_group", ""), "platform": r.get("platform", ""),
                         "spend": round(spend, 2)})
    except Exception:
        pass
    n = max(len(rows), 1)
    # 合理分布：拿前半部分为优秀，后半部分有低效组
    roi_pool = [2.6, 3.1, 2.2, 1.9, 1.7, 0.9, 1.2, 0.6, 3.4, 1.1]
    findings = []
    total_rev = 0.0
    good = 0
    low = 0
    for i, r in enumerate(rows):
        roas = roi_pool[i % len(roi_pool)]
        total_rev += r["spend"] * roas
        if roas >= 1.5:
            good += 1
        if roas < 1:
            low += 1
        findings.append({
            "ad_group": r["ad_group"], "platform": r["platform"], "spend": r["spend"], "roas": roas,
            "status": "优秀" if roas >= 2 else ("正常" if roas >= 1.5 else "偏低"),
            "issue": "效率高，建议加码" if roas >= 1.5 else "成本偏高，建议优化素材/出价",
            "action": "加码预算" if roas >= 1.5 else ("暂停观察或换素材" if roas < 1 else "保持优化"),
        })
    overall_roas = round(total_rev / total_spend, 2) if total_spend else 0
    save = int(total_spend * 0.12)
    return {
        "overall_health": "整体投放%s，%d/%d个广告组达标（ROAS>=1.5），%d个组ROAS<1需清理" % (
            "健康" if overall_roas >= 1.5 else "需优化", good, len(rows), low),
        "total_spend": "$%.0f" % total_spend,
        "total_revenue": "$%.0f" % total_rev,
        "overall_roas": overall_roas,
        "findings": findings[:6],
        "wasted_budget": "$%d（建议送低效组预算向优质组倾斜）" % save,
        "action_list": [
            {"priority": 1, "action": "暌停ROAS<1的广告组", "expected_impact": "预计节省15%无效支出"},
            {"priority": 2, "action": "优质素材扩量至TikTok/IG Reels", "expected_impact": "ROAS提升0.3-0.5"},
            {"priority": 3, "action": "预算向高转化时段集中", "expected_impact": "整体转化率提升10%"},
        ],
        "budget_reallocation": "将低效组预算向ROAS>2高效组倾斜",
        "creative_fatigue": "高点击广告组进入疲劳期，建议每7天更新一次素材",
        "mock_note": "模拟数据（不消耗额度）",
    }




def mock_loop(diagnosis, product=None):
    return {
        "content_pivot": "从功能罗列转向场景化叙事，突出使用前后对比与真实用户反馈",
        "new_selling_points": ["真实场景可视化", "材质/工艺细节特写", "礼盒包装适配节日场景"],
        "image_style_change": "采用更自然的光线环境（居家/户外），减少棚拍感提升真实度",
        "copy_tone_change": "从促销导向改为生活方式陪伴语气，降低压迫感",
        "channel_shift": "将预算转向TikTok Spark Ads + Instagram Reels双开，放大病毒内容",
        "budget_adjustment": "广告与KOL预算各上调5%，优先刺激优质内容再营销",
        "mock_note": "模拟数据（不消耗额度）",
    }


MOCK_ANALYZE = {
    "策略": "关键发现：1)TikTok获最高预算权重，符合短视频种草特性；2)目标人群与产品定位契合度高；3)节奏规划清晰。风险：单平台依赖较高，建议以素材质量双平台并行。",
    "素材": "关键发现：1)文案覆盖多平台不同语境；2)主图风格适配社媒竖屏场景；3)卖点聚焦真实场景价值。建议：增加前3秒钩子文案与多尺寸适配。",
    "红人": "关键发现：1)覆盖TikTok/Instagram/YouTube三平台；2)腰部KOL性价比高、互动强；3)触达话术可直接复用。建议：预留20%预算给长尾持续内容。",
    "诊断": "关键发现：1)高ROAS集中在主投渠道；2)存在需清理的低效广告组；3)素材疲劳信号初现。建议：清理低效组、优质组加码、2周换新素材。",
    "迭代": "关键发现：1)转向场景化叙事；2)预算向优势渠道倾斜；3)新一轮策略可自动吸收改进点，闭环衔接顺畅。",
}


def mock_analyze_text(module_name, service_name=""):
    tpl = MOCK_ANALYZE.get(module_name, "模块执行完成，结果与预期一致；建议下一轮保持节奏并滚动优化。")
    return "[%s] %s" % (service_name, tpl) if service_name else tpl


def mock_optimize_text(has_kol=True):
    head = "整体评价：全流程执行完整，策略-素材-红人-投流-诊断形成有效闭环"
    kol_part = "；红人种草与广告投流双引擎协同，腰部达人+付费放大组合合理" if has_kol else "；本轮以广告投流为主，红人种草未启用，建议后续补充以提升信任背书"
    return (head + kol_part +
            "。优化建议：1)清理ROAS<1的广告组并加码优质组；2)素材每7天轮换一次防疲劳；3)预算向TikTok+IG Reels倾斜。"
            "下轮重点：场景化素材+腰部KOL扩量。全流程闭环完成，上轮迭代已自动应用到下轮策略。")
