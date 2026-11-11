# -*- coding: utf-8 -*-
"""本地自测：不依赖 API Key，验证 RAG 检索与规则防护。运行：python selftest.py"""
import json
from core import rag, guard


def test_rag():
    docs = rag.load_documents()
    print(f"知识库片段数：{len(docs)}")
    assert docs, "知识库为空"
    cases = [
        ("退换货政策是什么", "return_policy.txt"),
        ("空气净化器适用多大面积", "product.txt"),
        ("发票怎么开", "faq.txt"),
    ]
    for q, expect in cases:
        r = rag.retrieve(q, top_k=1)
        got = r[0]["source"] if r else None
        ok = "✓" if got == expect else "✗"
        print(f"  {ok} '{q}' -> {got} (期望 {expect})")
    print()


def test_guard():
    attacks = json.load(open("data/attack_set/injections.json", encoding="utf-8"))
    blocked_expected = blocked_got = 0
    normal_expected = normal_got = 0
    for a in attacks:
        hit, _ = guard.detect_injection(a["text"])
        is_attack = a["type"] != "normal"
        if is_attack:
            blocked_expected += 1
            blocked_got += int(hit)
        else:
            normal_expected += 1
            normal_got += int(not hit)
        flag = "拦截" if hit else "放行"
        want = "拦截" if is_attack else "放行"
        print(f"  [{a['id']:>2}] {a['type']:<9} {flag:<4} (期望{want})  {a['text'][:26]}")
    print()
    print(f"攻击样本拦截率：{blocked_got}/{blocked_expected}")
    print(f"正常样本放行率：{normal_got}/{normal_expected}")


if __name__ == "__main__":
    print("=== RAG 检索自测 ===")
    test_rag()
    print("=== 规则防护自测 ===")
    test_guard()
