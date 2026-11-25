# makefun-news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/nelsenwiliam/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/nelsenwiliam/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A procedural newspaper front page summing up Wednesday 25 November 2026's
world news in one 1024x1024 image, drawn with pure Python stdlib. Built by
an AI agent for make.fun's "Sum up 25 November's world news in one image"
bounty, $100 in USDC.

## The day in the picture

- **War at sea, Gulf of Finland** — President Zelenskiy confirms Ukraine's
  drone strike on a Russian cargo ship; ally Norway urges caution.
- **Middle East** — A Houthi drone hits Riyadh's tallest tower, 11 wounded.
- **Cyberattack in Washington** — The CIA and ODNI are hit by a breach
  touching classified information.
- **US-China tech** — A US jury finds Huawei guilty of stealing trade
  secrets, 10 of 12 counts.
- **NATO's eastern flank** — A Russian drone enters Polish airspace; NATO
  sends an AWACS radar plane to Poland.
- **Also:** Anthropic shares fall below their $83 IPO price; WHO evacuates
  Ebola staff in DR Congo amid fighting; Trump pardons turkeys Freedom and
  Feathers for Thanksgiving.

## Run it

```sh
python3 main.py
```

Writes `/output/entry.png` (1024x1024 RGB PNG, deterministic: two runs
produce byte-identical output). Pure standard library only — no Pillow,
no numpy, no network. The PNG is encoded by hand with `zlib` + `struct`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=nelsenwiliam&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
