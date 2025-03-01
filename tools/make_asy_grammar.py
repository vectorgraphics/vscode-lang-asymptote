#!/usr/bin/env python3
import json
import sys
import re


def generate_base_pattern():
    return [
        {"match": r"//.*$", "name": "comment.line.double-slash"},
        {
            "match": r"\b(const|static|explicit|struct|typedef)\b",
            "name": "storage.modifier",
        },
        {"match": r"\b(true|false)\b", "name": "constant.language"},
        {"begin": r"/\*", "end": r"\*/", "name": "comment.block"},
        {"match": r'\s+"(.*)"', "name": "string.quoted.double"},
        {
            "begin": r'(?<!\s)"{1}',
            "end": r'"{1}',
            "name": "string.quoted.double",
            "patterns": [{"include": "text.tex.latex"}],
        },
        {"match": r"\'.*?\'", "name": "string.quoted.single"},
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
    final_output = json.dumps(base_grammar, indent=4)

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
