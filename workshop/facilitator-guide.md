# Vibe Analytics — Full Workshop Guide

**3 hours · 8 blocks · everything you say and everything they do**

This is your minute-by-minute script for running the workshop. Every command
is copy-pasteable. Every step has both Windows and Mac/Linux variants. Nothing
is assumed about participants' experience level — if a step says "open a
terminal," it says where to find one.

Print this. Bring it on a second screen. Don't wing it.

---

## Before the day: your checklist

- [ ] You have run `check_setup.py` yourself and it says **Ready**
- [ ] You have run `run_my_ablation.py` yourself at least once (smoke test)
- [ ] You have done a full timed read-through of the deck, out loud, alone
- [ ] You have printed the **data dictionary** (`workshop/data-dictionary.html`)
      — one copy per participant plus two spares
- [ ] You have printed the **worksheets** — one of each per participant:
  - `workshop/define-worksheet.md`
  - `workshop/validate-worksheet.md`
  - `workshop/build-worksheet.md`
- [ ] You have the deck ready (`cd workshop && node build_deck.js` rebuilds it)
- [ ] You have the failure-demo script (`workshop/failure-demo-script.md`) open
      where you can read it while presenting — not on the projector
- [ ] Every participant has replied to the pre-work email with **Ready** from
      `check_setup.py`, or you've followed up directly
- [ ] You have 2–3 spare API keys with credit loaded, for anyone whose setup
      fails day-of despite the pre-work (this will happen at least once)
- [ ] You know the wifi password and have tested it can handle the room

---

## Arrival and setup — 15 minutes before start

As people arrive, have them open a terminal and verify:

**Say out loud:**
> "Before we start, please open a terminal and run the setup checker. This
> takes ten seconds and tells us if anything needs fixing before we begin."

**Windows — PowerShell:**
```powershell
cd "C:\path\to\analytics-skills"
python check_setup.py
```

**Mac/Linux — Terminal:**
```bash
cd ~/path/to/analytics-skills
python3 check_setup.py
```

**How to open a terminal if someone doesn't know:**
- **Windows:** press `Win + X`, click "Terminal" or "PowerShell"
- **Mac:** press `Cmd + Space`, type "Terminal", press Enter
- **Linux:** press `Ctrl + Alt + T`

**If someone sees anything other than "Ready":** the output tells them exactly
what's wrong and the command to fix it. Help them through it now. The two most
common issues:

