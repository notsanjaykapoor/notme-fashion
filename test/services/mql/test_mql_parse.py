import models
import services.mql


def test_mql_parse():
    # should parse simple single token query
    parse_result = services.mql.parse(query="name:foo")

    assert parse_result.code == 0
    assert len(parse_result.tokens) == 1
    assert parse_result.tokens[0] == {
        "field": "name",
        "value": "foo",
    }

    # should parse query with space in value
    parse_result = services.mql.parse(query="name:foo bar")

    assert parse_result.code == 0
    assert len(parse_result.tokens) == 1
    assert parse_result.tokens[0] == {
        "field": "name",
        "value": "foo bar",
    }

    # should parse query with single quoted value
    parse_result = services.mql.parse(query="name:'foo bar'")

    assert parse_result.code == 0
    assert len(parse_result.tokens) == 1
    assert parse_result.tokens[0] == {
        "field": "name",
        "value": "'foo bar'",
    }

    # should parse query with double quoted value
    parse_result = services.mql.parse(query="name:\"foo bar\"")

    assert parse_result.code == 0
    assert len(parse_result.tokens) == 1
    assert parse_result.tokens[0] == {
        "field": "name",
        "value": '"foo bar"',
    }

    # should parse query with field value with extra space
    parse_result = services.mql.parse(query="name: foo")

    assert parse_result.code == 0
    assert len(parse_result.tokens) == 1
    assert parse_result.tokens[0] == {
        "field": "name",
        "value": "foo",
    }

    # should parse query with multiple fields
    parse_result = services.mql.parse(query="key1:foo key2:val with space key3:more space")

    assert parse_result.code == 0
    assert len(parse_result.tokens) == 3
    assert parse_result.tokens[0] == {
        "field": "key1",
        "value": "foo",
    }
    assert parse_result.tokens[1] == {
        "field": "key2",
        "value": "val with space",
    }
    assert parse_result.tokens[2] == {
        "field": "key3",
        "value": "more space",
    }

    # should parse empty query
    parse_result = services.mql.parse(query="")

    assert parse_result.code == 0
    assert len(parse_result.tokens) == 0


