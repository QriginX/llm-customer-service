# -*- coding: utf-8 -*-
"""轻量 RAG：BM25 关键词检索（中文字符 n-gram），零重依赖，无需向量模型。"""
import os
import math
import numpy as np
from . import config

_docs = []
_tokens = []
_bm25 = None


def _tokenize(text):
    """中文字符 1-gram + 2-gram，兼顾单字与词组匹配。"""
    text = text.lower()
    unigrams = list(text)
    bigrams = [text[i:i + 2] for i in range(len(text) - 1)]
    return [t for t in unigrams + bigrams if t.strip()]


class BM25:
    """Okapi BM25 打分。"""

    def __init__(self, corpus, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.corpus = corpus
        self.N = len(corpus)
        self.doc_len = [len(d) for d in corpus]
        self.avgdl = float(np.mean(self.doc_len)) if self.doc_len else 0.0
        self.df = {}
        for doc in corpus:
            for t in set(doc):
                self.df[t] = self.df.get(t, 0) + 1

    def score(self, query):
        scores = np.zeros(self.N)
        for t in query:
            df = self.df.get(t)
            if df is None:
                continue
            idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
            for i, doc in enumerate(self.corpus):
                tf = doc.count(t)
                if tf == 0:
                    continue
                denom = tf + self.k1 * (1 - self.b + self.b * self.doc_len[i] / self.avgdl)
                scores[i] += idf * (tf * (self.k1 + 1)) / denom
        return scores


def load_documents(directory=None):
    """读取知识库 .txt，按空行分段为检索单元，构建 BM25 索引。"""
    global _docs, _tokens, _bm25
    directory = directory or config.KNOWLEDGE_DIR
    docs = []
    if os.path.isdir(directory):
        for fn in sorted(os.listdir(directory)):
            if fn.lower().endswith(".txt"):
                with open(os.path.join(directory, fn), encoding="utf-8") as f:
                    text = f.read().strip()
                for para in text.split("\n\n"):
                    para = para.strip()
                    if para:
                        docs.append({"text": para, "source": fn})
    if not docs:
        _docs, _tokens, _bm25 = [], [], None
        return docs
    _docs = docs
    _tokens = [_tokenize(d["text"]) for d in docs]
    _bm25 = BM25(_tokens)
    return docs


def retrieve(query, top_k=None):
    """返回与 query 最相关的 top_k 个文档片段。"""
    top_k = top_k or config.TOP_K
    if _bm25 is None or not _docs:
        return []
    q = _tokenize(query)
    scores = _bm25.score(q)
    order = np.argsort(-scores)[:top_k]
    out = []
    for i in order:
        out.append({
            "text": _docs[i]["text"],
            "source": _docs[i]["source"],
            "score": float(scores[i]),
        })
    return out
