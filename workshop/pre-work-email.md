# Pre-Work Email — Vibe Analytics Workshop

**Send by:** September 15 (two weeks before the workshop)
**Purpose:** Get everyone's environment working before they're in the room. Every step below has failed at least once during development — this email exists to catch each of those failures in an email thread instead of at minute 12.

---

**Subject: Vibe Analytics — 15 minutes of setup before we meet (please do this by [DATE])**

Hi all,

Looking forward to Vibe Analytics on September 29. This is a hands-on workshop — you'll write a real skill, run it against a real warehouse, and measure whether it actually helped. To make the most of our three hours together, I need everyone's laptop ready to go *before* we start.

Please do the following now and reply to this email if anything doesn't work. Don't wait until the morning of — if you hit a snag, we have time to fix it now and none the day of.

**This takes about 15 minutes if everything goes smoothly, and everything below has broken for someone during testing — so budget a little extra the first time.**

## 1. Bring a laptop with admin rights

You'll install Python packages and clone a repo. If your machine is locked down by IT, please sort that out with them this week.

## 2. Get the materials

```
git clone https://github.com/RobStilson/analytics-skills.git
```

No git? Download the ZIP from the green "Code" button on that page instead.

## 3. Install Python 3.9 or newer

Check what you have:

```
python --version
```

If you don't have Python, or it's older than 3.9, grab it from [python.org](https://www.python.org/downloads/).

**If you're on Windows and have more than one Python installed** (common if you've used the Microsoft Store version), use `python -m pip` instead of a bare `pip` for the next step — otherwise packages can install to a different Python than the one that runs your scripts.

## 4. Install the dependencies

From inside the folder you cloned or unzipped:

```
python -m pip install -r requirements.txt
```

## 5. Get an Anthropic API key — and add credit

Go to [console.anthropic.com](https://console.anthropic.com), create an API key, and **add a small amount of credit to the account** ($5 is plenty). The key alone isn't enough — a key with no credit fails in a way that looks like a bug but isn't.

Set it as an environment variable:

**Windows (PowerShell):**
```
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

**Mac/Linux:**
```
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

(This only lasts for your current terminal session — that's fine, just re-set it if you close and reopen your terminal before the workshop.)

## 6. Verify everything works

This is the step that matters most. Run:

```
python check_setup.py
```

It checks your Python version, your packages, the workshop data file, and — if you've set your API key — makes one small live test call. You should see:

```
Ready. Everything required is working.
```

**If you see anything other than "Ready," reply to this email with the full output.** It will tell you exactly what's wrong and how to fix it — most issues are one line to resolve, but I'd rather solve it this week over email than in the room.

## What if I can't get an API key through my company?

Some corporate networks block API access or don't allow personal billing. If that's you, reply now and we'll either get you a temporary key for the day or pair you with someone else for the hands-on portions. Please don't wait until the morning of to mention this.

---

That's it — six steps, and step 6 tells you if you're actually ready. See you on the 29th.

[Your name]

---

## Facilitator notes (delete before sending)

- **Two-week lead time is deliberate.** During development, environment setup failed four separate times — a Python version mismatch, a missing package, a wrong working directory, and an exhausted API key. Every one of those is a five-minute fix over email and a workshop-derailing problem in person.
- **The credit warning is not boilerplate.** An API key with zero credit fails with a real, correctly-formatted API error — it looks exactly like something is broken with the setup, and it is the single most likely support email you'll get.
- **`check_setup.py` is the whole point of this email.** Everything above exists to get people to a point where that script can run and tell them, specifically, what's still wrong. Don't let anyone skip straight to "I think I'm fine" — have them paste the actual output.
- **Track responses.** If you don't get a "Ready" confirmation from someone by September 20, follow up directly — don't assume silence means success.
