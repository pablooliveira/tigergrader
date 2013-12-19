# Copyright (C) 2012-2013 Pablo Oliveira <pablo@sifflez.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
