#!/usr/bin/env python3
import json
import sys
import re


DBL_QUOTED_STR_MATCH = r'".*?(?<!\\)"'
SNG_QUOTED_STR_MATCH = r"'.*?(?<!\\)'"
VARIABLE_MATCHES = r"[a-zA-Z_]\w*"

IMPORT_NAME_MATCHES = (
    f"(?:{DBL_QUOTED_STR_MATCH})|(?:{SNG_QUOTED_STR_MATCH})|"
    + rf"(?:{VARIABLE_MATCHES})"
)

TEMPLATED_IMPORT_TYPE_ARG_MATCH_PATTERN = {
    "match": rf"({VARIABLE_MATCHES})=({VARIABLE_MATCHES}(?:\[])?)",
    "captures": {
        "1": {"name": "variable.parameter"},
        "2": {"name": "support.class"},
    },
}

OPERATOR_MATCH_PATTERN = {
    "match": r"\b(operator)\b\s*.*(?!(\s|,|;))",
    "captures": {"1": {"name": "keyword.other"}},
}


def generate_base_pattern():
    return [
        {  # templated import statements
            "begin": r"^\s*(typedef)\s+(import)\s*\(",
            "end": r"\)",
            "beginCaptures": {
                "1": {"name": "storage.modifier"},
                "2": {"name": "keyword.other"},
            },
            "patterns": [{"name": "variable", "match": VARIABLE_MATCHES}],
            "name": "meta.storage",
        },
        {
            # templated accesses
            "begin": rf"^\s*(access)\s+({IMPORT_NAME_MATCHES})\s*\(",
            "end": rf"\)\s*(as)\s+({VARIABLE_MATCHES})\s*;",
            "beginCaptures": {
                "1": {"name": "keyword.other"},
                "2": {"name": "support.class"},
            },
            "endCaptures": {
                "1": {"name": "keyword.other"},
                "2": {"name": "support.class"},
            },
            "name": "meta.support",
            "patterns": [TEMPLATED_IMPORT_TYPE_ARG_MATCH_PATTERN],
        },
        {
            # "from filename(T1=Tx, ..." part of templated import
            "begin": rf"^\s*(from)\s+({IMPORT_NAME_MATCHES})\s*\(",
            "end": r"\)",
            "beginCaptures": {
                "1": {"name": "keyword.other"},
                "2": {"name": "support.class"},
            },
            "patterns": [TEMPLATED_IMPORT_TYPE_ARG_MATCH_PATTERN],
        },
        {
            # acccess f1 as fn, f2, operator!=, ...; part of templated imports
            "begin": r"(?<=\)\s*)(access)",
            "end": ";",
            "beginCaptures": {
                "1": {"name": "keyword.other"},
            },
            "name": "meta.support",
            "patterns": [
                OPERATOR_MATCH_PATTERN,
                {
                    "match": rf"({VARIABLE_MATCHES})\s+(as)\s+({VARIABLE_MATCHES})",
                    "captures": {
                        "1": {"name": "support.class"},
                        "2": {"name": "keyword.other"},
                        "3": {"name": "support.class"},
                    },
                },
                {"match": VARIABLE_MATCHES, "name": "support.class"},
            ],
        },
        {"match": r"//.*$", "name": "comment.line.double-slash"},
        {
            "match": r"\b(const|static|explicit|struct|typedef)\b",
            "name": "storage.modifier",
        },
        {"match": r"\b(true|false)\b", "name": "constant.language"},
        {"begin": r"/\*", "end": r"\*/", "name": "comment.block"},
        {"match": DBL_QUOTED_STR_MATCH, "name": "string.quoted.double"},
        {"match": SNG_QUOTED_STR_MATCH, "name": "string.quoted.single"},
        {
            "match": r"\b(if|else|while|for|do|break|return|continue|unravel)\b",
            "name": "keyword.control",
        },
        {"match": r"\b(new|cast|ecast|init)\b", "name": "keyword.operator"},
        {
            "match": r"\b(import|include|as|access|from|operator|quote)\b",
            "name": "keyword.other",
        },
        {"match": r"\b(\d*)(\.?)\d+", "name": "constant.numeric"},
        {
            # see https://regex101.com/r/IViUjM/1 for info
            "match": r"\b([a-zA-Z_]\w*)\s*\(",
            "captures": {"1": {"name": "entity.name.function"}},
        },
        {
            # quote
            "begin": r"\b(quote)\s*\{",
            "end": r"\}",
            "patterns": [{"include": "$self"}],
        },
    ]


