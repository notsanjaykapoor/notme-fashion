import dataclasses
import urllib.parse

@dataclasses.dataclass
class Struct:
    code: int
    tokens: list[dict]
    errors: list[str]


def parse(query: str, unquote: int=0) -> Struct:
    struct = Struct(0, [], [])

    tokens_list = query.strip().split(" ")
    tokens_count = len(tokens_list)
    tokens_i = 0

    while tokens_i < tokens_count:
        token = tokens_list[tokens_i]

        if not token or ":" not in token:
            tokens_i += 1
            continue

        field, value = token.split(":")

        while tokens_i+1 < tokens_count:
            # greedy parse value until we find next field
            token_j = tokens_list[tokens_i+1]
            if ":" in token_j:
                # found next field
                break
            # append this token to current value
            value = f"{value} {token_j}"
            tokens_i += 1

        value_norm = value.strip()

        if unquote == 1:
            # url normalize value, e.g' 'foo+1' => 'foo 1'
            value_norm = urllib.parse.unquote_plus(value_norm)

        struct.tokens.append(
            {
                "field": field,
                "value": value_norm,
            }
        )

        tokens_i += 1

    return struct
