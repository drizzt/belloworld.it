#!/usr/bin/env python3
"""Draw the carousel images for the /belli/ pieces.

Every bello carries an `extra.slides` array in its front matter: one entry per
slide, and inside it one string per line, exactly as it should be read. This
turns each of those into a 1080x1080 slide under static/img/slides/<slug>/, and
redraws the section's fallback sharing image from _index.md.

Each slide is written twice, from the same measurements. The SVG is the copy
that is committed: it diffs as the words themselves, so a change of wording
reads as a change of wording. The PNG is what Instagram, Facebook and the
og:image tag actually need, and it is build output, redrawn here and in CI and
never committed.

Lines are never broken automatically. Where a sentence turns is a decision
about how it reads out loud, and a greedy wrap makes that decision badly. The
script only chooses the type size: the largest at which the lines as written
fit the frame.

The look follows sass/belli.scss: carta on verde, with the vermilion only ever
a bar along the bottom edge. It never carries text, where it sits at 1.3:1.

Run it from anywhere: python3 slides.py [name ...], where a name is the file
of a piece without its .md.
"""

import sys
import tomllib
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
CONTENT = ROOT / "content/belli"
FONTS = ROOT / "static/fonts"
OUT = ROOT / "static/img/slides"
OG = ROOT / "static/img/belli-og.png"

SIZE = 1080
MARGIN = 100
BAR = SIZE // 40
LEADING = 1.35
FOOTER_SIZE = 32

# The same four values as the :root block in sass/belli.scss, which the site
# reads and an image cannot.
VERDE = "#1f4a45"
CARTA = "#f7f5f0"
CARTA_TENUE = "#b9c6c0"
VERMIGLIO = "#c42b14"

# The footer only, which is chrome and matches the site rather than the slide.
ROMAN = FONTS / "ibm-plex-sans-latin-400-normal.woff2"
DISPLAY = FONTS / "ibm-plex-sans-condensed-latin-700-normal.woff2"
# Every slide after the cover. Condensed because the width is what runs out
# first on a square, and 500 rather than 400 because the cream loses weight
# against the green. The cover stays at 700, far enough above 500 to read as
# the cover on its own.
BODY = FONTS / "ibm-plex-sans-condensed-latin-500-normal.woff2"

# Pillow's FreeType reads woff2 straight from the repo, so the fonts need no
# unpacking and nothing gets installed system-wide.

# The same faces named the way CSS has to name them, for the @font-face rules in
# the SVG. An SVG cannot embed a font by file path: it has to declare the family
# and point at the woff2 the site already serves.
FAMILY = {
    ROMAN: ("IBM Plex Sans", 400),
    DISPLAY: ("IBM Plex Sans Condensed", 700),
    BODY: ("IBM Plex Sans Condensed", 500),
}

# Wherever the woff2 cannot be fetched, the type falls back to whatever is
# installed, matched by name. Fontconfig files the condensed face under three
# names at once, "IBM Plex Sans Condensed" being an alias rather than the
# preferred one, and a browser that only knows the preferred name would go and
# set the cover in a system sans. Cheap insurance: name all three.
CONDENSED = ["IBM Plex Sans Cond", "IBM Plex Sans"]
FALLBACK = {DISPLAY: CONDENSED, BODY: CONDENSED}


def parse(path):
    """Front matter of a Zola page, as a dict."""
    text = path.read_text(encoding="utf-8")
    _, front, _ = text.split("+++", 2)
    return tomllib.loads(front)


# Escapes rather than the characters themselves: in a diff the typewriter mark
# and the typographic one are a pixel apart, and the code says which is which.
SMART = [("---", "\u2014"), ("--", "\u2013"), ("...", "\u2026"), ("'", "\u2019")]
QUOTES = ("\u201c", "\u201d")


def smart(lines):
    """The typographic marks the site already sets.

    config.toml turns on smart_punctuation, so the prose gets curly quotes, real
    dashes and one ellipsis character. A slide drawn with the typewriter marks it
    was typed with would be the same words in a different voice.
    """
    out, opening = [], True
    for line in lines:
        for typed, set_in_type in SMART:
            line = line.replace(typed, set_in_type)
        marks = []
        for char in line:
            if char == '"':
                # Open and close alternate across the whole slide, so a quotation
                # may begin on one line and end on another.
                marks.append(QUOTES[not opening])
                opening = not opening
            else:
                marks.append(char)
        out.append("".join(marks))
    return out


