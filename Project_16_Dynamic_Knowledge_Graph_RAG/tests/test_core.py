from app.core import parse_json, build_graph, retrieve_subgraph, graph_context

def test_parse_json_fence():
    assert parse_json('```json\n{"entities":[]}\n```') == {"entities": []}

def test_invalid_json():
    try:
        parse_json("not json")
        assert False
    except ValueError:
        assert True

def test_build_graph_and_sources():
    docs = [
      {"entities":[{"id":"alice","name":"Alice","type":"PERSON","description":"","source":"a"}],
       "relations":[]},
      {"entities":[{"id":"alice","name":"Alice","type":"PERSON","description":"Engineer","source":"b"},
                   {"id":"acme","name":"Acme","type":"ORG","description":"","source":"b"}],
       "relations":[{"source":"alice","target":"acme","relation":"works_at","evidence":"Alice works at Acme","source_doc":"b"}]}
    ]
    g = build_graph(docs)
    assert g.number_of_nodes() == 2
    assert set(g.nodes["alice"]["sources"]) == {"a","b"}
    assert g.number_of_edges() == 1

def test_subgraph_retrieval():
    docs = [{"entities":[
        {"id":"alice","name":"Alice","type":"PERSON","description":"engineer","source":"a"},
        {"id":"acme","name":"Acme","type":"ORG","description":"technology company","source":"a"},
        {"id":"paris","name":"Paris","type":"LOCATION","description":"city","source":"a"}],
        "relations":[{"source":"alice","target":"acme","relation":"works_at","evidence":"works at","source_doc":"a"}]}]
    g = build_graph(docs)
    result = retrieve_subgraph(g, "Who works at Acme?")
    assert {x["id"] for x in result["nodes"]} >= {"alice","acme"}

def test_context_has_source():
    context = graph_context({"nodes":[],"edges":[{"source":"a","target":"b","relation":"knows","evidence":"quote","source_doc":"doc.txt"}]})
    assert "doc.txt" in context
