#
# Parley Who Vertigo
# Copyright 2016, 2017 Thomas Perl, Josef Who
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#

import psmoveapi

class Color(psmoveapi.RGB):
    BLACK = psmoveapi.RGB(0.0, 0.0, 0.0)
    WHITE = psmoveapi.RGB(1.0, 1.0, 1.0)
    MAGENTA = psmoveapi.RGB(1.0, 0.0, 1.0)
    GREEN = psmoveapi.RGB(0.0, 1.0, 0.0)
    BLUE = psmoveapi.RGB(0.0, 0.0, 1.0)
    RED = psmoveapi.RGB(1.0, 0.0, 0.0)


def to_rgba32(color, opacity):
    r = int(255 * min(1, max(0, color.r)))
    g = int(255 * min(1, max(0, color.g)))
    b = int(255 * min(1, max(0, color.b)))
    a = int(255 * min(1, max(0, opacity)))
    return (r << 24) | (g << 16) | (b << 8) | a
