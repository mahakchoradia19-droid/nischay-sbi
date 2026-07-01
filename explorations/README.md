# explorations/ — the individual-customer build this grew out of

Before the DBT-rescue idea, I built the *individual* version of the same thesis:
agentic AI that acquires, onboards, engages and educates one customer at a time.
It's real, it runs, and it's the machinery that made the rescue demo possible — the
voice KYC, the fuzzy name matcher, the compliance gate, and the honest-metrics
discipline all started here.

It lives in `explorations/` rather than the front page on purpose. The proposal is
about **one** uncopyable idea; these are kept as evidence of range and as the origin
story, not as competing pillars.

| Folder | What it is | Run |
|---|---|---|
| `onboarding/` | Voice-led KYC onboarding agent (this is the engine the rescue reuses) | `cd explorations/onboarding && python3 app.py` → :8000 |
| `scout/` | Acquisition agent — ranks prospects across channels | `cd explorations/scout && python3 app.py` → :8002 |
| `engage/` | SAARTHI — proactive engagement, one timely nudge | `cd explorations/engage && python3 app.py` → :8003 |
| `finpulse/` | A transparent Money Health Score + self-evaluation | `cd explorations/finpulse && python3 app.py` → :8004 |
| `finlearn/` | FinSmart Academy — a voice tutor + fresh, computed questions | `cd explorations/finlearn && python3 game_server.py` → :8001 |
| `community/` | The first, standalone version of the DBT Gap Agent (now superseded by the root demo) | `cd explorations/community && python3 app.py` → :8005 |

`security.py` (shared middleware) and the old design docs (`docs/`) live here too.
The current, focused build is the repository root.