def fit(lines, font_path, width, height):
    """Largest size at which the lines as written fit the box.

    Measured in pixels: character counts are meaningless in proportional type,
    where "MMMM" and "iiii" are the same length and nowhere near the same width.
    """
    for size in range(96, 31, -2):
        font = ImageFont.truetype(font_path, size)
        if (max(font.getlength(line) for line in lines) <= width
                and len(lines) * size * LEADING <= height):
            return font
    # Nothing is broken silently, so a line that cannot fit has to be reported
    # as the line it is: shortening it is a decision only the author can make.
    font = ImageFont.truetype(font_path, 32)
    longest = max(lines, key=font.getlength)
    raise SystemExit(
        f"does not fit even at 32pt: {longest!r}\n"
        f"  {round(font.getlength(longest))}px wide against {width}, "
        f"{len(lines)} lines against {int(height / (32 * LEADING))}")


def layout(lines, font_path, footer=None):
    """Where every line sits, as (text, baseline) pairs, and in what size.

    The two drawings share this and nothing else, so the PNG and the SVG cannot
    say different things about the same slide.
    """
    # Before fitting, not after: the marks have their own widths and the line
    # that fits is the line as it will be drawn.
    lines = smart(lines)
    box_h = SIZE - 2 * MARGIN - (FOOTER_SIZE * 2 if footer else 0)
    font = fit(lines, font_path, SIZE - 2 * MARGIN, box_h)

    # Set from the bottom up, so the last line sits on the same baseline on every
    # slide and the block grows upwards. Centred, the text would float to a
    # different height on each one and the carousel would read as seven loose
    # images instead of a single object being swiped through. The baseline rather
    # than the block's edge is the fixed point, because the type size changes
    # from slide to slide and only the baseline is where the eye actually rests.
    # Walked from the bottom but handed back in reading order, so the SVG says
    # the lines in the order they are read rather than in the order they were
    # measured. It is a file meant to be read in a diff.
    step = font.size * LEADING
    bottom = MARGIN + box_h
    last = len(lines) - 1
    return font, [(line, bottom - (last - n) * step)
                  for n, line in enumerate(lines)]


def render(lines, font_path, footer=None):
    font, placed = layout(lines, font_path, footer)
    img = Image.new("RGB", (SIZE, SIZE), VERDE)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, SIZE - BAR, SIZE, SIZE), fill=VERMIGLIO)

    for line, baseline in placed:
        draw.text((MARGIN, baseline), line, font=font, fill=CARTA, anchor="ls")

    if footer:
        small = ImageFont.truetype(ROMAN, FOOTER_SIZE)
        top = SIZE - MARGIN + FOOTER_SIZE / 2
        draw.text((MARGIN, top), "belloworld.it", font=small, fill=CARTA_TENUE)
        draw.text((SIZE - MARGIN, top), footer, font=small,
                  fill=CARTA_TENUE, anchor="ra")
    return img


def svg(lines, font_path, footer=None):
    """The same slide as text, which is the copy worth keeping in git."""
    font, placed = layout(lines, font_path, footer)

    def text(x, baseline, string, face, size, fill, anchor=None):
        # The weight is stated on every line: the condensed face ships in 700
        # alone, and asked for a 400 it does not have, a browser draws the 700
        # and thickens it again on its own.
        name, weight = FAMILY[face]
        name = ", ".join([name] + FALLBACK.get(face, []))
        end = ' text-anchor="end"' if anchor == "end" else ""
        return (f'<text x="{x:g}" y="{baseline:g}" font-family="{name}" '
                f'font-size="{size:g}" font-weight="{weight}"{end} '
                f'fill="{fill}">{escape(string)}</text>')

    # Pillow's "ls" anchor is a baseline, which is what SVG puts a <text> on
    # already; the footer's "la"/"ra" are the top of the ascender, so that one
    # has the ascent added to it rather than being declared to SVG differently.
    # No @font-face: it only ever worked on the site, and the one place these
    # files get opened is here, where the faces are installed. The PNG is what
    # readers are given, and it carries its type baked in.
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" '
           f'height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">',
           f'<rect width="{SIZE}" height="{SIZE}" fill="{VERDE}"/>',
           f'<rect y="{SIZE - BAR}" width="{SIZE}" height="{BAR}" '
           f'fill="{VERMIGLIO}"/>']
    # A blank line still takes up its baseline, which is what makes the gap, but
    # it has nothing to set: an empty <text> is a tag saying nothing.
    out += [text(MARGIN, baseline, line, font_path, font.size, CARTA)
            for line, baseline in placed if line.strip()]

    if footer:
        small = ImageFont.truetype(ROMAN, FOOTER_SIZE)
        baseline = SIZE - MARGIN + FOOTER_SIZE / 2 + small.getmetrics()[0]
        out.append(text(MARGIN, baseline, "belloworld.it", ROMAN,
                        FOOTER_SIZE, CARTA_TENUE))
        out.append(text(SIZE - MARGIN, baseline, footer, ROMAN,
                        FOOTER_SIZE, CARTA_TENUE, anchor="end"))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def carousel(path):
    front = parse(path)
    slides = front.get("extra", {}).get("slides")
    if not slides:
        return
    # Drawn before anything is written, so a slide that does not fit leaves no
    # half-made folder behind.
    # The first slide is the cover and carries the title, so it is set in the
    # condensed display face like the headings on the site. The rest share the
    # same condensed family a weight lighter.
    drawn = []
    for n, lines in enumerate(slides, 1):
        face = DISPLAY if n == 1 else BODY
        number = f"{n}/{len(slides)}"
        drawn.append((svg(lines, face, number), render(lines, face, number)))
    # Zola falls back to the file name when the front matter has no slug, and
    # the address has to be the one the template will build.
    folder = OUT / front.get("slug", path.stem)
    folder.mkdir(parents=True, exist_ok=True)
    for n, (vector, image) in enumerate(drawn, 1):
        out = folder / f"{n:02d}.svg"
        out.write_text(vector, encoding="utf-8")
        image.save(out.with_suffix(".png"))
        print(out.relative_to(ROOT))