1. **"ANTHROPIC_API_KEY not set"** — they need to set it in this terminal
   session:

   **Windows PowerShell:**
   ```powershell
   $env:ANTHROPIC_API_KEY = "sk-ant-their-key-here"
   ```

   **Mac/Linux:**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-their-key-here"
   ```

   Then run `python check_setup.py` again. This only lasts for the current
   terminal window — if they close it, they'll need to set it again.

2. **"duckdb not installed" or similar missing package** — they used the wrong
   pip:

   **Windows:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

   **Mac/Linux:**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

   Always `python -m pip`, never bare `pip` — bare `pip` may install to a
   different Python than the one running the scripts.

3. **If nothing works and you're burning time:** hand them one of your spare
   API keys, have them set it, and move on. Fix the root cause at the break.

**Once everyone shows "Ready":** start the clock.

---

## Block 1: Framing — 0:00 to 0:20

### What you do

Present deck slides 1–9. This is the "why this matters" setup. You're
making the case that analytics has a structural problem coding doesn't:
one correct answer, many plausible wrong ones, and nothing that flags the
difference.

**Key points to hit (not a script — say it in your own words):**

- Coding agents worked first because code has compilers and tests. Analytics
  has no equivalent. A wrong query runs perfectly and produces a number that
  looks fine.
- Three failure modes: entity ambiguity (many plausible tables), staleness
  (docs and schemas drift), retrieval failure (the right answer is
  documented but the agent doesn't find it). Plus the one that hides:
  silent wrongness.
- The reframe: a skill is markdown, not code. The bottleneck is judgment,
  which analysts have and models don't. Anyone in this room can contribute.

### What they do

Listen. Laptops can stay open but nobody's typing yet.

### Timing check

If you hit 0:18 and you're still on slide 5, skip ahead to slide 8 (the
demo-setup slide) and say: "Let me show you what I mean instead of telling
you." The demo is more persuasive than any slide.

---

## Block 2: Failure Demo — 0:20 to 0:40

### What you do

Follow `workshop/failure-demo-script.md` exactly. Have it open on a device
you can read from — not on the projector.

**The short version of the demo:**

1. Open a terminal connected to the warehouse (you already verified this
   works during your smoke test)
2. Ask the agent, with no skill loaded: *"How many employees do we have?
   Just give me the number, I'm in a hurry."*
3. Show the response. Ask the room: "Would you forward this to your VP?"
4. Load the `provenance-footer` skill and ask the identical question
5. Show the difference — the footer, the stated assumptions, the named
   alternative number

**The captured responses are already in the script** — if the live demo
fails (API error, wifi issue, unexpectedly good baseline), switch to
showing the captured version. One sentence: "Here's what I got earlier —
same result." No drama, no apology.

### What they do

Watch. Answer your discussion prompts. Start to believe the problem is real.

### Timing check

If the live demo works on the first try, you'll finish early. That's fine —
use the extra time to let the room discuss. Don't rush into Define early;
let the point land.

---

## Block 3: Define — 0:40 to 1:00

### What you do

**Say out loud:**
> "For the rest of today, you're going to do one complete cycle: specify a
> question, write the test, build the reference doc, and measure whether it
> helped. Everything starts with the question — and you're going to spec it
> before you look at any data, on purpose."

**Hand out:**
- The **define-worksheet.md** printout (or tell them to open it:
  `workshop/define-worksheet.md`)
- The **data dictionary** printout — this is their map of the warehouse

**Say out loud:**
> "The data dictionary is your map. It shows every table, every column, and
> every gotcha I know about. You don't need to open the database to figure
> out what's in it — it's all on this sheet. Don't worry about the 28 empty
> tables at the bottom — those are deliberately empty. If you query one and
> get zero rows, it's the table, not your SQL."

**Say out loud:**
> "Step zero on the worksheet: pick a domain. You have three choices —
> Attrition, Compensation, or Engagement. This choice sticks for the rest
> of the day, so pick the one you'd actually encounter at work. If we have
> more than three people, double up on a domain — two people writing one
> excellent doc beats two mediocre ones. Say your choice out loud so I can
> make sure we're spread across all three."

Wait for everyone to pick. Write it on a whiteboard or notepad:
`[Name] → [Domain]`. You'll reference this list in every subsequent block.

**Then say:**
> "You have 18 minutes. Work through the worksheet top to bottom. You're
> specifying the question, not answering it — resist the urge to start
> querying. The last step is 'Emit the spec.' If you get there with time
> left, great. If you're still on step 3 at minute 15, skip to 'Emit the
> spec' and fill in what you have — a partial spec you wrote down is more
> useful than a perfect one you didn't."

**Then:** circulate. Don't hover. Answer questions when asked.

### What they do

Work `define-worksheet.md`:
- Step 0: pick a domain (2 min)
- Step 1: restate the question and set the population (3 min)
- Step 2: time basis and grain (4 min)
- Step 3: name the measure (4 min)
- Step 4: comparison, decision, precision (5 min)
- Step 5: existing coverage and open assumptions (2 min)
- Emit the spec

### At minute 18, call time

**Say out loud:**
> "Time. Give me one sentence each: what's your question, and what's your
> biggest open assumption?"

Go around the room. This takes 2 minutes and confirms everyone has a spec.

---

## Block 4: Validate — 1:00 to 1:30

### What you do

**Say out loud:**
> "Now you're going to write the test before the answer exists. This feels
> backwards the first time. It's the same idea as test-driven development:
> define what 'good' looks like before you've seen the output, so you have
> something objective to measure against later."

**Hand out:** the **validate-worksheet.md** printout (or direct them to
`workshop/validate-worksheet.md`)

**Say out loud:**
> "You're writing 2 to 3 assertions about what a good answer to your
> question looks like. Not 'the answer is correct' — you don't know the
> answer yet. Something a stranger could check by reading the response:
> 'the response states which table the number came from,' 'the response
> names the denominator used.' The worksheet has examples of weak vs.
> strong assertions."
>
> "At the end, you'll save this as a JSON file. The format is on the
> worksheet. Don't worry about getting the JSON perfect — if there's a
> syntax error, the tool will catch it later and tell you exactly what's
> wrong."

**Critical instruction:**
> "Do NOT open the database yet. Do NOT start querying. You're reasoning
> about what a good process looks like, based on what you already know about
> your domain. You'll query the warehouse in the next block."

**Then:** circulate. The JSON schema is the most likely friction point —
help anyone who's struggling with the format. Common issues:
- Trailing comma after the last item in a list (JSON doesn't allow it)
- Single quotes instead of double quotes (JSON requires double)
- Missing closing brace or bracket

### Saving the eval file

At around minute 20, say:

> "Save your eval as `evals/my-eval.json` in the repo. That exact filename
> and location — the ablation script looks for it there by default."

**Walk them through saving it:**

**If they're using a text editor (Notepad, VS Code, etc.):**
> "File → Save As → navigate to the `evals` folder inside
> `analytics-skills` → filename: `my-eval.json` → Save"

**If anyone asks "is my JSON valid?":** have them run this in their terminal:

**Windows:**
```powershell
python -c "import json; json.load(open('evals/my-eval.json')); print('Valid!')"
```

**Mac/Linux:**
```bash
python3 -c "import json; json.load(open('evals/my-eval.json')); print('Valid!')"
```

If it prints "Valid!" they're good. If it prints an error, it will say
exactly where the problem is (line number and character).

### At minute 25, the prediction step

**Say out loud:**
> "Last five minutes. Step 5 on the worksheet: for each assertion you
> wrote, predict whether a plain agent with no reference doc would pass or
> fail it. Write your prediction down — you'll check it against reality in
> about 45 minutes, and being wrong is just as useful as being right."

### At minute 30, call time

**Say out loud:**
> "Time. One sentence each: what's your strongest assertion, and do you
> think a plain agent passes it or fails it?"

Go around the room.

---

## Block 5: Build — 1:30 to 2:15

### What you do

**This is the main block. It's the longest, the most hands-on, and the one
the whole workshop is built around.**

**Say out loud:**
> "Now you open the database. You're filling in a reference doc for your
> domain — the same template that produced the headcount example you saw
> earlier. The worksheet walks you through it section by section, with time
> budgets for each."
>
> "You'll run SQL queries against the warehouse using Python. Here's the
> pattern — this is the only pattern you need today."

**Write this on the whiteboard or project it:**

```python
import duckdb
con = duckdb.connect("warehouse/people_analytics.duckdb", read_only=True)

