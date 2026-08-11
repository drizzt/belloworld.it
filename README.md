# belloworld.it

Source of <https://belloworld.it>. Built with [Zola](https://www.getzola.org/),
which compiles the Sass and renders every template. The only other moving part
is `slides.py`, which draws the slide images for `/belli/` and wants Python and
[Pillow](https://python-pillow.org/).

The site is one thing: ["Bello, World"](https://belloworld.it/belli/), a section
in Italian of short pieces explaining one computing thing each to people who are
not in the trade. The root of the domain plays the intro video the name comes
from, and hands the reader to `/belli/` when it ends. The video ships twice,
`static/bello.av1.mp4` and `static/bello.h264.mp4`, and the browser fetches whichever
of the two it can decode, never both. It
makes no external request and reads fine with stylesheets disabled. It loads one
script, `static/js/carousel.js`, on the pieces that carry slides, and carries a
few inline lines on the root, for the jump to the section: without either, the
strip still scrolls and the root still has its link.

A piece is one markdown file in `content/belli/`, and its address comes from the
`slug` in the front matter. The slides travel in an `extra.slides` array there,
one entry per slide, one string per line as it should be read: `slides.py` turns
them into the images, and its docstring is the reference for what it will and
will not do with them.

## Running it

```
python3 slides.py
zola serve
```

The templates use Tera v2, so Zola 0.23 or newer is required. An older one stops
at `Unknown tag`. To install or upgrade:

```
cargo install --locked --git https://github.com/getzola/zola
```

Then <http://127.0.0.1:1111>. The first line is not optional on a fresh clone:
only the SVG of each slide is committed, and the templates read the dimensions
of the PNG beside it for the `og:image` tags, so a missing PNG is a build that
fails rather than a picture that is missing. Run it again after editing any
`extra.slides`.

Check every change in the browser before pushing: a push to `master` publishes
the site through GitHub Actions, onto the `gh-pages` branch, served at the
domain in `static/CNAME`. The same workflow redraws the slides first, and fails
the build if the committed SVGs no longer say what the front matter says.

## Where everything lives

| What | Where |
|---|---|
| Site and author settings | `config.toml`, `[extra]` |
| The root of the domain, video and all | `content/_index.md`, `templates/home.html`, `static/bello.av1.mp4`, `static/bello.h264.mp4` |
| The section itself | `content/belli/`, `templates/belli/`, `sass/belli.scss` |
| The page shown for an address that leads nowhere | `templates/404.html` |
| The slides, and how they are drawn | `slides.py`, into `static/img/slides/<slug>/` |
| Fonts, images, scripts | `static/` |
| The deploy, and the slide redraw before it | `.github/workflows/build-action.yaml` |

All fonts are self-hosted from `static/fonts/`, subset to latin. The site loads
nothing from a CDN and calls no third party, so no external service learns who
reads it. Whatever gets added, keep that true.

## Credits

Typefaces: IBM Plex Sans and IBM Plex Sans Condensed, under the SIL Open Font
License.

[LICENSE.md](LICENSE.md) is the MIT license of
[particle](https://github.com/nrandecker/particle) by Nathan Randecker, [ported
to Zola](https://github.com/svavs/particle-zola) by Silvano Sallese. This
repository began as a copy of that theme. None of its code is left, and the
file stays for the history.
