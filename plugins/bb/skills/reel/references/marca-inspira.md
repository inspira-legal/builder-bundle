# Inspira brand rules for reel films

Every film about Inspira or its product follows this file. It comes from two sources: the brand's DNA Criativo (sections 3 and 3.9.11 to 3.9.13) and the films the brand team approved for Fenalaw 2026 (the Acervo ad for LinkedIn, 1:1, approved on 20/10/2026; the booth TV loop; the panel opener). Where the DNA and an approved film disagree, the approved film wins: the DNA marks its video lines as a proposal to confirm, and use is what confirms them.

Read it before writing `spec.md`. Where it conflicts with a house default in `<studio>/CLAUDE.md` (UI overshoot, the synthesized beat), this file prevails for Inspira films.

The base scene is `<studio>/scenes/inspira-acervo-1x1`: it applies every rule below. Start from it, and reframe it for other formats.

## Field

- One light field from the first frame to the last: the hero of inspire-se.co, `linear-gradient(180deg, rgba(195,214,247,.73) -9%, #F0F5FE 29%)` over Link Water `#F0F5FE`, with at most a soft radial glow of the same blue.
- No dark opening or closing: no Ink field, no navy gradient, no circular wipe into a dark card.
- No scrim. To focus one element, step the other card back (scale 0.95, lower opacity) instead of darkening the screen.
- Pure white is for cards only. Link Water is the brand's white and Ink `#070C21` its black.

## Product on screen

- Loose white cards floating on the field. Never the whole app window: no sidebar, no browser chrome, no app frame around the card.
- Each card copies the real component from app.inspira.legal, measured in the app on the day: type, colors, borders, radii, icons and copy. Never invented UI. The app needs a login, so the person opens it in their own browser. Claude never signs in for them.
- When nobody can open the app: build the card from the components of the base scene, which were measured in the app on 20/10/2026, and put on screen no component, answer or number that the scene does not already carry. Say in the delivery that the screens were not checked against the app, and answer question 3 of the brand check with "not checked", not "yes".
- Measured on 21/10/2026, at 1x (scale everything by `k`, defined under Formats):

| Element              | Value in the app                                                                       |
| -------------------- | -------------------------------------------------------------------------------------- |
| Type                 | Poppins 400, 500 and 600 everywhere                                                    |
| Page title           | 32 px, 400, `rgb(28,38,79)`                                                            |
| Text                 | 13 to 14 px, `rgb(54,63,73)`; secondary 12 px, `rgb(101,108,116)`                      |
| Card and row         | white, 1 px border `rgb(220,222,224)`, radius 10 px; row divider `rgb(238,240,243)`    |
| Table header         | `rgb(246,247,249)`, 13 px, 600, `rgb(101,108,116)`                                     |
| Pill button          | white, border `rgb(220,222,224)`, full radius, 12 px, 500                              |
| Selected item        | `#F0F5FE`, radius 12 px                                                                |
| Active badge         | background `rgb(232,250,246)`, text `rgb(4,107,87)`, dot `rgb(15,148,122)`, 11 px, 500 |
| Floating card shadow | `0 4px 12px 4px #346BD11C`                                                             |

- Answers on screen come from the product: run the request in Inspira, copy the real answer, then rebuild the card. Never write an answer by hand.
- Demo documents and case numbers are fictitious, and a demo document says so on the page ("Documento fictício, criado para demonstração"). Any legal basis shown is checked at the official source before render.
- Get closer, not wider: a tight frame on the part that matters, with the camera moving across it, reads better than the full screen in small type.

## Logo

- `logo_inspira_dark.svg` on the light field, `logo_inspira_light.svg` on a dark one. The file as it is: never the symbol inside a gradient tile, never redrawn, recolored, shadowed or animated apart.
- Minimum size: 120 px wide for the full logo on screen.
- A partner logo (event, client) is sized by the cap height of the "inspira" letters, not by the outer box of each file.

## Type and captions

