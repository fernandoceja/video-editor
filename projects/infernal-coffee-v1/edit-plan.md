# Infernal Coffee, Fontana — execution-ready edit plan, awaiting approval

Owner: 80s Obsession Company. TikTok @80s.obsession.company; Instagram @80sobsessioncompany. Shop name and city were confirmed by the owner. Use only the eight owner-supplied Drive files already in `work/infernal-coffee-v1/raw/`; preserve originals and never commit them. No stock, generated media or other external media. The single exception proposed below is external licensed music: **do not acquire or use it unless the owner explicitly authorizes that exception**. Merely approving the visual edit does not authorize outside music.

Default: 36.0 s, 1080x1920, 30 fps. Include all three shop videos and four photos. Direct cuts; each photo slowly pushes in 1.00× to 1.08× over its full duration. Captions are burned in, white bold with dark outline/shadow, positioned within left 90 px, right 140 px and 430 px above the bottom. Keep faces and products visible; inspect actual frames before claiming readability. All intervals are half-open; each caption is visible for its entire listed interval. Clip in/out times below are source seconds. Stills have no in/out: display for the listed duration.

| Time (output) | Footage and exact source in–out | Caption and treatment | Purpose |
|---|---|---|---|
| 00:00.0–00:03.0 | `Inside-Infernal-Coffee.MOV` 20.0–23.0 | A HORROR-THEMED COFFEE SHOP? | Sign and hook in first two seconds |
| 00:03.0–00:08.0 | `Inside-Infernal-Coffee.MOV` 1.0–6.0 | INFERNAL COFFEE · FONTANA | Introduce shop and city |
| 00:08.0–00:12.0 | `Inside-Internal-coffee part 2.MOV` 6.0–10.0 | THE DETAILS ARE EVERYTHING | Show horror display |
| 00:12.0–00:16.0 | `Inside-Internal-Coffee part 3.MOV` 2.0–6.0 | HORROR FANS, LOOK AROUND | Continue shop tour |
| 00:16.0–00:20.0 | `Jason Vorhees Banana Horchata latte .HEIC`, still | THE DRINKS DESERVE A CLOSE-UP; push-in | Drink reveal |
| 00:20.0–00:24.0 | `Cyndi’s Freedy Kreuger Red Velvet Latte.HEIC`, still | AND THIS ONE? SO FUN; push-in | Second drink |
| 00:24.0–00:28.0 | `Silly Cyndi with Kreuger Latte.HEIC`, still | WE LOVED OUR VISIT; push-in | Personal reaction |
| 00:28.0–00:32.0 | `Chucky and Tiff Strawberry dessert.HEIC`, still | DON’T SKIP THE DESSERT; push-in | Dessert |
| 00:32.0–00:36.0 | `Inside-Infernal-Coffee.MOV` 23.0–27.0 | FOLLOW FOR MORE LOCAL FINDS / @80s.obsession.company · TikTok / @80sobsessioncompany · Instagram | Soft follow CTA; slash denotes line break |

**Owner decision at approval — optional Cynthia insert:** `Cyndi about to enjoy Kreuger Latte.MOV` 0.0–1.5, caption `A LITTLE TASTE TEST`, placed after the red velvet photo at 00:24.0–00:25.5. Purpose: add a personal tasting moment. If included, the remaining three rows shift 1.5 seconds later: Cyndi photo 25.5–29.5, dessert 29.5–33.5, CTA 33.5–37.5. Total becomes 37.5 s. Use `timeline-with-cynthia.json` only if the owner chooses it; otherwise use `timeline-no-cynthia.json` only if they choose to omit it. Do not guess.

## Music and credit

