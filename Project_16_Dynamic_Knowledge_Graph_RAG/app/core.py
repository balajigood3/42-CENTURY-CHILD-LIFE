import json, re
from pathlib import Path
from typing import Any

def parse_json(text: str) -> Any:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", text, re.S)
        if not match:
            raise ValueError("LLM response did not contain valid JSON")
        return json.loads(match.group(0))

class OllamaClient:
    def __init__(self, model="qwen2.5:3b", host="http://localhost:11434"):
        self.model, self.host = model, host.rstrip("/")

    def generate(self, prompt: str) -> str:
        import urllib.request
        payload = json.dumps({
            "model": self.model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0.1}
        }).encode()
        request = urllib.request.Request(
            self.host + "/api/generate", data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode())["response"]
        except Exception as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

def extract_graph(text: str, source: str, client: OllamaClient) -> dict:
    prompt = (
        "Extract a compact knowledge graph from the document. Return ONLY JSON object with "
        '"entities":[{"id":"stable_snake_case","name":"...","type":"PERSON|ORG|PRODUCT|'
        'LOCATION|CONCEPT|EVENT|OTHER","description":"..."}], '
        '"relations":[{"source":"entity_id","relation":"SHORT_VERB_OR_RELATION",'
        '"target":"entity_id","evidence":"short exact supporting quote"}]. '
        "Only include facts explicitly supported by the document. Do not infer missing links. "
        "Use entity IDs consistently. Limit to 40 entities and 80 relations.\n"
        f"Document source: {source}\nDOCUMENT:\n{text[:16000]}"
    )
    data = parse_json(client.generate(prompt))
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object with entities and relations")
    entities, relations = [], []
    for e in data.get("entities", []):
        if not isinstance(e, dict) or not e.get("name"):
            continue
        eid = str(e.get("id") or re.sub(r"\W+", "_", str(e["name"]).lower())).strip("_")
        entities.append({
            "id": eid, "name": str(e["name"]), "type": str(e.get("type", "OTHER")).upper(),
            "description": str(e.get("description", "")), "source": source
        })
    known = {e["id"] for e in entities}
    for r in data.get("relations", []):
        if not isinstance(r, dict):
            continue
        src, dst = str(r.get("source", "")), str(r.get("target", ""))
        if src in known and dst in known and src != dst and r.get("relation"):
            relations.append({
                "source": src, "relation": str(r["relation"]),
                "target": dst, "evidence": str(r.get("evidence", "")),
                "source_doc": source
            })
    return {"entities": entities, "relations": relations}

def build_graph(doc_graphs: list[dict]):
    import networkx as nx
    graph = nx.MultiDiGraph()
    for item in doc_graphs:
        for entity in item["entities"]:
            eid = entity["id"]
            if graph.has_node(eid):
                existing = graph.nodes[eid]
                sources = set(existing.get("sources", []))
                sources.add(entity["source"])
                existing["sources"] = sorted(sources)
                if not existing.get("description") and entity.get("description"):
                    existing["description"] = entity["description"]
            else:
                graph.add_node(eid, name=entity["name"], type=entity["type"],
                               description=entity["description"], sources=[entity["source"]])
        for rel in item["relations"]:
            if graph.has_node(rel["source"]) and graph.has_node(rel["target"]):
                graph.add_edge(rel["source"], rel["target"],
                    relation=rel["relation"], evidence=rel["evidence"],
                    source_doc=rel["source_doc"])
    return graph

def lexical_rank(query: str, texts: list[str]) -> list[tuple[int, float]]:
    q = set(re.findall(r"[a-z0-9]+", query.lower()))
    scored = []
    for i, text in enumerate(texts):
        words = set(re.findall(r"[a-z0-9]+", text.lower()))
        score = len(q & words) / max(1, len(q))
        if score > 0:
            scored.append((i, score))
    return sorted(scored, key=lambda x: x[1], reverse=True)

def retrieve_subgraph(graph, query: str, max_hops: int = 2, max_nodes: int = 30) -> dict:
    import networkx as nx
    query_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    seeds = []
    for node, data in graph.nodes(data=True):
        searchable = " ".join([data.get("name", ""), data.get("description", "")]).lower()
        terms = set(re.findall(r"[a-z0-9]+", searchable))
        overlap = len(query_terms & terms)
        if overlap:
            seeds.append((node, overlap))
    seeds.sort(key=lambda x: x[1], reverse=True)
    selected = set()
    for node, _ in seeds[:8]:
        selected.add(node)
        frontier = {node}
        for _ in range(max_hops):
            nxt = set()
            for current in frontier:
                nxt.update(graph.predecessors(current))
                nxt.update(graph.successors(current))
            nxt -= selected
            selected.update(nxt)
            frontier = nxt
            if len(selected) >= max_nodes:
                break
        if len(selected) >= max_nodes:
            break
    sub = graph.subgraph(selected).copy()
    nodes = [{"id": n, **dict(d)} for n, d in sub.nodes(data=True)]
    edges = [{"source": u, "target": v, **dict(d)} for u, v, d in sub.edges(data=True)]
    return {"nodes": nodes, "edges": edges}

def graph_context(subgraph: dict) -> str:
    lines = ["ENTITIES:"]
    for n in subgraph["nodes"]:
        lines.append(f'- {n["id"]}: {n.get("name")} ({n.get("type")}); {n.get("description","")}; sources={n.get("sources",[])}')
    lines.append("RELATIONS:")
    for e in subgraph["edges"]:
        lines.append(f'- {e["source"]} --{e.get("relation")}--> {e["target"]}; evidence="{e.get("evidence","")}"; source={e.get("source_doc")}')
    return "\n".join(lines)

def answer_query(query: str, graph, client: OllamaClient) -> tuple[str, dict]:
    sub = retrieve_subgraph(graph, query)
    context = graph_context(sub)
    prompt = (
        "Answer the question using ONLY the supplied knowledge graph context. "
        "Cite source document names inline in square brackets. If the graph lacks evidence, "
        "say so. Do not invent entities or relationships.\n"
        f"QUESTION: {query}\nGRAPH CONTEXT:\n{context}"
    )
    return client.generate(prompt), sub

def export_graph(graph, path: str):
    import networkx as nx
    nx.write_graphml(graph, path)