- Poppins 400, 500 and 600. Instrument Serif italic for one line at most (the second half of the signature), never under 20 px and never for running text.
- A caption is a title, not a step. Two short lines, loose on the field and centered at the top: Poppins 600 (56 px at 1080 wide), the second line in Cornflower `#6A97EB`. No box, no lower third, no "PASSO 1", no uppercase label followed by a description.
- The caption says what the person gets, in their words ("A resposta já vem" / "com a fonte indicada"), never the instruction ("Clique em…", "PERGUNTE"). One pair per chapter. It rises behind a mask and leaves the same way.
- A highlight phrase has no final full stop. The official signature keeps both: "IA é fundamento. Construa o que vem depois."
- Cornflower carries 1 to 3 words per block and only in large type (40 px and up at 1080 wide). Small text goes in Ink or `#656C74`.
- Copy follows the brand voice: no em dash anywhere, no "Descubra", no "Em um mundo onde", no alarmism. Check every accent.
- Minimum sizes on a TV seen from 4 m: title 72 px, quote 60 px, text inside a card 26 px (smaller only reads as texture).

## Opening

The hook sits on the same light field in the first 2 s: the logo small at the top, two big lines (Poppins 600, the second in Cornflower) and one support line in `#656C74`. Then the hook rises away and the first product card rises in from below. No dark intro, no logo tile zooming in, no slogan with a full stop in the style of a launch.

## Closing

Same light field: the dark logo; one idea in two big lines (the second in Cornflower); a thin divider; one context line (site, event, date); the signature in two lines, "IA é fundamento." in Poppins 500 and "Construa o que vem depois." in Instrument Serif italic. A film that loops makes its last frame continue into the first.

## Motion

- Calm and editorial, never bouncy. Presets `default` and `heavy` for cards, type and logo; `snappy` only for small UI states (focus ring, button press); never `playful`. No visible overshoot on type, logo or cards.
- Cursor on a critically damped glide, `{ w: 10, z: 1 }`, large enough to read on a phone, with a click ripple in `#5187EC`.
- Lines rise behind a mask with 0.08 to 0.12 s between them. No scale-in, rotation, zoom transition, whip or glitch.
- One continuous element per chapter (the question bar opens into the answer card), as in the reference scene.
- Shot length: 1.5 to 2.5 s in a product film, 2.5 to 4 s in an institutional one.

## Sound

- No synthesized beat in an Inspira film. Leave `window.BPM` unset, so the render outputs a silent video, and keep the beat grid in a local constant (`const B = (n) => motion.beat(n, 112)`). No UI click blips either.
- The person chooses the track. With a track, it goes in the scene as `audio.wav` and the cuts land on its beat. The DNA asks for contained instrumental music, 70 to 95 BPM, with no marked electronic percussion, and for silence or ambient sound on sensitive topics.

## Formats

| Format                      | Size                       | Notes                                                 |
| --------------------------- | -------------------------- | ----------------------------------------------------- |
| LinkedIn and Instagram feed | 1080 × 1080 or 1080 × 1440 | 3:4 is the brand's feed format                        |
| Reel and story              | 1080 × 1920                | keep text out of the top 250 px and the bottom 350 px |
| TV and presentation         | 1920 × 1080                | see the TV type sizes above                           |

Every size in this file given "at 1080 wide" is a size at `k = 1`, where `k = min(w, h) / 1080`. A 1080 × 1920 film and a 1920 × 1080 one both have `k = 1`, which is why the TV sizes above are absolute; a 1280 × 720 film has `k = 0.67`, and every size, margin and distance is multiplied by it. Text, logo and lines stay inside a margin of `120 × k` on every side. Reframe per format, never crop.

The base scene is drawn on a fixed 1080 × 1080 canvas. For another format, rewrite its positions as a function of `(w, h)` and `k` (the layout rule of `<studio>/CLAUDE.md`): center the content block on the longer side, and in 9:16 stack it vertically inside the safe area above instead of shrinking it.

## Internal repertoire

Legal tech launch films (a giant typed prompt that shrinks into the product; an agent at the center with tasks in orbit; a tight camera over the interface with a cursor) are repertoire for pacing. A film never names or imitates another brand.

## Brand check, added to the critique loop

Before scoring a round, answer each one with yes or no:

1. Is the field light from the first frame to the last, with no dark wipe or scrim?
2. Is every screen a loose card, with no sidebar or app window?
3. Does every card match the real app, and is every answer a real one? ("Not checked" when nobody could open the app; it is not a "yes".)
4. Are the captions titles at the top, with no box and no step label?
5. Do the highlights have no final full stop, and does the copy have no em dash?
6. Is the logo the right file for its background, at 120 px or more?
7. Is the motion free of bounce, and is the sound either the person's track or silence?