Proposed track: “Darkest Child” — Kevin MacLeod, the [Wikimedia Commons edition](https://commons.wikimedia.org/wiki/File:Darkest_Child_(ISRC_USUAN1100783).mp3), CC BY 3.0 (commercial and social use permitted with attribution). Intended local path: `projects/infernal-coffee-v1/music/Darkest-Child.mp3`. **The file is not present.** No external media download is allowed under the owner's current rule; stop and report unless the owner explicitly approves this exception and the exact file is present. Do not substitute another track or silently render without music. `projects/infernal-coffee-v1/music/CREDIT.txt` must contain exactly:

```text
“Darkest Child” — Kevin MacLeod (incompetech.com), via Wikimedia Commons. CC BY 3.0: https://creativecommons.org/licenses/by/3.0/. Trimmed, faded and mixed with original audio.
Source: https://commons.wikimedia.org/wiki/File:Darkest_Child_(ISRC_USUAN1100783).mp3
```

Preserve source audio at unity before final mastering. Mix the track at approximately −25 dB RMS, duck it 23 dB under Silero-detected speech, and fade music during the last 1.5 s. Listen to the original clips before render: speech detection is not proof of silence, and any incidental copyrighted music needs the owner's decision. The main shop clips detected speech at 3.936–4.064 s, part 2 at 1.984–2.656 s, part 3 at 0.256–0.416 s; Cynthia clip none. All have -90° rotation metadata. Verify intended picture orientation and subject crops in proof frames.

## Posting caption draft

We found a horror-themed coffee shop in Fontana ☕🖤 Infernal Coffee was such a fun visit! Follow @80s.obsession.company on TikTok and @80sobsessioncompany on Instagram for more local finds.

#InfernalCoffee #Fontana #CoffeeShop #HorrorFans #LocalFinds

If and only if the proposed music is approved and used, append this exact line:

“Darkest Child” — Kevin MacLeod (incompetech.com), via Wikimedia Commons. CC BY 3.0: https://creativecommons.org/licenses/by/3.0/. Trimmed, faded and mixed with original audio.

## Execution — only after explicit plan approval and the Cynthia decision

1. Work from `/workspace/video-editor`. Read this entire plan and `CLAUDE.md`; confirm the user has approved the plan, decided whether Cynthia is included, and separately authorized external music. **Stop and report any missing approval or file.** Use only the matching existing timeline JSON. Do not infer consent from this plan.
2. Confirm all eight raw files listed above exist, the correct timeline, `music/Darkest-Child.mp3`, the exact credit file, `/usr/bin/chromium`, `work/.venv/bin/python`, and `projects/infernal-coffee-v1/remotion/node_modules/.bin/remotion` exist. Listen to the four source audio tracks and inspect the existing `work/infernal-coffee-v1/contact/` stills. Stop and report uncertain speech, incidental music rights, incorrect orientation, or another problem requiring an editorial decision. Never print secrets.
3. Ensure there is no prior `work/infernal-coffee-v1/prepared` directory or `projects/infernal-coffee-v1/final/infernal-coffee-v1.mp4`. If either exists, **stop** and report; do not overwrite or delete prior work.
4. Run exactly one command, selected by the owner's Cynthia decision:

```bash
cd /workspace/video-editor
bash projects/infernal-coffee-v1/scripts/render.sh projects/infernal-coffee-v1/timeline-no-cynthia.json
# OR, only if inclusion was approved:
bash projects/infernal-coffee-v1/scripts/render.sh projects/infernal-coffee-v1/timeline-with-cynthia.json
```

This calls `prepare.py` to make upright local proxies and photo copies, concatenates original audio and silence for photos, applies `mix.py`, renders Remotion composition `InfernalCoffee` with `/usr/bin/chromium`, and muxes H.264/yuv420p video plus stereo 48 kHz AAC after two-pass −14 LUFS/−1.7 dBTP normalization. Output: `projects/infernal-coffee-v1/final/infernal-coffee-v1.mp4`. The shell script runs the verification command below. Stop on any nonzero exit; report the exact failing step without improvising or overwriting.

5. Verification command (already run by the script; do not rerun unless needed):

```bash
work/.venv/bin/python tools/verify_final.py projects/infernal-coffee-v1/final/infernal-coffee-v1.mp4
```

Pass means every check in `projects/infernal-coffee-v1/final/infernal-coffee-v1.verification.json` is true: 1080x1920, exactly 30 fps, stereo AAC, clean full decode, −14.5 to −13.5 integrated LUFS, and true peak at most −1 dBTP. Independently sample frames throughout, particularly the CTA and optional insert; review caption wording, safe-zone fit, cuts, orientation and photo framing, and listen to the finished video for audio and music balance. If any check fails or review cannot be performed, stop and report; do not claim a pass or upload.
6. Deliver the review MP4 in the session and **STOP for the owner's explicit OK after they review the rendered video**. This is a separate approval from the plan. Never upload raw sources.
7. Drive status as of setup: OAuth refresh returned `invalid_grant`; folder visibility and write access are unverified. The `feat/drive-video-edit` helper's CLI downloads an existing Drive video and uploads an edited result to Drive root; its `upload` method does not specify a folder parent. It cannot currently fulfill upload into `edited videos` as-is. After the owner's final OK, stop and report this limitation unless credentials and a suitable folder-aware, create-only helper have been verified; never upload to root as a substitute. If access remains blocked, use session delivery. Do not ask for secrets in chat.

## v5 approved addendum — October 28, 2026

38.5 s, same v4 edit/captions/style/music except these owner-approved replacements. Use `timeline-v5.json`. Remove both Cynthia media and the original Freddy photo entirely. At 20–24 s use new signage HEIC crop x=650,y=1450,w=850,h=1400, caption AND THIS ONE? SO FUN. At 24–28 s use that same photo uncropped, contain fit with scale .90→.972, 45% horizontal anchor, caption WE LOVED OUR VISIT; this retains both drinks and the window display. New original: `work/infernal-coffee-v5/raw/Kreuger&Jason Latte w_Infernal Coffee signage_1322.HEIC`; upright JPG derivative at `work/infernal-coffee-v5/signage.jpg`, 2142×2856, analyzed with tools/analyze.py. Original times: hook 0–3, shop 3–8, details 8–12, look around 12–16, Jason 16–20, Freddy 20–24, wide 24–28, dessert 28–32, CTA 32–36. Append black logo card 36–38.5: brand logo 920 px wide centered, 0.4 s fade-in, white TikTok and Instagram lines beneath. Brand PNG: `projects/_brand/logo-80s-obsession-company.png` (889×618), matching the owner-attached logo and existing repo brand original.

Privacy: start/mid/end proofs extracted for each footage/photo segment, accounting for photo scale; inspected and no Cynthia visible. Proofs at `work/infernal-coffee-v5/privacy-v5/`. Hook edge is a horror prop (additional context frame confirms); wide signage shows Fernando, not Cynthia. Preserve owner privacy gate: stop if any new proof fails. Logo art is illustrative brand artwork. The old Cyndi photo and clip are excluded entirely.

Execute `work/.venv/bin/python projects/infernal-coffee-v1/scripts/prepare_v5.py projects/infernal-coffee-v1/timeline-v5.json`, then `work/.venv/bin/python projects/infernal-coffee-v1/scripts/render_v5.py`. New work directory only; never overwrite existing v1–v4. Mastering uses v4 proven recipe: dynamic loudnorm −14 LUFS / TP −2.9 / LRA11, 48k WAV, measure; stop unless I in [−15,−13] and TP≤−2.6; g=min(−14−I,−2.5−TP); apply volume g; measure post-trim and require TP≤−2.5; encode AAC and copy picture; run tools/verify_final.py and require all gates and duration 38.5 s. Source audio unity, silence for photos and logo, original audio ends 36 s; Darkest Child bed and existing CREDIT.txt unchanged, final music fade 1.5 s. Deliver only after verification by authenticated local clone/copy/hash/commit/git push into private `fernandoceja/video-review-scratch`, filename `infernal-coffee-v1-v5-REVIEW.mp4`. No release assets, blob API or Drive upload. Owner reviews before posting.
