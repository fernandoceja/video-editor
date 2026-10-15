# zoe-dumpling-v2 caption approval table (C1 and C3)

Times are clip seconds (0 = first frame, before the 2 s end card). Source: faster-whisper large-v3 on the cleaned, loudness-normalised
voice track, with context words as a prompt. Any word under 0.80 confidence is listed as word(0.xx). Confidence = lowest word in the line.

## C1

| Clip | Start-end (s) | Caption text | Confidence | Flagged words / note |
|---|---|---|---|---|
| C1 | 0.2-0.7 | BUT YEAH, | medium | but(0.78) |
| C1 | 0.7-1.9 | WE CAN OPEN THEM, | low | them(0.31) |
| C1 | 1.7-3.3 | ~~SET IT,~~ | low | SKIP: SET IT: low confidence (0.41/0.76), unclear what was said |
| C1 | 1.9-4.2 | (gap) | - | no caption: silence or non-speech |
| C1 | 4.2-5.0 | THREE, | medium | three(0.71) |
| C1 | 5.0-5.8 | TWO, | high | - |
| C1 | 5.8-7.5 | (gap) | - | no caption: silence or non-speech |
| C1 | 7.5-8.2 | PURPLE, | medium | purple(0.74) |
| C1 | 8.2-11.5 | (gap) | - | no caption: silence or non-speech |
| C1 | 11.5-14.4 | YEAH, IT'S RIGHT HERE, | medium | yeah(0.71), it's(0.66) |
| C1 | 14.4-17.4 | (gap) | - | no caption: silence or non-speech |
| C1 | 17.4-18.8 | JUST DO THE LITTLE SQUISHY, | high | - |
| C1 | 18.8-20.5 | (gap) | - | no caption: silence or non-speech |
| C1 | 20.5-21.6 | WE JUST FOUND OUT, | medium | out(0.52) |
| C1 | 21.7-24.1 | IT LIGHTS UP, | low | it(0.23) |
| C1 | 24.1-26.9 | (gap) | - | no caption: silence or non-speech |
| C1 | 26.9-27.8 | IT'S PURPLE, | high | - |
| C1 | 28.9-30.3 | ~~THIS ONE'S ALSO RARE,~~ | medium | SKIP: THIS ONE'S ALSO RARE: product claim, not captioned |
| C1 | 27.8-30.4 | (gap) | - | no caption: silence or non-speech |
| C1 | 30.4-31.5 | I HAVE TWO MORE. | low | two(0.52), more(0.14) |

## C3

| Clip | Start-end (s) | Caption text | Confidence | Flagged words / note |
|---|---|---|---|---|
| C3 | 0.0-1.3 | ~~DO YOU WANT,~~ | low | SKIP: DO YOU WANT: repeated start, first "Do" 0.37, looks like a stutter |
| C3 | 1.1-2.7 | DO YOU WANT TO SEE | high | - |
| C3 | 2.7-3.2 | THIS ONE? | high | - |
| C3 | 3.3-5.0 | THIS ONE'S VERY PRETTY. | high | - |
| C3 | 5.3-6.8 | IT IS, ISN'T IT? | high | - |
| C3 | 6.9-8.2 | YEAH, LET'S SEE. | high | - |
| C3 | 8.2-13.3 | (gap) | - | no caption: silence or non-speech |
| C3 | 13.3-14.5 | DON'T POP IT. | medium | Don't(0.54), pop(0.67) |
| C3 | 14.5-15.7 | REMEMBER YOU'RE STRONG. | medium | you're(0.66) |
| C3 | 15.7-20.1 | (gap) | - | no caption: silence or non-speech |
| C3 | 20.1-21.8 | I LIKE THIS ONE. | medium | I(0.68), like(0.78) |
| C3 | 21.6-24.4 | ~~MY SISTER JOSIE GAVE ME THIS ONE.~~ | medium | SKIP: MY SISTER JOSIE GAVE ME THIS ONE: relative's name, not captioned unless you say so |
| C3 | 21.8-26.9 | (gap) | - | no caption: silence or non-speech |
| C3 | 26.9-27.7 | IT KIND OF HAS | medium | It(0.79), kind(0.54) |
| C3 | 27.8-28.8 | GLUE IN IT. | high | - |
| C3 | 28.9-29.7 | IT LOOKS LIKE GLUE. | high | - |
| C3 | 29.8-31.0 | EACH ONE OF THESE | low | each(0.22) |
| C3 | 31.0-32.1 | ARE SO UNIQUE | high | - |
| C3 | 32.2-34.0 | INSIDE THEY'RE ALL DIFFERENT | high | - |