def main():
    base_grammar = {
        "$schema": "https://raw.githubusercontent.com/martinring/"
        + "tmlanguage/master/tmlanguage.json",
        "scopeName": "source.asymptote",
        "name": "Asymptote",
        "foldingStartMarker": r"(\{|\[|\()\s*$",
        "foldingStopMarker": r"^\s*(\}|\]\))",
        "repository": {},
    }

    # basic semantics not covered by asy -l

    base_pattern = generate_base_pattern()
    asy_list_raw = sys.stdin.read()

    operator_list = {"=", ","}
    const_list = set()
    type_list = set()
    prim_type_list = {"code", "void"}

    # print(json.dumps(base_grammar, indent=4))

    for asydef in asy_list_raw.splitlines():
        if parse_constant(asydef) is not None:
            const_list.add(parse_constant(asydef))
        elif parse_type(asydef) is not None:
            type_list.add(parse_type(asydef))
        elif parse_operators(asydef) is not None:
            operator_list.add(parse_operators(asydef))

    # setup repos

    if const_list:
        base_grammar["repository"]["const_keywords"] = {
            "match": r"\b({0})\b".format(
                "|".join([re.escape(kw) for kw in const_list])
            ),
            "name": "support.constant",
        }
        base_pattern.append({"include": "#const_keywords"})

    if type_list:
        base_grammar["repository"]["type_keywords"] = {
            "match": r"\b({0})\b".format("|".join([re.escape(kw) for kw in type_list])),
            "name": "support.class",
        }
        base_pattern.append({"include": "#type_keywords"})

    if operator_list:
        base_grammar["repository"]["operator_keywords"] = {
            "match": r"({0})".format("|".join([re.escape(kw) for kw in operator_list])),
            "name": "keyword.operator",
        }
        base_pattern.append({"include": "#operator_keywords"})

    if prim_type_list:
        base_grammar["repository"]["prim_type_keywords"] = {
            "match": r"\b({0})\b".format(
                "|".join([re.escape(kw) for kw in prim_type_list])
            ),
            "name": "storage.type",
        }
        base_pattern.append({"include": "#prim_type_keywords"})

    base_grammar["patterns"] = base_pattern
    final_output = json.dumps(base_grammar)

    print(final_output)


def parse_constant(line):
    # parse constant in <type><[]*> <kw>;
    # see https://regex101.com/r/dSExOo/3/ for format.
    match_data = re.match(r"^[a-zA-Z_]\w*\s*(?:\[]\s*)*\w*\s+([a-zA-Z_]\w*)\s*;$", line)
    if match_data is None:
        return None
    else:
        return match_data.group(1)


def parse_type(line):
    # See https://regex101.com/r/sf4Mj7/1 for format
    match_data = re.match(r"^([a-zA-Z_]\w*)\s*operator\s*init\s*\(\s*\)\s*;$", line)
    if match_data is None:
        return None
    else:
        return match_data.group(1)


def parse_operators(line):
    # See https://regex101.com/r/F9DUaQ/1 for format.
    match_data = re.match(r"^(?:[a-zA-Z_]\w*)\s*operator\s*([\W]+)\(.*\);$", line)
    if match_data is None:
        return None
    else:
        return match_data.group(1)


if __name__ == "__main__":
    sys.exit(main() or 0)
