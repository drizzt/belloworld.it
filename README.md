# belloworld.it

Source of <https://belloworld.it>. Built with [Zola](https://www.getzola.org/),
which compiles the Sass and renders every template. The only other moving part
is `slides.py`, which draws the slide images for `/belli/` and wants Python and
[Pillow](https://python-pillow.org/).

The site is two halves that share a domain and nothing else.

**The homepage** is a portfolio in English, built on the particle theme (see
Credits). It has particles.js, a scrolling script and an autoplaying video, and
it speaks to people who take computers apart. Its content is not in
`content/`: the projects, services and talks are written directly in
`templates/content.html`.

**`/belli/`** is a section in Italian, ["Bello,
World"](https://belloworld.it/belli/), short pieces explaining one computing
thing each to people who are not in the trade. It makes no external request and
reads fine with stylesheets disabled. The one script it loads is
`static/js/carousel.js`, on the pieces that carry slides. It has its own
stylesheet, its own typefaces and its own templates, on purpose.

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
| Homepage frame and its four sections | `templates/index.html` |
| Homepage copy: projects, services, talks | `templates/content.html` |
| Homepage styles | `sass/main.scss` and its partials, colours in `sass/_vars.scss` |
| The Italian section | `content/belli/`, `templates/belli/`, `sass/belli.scss` |
| The slides, and how they are drawn | `slides.py`, into `static/img/slides/<slug>/` |
| Fonts, images, scripts | `static/` |
| The deploy, and the slide redraw before it | `.github/workflows/build-action.yaml` |

All fonts are self-hosted from `static/fonts/`, subset to latin. The site loads
nothing from a CDN and calls no third party, so no external service learns who
reads it. Whatever gets added, keep that true.

`theme.toml` is here because this repository is a copy of the particle theme
rather than a site that installs it. Zola ignores the file.

## Credits

The homepage is built on [particle](https://github.com/nrandecker/particle) by
Nathan Randecker, [ported to
Zola](https://github.com/svavs/particle-zola) by Silvano Sallese, MIT licensed,
see [LICENSE.md](LICENSE.md). It carries
[particles.js](https://github.com/VincentGarreau/particles.js/) by Vincent
Garreau, [sweet-scroll](https://github.com/tsuyoshiwada/sweet-scroll) 2.2.0 by
tsuyoshiwada, and [Font Awesome](https://fontawesome.com/v4/) 4.7.

Typefaces: Montserrat and VT323 on the homepage, IBM Plex Sans and IBM Plex Sans
Condensed in `/belli/`, all under the SIL Open Font License.