result = con.execute("""
    YOUR SQL HERE
""").fetchall()

for row in result:
    print(row)

con.close()
```

**Say out loud:**
> "Save this as a .py file — call it `explore.py` or whatever you like —
> in the repo root, and run it from your terminal. Change the SQL inside
> the triple quotes each time you want to try a different query. The
> `read_only=True` is important — leave it in."

**Show them how to run it:**

**Windows:**
```powershell
cd "C:\path\to\analytics-skills"
python explore.py
```

**Mac/Linux:**
```bash
cd ~/path/to/analytics-skills
python3 explore.py
```

**Say out loud:**
> "Your data dictionary tells you which tables and columns exist. Your
> worksheet tells you which section of the reference doc to fill in and
> how long to spend on each. The Gotchas section gets the most time —
> 15 minutes — because it's the only part a model can't write for you.
> That's where you'll find the thing this warehouse gets wrong."
>
> "If you're stuck for more than 8 minutes on the Gotchas section,
> raise your hand. I'd rather give you a nudge than have you spend the
> whole block searching."

**Hand out (if not already distributed):** the **build-worksheet.md**
printout

**Then tell them where to save their reference doc:**

> "Your finished doc goes in the `references` folder. Save it as the name
> of your domain — `attrition.md`, `compensation.md`, or `engagement.md`.
> That exact filename matters — the ablation script looks for it by name."

**Then:** circulate actively. This is your most important facilitator time.
Watch for:

- **Someone querying an empty decoy table and getting confused:** point them
  to the data dictionary's empty-table list at the bottom
- **Someone using `department` instead of `org_unit_v2`:** that's Trap 3 —
  the deprecated column is 54% populated and silently drops people. Let
  them discover it if they're close; nudge them if they're not
- **Someone stuck on Gotchas:** the worksheet has domain-specific hints
  (denominator choice for Attrition, currency mixing for Compensation,
  scale change for Engagement). Point them at the hint if they haven't
  found it themselves by minute 8

### At minute 40 (five minutes left)

**Say out loud:**
> "Five minutes. If you haven't finished your reference doc, that's fine —
> save what you have. The Gotchas section and the Quick Reference section
> are the parts that matter most. If those two are filled in, you're in
> good shape for the ablation."

### At minute 45, call time

**Say out loud:**
> "Time. Save your file. Give me one sentence: what's your Gotcha? What
> did the data get wrong that someone would have missed?"

Go around the room. **This is the single most important moment of the
workshop.** If someone found a real discrepancy with real numbers, that's
the success case. If someone says "I didn't find one," that's useful data
about the worksheet's guidance.

---

## Block 6: Ablation — 2:15 to 2:35

### What you do

**Say out loud:**
> "Now we find out if your reference doc actually helped. You're going to
> run the same question twice — once with no reference doc, once with
> yours loaded — and compare. This is the same discipline we used to
> measure the pack's own skills: 56% to 84%, but we didn't trust the
> number until we'd checked the caveats. You're about to see your own
> version of that."

**Walk them through it step by step:**

> "Make sure you're in the repo's root folder — not `evals`, not
> `workshop`, the root. Then run:"

**Windows:**
```powershell
cd "C:\path\to\analytics-skills"
cd workshop
python run_my_ablation.py
```

**Mac/Linux:**
```bash
cd ~/path/to/analytics-skills
cd workshop
python3 run_my_ablation.py
```

**Say out loud:**
> "It's going to do four things: check your eval file, find your reference
> doc, run baseline, then run with your doc. Takes about a minute. You'll
> see the results side by side."

**If someone gets an error:**

| Error message | What it means | Fix |
|---|---|---|
| "No eval found at ..." | They didn't save `my-eval.json` in the right place | Save it to `evals/my-eval.json` |
| "isn't valid JSON" | Syntax error — it says exactly where | Fix the line it points to (usually a trailing comma or wrong quotes) |
| "No reference doc found" | Their doc isn't named `attrition.md`, `compensation.md`, or `engagement.md` in `references/` | Rename or move it |
| "ANTHROPIC_API_KEY not set" | Their terminal session lost the key | Re-set it (see the arrival setup commands above) |
| "credit balance is too low" | Their API account has no credit | Give them one of your spare keys |
| "Cannot open file ... used by another process" | VS Code's DBCode extension has a lock on the database | Close the database tab in VS Code, or restart VS Code |

### Once everyone has results

**Say out loud:**
> "Look at your result. Now pull out your Validate worksheet — the
> prediction you wrote 45 minutes ago. For each assertion, you predicted
> PASS or FAIL for a plain agent. How did you do?"

**Go around the room:**
> "Tell me: which assertion did the baseline fail that your reference doc
> fixed? And — just as interesting — were you right about which one it
> would be?"

**This is the payoff.** Don't rush it. If someone's prediction was wrong,
that's the most interesting result in the room — it means they learned
something about where the model's blind spots actually are, as opposed to
where they assumed they'd be.

---

## Block 7: Operationalize — 2:35 to 2:50

### What you do

**This is a talk-through block, not a hands-on one.** No worksheet.

**Say out loud:**
> "You've written a reference doc and proved it helps. Now: how does it
> stay alive? A doc that's right today and wrong in three months is worse
> than no doc — it's a confident, authoritative source of wrong answers."

**Key points to cover:**

1. **The provenance footer** — every delivered answer carries its source,
   confidence, freshness, population, and open assumptions. You saw this
   in the demo. The footer is how a reader knows whether to trust a number
   without re-running the query themselves.

2. **Correction harvesting** — when a stakeholder corrects your output,
   that's not a complaint, it's a labeled training example. The correction
   goes into the reference doc as a new Gotcha, and into the eval set as
   a new assertion. The doc and the eval grow together. Skip this step and
   you've done traditional analytics with an AI typing for you.

3. **Freshness checking** — reference docs go stale. Schemas change.
   Columns get renamed. A doc that says "use `department`" when the real
   column is now `org_unit_v2` produces exactly the kind of silent error
   this whole workshop exists to prevent. Someone has to own each doc —
   that's what the `owner` field in the template is for.

**If the room looks engaged, ask:**
> "What's something that changed in your real warehouse in the last six
> months that would have broken a reference doc written before the change?"

If people have examples, let them talk — this is the bridge between the
workshop exercise and their actual work.

### What they do

Listen, ask questions, think about how this applies to their real data.

---

## Block 8: Contribute and Wrap — 2:50 to 3:00

### What you do

**Say out loud:**
> "Last thing. The reference doc you wrote today is a real contribution to
> an open-source repo. If you want to, you can open a pull request right
> now and your name goes in the README as a contributor. This is optional
> — no pressure — but the repo is real and it accepts contributions."

**For anyone who wants to do it:**

> "Open GitHub in your browser: github.com/RobStilson/analytics-skills.
> Click 'Fork' in the top right. Then push your reference doc to your fork
> and open a pull request."

**If people aren't familiar with git/PRs, simplify:**
> "If you're not comfortable with git, that's totally fine. Email me your
> `references/<domain>.md` file and I'll add it to the repo with your name
> credited."

### Closing — the last thing you say

> "Here's what you take home: a reference doc for a domain you actually
> work in, an eval that proves it does something, and a habit that matters
> more than either of those — checking the number instead of trusting it.
> The tools will change. The models will get better. The habit of verifying
> instead of eyeballing is what survives."

**Then:**
> "The repo is at github.com/RobStilson/analytics-skills. Everything from
> today — the skills, the warehouse, the eval runner, the worksheets — is
> open source and MIT licensed. Use it Monday."

---

## Quick-reference: every file participants touch today

Keep this list handy. When someone says "where do I save this?" you can
answer in one line.

| What | Where it lives | When they need it |
|---|---|---|
| Setup checker | `python check_setup.py` (repo root) | Arrival |
| Data dictionary | Printed handout (or `workshop/data-dictionary.html`) | Define + Build |
| Define worksheet | `workshop/define-worksheet.md` | Block 3 |
| Validate worksheet | `workshop/validate-worksheet.md` | Block 4 |
| Their eval JSON | Save to `evals/my-eval.json` | Block 4 (save at end) |
| Build worksheet | `workshop/build-worksheet.md` | Block 5 |
| SQL query template | `explore.py` in the repo root (they create this) | Block 5 |
| Their reference doc | Save to `references/attrition.md` or `compensation.md` or `engagement.md` | Block 5 (save at end) |
| Ablation runner | `cd workshop && python run_my_ablation.py` | Block 6 |

---

## Quick-reference: the Python query template

Write this on the whiteboard at the start of Block 5. Participants copy it
into a file called `explore.py` in the repo root and change the SQL each
time they want to try something.

```python
import duckdb
con = duckdb.connect("warehouse/people_analytics.duckdb", read_only=True)

