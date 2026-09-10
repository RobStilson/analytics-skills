# Pre-Work Email — Vibe Analytics Workshop

**Send by:** September 15 (two weeks before the workshop)
**Purpose:** Get everyone's environment working before they're in the room. Every step below has failed at least once during development — this email exists to catch each of those failures in an email thread instead of at minute 12.

---

**Subject: Vibe Analytics — 20 minutes of setup before we meet (please do this by [DATE])**

Hi all,

Looking forward to Vibe Analytics on September 29. This is a hands-on workshop — you'll write a real skill, run it against a real warehouse, and measure whether it actually helped. To make the most of our three hours together, I need everyone's laptop ready to go *before* we start.

Please do the following now and reply to this email if anything doesn't work. Don't wait until the morning of — if you hit a snag, we have time to fix it now and none the day of.

**This takes about 20 minutes if everything goes smoothly, and everything below has broken for someone during testing — so budget a little extra the first time.**

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

## 4. Install VS Code and connect it to the right Python

[Download VS Code](https://code.visualstudio.com/) — it's free, and it's what we'll use to edit files and run scripts during the workshop.

Once it's installed, open the folder you downloaded in step 2 (**File → Open Folder**, then pick the `analytics-skills` or `analytics-skills-main` folder).

**Install the Python extension:** click the Extensions icon in the left sidebar (four squares), search for "Python," and install the one published by Microsoft.

**Point VS Code at the same Python you just installed:**

1. Press `Ctrl+Shift+P` (Mac: `Cmd+Shift+P`) to open the command palette
2. Type "Python: Select Interpreter" and press Enter
3. Pick the one that matches the version you saw in step 3

This step matters more than it looks like it should. If VS Code is pointed at a different Python than your terminal, scripts will fail with `ModuleNotFoundError` even though you installed everything correctly — the packages just aren't where VS Code is looking.

**When you run a script during the workshop, always do it from VS Code's terminal, not the green "Run" play button.** Open a terminal inside VS Code with **Terminal → New Terminal**, and run scripts by typing `python filename.py` there. The play button has caused exactly the `ModuleNotFoundError` problem above for multiple people during testing — it can quietly use a different Python than the one you selected above. The terminal doesn't have that problem.

**About Claude:** you don't need to install anything extra to connect VS Code to Claude. The scripts in this repo talk to Claude directly through the API key you'll set in step 6, using a Python package (`anthropic`) that's already in the dependency list. There's no separate app or extension to configure — once your API key is set and `check_setup.py` says Ready, you're connected.

## 5. Install the dependencies

Open your terminal, navigate to the folder you downloaded, and run:

**Windows:**
```
cd Desktop\analytics-skills-main
python -m pip install -r requirements.txt
```

**Mac/Linux:**
```
cd ~/Desktop/analytics-skills-main
python3 -m pip install -r requirements.txt
```

(If you downloaded the ZIP, the folder may be called `analytics-skills-main`
instead of `analytics-skills` — look for whichever one you have.)

**If you get a credentials error, proxy error, or 401 from an internal
server** (common on corporate networks that route pip through an internal
mirror): add `--index-url https://pypi.org/simple/` to the end of the command:

```
python -m pip install -r requirements.txt --index-url https://pypi.org/simple/
```

If that still doesn't work, your IT department may need to whitelist
`pypi.org` and `files.pythonhosted.org`. Reply to this email and we'll sort
it out before the workshop.

## 6. Get an Anthropic API key — and add credit

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

## 7. Verify everything works

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

That's it — seven steps, and step 7 tells you if you're actually ready. See you on the 29th.

[Your name]

---

## Facilitator notes (delete before sending)

- **Two-week lead time is deliberate.** During development, environment setup failed four separate times — a Python version mismatch, a missing package, a wrong working directory, and an exhausted API key. Every one of those is a five-minute fix over email and a workshop-derailing problem in person.
- **The VS Code interpreter-selection step (step 4) is not optional polish.** The single most repeated setup failure during development — hit on two different machines — was VS Code's play button silently running scripts with a different Python than the terminal, producing a `ModuleNotFoundError` that looks like a broken install when it isn't. Pointing VS Code at the same interpreter up front, and training people to use the integrated terminal instead of the play button, prevents this before it happens rather than debugging it live.
- **"Connecting Claude to VS Code" is explicitly addressed as a non-step.** It's a reasonable thing to expect needs setup, and if the email doesn't say otherwise, someone will spend time hunting for an extension that doesn't exist for this workshop. The scripts talk to Claude through the API key alone.
- **The credit warning is not boilerplate.** An API key with zero credit fails with a real, correctly-formatted API error — it looks exactly like something is broken with the setup, and it is the single most likely support email you'll get.
- **`check_setup.py` is the whole point of this email.** Everything above exists to get people to a point where that script can run and tell them, specifically, what's still wrong. Don't let anyone skip straight to "I think I'm fine" — have them paste the actual output.
- **Track responses.** If you don't get a "Ready" confirmation from someone by September 20, follow up directly — don't assume silence means success.
