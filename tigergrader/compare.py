#!/usr/bin/env python
import re


def compare(expected, produced, strict=False):
    expected_toks = re.split("\W+", expected)
    expected_toks.reverse()

    for l, line in enumerate(produced.split("\n")):
        produced_toks = re.split("\W+", line)
        for t in produced_toks:
            # Are we still expecting tokens
            if len(expected_toks) == 0:
                if strict:
                    return (False,
                            "At line {0}, got {1} but nothing was expected"
                            .format(l + 1, t))
                else:
                    return (True, "")

            if expected_toks[-1] == t:
                expected_toks.pop()
            else:
                if strict:
                    return (False,
                            "At line {0}, expected {1} got {2}"
                            .format(l + 1, expected_toks[-1], t))

    if len(expected_toks) > 0:
        return (False,
                "Output too short, was expecting {0} at the end, got nothing"
                .format(expected_toks[-1]))
    else:
        return (True, "")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare output and expected runs")
    parser.add_argument('expected', help='The reference output')
    parser.add_argument('produced', help='The produced output')

    args = parser.parse_args()
    with file(args.expected) as e:
        with file(args.produced) as p:
            print compare(e.read(), p.read())