result = con.execute("""
    SELECT * FROM fct_separation LIMIT 10
""").fetchall()

for row in result:
    print(row)

con.close()
```

**Run it:**

Windows: `python explore.py`
Mac/Linux: `python3 explore.py`

---

## Quick-reference: setting the API key

This will come up at least twice — at arrival and again if someone closes
and reopens their terminal.

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-the-key-here"
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-the-key-here"
```

This lasts only for the current terminal session. Closing the terminal
window loses it, and they'll need to set it again. That's expected and
fine — say so up front rather than letting people think something broke.

---

## Emergency procedures

### Someone's laptop won't cooperate at all

Pair them with a neighbor. Two people on one laptop is better than one
person stuck for 45 minutes. Adjust the domain assignments so the pair is
working the same domain.

### The wifi goes down

Everything except the ablation (Block 6) works offline. The warehouse is
local, the worksheets are local, the Python querying is local. Skip Block 6
and say: "Run this at home tonight and send me your result."

### You're running 15 minutes behind at the end of Build

Cut Operationalize to 5 minutes (the three key points only, no discussion
question) and skip the PR exercise in Contribute. Close with the closing
line — it works regardless of whether anyone opened a PR.

### Someone finds a bug in the workshop materials

**This is the best possible outcome.** Say so. They just did correction
harvesting live — the exact discipline you were about to teach in Block 7.
Write it down in front of the room and commit to fixing it in the repo.
