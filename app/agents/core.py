# -*- coding: utf-8 -*-
import json
from ..llm import chat
from .. import config
from .. import mockdata as _mock


def _svc_text(services):
    """Format services dict to readable string (handles list values)"""
    if not services:
        return "\u672a\u8bbe\u7f6e"
    names = {"strategy": "\u7b56\u7565", "content": "\u7d20\u6750", "kol": "\u7ea2\u4eba", "placement": "\u6295\u6d41", "diagnosis": "\u8bca\u65ad"}
    parts = []
    for k, v in services.items():
        if isinstance(v, list):
            v = " + ".join(v)
        parts.append("%s=%s" % (names.get(k, k), v))
    return " | ".join(parts)


from ..prompts import STRATEGY_PROMPT, CONTENT_PROMPT, DIAGNOSIS_PROMPT, LOOP_PROMPT, KOL_PROMPT, STEWARD_CHAT_PROMPT, STEWARD_ANALYZE_PROMPT, STEWARD_OPTIMIZE_PROMPT


def generate_strategy(product, budget, market, extra="", loop_feedback=None, service_name="Smartly.io"):
    """\u529f\u80fd\u4e00\uff1a\u5bf9\u8bdd\u5f0f\u8425\u9500\u7b56\u7565\u751f\u6210\uff08\u652f\u6301\u95ed\u73af\u53cd\u54fa\uff09"""
    if config.MOCK_MODE:
        return _mock.mock_strategy(product, budget, market, extra)
    loop_text = ""
    if loop_feedback:
        loop_text = "\n\u4e0a\u4e00\u8f6e\u8fed\u4ee3\u5efa\u8bae\uff08\u8bf7\u5728\u6b64\u57fa\u7840\u4e0a\u4f18\u5316\u7b56\u7565\uff09\uff1a\n" + json.dumps(loop_feedback, ensure_ascii=False)
    prompt = STRATEGY_PROMPT.format(
        product=product, budget=budget, market=market, extra=extra, loop_feedback=loop_text, service_name=service_name
    )
    raw = chat(
        [{"role": "system", "content": "\u4f60\u662f\u8de8\u5883\u7535\u5546\u8425\u9500\u64cd\u76d8\u624b\uff0c\u53ea\u8f93\u51faJSON\u3002"},
         {"role": "user", "content": prompt}],
        temperature=0.7,
        json_mode=True,
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def generate_content(product, market, strategy, service_name="Canva"):
    """\u529f\u80fd\u4e8c\uff1aAI\u7d20\u6750\u5de5\u5382\uff08\u6587\u6848+\u51fa\u56fe\uff09"""
    if config.MOCK_MODE:
        return _mock.mock_content(product, market)
    strat_text = json.dumps(strategy, ensure_ascii=False) if isinstance(strategy, dict) else str(strategy)
    prompt = CONTENT_PROMPT.format(
        product=product, market=market, strategy=strat_text, service_name=service_name
    )
    raw = chat(
        [{"role": "system", "content": "\u4f60\u662f\u8de8\u5883\u7535\u5546\u8425\u9500\u6587\u6848\u4e13\u5bb6\uff0c\u53ea\u8f93\u51faJSON\u3002"},
         {"role": "user", "content": prompt}],
        temperature=0.8,
        json_mode=True,
    )
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {"raw": raw}
    image_url = None
    image_prompt = result.get("image_prompt", "") if isinstance(result, dict) else ""
    if image_prompt:
        from ..llm import generate_image
        try:
            image_url = generate_image(image_prompt)
        except Exception as e:
            result["image_error"] = str(e)
    if image_url:
        result["image_url"] = image_url
    return result


def generate_kol(product, market, strategy, service_name="Upfluence"):
    """\u529f\u80fd\u4e09\uff1a\u667a\u80fdKOL\u5339\u914d\u4e0e\u81ea\u52a8\u89e6\u8fbe"""
    if config.MOCK_MODE:
        return _mock.mock_kol(product, market, strategy)
    strat_text = json.dumps(strategy, ensure_ascii=False) if isinstance(strategy, dict) else str(strategy)
    prompt = KOL_PROMPT.format(
        product=product, market=market, strategy=strat_text, service_name=service_name
    )
    raw = chat(
        [{"role": "system", "content": "\u4f60\u662f\u8de8\u5883\u7535\u5546\u7ea2\u4eba\u8425\u9500\u4e13\u5bb6\uff0c\u53ea\u8f93\u51faJSON\u3002"},
         {"role": "user", "content": prompt}],
        temperature=0.7,
        json_mode=True,
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def diagnose_ads(csv_text, product="\u901a\u7528\u4ea7\u54c1", market="\u7f8e\u56fd", service_name="Northbeam"):
    """AI\u6295\u653e\u8bca\u65ad"""
    if config.MOCK_MODE:
        return _mock.mock_diagnosis(csv_text, product, market)
    prompt = DIAGNOSIS_PROMPT.format(
        csv_data=csv_text[:8000], product=product, market=market, service_name=service_name
    )
    raw = chat(
        [{"role": "system", "content": "\u4f60\u662f\u8de8\u5883\u7535\u5546\u5e7f\u544a\u6295\u653e\u4f18\u5316\u4e13\u5bb6\uff0c\u53ea\u8f93\u51faJSON\u3002"},
         {"role": "user", "content": prompt}],
        temperature=0.3,
        json_mode=True,
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def generate_loop(diagnosis, service_name="Rockerbox"):
    """\u529f\u80fd\u56db\uff1a\u95ed\u73af\u8fed\u4ee3\u5efa\u8bae"""
    if config.MOCK_MODE:
        return _mock.mock_loop(diagnosis)
    summary = json.dumps(diagnosis, ensure_ascii=False)[:4000] if isinstance(diagnosis, dict) else str(diagnosis)
    prompt = LOOP_PROMPT.format(diagnosis_summary=summary, service_name=service_name)
    raw = chat(
        [{"role": "system", "content": "\u4f60\u662f\u8de8\u5883\u7535\u5546\u8425\u9500\u64cd\u76d8\u624b\uff0c\u53ea\u8f93\u51faJSON\u3002"},
         {"role": "user", "content": prompt}],
        temperature=0.6,
        json_mode=True,
    )
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def steward_chat(user_message, state_summary, services=None):
    """\u5927\u7ba1\u5bb6\u5bf9\u8bdd\uff1a\u7406\u89e3\u7528\u6237\u610f\u56fe\uff0c\u8fd4\u56de\u52a8\u4f5c\u548c\u56de\u590d"""
    if any(k in user_message for k in ["\u5168\u6d41\u7a0b", "\u5168\u81ea\u52a8", "\u5168\u90e8", "\u4e00\u952e", "\u95ed\u73af"]):
        return {"action": "run_all", "response": "\u597d\u7684\uff0c\u6211\u6765\u4e3a\u60a8\u6267\u884c\u5168\u6d41\u7a0b\u95ed\u73af\uff01\u4ece\u7b56\u7565\u751f\u6210\u5f00\u59cb..."}
    elif "\u7b56\u7565" in user_message:
        return {"action": "run_strategy", "response": "\u597d\u7684\uff0c\u6b63\u5728\u4e3a\u60a8\u751f\u6210\u8425\u9500\u7b56\u7565..."}
    elif any(k in user_message for k in ["\u7ea2\u4eba", "KOL", "kol", "\u8fbe\u4eba", "\u7f51\u7ea2"]):
        return {"action": "run_kol", "response": "\u597d\u7684\uff0c\u6b63\u5728\u667a\u80fd\u5339\u914dKOL\u5e76\u751f\u6210\u89e6\u8fbe\u8bdd\u672f..."}
    elif any(k in user_message for k in ["\u7d20\u6750", "\u6587\u6848", "\u56fe\u7247", "\u4e3b\u56fe"]):
        return {"action": "run_content", "response": "\u597d\u7684\uff0c\u6b63\u5728\u4e3a\u60a8\u751f\u6210\u8425\u9500\u7d20\u6750\uff08\u6587\u6848+\u4e3b\u56fe\uff09..."}
    elif any(k in user_message for k in ["\u6295\u6d41", "\u6295\u653e", "\u542f\u52a8"]):
        return {"action": "run_placement", "response": "\u597d\u7684\uff0c\u6b63\u5728\u542f\u52a8\u6295\u6d41\uff0c\u751f\u6210\u6295\u653e\u6570\u636e..."}
    elif any(k in user_message for k in ["\u8bca\u65ad", "ROI", "\u6570\u636e", "\u5206\u6790"]):
        return {"action": "run_diagnosis", "response": "\u597d\u7684\uff0c\u6b63\u5728\u8bca\u65ad\u6295\u653e\u6570\u636e\u5e76\u751f\u6210\u8fed\u4ee3\u5efa\u8bae..."}
    elif any(k in user_message for k in ["\u8fed\u4ee3", "\u5efa\u8bae", "\u4f18\u5316", "\u6539\u8fdb", "\u8c03\u6574"]):
        return {"action": "run_loop", "response": "\u597d\u7684\uff0c\u6b63\u5728\u751f\u6210\u8fed\u4ee3\u5efa\u8bae..."}
    else:
        if config.MOCK_MODE:
            return {"action": "chat", "response": "\uff08\u6a21\u62df\u6f14\u793a\u6a21\u5f0f\uff09\u5df2\u6536\u5230\u60a8\u7684\u6307\u4ee4\u3002\u53ef\u8f93\u5165\uff1a\u5168\u6d41\u7a0b / \u7b56\u7565 / \u7d20\u6750 / \u7ea2\u4eba / \u6295\u6d41 / \u8bca\u65ad / \u8fed\u4ee3\u3002"}
        services_overview = _svc_text(services)
        prompt = STEWARD_CHAT_PROMPT.format(state=state_summary, user_message=user_message, services_overview=services_overview)
        response = chat(
            [{"role": "system", "content": "\u4f60\u662f\u51fa\u6d77\u6307\u6325\u5b98\u7684\u5927\u7ba1\u5bb6\u3002"},
             {"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return {"action": "chat", "response": response}


def steward_analyze(module_name, result, service_name=""):
    """\u7ba1\u5bb6\u5206\u6790\uff1a\u89e3\u8bfb\u5355\u4e2a\u6a21\u5757\u7ed3\u679c\uff0c\u7528\u5feb\u6a21\u578b\u51cf\u5c11\u7b49\u5f85"""
    if config.MOCK_MODE:
        return _mock.mock_analyze_text(module_name, service_name)
    result_summary = json.dumps(result, ensure_ascii=False)[:2000] if isinstance(result, dict) else str(result)[:2000]
    prompt = STEWARD_ANALYZE_PROMPT.format(
        module_name=module_name,
        result_summary=result_summary, service_name=service_name
    )
    return chat(
        [{"role": "system", "content": "\u4f60\u662f\u51fa\u6d77\u6307\u6325\u5b98\u7684\u5927\u7ba1\u5bb6\uff0c\u8d1f\u8d23\u5206\u6790\u6a21\u5757\u7ed3\u679c\u3002"},
         {"role": "user", "content": prompt}],
        model="qwen3.6-flash",
        temperature=0.3,
    )


def steward_optimize(strategy, content, kol, diagnosis, loop, services=None):
    """\u7ba1\u5bb6\u4f18\u5316\uff1a\u7efc\u5408\u5168\u6d41\u7a0b\u7ed3\u679c\u7ed9\u51fa\u4f18\u5316\u65b9\u5411"""
    if config.MOCK_MODE:
        has_kol = kol is not None and not (isinstance(kol, dict) and "error" in kol)
        return _mock.mock_optimize_text(has_kol)
    def trunc(obj):
        if obj is None:
            return "\u672a\u6267\u884c"
        return json.dumps(obj, ensure_ascii=False)[:1000] if isinstance(obj, dict) else str(obj)[:1000]
    services_overview = _svc_text(services)
    prompt = STEWARD_OPTIMIZE_PROMPT.format(
        services_overview=services_overview,
        strategy_summary=trunc(strategy),
        content_summary=trunc(content),
        kol_summary=trunc(kol),
        diagnosis_summary=trunc(diagnosis),
        loop_summary=trunc(loop),
    )
    return chat(
        [{"role": "system", "content": "\u4f60\u662f\u51fa\u6d77\u6307\u6325\u5b98\u7684\u5927\u7ba1\u5bb6\uff0c\u8d1f\u8d23\u7efc\u5408\u4f18\u5316\u3002"},
         {"role": "user", "content": prompt}],
        model="qwen3.6-flash",
        temperature=0.4,
    )
