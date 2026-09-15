# -*- coding: utf-8 -*-
"""出海指挥官 - 跨境AI营销增长引擎（大管家 x 第三方服务闭环）"""
import sys
import os
import json
import time
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd

from app.agents.core import (
    generate_strategy, generate_content, generate_kol, diagnose_ads, generate_loop,
    steward_chat, steward_analyze, steward_optimize
)
from app.tools.mock_data import generate_mock_csv
from app.config import TEXT_MODEL, IMAGE_MODEL
import app.config as _app_config

st.set_page_config(page_title="出海指挥官 · AI跨境营销闭环", page_icon="🚀", layout="wide")

# ===== 运行模式（侧边栏） =====
with st.sidebar:
    st.markdown("### 🧠 出海指挥官")
    _mock_on = st.toggle("🧪 模拟演示模式（不消耗Token）",
                         value=_app_config.MOCK_MODE,
                         help="开：所有AI能力返回预置模拟数据，用于演示；关：调用真实大模型（需额度）")
_app_config.MOCK_MODE = _mock_on
if _mock_on:
    st.caption("当前：模拟模式 — 全程离线，不调用 API")
else:
    st.caption("当前：真实模式 — 调用百炼大模型")

# =====================================================================
# 全局样式
# =====================================================================
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
        background:
            radial-gradient(1200px 600px at 15% -10%, rgba(0,212,255,0.10), transparent 60%),
            radial-gradient(1000px 500px at 110% 10%, rgba(124,58,237,0.12), transparent 55%),
            radial-gradient(900px 700px at 50% 120%, rgba(0,212,255,0.06), transparent 60%),
            #070b16;
        color: #dfe8ff;
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1560px; }
    hr { display: none !important; }

    .hero { text-align: center; padding: 0.3rem 0 0.1rem 0; }
    .hero-title {
        font-size: 2.3rem; font-weight: 900; letter-spacing: 4px;
        background: linear-gradient(90deg, #7ff7ff 0%, #00d4ff 35%, #7c8cff 70%, #b07cff 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; filter: drop-shadow(0 0 14px rgba(0,212,255,0.25));
    }
    .hero-sub { font-size: 0.75rem; color: #6f83ad; letter-spacing: 6px; margin-top: -2px; }
    .hero-badges { text-align:center; margin: 0.3rem 0 0.4rem 0; }
    .hbadge {
        display:inline-block; padding: 3px 12px; margin: 0 4px; font-size: 0.67rem;
        border-radius: 999px; border: 1px solid rgba(0,212,255,0.28);
        color:#00d4ff; background: rgba(0,212,255,0.06); letter-spacing: 1px; font-weight:600;
    }
    .hbadge.v { border-color: rgba(124,58,237,0.35); color:#b78cff; background: rgba(124,58,237,0.08); }

    .kpis { display:flex; gap:10px; margin: 0.5rem 0 0.7rem 0; }
    .kpi {
        flex:1; padding: 10px 14px; border-radius: 14px; min-width:0;
        background: linear-gradient(160deg, rgba(20,30,62,0.85), rgba(10,16,34,0.85));
        border: 1px solid rgba(0,212,255,0.16);
        box-shadow: 0 4px 18px rgba(0,0,0,0.25);
    }
    .kpi-label { font-size: 0.62rem; color: #6f83ad; letter-spacing: 1px; }
    .kpi-value { font-size: 1.02rem; font-weight: 800; color: #e6efff; margin-top: 2px; }
    .kpi-value.cyan { color: #00d4ff; }
    .kpi-value.violet { color: #b78cff; }
    .kpi-value.green { color: #2fe6b2; }

    .execbar {
        display:flex; align-items:center; gap:10px; margin: 4px 0 6px 0; padding: 8px 14px;
        border-radius: 12px; border: 1px solid rgba(0,212,255,0.25);
        background: linear-gradient(90deg, rgba(0,212,255,0.10), rgba(124,58,237,0.10));
    }
    .execbar .spin { animation: rot 1.4s linear infinite; font-size: 1.1rem; }
    @keyframes rot { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }
    .execbar .txt { font-size: 0.85rem; font-weight: 700; color: #7fe7ff; flex:1; }
    .execbar .step { font-size: 0.72rem; color: #b78cff; }

    .pipe { display:flex; align-items:center; gap:6px; overflow-x:auto; padding: 8px 4px 10px 4px; }
    .pnode {
        display:flex; align-items:center; gap:8px; padding: 6px 11px; border-radius: 12px;
        border: 1px solid rgba(125,141,176,0.22); background: rgba(15,22,44,0.7); white-space:nowrap;
    }
    .pnode .ic { font-size: 1rem; }
    .pnode .nm { font-size: 0.75rem; font-weight: 700; color: #9db0d5; }
    .pnode.done { border-color: rgba(63,230,178,0.45); background: rgba(63,230,178,0.08); }
    .pnode.done .nm { color: #3fe6b2; }
    .pnode.run { border-color: rgba(0,212,255,0.55); background: rgba(0,212,255,0.10); box-shadow: 0 0 12px rgba(0,212,255,0.2); }
    .pnode.run .nm { color: #00d4ff; }
    .parr { color: #3f5178; font-size: 0.9rem; flex-shrink: 0; }

    .cycle-bar { display:flex; gap:12px; overflow-x:auto; padding: 6px 0 10px 0; }
    .cycle-card {
        min-width: 218px; padding: 10px 14px; border-radius: 14px; flex-shrink:0;
        background: linear-gradient(160deg, rgba(22,34,70,0.9), rgba(11,18,40,0.9));
        border: 1px solid rgba(0,212,255,0.18); position: relative;
    }
    .cycle-card::before {
        content:""; position:absolute; left:0; top:10px; bottom:10px; width:3px;
        border-radius: 3px; background: linear-gradient(#00d4ff, #7c3aed);
    }
    .cycle-round { font-size: 0.6rem; color: #00d4ff; font-weight: 800; letter-spacing: 2px; }
    .cycle-round span { color: #4a5f8a; font-weight: 400; }
    .cycle-product { font-size: 0.86rem; color: #e7efff; font-weight: 700; margin: 3px 0 6px 0; }
    .cycle-metrics { display: flex; gap: 18px; }
    .cycle-metric-label { font-size: 0.56rem; color: #5d719e; }
    .cycle-metric-value { font-size: 0.92rem; font-weight: 800; color: #c9d8ff; }
    .mv-good { color: #3fe6b2; } .mv-mid { color: #f5b544; } .mv-bad { color: #ff6b81; }
    .cycle-services { font-size: 0.56rem; color: #4a5f8a; margin-top: 6px; word-break: break-all; }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid rgba(0,212,255,0.16) !important;
        background: linear-gradient(165deg, rgba(18,28,58,0.82), rgba(9,15,32,0.86)) !important;
        box-shadow: 0 8px 28px rgba(0,0,0,0.32) !important;
        padding: 2px 6px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: rgba(0,212,255,0.35) !important; }
    div[data-testid="stColumn"] { padding: 0 6px; }
    div[data-testid="stChatMessage"] { padding: 4px 0; }

    .stButton > button {
        border-radius: 10px !important; font-weight: 600 !important;
        border: 1px solid rgba(0,212,255,0.25) !important;
        background: rgba(0,212,255,0.06) !important; color: #bfeaff !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px); box-shadow: 0 6px 20px rgba(0,212,255,0.25) !important;
        border-color: rgba(0,212,255,0.6) !important; color: #fff !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #00b8e4, #7c3aed) !important;
        border: none !important; color: #04121a !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 26px rgba(0,212,255,0.45) !important; color: #fff !important;
    }

    .svc-head { display:flex; align-items:center; gap:12px; margin-bottom: 4px; flex-wrap:wrap; }
    .svc-logo-box {
        width: 46px; height: 46px; border-radius: 13px;
        display:flex; align-items:center; justify-content:center; font-size: 1.6rem; flex-shrink:0;
        border: 1px solid rgba(255,255,255,0.08);
    }
    .svc-name { font-size: 1.0rem; font-weight: 800; }
    .svc-desc { font-size: 0.68rem; color: #6f83ad; margin-top: 1px; }
    .svc-module-label { font-size: 0.72rem; color: #4a5f8a; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 6px; margin-bottom: 8px; }
    .svc-chips { display:flex; flex-wrap:wrap; gap:6px; }
    .svc-chip {
        display:inline-flex; align-items:center; gap:5px; padding: 3px 10px; border-radius: 999px;
        font-size: 0.66rem; font-weight: 700;
    }

    .chip {
        display:inline-flex; align-items:center; gap:5px; padding: 3px 10px;
        border-radius: 999px; font-size: 0.66rem; font-weight: 800; letter-spacing: 0.5px;
        white-space:nowrap; border: 1px solid;
    }
    .chip-done { color:#3fe6b2; border-color: rgba(63,230,178,0.4); background: rgba(63,230,178,0.08); }
    .chip-run  { color:#00d4ff; border-color: rgba(0,212,255,0.5); background: rgba(0,212,255,0.10); animation: pulse 1.1s infinite; }
    .chip-wait { color:#7d8db0; border-color: rgba(125,141,176,0.25); background: rgba(125,141,176,0.05); }
    @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.55; } }

    .side-title { font-size: 0.9rem; font-weight: 800; color: #cfdcff; margin: 0.3rem 0 0.5rem 0; display:flex; align-items:center; justify-content: space-between; }
    .side-count { font-size: 0.62rem; color: #00d4ff; background: rgba(0,212,255,0.1); padding: 2px 8px; border-radius: 999px; }
    .pdots { display:flex; gap:5px; margin: -4px 0 8px 2px; }
    .dot { width: 21px; height: 21px; border-radius: 6px; display:flex; align-items:center; justify-content:center; font-size: 0.56rem; font-weight: 800; }
    .dot-on { background: rgba(63,230,178,0.16); color: #3fe6b2; border: 1px solid rgba(63,230,178,0.35); }
    .dot-off { background: rgba(125,141,176,0.07); color: #4a5f8a; border: 1px solid rgba(125,141,176,0.2); }

    .steward-head { display:flex; align-items:center; gap:10px; margin-bottom: 8px; }
    .steward-avatar {
        width:44px; height:44px; border-radius: 12px; font-size:1.5rem; display:flex; align-items:center; justify-content:center;
        background: linear-gradient(135deg, rgba(0,212,255,0.22), rgba(124,58,237,0.25));
        border:1px solid rgba(0,212,255,0.35);
    }
    .steward-name { font-size: 1.0rem; font-weight: 900; color:#eaf3ff; }
    .steward-status { font-size: 0.62rem; color: #3fe6b2; letter-spacing: 1px; }

    .closed-loop {
        text-align:center; padding:10px; margin: 8px 0;
        background: linear-gradient(90deg, rgba(0,212,255,0.07), rgba(124,58,237,0.07));
        border-radius: 12px; border: 1px solid rgba(0,212,255,0.18); color: #00d4ff; font-size: 0.78rem; font-weight: 600;
    }
    .parallel-branch {
        text-align:center; padding: 7px 12px; margin: 8px 0 2px 0;
        background: linear-gradient(90deg, rgba(124,58,237,0.08), rgba(0,212,255,0.08));
        border-radius: 10px; border: 1px dashed rgba(124,58,237,0.45); color: #c3a6ff; font-size: 0.74rem;
    }
    .footer { text-align:center; color:#44556f; font-size:0.7rem; padding: 14px 0 4px 0; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)
# =====================================================================
# 第三方服务清单
# =====================================================================
SERVICE_INFO = {
    "Smartly.io":   {"color": "#0091FF", "bg": "rgba(0,145,255,0.14)", "icon": "📊", "desc": "多渠道广告自动化，预算分配与A/B测试"},
    "AdRoll":       {"color": "#FF6B35", "bg": "rgba(255,107,53,0.14)", "icon": "🎯", "desc": "再营销与跨渠道归因，专注retargeting"},
    "店小秘":        {"color": "#4CAF50", "bg": "rgba(76,175,80,0.14)", "icon": "📦", "desc": "跨境电商ERP，商品管理与订单自动化"},
    "Canva":        {"color": "#8B5CF6", "bg": "rgba(139,92,246,0.14)", "icon": "🎨", "desc": "在线设计工具，拖拽式创意制作"},
    "AdCreative.ai":{"color": "#F97316", "bg": "rgba(249,115,22,0.14)", "icon": "🤖", "desc": "AI广告创意生成，转化率预测评分"},
    "Midjourney":   {"color": "#9AA4B2", "bg": "rgba(160,175,200,0.14)", "icon": "🖼️", "desc": "AI图像生成，prompt驱动艺术创作"},
    "Northbeam":    {"color": "#3B82F6", "bg": "rgba(59,130,246,0.14)", "icon": "🔍", "desc": "多触点归因分析，客户旅程追踪"},
    "Triple Whale": {"color": "#7C3AED", "bg": "rgba(124,58,237,0.14)", "icon": "🐳", "desc": "电商数据分析，ROAS与LTV看板"},
    "卖家精灵":        {"color": "#F59E0B", "bg": "rgba(245,158,11,0.14)", "icon": "📈", "desc": "跨境选品分析，关键词与竞品研究"},
    "Optmyzr":      {"color": "#0EA5E9", "bg": "rgba(14,165,233,0.14)", "icon": "⚙️", "desc": "PPC广告优化，智能建议与自动化规则"},
    "Albert AI":    {"color": "#A855F7", "bg": "rgba(168,85,247,0.14)", "icon": "🧠", "desc": "AI驱动营销自动化，自主优化投放"},
    "TikTok Ads":    {"color": "#FE2C55", "bg": "rgba(254,44,85,0.12)", "icon": "🎵", "desc": "短视频广告投放，Spark Ads与直播带货"},
    "Meta Ads":      {"color": "#1877F2", "bg": "rgba(24,119,242,0.12)", "icon": "📘", "desc": "FB/Instagram社交广告，精准受众定向"},
    "Google Ads":    {"color": "#4285F4", "bg": "rgba(66,133,244,0.12)", "icon": "🔍", "desc": "搜索广告与Shopping广告，关键词驱动"},
    "SimilarWeb":   {"color": "#1AD6A6", "bg": "rgba(26,214,166,0.14)", "icon": "📈", "desc": "竞品流量分析，市场洞察与行业对比"},
    "Jungle Scout": {"color": "#37B76B", "bg": "rgba(55,183,107,0.14)", "icon": "🏐", "desc": "亚马逊选品研究，市场机会与竞品分析"},
    "Rockerbox":    {"color": "#E84393", "bg": "rgba(232,67,147,0.14)", "icon": "🧮", "desc": "跨渠道多触点归因，投放效果总结"},
    "Synthesia":    {"color": "#9333EA", "bg": "rgba(147,51,234,0.14)", "icon": "🎬", "desc": "AI视频生成，数字人代短视频制作"},
    "Upfluence":    {"color": "#06B6D4", "bg": "rgba(6,182,212,0.14)", "icon": "🤝", "desc": "红人发现与自动触达，CRM管理"},
    "Grin":         {"color": "#F59E0B", "bg": "rgba(245,158,11,0.14)", "icon": "🌞", "desc": "红人营销平台，合作管理与材料追踪"},
    "HypeAuditor":  {"color": "#8B5CF6", "bg": "rgba(139,92,246,0.14)", "icon": "📊", "desc": "红人数据分析，虚假粉丝检测与匹配"},
}

MODULE_SERVICES = {
    "strategy":  ["卖家精灵", "SimilarWeb", "Jungle Scout"],
    "content":   ["Canva", "AdCreative.ai", "Midjourney", "Synthesia"],
    "placement": ["TikTok Ads", "Meta Ads", "Google Ads"],
    "kol":       ["Upfluence", "Grin", "HypeAuditor"],
    "diagnosis": ["Northbeam", "Triple Whale", "Rockerbox"],
}
MULTI_MODULES = {"placement", "content"}

PIPE_STEPS = [
    ("strategy",  "🧭", "策略"),
    ("content",   "🎨", "素材"),
    ("kol",       "🎯", "红人"),
    ("placement", "📣", "投流"),
    ("diagnosis", "🔍", "诊断"),
    ("loop",      "🔄", "迭代"),
]
STATUS_KEYS = {"strategy": "strategy", "content": "content", "kol": "kol",
               "placement": "csv_data", "diagnosis": "diagnosis", "loop": "loop"}
STEP_NAMES = {"plan": "全局规划", "strategy": "策略生成", "content": "素材生成",
              "kol": "红人匹配", "placement": "投流启动", "diagnose": "投放诊断",
              "iterate": "迭代优化", "optimize": "闭环复盘"}
EXEC_ALL = ["plan", "strategy", "content", "kol", "placement", "diagnose", "iterate", "optimize"]

# =====================================================================
# 会话初始状态
# =====================================================================
defaults = {
    "products": {
        "p1": {"name": "便携蓝牙音箱", "budget": "5000", "market": "美国", "extra": "防水IPX7,20W重低音,户外便携,3C数码",
               "strategy": None, "content": None, "kol": None, "diagnosis": None, "loop": None, "csv_data": None,
               "history": {"strategy": [], "content": [], "kol": [], "diagnosis": [], "loop": []},
               "services": {"strategy": "卖家精灵", "content": ["Canva"], "placement": ["TikTok Ads", "Meta Ads", "Google Ads"], "kol": "Upfluence", "diagnosis": "Northbeam"}},
        "p2": {"name": "高腰瑜伽Leggings", "budget": "3000", "market": "美国", "extra": "高腰提臀,无痕口袋,运动服饰",
               "strategy": None, "content": None, "kol": None, "diagnosis": None, "loop": None, "csv_data": None,
               "history": {"strategy": [], "content": [], "kol": [], "diagnosis": [], "loop": []},
               "services": {"strategy": "SimilarWeb", "content": ["AdCreative.ai"], "placement": ["Meta Ads"], "kol": "Upfluence", "diagnosis": "Triple Whale"}},
        "p3": {"name": "智能宠物喂食器", "budget": "8000", "market": "日本", "extra": "APP远程控制,定时定量,摄像头,宠物用品",
               "strategy": None, "content": None, "kol": None, "diagnosis": None, "loop": None, "csv_data": None,
               "history": {"strategy": [], "content": [], "kol": [], "diagnosis": [], "loop": []},
               "services": {"strategy": "卖家精灵", "content": ["Midjourney"], "placement": ["Google Ads"], "kol": "Upfluence", "diagnosis": "Rockerbox"}},
        "p4": {"name": "食品级硅胶厨具套装", "budget": "2000", "market": "德国", "extra": "锅铲勺垫六件套,耐高温,环保家居",
               "strategy": None, "content": None, "kol": None, "diagnosis": None, "loop": None, "csv_data": None,
               "history": {"strategy": [], "content": [], "kol": [], "diagnosis": [], "loop": []},
               "services": {"strategy": "Jungle Scout", "content": ["Canva"], "placement": ["Google Ads"], "kol": "Upfluence", "diagnosis": "Northbeam"}},
        "p5": {"name": "LED三色化妆镜", "budget": "4000", "market": "韩国", "extra": "触控调光,三色光源,桌面美妆个护",
               "strategy": None, "content": None, "kol": None, "diagnosis": None, "loop": None, "csv_data": None,
               "history": {"strategy": [], "content": [], "kol": [], "diagnosis": [], "loop": []},
               "services": {"strategy": "SimilarWeb", "content": ["AdCreative.ai"], "placement": ["Meta Ads"], "kol": "Upfluence", "diagnosis": "Triple Whale"}},
        "p6": {"name": "USB便携榨汁杯", "budget": "3500", "market": "美国", "extra": "Type-C充电,随榨随喝,健康小家电",
               "strategy": None, "content": None, "kol": None, "diagnosis": None, "loop": None, "csv_data": None,
               "history": {"strategy": [], "content": [], "kol": [], "diagnosis": [], "loop": []},
               "services": {"strategy": "卖家精灵", "content": ["Midjourney"], "placement": ["TikTok", "Meta Ads", "Google Ads"], "kol": "Upfluence", "diagnosis": "Rockerbox"}},
        "p7": {"name": "STEM儿童积木玩具", "budget": "6000", "market": "欧洲", "extra": "大颗粒,益智教育,安全材质,母婴玩具",
               "strategy": None, "content": None, "kol": None, "diagnosis": None, "loop": None, "csv_data": None,
               "history": {"strategy": [], "content": [], "kol": [], "diagnosis": [], "loop": []},
               "services": {"strategy": "Jungle Scout", "content": ["Canva"], "placement": ["Google Ads"], "kol": "Upfluence", "diagnosis": "Northbeam"}},
        "p8": {"name": "磁吸车载手机支架", "budget": "1500", "market": "美国", "extra": "重力夹持,360旋转,汽车配件",
               "strategy": None, "content": None, "kol": None, "diagnosis": None, "loop": None, "csv_data": None,
               "history": {"strategy": [], "content": [], "kol": [], "diagnosis": [], "loop": []},
               "services": {"strategy": "SimilarWeb", "content": ["AdCreative.ai"], "placement": ["Meta"], "kol": "Upfluence", "diagnosis": "Triple Whale"}},
    },
    "current_pid": "p1",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
for _k, _v in (("messages", []), ("cycle_history", []), ("exec_queue", []), ("apply_loop", True)):
    if _k not in st.session_state:
        st.session_state[_k] = _v


def cur():
    return st.session_state.products[st.session_state.current_pid]


def save_history(key, result):
    p = cur()
    if p.get(key):
        p["history"][key].append({"data": p[key], "time": time.strftime("%H:%M:%S")})
    p[key] = result


def get_loop_feedback():
    if st.session_state.apply_loop and cur().get("loop"):
        return cur()["loop"]
    return None


def get_state_summary():
    p = cur()
    parts = []
    parts.append("商品:" + p.get("name", ""))
    parts.append("策略:" + ("已生成" if p.get("strategy") else "未生成"))
    parts.append("素材:" + ("已生成" if p.get("content") else "未生成"))
    parts.append("红人:" + ("已匹配" if p.get("kol") else "未匹配"))
    parts.append("投流:" + ("已启动" if p.get("csv_data") else "未启动"))
    parts.append("迭代:" + ("已生成" if p.get("loop") else "未生成"))
    return "; ".join(parts)


def _svc_display(val):
    if isinstance(val, list):
        return " + ".join(val) if val else ""
    return val or ""


def _svc_list(val, all_svcs):
    if isinstance(val, list):
        return [v for v in val if v in all_svcs]
    if val and val in all_svcs:
        return [val]
    return [all_svcs[0]]


def _chip(kind, text):
    return '<span class="chip chip-%s">%s</span>' % (kind, text)


def _module_status(p, key):
    running = st.session_state.get("exec_queue", [])
    rk = STATUS_KEYS[key]
    if running and running[0] == key:
        return "run", "执行中…"
    if running and key in running:
        return "wait", "排队中"
    if p.get(rk):
        return "done", "已完成 ✓"
    return "wait", "待执行"


def _service_chip_html(name):
    info = SERVICE_INFO.get(name, {})
    color = info.get("color", "#9fb3d8")
    bg = info.get("bg", "rgba(120,140,180,0.1)")
    icon = info.get("icon", "🔧")
    tag = "data:image/svg+xml" if name.startswith("svg:") else icon
    return ('<span class="svc-chip" style="color:%s;background:%s;'
            'border:1px solid rgba(255,255,255,0.08);">%s %s</span>') % (color, bg, tag, name.replace("svg:", ""))


def _pipe_html():
    p = cur()
    running = st.session_state.get("exec_queue", [])
    run_key = running[0] if running else None
    cells = []
    for i, (key, icon, nm) in enumerate(PIPE_STEPS):
        has = bool(p.get(STATUS_KEYS[key]))
        if has:
            cls = "pnode done"
        elif key == run_key:
            cls = "pnode run"
        else:
            cls = "pnode"
        cells.append('<div class="%s"><span class="ic">%s</span><span class="nm">%s</span></div>' % (cls, icon, nm))
        if i < len(PIPE_STEPS) - 1:
            if key == "kol":
                cells.append('<span class="parr">🔀可并行</span>')
            else:
                cells.append('<span class="parr">→</span>')
    return '<div class="pipe">%s</div>' % "".join(cells)


def _dots(p):
    order = [("strategy", "策"), ("content", "材"), ("kol", "人"), ("csv_data", "投"), ("diagnosis", "诊"), ("loop", "循")]
    parts = []
    for k, lab in order:
        cls = "dot-on" if p.get(k) else "dot-off"
        parts.append('<span class="dot %s">%s</span>' % (cls, lab))
    return '<div class="pdots">%s</div>' % "".join(parts)


def _roas_cls(v):
    try:
        v = float(v)
    except Exception:
        return "mv-mid"
    if v >= 2:
        return "mv-good"
    if v >= 1.5:
        return "mv-mid"
    return "mv-bad"
# =====================================================================
# 队列式执行（每次 rerun 执行一步）
# =====================================================================
product = cur().get("name", "")
budget = cur().get("budget", "5000")
market = cur().get("market", "美国")
extra = cur().get("extra", "")

if st.session_state.get("exec_queue"):
    step = st.session_state.exec_queue.pop(0)
    svcs = cur().get("services", {})
    loop_fb = get_loop_feedback()
    if step == "plan":
        st.session_state.messages.append({"role": "assistant", "content": "好的，开始执行全流程：策略 -> 素材 -> [红人种草 ⊕ 投流放大] -> 诊断 -> 迭代，每步我会分析结果并给出建议。"})
    elif step == "strategy":
        save_history("strategy", generate_strategy(product, budget, market, extra, loop_fb, svcs.get("strategy", "卖家精灵")))
        analysis = steward_analyze("策略", cur()["strategy"], svcs.get("strategy", ""))
        st.session_state.messages.append({"role": "assistant", "content": "📊 [" + svcs.get("strategy", "") + "] 策略分析：" + analysis})
    elif step == "content":
        if cur().get("strategy"):
            save_history("content", generate_content(product, market, cur()["strategy"], _svc_display(svcs.get("content", "Canva"))))
            analysis = steward_analyze("素材", cur()["content"], _svc_display(svcs.get("content", "")))
            st.session_state.messages.append({"role": "assistant", "content": "📊 [" + _svc_display(svcs.get("content", "")) + "] 素材分析：" + analysis})
    elif step == "kol":
        if cur().get("strategy"):
            save_history("kol", generate_kol(product, market, cur()["strategy"], svcs.get("kol", "Upfluence")))
            analysis = steward_analyze("红人", cur()["kol"], svcs.get("kol", ""))
            st.session_state.messages.append({"role": "assistant", "content": "🎯 [" + svcs.get("kol", "") + "] 红人分析：" + analysis})
    elif step == "placement":
        cur()["csv_data"] = generate_mock_csv(product, market, float(budget), svcs.get("placement", ["TikTok Ads"]))
        st.session_state.messages.append({"role": "assistant", "content": "📣 [" + _svc_display(svcs.get("placement", "")) + "] 投流已启动（多渠道），投放数据已生成。"})
    elif step == "diagnose":
        if cur().get("csv_data"):
            save_history("diagnosis", diagnose_ads(cur()["csv_data"], product, market, svcs.get("diagnosis", "Northbeam")))
            analysis = steward_analyze("诊断", cur()["diagnosis"], svcs.get("diagnosis", ""))
            st.session_state.messages.append({"role": "assistant", "content": "📊 [" + svcs.get("diagnosis", "") + "] 诊断分析：" + analysis})
    elif step == "iterate":
        if cur().get("diagnosis"):
            save_history("loop", generate_loop(cur()["diagnosis"], svcs.get("diagnosis", "Rockerbox")))
            analysis = steward_analyze("迭代", cur()["loop"], svcs.get("diagnosis", ""))
            st.session_state.messages.append({"role": "assistant", "content": "📊 [" + svcs.get("diagnosis", "") + "] 迭代分析：" + analysis})
    elif step == "optimize":
        optimization = steward_optimize(cur()["strategy"], cur()["content"], cur()["kol"], cur()["diagnosis"], cur()["loop"], svcs)
        st.session_state.messages.append({"role": "assistant", "content": "🎯 全流程优化建议：" + optimization + "\n\n闭环完成。输入「全流程」再次执行，迭代建议自动应用。"})
        diag = cur().get("diagnosis", {})
        st.session_state.cycle_history.append({
            "round": len(st.session_state.cycle_history) + 1,
            "time": time.strftime("%H:%M:%S"),
            "product": product,
            "services": dict(svcs),
            "roas": diag.get("overall_roas", "N/A") if isinstance(diag, dict) else "N/A",
            "spend": diag.get("total_spend", "N/A") if isinstance(diag, dict) else "N/A",
            "revenue": diag.get("total_revenue", "N/A") if isinstance(diag, dict) else "N/A",
            "summary": optimization[:80] if optimization else "",
        })

# =====================================================================
# 顶部：标题 + 徽章 + KPI + 流水线 + 循环历史
# =====================================================================
st.markdown(
    '<div class="hero"><div class="hero-title">出海指挥官</div>'
    '<div class="hero-sub">EXPORT  COMMANDER  ·  AI  GROWTH  LOOP</div></div>',
    unsafe_allow_html=True)
st.markdown(
    '<div class="hero-badges">'
    '<span class="hbadge">🧠 大管家大脑 · 策略分析优化</span>'
    '<span class="hbadge v">🧩 第三方服务矩阵</span>'
    '<span class="hbadge">🔄 全链路闭环迭代</span>'
    '</div>', unsafe_allow_html=True)

_kp = cur()
_kpi_items = [
    ("当前商品", _kp.get("name", "-"), ""),
    ("预算", "$" + str(_kp.get("budget", "0")), "cyan"),
    ("目标市场", _kp.get("market", "-"), "violet"),
]
_done_n = sum(1 for _sk in PIPE_STEPS if _kp.get(STATUS_KEYS[_sk[0]]))
_kpi_items.append(("闭环进度", "%s / 6" % _done_n, "green"))
_diag0 = _kp.get("diagnosis") or {}
if _diag0:
    _kpi_items.append(("ROAS", _diag0.get("overall_roas", "N/A"), "green"))
_kpi_html = '<div class="kpis">'
for _lab, _val, _cls in _kpi_items:
    _kpi_html += '<div class="kpi"><div class="kpi-label">%s</div><div class="kpi-value %s">%s</div></div>' % (_lab, _cls, _val)
_kpi_html += '</div>'
st.markdown(_kpi_html, unsafe_allow_html=True)

_exec_q = st.session_state.get("exec_queue", [])
if _exec_q:
    _cur_done = len(EXEC_ALL) - len(_exec_q)
    st.markdown(
        '<div class="execbar"><span class="spin">⚡</span>'
        '<span class="txt">大管家执行中… 第 %d / %d 步</span>'
        '<span class="step">%s</span></div>'
        % (min(_cur_done + 1, len(EXEC_ALL)), len(EXEC_ALL), STEP_NAMES.get(_exec_q[0], "")), unsafe_allow_html=True)
    st.progress(min(1.0, (_cur_done + 1) / float(len(EXEC_ALL))))

st.markdown(_pipe_html(), unsafe_allow_html=True)

if st.session_state.get("cycle_history"):
    _ch = st.session_state.cycle_history
    _html = '<div class="cycle-bar">'
    for _c in _ch:
        _svc_str = " | ".join((v if isinstance(v, str) else "+".join(v)) for v in _c.get("services", {}).values()) if _c.get("services") else ""
        _html += (
            '<div class="cycle-card">'
            '<div class="cycle-round">ROUND %d <span>%s</span></div>'
            '<div class="cycle-product">%s</div>'
            '<div class="cycle-metrics">'
            '<div><div class="cycle-metric-label">ROAS</div><div class="cycle-metric-value %s">%s</div></div>'
            '<div><div class="cycle-metric-label">花费</div><div class="cycle-metric-value">%s</div></div>'
            '<div><div class="cycle-metric-label">收入</div><div class="cycle-metric-value">%s</div></div>'
            '</div>'
            '<div class="cycle-services">%s</div>'
            '</div>'
        ) % (_c["round"], _c.get("time", ""), _c["product"], _roas_cls(_c.get("roas")),
             _c.get("roas", "N/A"), _c.get("spend", "N/A"), _c.get("revenue", "N/A"), _svc_str)
    _html += '</div>'
    st.markdown(_html, unsafe_allow_html=True)
# =====================================================================
# 三栏布局
# =====================================================================
col_left, col_center, col_right = st.columns([1, 2.5, 1.3])

# =====================================================================
# 左栏：商品库 + 参数 + 历史
# =====================================================================
with col_left:
    st.markdown('<div class="side-title">📦 商品库 <span class="side-count">%d</span></div>' % len(st.session_state.products), unsafe_allow_html=True)
    for pid, _pp in st.session_state.products.items():
        is_cur = pid == st.session_state.current_pid
        _lbl = "%s · $%s · %s" % (_pp.get("name", ""), _pp.get("budget", ""), _pp.get("market", ""))
        if st.button(_lbl, key="btn_prod_%s" % pid, use_container_width=True,
                     type="primary" if is_cur else "secondary"):
            st.session_state.current_pid = pid
            st.rerun()
        st.markdown(_dots(_pp), unsafe_allow_html=True)
    if st.button("➕ 添加商品", key="btn_add", use_container_width=True):
        new_pid = "p%d" % (len(st.session_state.products) + 1)
        st.session_state.products[new_pid] = {
            "name": "新产品%d" % (len(st.session_state.products) + 1),
            "budget": "5000", "market": "美国", "extra": "",
            "strategy": None, "content": None, "kol": None, "diagnosis": None, "loop": None, "csv_data": None,
            "history": {"strategy": [], "content": [], "kol": [], "diagnosis": [], "loop": []},
            "services": {"strategy": "卖家精灵", "content": ["Canva"], "placement": ["TikTok Ads", "Meta Ads", "Google Ads"], "kol": "Upfluence", "diagnosis": "Northbeam"},
        }
        st.session_state.current_pid = new_pid
        st.rerun()

    st.markdown("---")
    st.markdown('<div class="side-title">⚙️ 商品参数</div>', unsafe_allow_html=True)
    with st.form("product_form"):
        st.text_input("产品名称", value=cur().get("name", ""), key="pf_name")
        st.text_input("预算 (USD)", value=cur().get("budget", "5000"), key="pf_budget")
        st.text_input("目标市场", value=cur().get("market", "美国"), key="pf_market")
        st.text_input("补充说明", value=cur().get("extra", ""), key="pf_extra")
        if st.form_submit_button("💾 保存参数", use_container_width=True):
            cur()["name"] = st.session_state.pf_name
            cur()["budget"] = st.session_state.pf_budget
            cur()["market"] = st.session_state.pf_market
            cur()["extra"] = st.session_state.pf_extra
            st.rerun()
    if cur().get("loop"):
        st.session_state.apply_loop = st.checkbox("🔄 自动复用上轮迭代建议", value=bool(st.session_state.apply_loop), key="cb_loop")

    st.markdown("---")
    st.markdown('<div class="side-title">📜 资产历史</div>', unsafe_allow_html=True)
    _h = cur().get("history", {})
    _cnt = " | ".join("%s×%d" % (lab, len(_h.get(k, []))) for lab, k in
                      [("策略", "strategy"), ("素材", "content"), ("红人", "kol"), ("诊断", "diagnosis"), ("迭代", "loop")])
    if _cnt:
        st.caption(_cnt)
    else:
        st.caption("暂无记录")
    if st.button("🗑️ 重置当前商品", key="btn_reset", use_container_width=True):
        pid = st.session_state.current_pid
        old_name = st.session_state.products[pid].get("name", "未命名")
        st.session_state.products[pid] = {
            "name": old_name, "budget": "5000", "market": "美国", "extra": "",
            "strategy": None, "content": None, "kol": None, "diagnosis": None, "loop": None, "csv_data": None,
            "history": {"strategy": [], "content": [], "kol": [], "diagnosis": [], "loop": []},
            "services": {"strategy": "卖家精灵", "content": ["Canva"], "placement": ["TikTok Ads", "Meta Ads", "Google Ads"], "kol": "Upfluence", "diagnosis": "Northbeam"},
        }
        st.rerun()
# =====================================================================
# 中间栏：五大闭环模块（第三方服务矩阵）
# =====================================================================
with col_center:

    def svc_header(module_key, module_num, title):
        p = cur()
        svcs = MODULE_SERVICES[module_key]
        stored = p.setdefault("services", {}).get(module_key, svcs[0])
        pid = st.session_state.current_pid
        if module_key in MULTI_MODULES:
            cur_list = _svc_list(stored, svcs)
            sel = st.multiselect("服务", svcs, default=cur_list, key="svc_%s_%s" % (module_key, pid), label_visibility="collapsed")
            if not sel:
                sel = [svcs[0]]
            p["services"][module_key] = sel
            logos = "".join(
                '<div style="display:flex;align-items:center;gap:6px;margin-right:6px;">'
                '<div class="svc-logo-box" style="background:%s;width:38px;height:38px;font-size:1.3rem;border-radius:11px;">%s</div>'
                '<span style="font-size:0.9rem;font-weight:800;color:%s;">%s</span>'
                '</div>' % (SERVICE_INFO[s]["bg"], SERVICE_INFO[s]["icon"], SERVICE_INFO[s]["color"], s)
                for s in sel)
            descs = "; ".join(SERVICE_INFO[s]["desc"] for s in sel)
            st.markdown(
                '<div class="svc-head">%s</div>'
                '<div class="svc-module-label">模块%s · %s · %s</div>'
                % ('<div style="display:flex;gap:2px;">%s</div>' % logos, module_num, title, descs),
                unsafe_allow_html=True)
            return sel
        current_svc = stored if isinstance(stored, str) else (stored[0] if isinstance(stored, list) and stored else svcs[0])
        svc = st.selectbox("服务", svcs, index=svcs.index(current_svc) if current_svc in svcs else 0,
                           key="svc_%s_%s" % (module_key, pid), label_visibility="collapsed")
        p["services"][module_key] = svc
        info = SERVICE_INFO[svc]
        st.markdown(
            '<div class="svc-head">'
            '<div class="svc-logo-box" style="background:%s;">%s</div>'
            '<div><div class="svc-name" style="color:%s;">%s</div><div class="svc-desc">%s</div></div>'
            '</div>'
            '<div class="svc-module-label">模块%s · %s</div>'
            % (info["bg"], info["icon"], info["color"], svc, info["desc"], module_num, title),
            unsafe_allow_html=True)
        return svc

    # ---------- 模块1：营销策略 ----------
    with st.container(border=True):
        svc_header("strategy", "1", "营销策略生成")
        st.markdown('<div style="display:flex;align-items:center;">%s</div>' % _chip(*_module_status(cur(), "strategy")), unsafe_allow_html=True)
        if cur().get("loop") and st.session_state.apply_loop:
            st.info("🔄 闭环反哺：上轮迭代建议已自动应用于本次策略")
        if st.button("🧭 生成策略", key="btn_strategy", type="primary", use_container_width=True):
            st.session_state.exec_queue = ["strategy"]
            st.rerun()
        _s = cur().get("strategy")
        if _s:
            if "raw" in _s:
                st.error("解析失败"); st.text(_s["raw"][:2000])
            else:
                st.markdown("**市场定位**：%s" % _s.get("market_positioning", ""))
                st.markdown("**目标用户**：%s" % _s.get("target_audience", ""))
                st.markdown("**渠道策略**：")
                for _ch in _s.get("channel_strategy", []):
                    st.markdown("- %s ｜ 预算占比 **%d%%** ｜ %s" % (_ch.get("channel", ""), _ch.get("budget_pct", 0), _ch.get("content_type", "")))
                _ca, _cb = st.columns(2)
                with _ca:
                    st.markdown("**内容规划**：")
                    for _i, _cp in enumerate(_s.get("content_plan", []), 1):
                        st.markdown("%d. %s" % (_i, _cp))
                with _cb:
                    _ba = _s.get("budget_allocation", {})
                    st.markdown("**预算分配**：")
                    for _k2, _v2 in _ba.items():
                        st.progress(min(max(float(_v2), 0.0), 100.0) / 100.0, text="%s: %d%%" % (_k2, _v2))
                st.markdown("**KOL建议**：%s" % _s.get("kol_suggestion", ""))
                st.markdown("**核心指标**：%s" % ", ".join(_s.get("key_metrics", [])))
                st.markdown("**时间线**：%s" % _s.get("timeline", ""))
        if cur().get("history", {}).get("strategy"):
            with st.expander("策略历史 (%d)" % len(cur()["history"]["strategy"])):
                for _i, _hd in enumerate(reversed(cur()["history"]["strategy"]), 1):
                    st.markdown("**第%d条（%s）**" % (_i, _hd["time"]))
                    st.json(_hd["data"])

    # ---------- 模块2：AI素材工厂 ----------
    with st.container(border=True):
        svc_header("content", "2", "AI素材工厂")
        st.markdown('<div style="display:flex;align-items:center;">%s</div>' % _chip(*_module_status(cur(), "content")), unsafe_allow_html=True)
        if not cur().get("strategy"):
            st.info("请先完成「策略」再生成素材")
        else:
            if st.button("🎨 生成素材（文案+主图）", key="btn_content", type="primary", use_container_width=True):
                st.session_state.exec_queue = ["content"]
                st.rerun()
        _c = cur().get("content")
        if _c:
            if "raw" in _c:
                st.error("解析失败"); st.text(_c["raw"][:2000])
            else:
                _cl, _cr = st.columns([3, 2])
                with _cl:
                    st.markdown("**产品标题**：%s" % _c.get("product_title", ""))
                    st.markdown("**英文标题**：%s" % _c.get("product_title_en", ""))
                    st.markdown("**Slogan**：%s" % _c.get("slogan", ""))
                    st.markdown("**TikTok 文案**：%s" % _c.get("ad_copy_tiktok", ""))
                    st.markdown("**Instagram 文案**：%s" % _c.get("ad_copy_instagram", ""))
                    st.markdown("**Meta 广告文案**：%s" % _c.get("ad_copy_meta", ""))
                    st.markdown("**核心卖点**：")
                    for _sp in _c.get("selling_points", []):
                        st.markdown("- %s" % _sp)
                    st.markdown("**文化适配提示**：%s" % _c.get("cultural_tips", ""))
                with _cr:
                    if _c.get("image_url"):
                        try:
                            _iu = _c["image_url"]
                            if _iu.startswith("http") or _iu.startswith("data:"):
                                st.image(_iu, caption="AI 生成主图 · 模拟", use_container_width=True)
                        except Exception as _e:
                            st.error("图片加载失败：%s" % _e)
                    elif _c.get("image_error"):
                        st.warning("图片生成异常：%s" % _c["image_error"][:200])
        if cur().get("history", {}).get("content"):
            with st.expander("素材历史 (%d)" % len(cur()["history"]["content"])):
                for _i, _hd in enumerate(reversed(cur()["history"]["content"]), 1):
                    st.markdown("**第%d条（%s）**" % (_i, _hd["time"]))
                    _dd = _hd["data"]
                    if isinstance(_dd, dict) and "raw" not in _dd:
                        st.markdown("标题：%s" % _dd.get("product_title", ""))
                    else:
                        st.json(_dd)
    st.markdown('<div class="parallel-branch">⚡ 红人种草 与 投流放大 是两条并行推广路径：可只做一条，也可同时开启双引擎</div>', unsafe_allow_html=True)

    # ---------- 模块3：红人种草 ----------
    with st.container(border=True):
        svc_header("kol", "3", "红人种草")
        st.markdown('<div style="display:flex;align-items:center;">%s</div>' % _chip(*_module_status(cur(), "kol")), unsafe_allow_html=True)
        if not cur().get("content"):
            st.info("请先完成素材生成")
        else:
            st.caption(" 📈 基于素材匹配腰部达人，并自动生成触达话术")
            if st.button("🎯 匹配 KOL", key="btn_kol", type="primary", use_container_width=True):
                st.session_state.exec_queue = ["kol"]
                st.rerun()
        _k = cur().get("kol")
        if _k:
            if "raw" in _k:
                st.error("解析失败"); st.text(_k["raw"][:2000])
            else:
                st.markdown("**KOL 匹配结果**：")
                for _m in _k.get("kol_matches", []):
                    _c1, _c2 = st.columns([3, 1])
                    with _c1:
                        st.markdown("- **%s** ｜ %s ｜ %s 粉丝 ｜ 互动率 %s" % (
                            _m.get("name", ""), _m.get("platform", ""), _m.get("followers", ""), _m.get("engagement_rate", "")))
                        st.markdown("  - 合作：%s ｜ 费用：%s" % (_m.get("collaboration_type", ""), _m.get("estimated_cost", "")))
                        st.markdown("  - 匹配理由：%s" % _m.get("reason", ""))
                    with _c2:
                        _score = _m.get("fit_score", 0)
                        st.metric("匹配度", _score if isinstance(_score, (int, float)) else str(_score))
                st.markdown("**触达话术**：")
                st.info(_k.get("outreach_script", ""))
                st.markdown("**合作方案**：%s" % _k.get("collaboration_plan", ""))
                st.markdown("**预算分配**：%s" % _k.get("budget_split", ""))
        if cur().get("history", {}).get("kol"):
            with st.expander("红人历史 (%d)" % len(cur()["history"]["kol"])):
                for _i, _hd in enumerate(reversed(cur()["history"]["kol"]), 1):
                    st.markdown("**第%d条（%s）**" % (_i, _hd["time"]))
                    st.json(_hd["data"])

    # ---------- 模块4：投流放大 ----------
    with st.container(border=True):
        svc_header("placement", "4", "投流放大")
        st.markdown('<div style="display:flex;align-items:center;">%s</div>' % _chip(*_module_status(cur(), "placement")), unsafe_allow_html=True)
        if not cur().get("content"):
            st.info("请先完成素材生成")
        else:
            st.caption(" 📢 多渠道智能投放 · 默认全选，可自定义渠道组合")
            if st.button("🚀 启动投放", key="btn_placement", type="primary", use_container_width=True):
                st.session_state.exec_queue = ["placement"]
                st.rerun()
            if cur().get("csv_data"):
                try:
                    _df = pd.read_csv(io.StringIO(cur()["csv_data"]))
                except Exception:
                    _df = None
                if _df is not None:
                    _c1, _c2, _c3, _c4 = st.columns(4)
                    _c1.metric("广告组数", len(_df))
                    _c2.metric("总花费", "$%.0f" % _df["spend"].sum())
                    _c3.metric("总转化", int(_df["conversions"].sum()))
                    _c4.metric("平均 ROAS", "%.2f" % _df["roas"].mean())
                    st.dataframe(_df, use_container_width=True, height=180)
        if cur().get("history", {}).get("diagnosis"):
            with st.expander("投放历史 (%d)" % len(cur()["history"]["diagnosis"])):
                for _i, _hd in enumerate(reversed(cur()["history"]["diagnosis"]), 1):
                    st.markdown("**第%d条（%s）**" % (_i, _hd["time"]))
                    st.json(_hd["data"])

    # ---------- 模块5：投放诊断与迭代 ----------
    with st.container(border=True):
        svc_header("diagnosis", "5", "投放诊断与迭代")
        st.markdown('<div style="display:flex;align-items:center;">%s</div>' % _chip(*_module_status(cur(), "diagnosis")), unsafe_allow_html=True)
        if not cur().get("csv_data"):
            st.info("请先启动投流")
        else:
            if st.button("🩺 诊断 + 生成迭代方案", key="btn_diag", type="primary", use_container_width=True):
                st.session_state.exec_queue = ["diagnose", "iterate"]
                st.rerun()
        _d = cur().get("diagnosis")
        if _d:
            if "raw" in _d:
                st.error("解析失败"); st.text(_d["raw"][:2000])
            else:
                _c1, _c2, _c3 = st.columns(3)
                _c1.metric("总花费", _d.get("total_spend", "N/A"))
                _c2.metric("总收入", _d.get("total_revenue", "N/A"))
                _c3.metric("整体 ROAS", _d.get("overall_roas", "N/A"))
                st.markdown("**整体评估**：%s" % _d.get("overall_health", ""))
                st.markdown("**广告组诊断**：")
                for _f in _d.get("findings", []):
                    st.markdown("- %s ｜ 状态 `%s` ｜ 花费 %s ｜ ROAS %s" % (_f.get("ad_group", ""), _f.get("status", ""), _f.get("spend", ""), _f.get("roas", "")))
                    st.markdown("  - 问题：%s" % _f.get("issue", ""))
                    st.markdown("  - 动作：%s" % _f.get("action", ""))
                st.markdown("**浪费预算**：%s" % _d.get("wasted_budget", "N/A"))
                st.markdown("**优化动作清单**：")
                for _a in _d.get("action_list", []):
                    st.markdown("%d. %s（预期：%s）" % (_a.get("priority", 0), _a.get("action", ""), _a.get("expected_impact", "")))
                st.markdown("**重分配**：%s" % _d.get("budget_reallocation", ""))
                st.markdown("**素材疲劳**：%s" % _d.get("creative_fatigue", ""))
        _l = cur().get("loop")
        if _l:
            if "raw" not in _l:
                st.markdown("---")
                st.markdown("**内容方向调整**：%s" % _l.get("content_pivot", ""))
                st.markdown("**新卖点**：%s" % ", ".join(_l.get("new_selling_points", [])))
                st.markdown("**主图风格调整**：%s" % _l.get("image_style_change", ""))
                st.markdown("**文案语气调整**：%s" % _l.get("copy_tone_change", ""))
                st.markdown("**渠道策略调整**：%s" % _l.get("channel_shift", ""))
                st.markdown("**预算调整**：%s" % _l.get("budget_adjustment", ""))
                st.markdown('<div class="closed-loop">🧭 策略<b>→</b>🎨 素材<b>→</b>[ 🎯 红人种草 ⊕ 📣 投流放大 ]<b>→</b>🔍 诊断<b>→</b>🔄 迭代<b>→</b>🔁 反哺策略</div>', unsafe_allow_html=True)
        if cur().get("history", {}).get("loop"):
            with st.expander("迭代历史 (%d)" % len(cur()["history"]["loop"])):
                for _i, _hd in enumerate(reversed(cur()["history"]["loop"]), 1):
                    st.markdown("**第%d条（%s）**" % (_i, _hd["time"]))
                    st.json(_hd["data"])
# =====================================================================
# 右栏：大管家（对话 + 全链路调度）
# =====================================================================
with col_right:
    st.markdown(
        '<div class="steward-head"><div class="steward-avatar">🧠</div>'
        '<div><div class="steward-name">大管家 Steward</div>'
        '<div class="steward-status">● 在线 · 全链路智能调度</div></div></div>', unsafe_allow_html=True)

    def steward_handle(text):
        st.session_state.messages.append({"role": "user", "content": text})
        result = steward_chat(text, get_state_summary(), cur().get("services", {}))
        st.session_state.messages.append({"role": "assistant", "content": result["response"]})
        action = result.get("action", "chat")
        if action == "run_all":
            st.session_state.exec_queue = ["plan", "strategy", "content", "kol", "placement", "diagnose", "iterate", "optimize"]
        elif action == "run_strategy":
            st.session_state.exec_queue = ["strategy"]
        elif action == "run_content":
            st.session_state.exec_queue = ["content"]
        elif action == "run_kol":
            st.session_state.exec_queue = ["kol"]
        elif action == "run_placement":
            st.session_state.exec_queue = ["placement"]
        elif action == "run_diagnosis":
            st.session_state.exec_queue = ["diagnose", "iterate"]
        elif action == "run_loop":
            st.session_state.exec_queue = ["iterate"]
        st.rerun()

    st.markdown("**⚡ 快捷指令**")
    _qa = [("q_all", "🚀 全流程"), ("q_strat", "🧭 策略"), ("q_cont", "🎨 素材")]
    _qb = [("q_kol", "🎯 红人"), ("q_place", "📣 投流"), ("q_diag", "🩺 诊断")]
    _qa_c1, _qa_c2, _qa_c3 = st.columns(3)
    for _c, (_kq, _lb) in zip((_qa_c1, _qa_c2, _qa_c3), _qa):
        if _c.button(_lb, key=_kq, use_container_width=True):
            steward_handle({"q_all": "全流程", "q_strat": "生成策略", "q_cont": "生成素材",
                            "q_kol": "匹配红人", "q_place": "启动投流", "q_diag": "诊断分析"}[_kq])
    _qb_c1, _qb_c2, _qb_c3 = st.columns(3)
    for _key, (_k, _txt) in zip((_qb_c1, _qb_c2, _qb_c3), _qb):
        if _key.button(_txt, key=_k, use_container_width=True):
            steward_handle({"q_all": "全流程", "q_strat": "生成策略", "q_cont": "生成素材",
                            "q_kol": "匹配红人", "q_place": "启动投流", "q_diag": "诊断分析"}[_k])

    if not st.session_state.get("messages"):
        st.session_state.messages.append({
            "role": "assistant",
            "content": "您好，我是您的出海营销大管家。\n\n我负责调度 **策略生成 → AI素材工厂 → 红人种草 / 投流放大 → 诊断分析 → 迭代优化** 全链路，并在每一步分析结果、闭环后给出整体优化建议。\n\n试试对我说 **「全流程」**，或点击上方快捷指令，一键跑完整个闭环。"
        })

    for _m in st.session_state.messages:
        with st.chat_message(_m["role"]):
            st.markdown(_m["content"])

    with st.form("steward_form", clear_on_submit=True):
        user_input = st.text_input("💬 和管家对话…", key="steward_input")
        submitted = st.form_submit_button("发送")
    if submitted and user_input:
        steward_handle(user_input)

# =====================================================================
# 自动续跑 + 页脚
# =====================================================================
if st.session_state.get("exec_queue"):
    time.sleep(1)
    st.rerun()

_mock_note = "模拟演示模式 · 不消耗 Token" if _mock_on else ("百炼大模型 · " + TEXT_MODEL)
st.markdown('<div class="footer">出海指挥官 · 跨境AI营销闭环系统 ｜ %s</div>' % _mock_note, unsafe_allow_html=True)