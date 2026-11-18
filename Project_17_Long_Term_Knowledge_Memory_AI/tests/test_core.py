from app.core import parse_json,content_hash,retrieve_memories,normalize_memory
from app.storage import MemoryStore

def test_parse_json():
    assert parse_json('```json\n[{"memory":"pref"}]\n```')[0]["memory"]=="pref"

def test_parse_invalid():
    try: parse_json("not json")
    except ValueError: assert True
    else: assert False

def test_hash_stable():
    assert content_hash("hello")==content_hash("hello")
    assert content_hash("hello")!=content_hash("world")

def test_retrieval_ranks_relevant():
    mem=[{"memory":"User prefers Python coding examples","category":"preference","importance":5},
         {"memory":"User likes gardening","category":"hobby","importance":3}]
    got=retrieve_memories("Python examples",mem)
    assert got and "Python" in got[0]["memory"]

def test_normalize():
    assert normalize_memory("  Hello   WORLD ")=="hello world"

def test_store_dedupe_and_deactivate(tmp_path):
    store=MemoryStore(str(tmp_path/"memory.db"))
    item={"memory":"Prefers Python","category":"preference","importance":4,"confidence":.9,"source":"test"}
    store.add_many([item]); store.add_many([item])
    assert store.count()==1
    mid=store.all()[0]["id"]
    assert store.deactivate(mid) is True
    assert store.count()==0
