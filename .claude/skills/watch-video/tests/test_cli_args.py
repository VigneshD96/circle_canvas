import json

import watch


def test_long_inline_map_is_parsed_not_treated_as_a_path():
    # Path(value).exists() raised OSError (File name too long) for an inline --map over 255 bytes (2026-10-03).
    data = {"speakers": {f"S{i}": {"name": f"Person {i}", "confidence": "high", "evidence": "x" * 20} for i in range(8)},
            "overrides": []}
    assert watch._json_arg(json.dumps(data)) == data


def test_map_file_path_still_works(tmp_path):
    p = tmp_path / "map.json"
    p.write_text('{"speakers": {}}')
    assert watch._json_arg(str(p)) == {"speakers": {}}
