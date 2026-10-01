# Your first hour with Claude: practice files

These are the practice files for "Your first hour with Claude," a one-hour tutorial from the AdVenture Media membership. They describe a small company called Northwind Home Services, a residential cleaning and handyman business in Portland, Maine, run by an owner named Dana. In the tutorial, you play Dana. Every company, person, customer, address and dollar figure in these files is invented. Any resemblance to a real business or person is a coincidence.

## How to download

1. Click the green **Code** button at the top of this page.
2. Choose **Download ZIP**.
3. Unzip the file (double-click it on a Mac, right-click and Extract All on Windows).
4. Drag the `practice` folder to your Desktop. That is where the tutorial expects it.

If you only want the practice folder, download `practice.zip` from this page instead. It holds the same files.

## What is in the practice folder

| File | What it is |
|------|-----------|
| `weekly/leadership updates - week of Sept 21.md` | Six short weekly updates from Dana's leadership team, written the way busy people write them |
| `jobs/jobs.csv` | Every job from January 2025 through September 25, 2026 (about 3,700 rows): customer, service, crew, arrival window, arrival time, price, rating |
| `customers/customers.csv` | The 300 customers: who they are, where they are, which crew they prefer, and notes |
| `policies/Northwind service standards.md` | The two-page policy on arrival windows, credits, cancellations, what crews never do, and review follow-up |
| `emails/three emails Dana sent.md` | Three emails in Dana's voice, enough to teach Claude how she writes |
| `CLAUDE.md` | Who Dana is, her team and how each person likes to be reached, and how she likes answers. Claude reads it before every task in this folder |
| `VOICE.md` | How Dana writes, taken from her three emails. Claude uses it to draft in her voice |

The jobs file starts in January 2025. Some customers in `customers.csv` have a first job date before that, because they were already customers when the export begins.

## For the curious

`tools/generate.py` is the script that produced the two CSV files. It uses a fixed seed, so running it again gives the same files. It prints the facts that are planted in the data so they can be checked. Run it from this folder with `uv run python3 tools/generate.py`. The markdown files were written by hand.

## The tutorial

The tutorial itself lives in the AdVenture Media membership: https://adventuremedia.ai/dashboard#learn

## License

MIT. See `LICENSE`.
