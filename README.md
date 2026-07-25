# belloworld.it

Source of <https://belloworld.it>. Built with [Zola](https://www.getzola.org/).
No toolchain beyond Zola itself: it compiles the Sass, and everything else is a
template.

The site is two halves that share a domain and nothing else.

**The homepage** is a portfolio in English, built on the particle theme (see
Credits). It has particles.js, a scrolling script and an autoplaying video, and
it speaks to people who take computers apart. Its content is not in
`content/`: the projects, services and talks are written directly in
`templates/content.html`.

**`/belli/`** is a section in Italian, ["Bello,
World"](https://belloworld.it/belli/), short pieces explaining one computing
thing each to people who are not in the trade. It ships no JavaScript, makes no
external request and reads fine with stylesheets disabled. It has its own
stylesheet, its own typefaces and its own templates, on purpose. To add a piece
or change how the section looks, read [BELLI.md](BELLI.md).

## Running it

```
zola serve
```

Then <http://127.0.0.1:1111>. Check every change there before pushing: a push to
`master` publishes the site through GitHub Actions, onto the `gh-pages` branch,
served at the domain in `static/CNAME`.

## Where everything lives

| What | Where |
|---|---|
| Site and author settings | `config.toml`, `[extra]` |
| Homepage frame and its four sections | `templates/index.html`, `templates/macros.html` |
| Homepage copy: projects, services, talks | `templates/content.html` |
| Homepage styles | `sass/main.scss` and its partials, colours in `sass/_vars.scss` |
| The Italian section | `content/belli/`, `templates/belli/`, `sass/belli.scss` |
| Fonts, images, scripts | `static/` |

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
