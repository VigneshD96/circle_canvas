from wv.scenes import name_pattern, select


def W(w, s, spk):
    return {"w": w, "start": s, "end": s + 0.3, "spk": spk}


SCENES = [
    {"start": 0, "end": 80, "setting": "Monica's apartment, cold open", "on_screen": ["Ross (S1)", "Rachel (S2)", "Monica (S5)"]},
    {"start": 80, "end": 120, "setting": "Title sequence", "on_screen": ["FRIENDS logo", "cast credit clips"]},
    {"start": 187, "end": 236, "setting": "Monica's apartment", "on_screen": ["Chandler (S3)", "Monica (S5)", "Phoebe (S7)"]},
    {"start": 236, "end": 300, "setting": "Street, Porsche", "on_screen": ["Rachel (S2)", "Ross (S1)"]},
    {"start": 653, "end": 664, "setting": "Las Vegas exteriors", "on_screen": ["The Mirage hotel", "Four Queens neon sign"]},
    {"start": 664, "end": 712, "setting": "Drag club", "on_screen": ["Chandler", "Monica", "drag waiter"]},
    {"start": 712, "end": 731, "setting": "Drag club stage", "on_screen": ["Chandler", "Monica", "Helena (Chandler's dad)"]},
    {"start": 878, "end": 918, "setting": "Drag club floor", "on_screen": ["Helena (Chandler's dad)", "blond audience man"]},
]
WORDS = [W("hi", 190, "Chandler"), W("there", 191, "Chandler"), W("Bakersfield", 900, "Bakersfield guy"),
         W("he's", 891, "Chandler"), W("coming", 891.4, "Chandler"), W("keys", 250, "Ross")]
KNOWN = ["Ross", "Rachel", "Monica", "Chandler", "Phoebe", "Helena", "Helena (Chandler's dad)"]


def test_name_pattern_ignores_possessive():
    p = name_pattern("Chandler")
    assert p.search("Chandler (S3)") and not p.search("Helena (Chandler's dad)") and not p.search("Chandler’s flat")


def test_select_scenes_bridges_merge_and_snap():
    cuts = [80.2, 119.6, 187.4, 235.8, 652.9, 663.7, 711.9, 730.6, 877.9, 918.4]
    res = select(SCENES, WORDS, "Chandler", KNOWN, cuts, duration=1318)
    segs = [(s["start"], s["end"]) for s in res["segments"]]
    # apartment scene; Vegas establishing shot (bridge) + club + stage merged; floor scene kept because he speaks
    assert segs == [(187.4, 235.8), (652.9, 730.6), (877.9, 918.4)]
    dropped = {d["setting"] for d in res["dropped_scenes"]}
    assert {"Monica's apartment, cold open", "Title sequence", "Street, Porsche"} <= dropped

