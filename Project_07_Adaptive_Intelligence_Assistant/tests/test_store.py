from src.store import PreferenceStore

def test_preference_round_trip(tmp_path):
    s=PreferenceStore(tmp_path/"prefs.db")
    data={"tone":"Friendly","detail":"Short","language":"Tamil"}
    s.save(data)
    assert s.load()==data

def test_empty_store(tmp_path):
    assert PreferenceStore(tmp_path/"empty.db").load() is None
