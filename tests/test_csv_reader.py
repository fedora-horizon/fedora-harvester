import json

from src.csv_reader import parse_csv


def test_valid_row(tmp_path):
    csv = tmp_path / "sources.csv"
    csv.write_text("name,url,source_type,owner_org\ns1,http://ex.com,ckan,org1\n")
    rows = parse_csv(str(csv))
    assert len(rows) == 1
    assert rows[0]["name"] == "s1"


def test_skips_missing_required(tmp_path):
    csv = tmp_path / "sources.csv"
    csv.write_text("name,url\ns1,http://ex.com\n")
    rows = parse_csv(str(csv))
    assert len(rows) == 0


def test_skips_invalid_config(tmp_path):
    csv = tmp_path / "sources.csv"
    csv.write_text("name,url,source_type,config\ns1,http://ex.com,ckan,{bad\n")
    rows = parse_csv(str(csv))
    assert len(rows) == 0


def test_accepts_valid_config(tmp_path):
    csv = tmp_path / "sources.csv"
    csv.write_text('name,url,source_type,config\ns1,http://ex.com,ckan,{"a":1}\n')
    rows = parse_csv(str(csv))
    assert len(rows) == 1
    assert json.loads(rows[0]["config"]) == {"a": 1}


def test_multiple_rows(tmp_path):
    csv = tmp_path / "sources.csv"
    csv.write_text("name,url,source_type\ns1,http://a.com,ckan\ns2,http://b.com,dcat\n")
    rows = parse_csv(str(csv))
    assert len(rows) == 2


def test_strips_whitespace(tmp_path):
    csv = tmp_path / "sources.csv"
    csv.write_text("name,url,source_type\n  s1 ,  http://ex.com ,  ckan  \n")
    rows = parse_csv(str(csv))
    assert rows[0]["name"] == "s1"


def test_bom_handling(tmp_path):
    csv = tmp_path / "sources.csv"
    csv.write_text("\ufeffname,url,source_type\ns1,http://ex.com,ckan\n")
    rows = parse_csv(str(csv))
    assert len(rows) == 1
