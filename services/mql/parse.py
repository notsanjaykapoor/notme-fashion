import dataclasses
import urllib

@dataclasses.dataclass
class Struct:
    code: int
    tokens: list[dict]
    errors: list[str]


def parse(query: str) -> Struct:
    struct = Struct(0, [], [])

    tokens = query.split(" ")

    for token in tokens:
        if len(token) == 0:
            # no more tokens to parse
            break

        field, value = token.split(":")

        # url unparse value, e.g' 'foo+1' => 'foo 1'
        value_parsed = urllib.parse.unquote_plus(value)

        # append to list
        struct.tokens.append(
            {
                "field": field,
                "value": value_parsed,
            }
        )

    return struct