def fallback():
    """The sharing image for anything without slides of its own."""
    front = parse(CONTENT / "_index.md")
    OG.with_suffix(".svg").write_text(svg(front["extra"]["og"], DISPLAY),
                                      encoding="utf-8")
    render(front["extra"]["og"], DISPLAY).save(OG)
    print(OG.with_suffix(".svg").relative_to(ROOT))


def selftest():
    assert smart(['dice "cosi", poi tace']) == ['dice \u201ccosi\u201d, poi tace'], \
        "double quotes open and close"
    assert smart(['apre "qui', 'e chiude" li']) == ['apre \u201cqui', 'e chiude\u201d li'], \
        "a quotation may span two lines of the same slide"
    assert smart(["ce l'hai", "tre... o --- due"]) == \
        ["ce l\u2019hai", "tre\u2026 o \u2014 due"], "apostrophe, ellipsis and dashes"

    # The cover is told apart from the slides behind it by weight alone, since
    # the two share a family: 500 against 700, with nothing else to separate them.
    assert FAMILY[BODY][0] == FAMILY[DISPLAY][0], "cover and body share a family"
    assert FAMILY[BODY][1] < FAMILY[DISPLAY][1], "and the cover is the heavier of the two"

    box = SIZE - 2 * MARGIN
    assert fit(["corto"], ROMAN, box, box).size == 96, "a short line takes the ceiling"
    assert fit(["Una riga parecchio piu lunga di quella"], ROMAN, box, box).size < 96, \
        "a long line is set smaller, never broken"
    assert fit(["riga"] * 12, ROMAN, box, box).size < 96, "many lines are set smaller too"
    try:
        fit(["parolalunghissima" * 4], ROMAN, box, box)
    except SystemExit:
        pass
    else:
        raise AssertionError("a line that cannot fit must be an error, not an overflow")

    vector = svg(["Tizio & Caio", "5 < 6"], ROMAN, "2/7")
    assert "Tizio &amp; Caio" in vector and "5 &lt; 6" in vector, \
        "a line is escaped, or the file stops being XML at the first ampersand"
    assert vector.count("<text ") == 4, "two lines plus the two footer strings"
    gapped = svg(["sopra", "", "sotto"], ROMAN, "2/7")
    _, spaced = layout(["sopra", "", "sotto"], ROMAN, "2/7")
    assert gapped.count("<text ") == 4, "a blank line writes no tag of its own"
    assert f'y="{spaced[2][1]:g}"' in gapped, \
        "and the line under it still sits where the blank one pushed it"
    assert f'y="{spaced[1][1]:g}"' not in gapped, "nothing is set on the blank baseline"
    # The one number the two drawings must agree on, since the fitting happens
    # once and only the drawing is duplicated.
    font, placed = layout(["Tizio & Caio", "5 < 6"], ROMAN, "2/7")
    assert [line for line, _ in placed] == ["Tizio & Caio", "5 < 6"], \
        "the lines come back in reading order, whatever order they were measured in"
    assert placed[0][1] < placed[1][1], "and the first one sits above the second"
    assert f'y="{placed[0][1]:g}"' in vector, "on the baseline the SVG sets it on"
    print("ok")


def main(argv):
    if "--selftest" in argv:
        return selftest()
    for path in [CONTENT / f"{name}.md" for name in argv] or sorted(CONTENT.glob("[!_]*.md")):
        carousel(path)
    if not argv:
        fallback()


if __name__ == "__main__":
    main(sys.argv[1:])
