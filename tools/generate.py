"""Generate the fictional Northwind Home Services practice data.

Every customer, person, address and dollar figure here is invented.
Deterministic: same seed, same files. Run from the repo root with

    uv run python3 tools/generate.py

It writes practice/jobs/jobs.csv and practice/customers/customers.csv and then
prints the planted facts so they can be checked against the tutorial's answers.

Planted stories (a question across jobs.csv should reveal these):
  (a) Harbor Pointe Property Management sent the most jobs in 2026, well ahead
      of the next customer. Its September 2026 count is down.
  (b) Crew B's on-time rate dropped the most: about 94% January to June 2026,
      about 71% from July 2026 on. Crew A stays about 95%, Crew H about 90%.
  (c) Seaside Dental Group stops sending jobs after April 2026. No file says why.
  (d) August is the busiest month in both 2025 and 2026.
  (e) Crew B's ratings dip after July 2026.
  Small extras that match the weekly updates: Crew B misses exactly 4 arrival
  windows in the week of September 21, 2026; exactly 11 households have their
  first job in September 2026; Grace Okafor had a late Crew B visit in September.
"""
import csv
import datetime as dt
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "practice"
rng = random.Random(20260921)

START = dt.date(2025, 1, 1)
TODAY = dt.date(2026, 9, 25)

# Relative volume by month. August is the peak both years.
SEASON = {1: 0.85, 2: 0.80, 3: 0.95, 4: 1.05, 5: 1.08, 6: 1.10, 7: 1.15, 8: 1.40,
          9: 1.05, 10: 1.00, 11: 0.90, 12: 0.85}

NEIGHBORHOODS_A = ["West End", "Parkside", "Libbytown", "Stroudwater", "Rosemont", "Oakdale",
                   "South Portland", "Cape Elizabeth", "Scarborough", "Westbrook"]
NEIGHBORHOODS_B = ["East End", "Munjoy Hill", "Bayside", "Back Cove", "Deering Center",
                   "North Deering", "Woodfords Corner", "Riverton", "Old Port", "Falmouth"]

FIRST = ["Grace", "Liam", "Maya", "Noah", "Olivia", "Ethan", "Ava", "Lucas", "Sophie", "Mason",
         "Isla", "Caleb", "Nora", "Owen", "Ruby", "Eli", "Hazel", "Jonah", "Clara", "Theo",
         "Margaret", "Walter", "Dorothy", "Harold", "Evelyn", "Arthur", "Rose", "Frank", "Helen",
         "Raymond", "Priya", "Tomas", "Amara", "Kenji", "Leila", "Mateo", "Fatima", "Dmitri",
         "Ingrid", "Omar", "Beatrice", "Colin", "Delphine", "Emmett", "Fiona", "Gideon", "Harriet",
         "Ivan", "June", "Kofi", "Lorna", "Marcel", "Nadia", "Oscar", "Paloma", "Quinn", "Rhea",
         "Silas", "Tessa", "Ulrich", "Vera", "Wes", "Yara", "Zoe", "Annika", "Bram", "Celeste"]
LAST = ["Okafor", "Thibodeau", "Pelletier", "Gagnon", "Lavoie", "Cushing", "Brackett", "Dyer",
        "Sawyer", "Merrill", "Hodgkins", "Tibbetts", "Perkins", "Whitney", "Ames", "Coombs",
        "Nakamura", "Castellano", "Haddad", "Lindgren", "Moreau", "Osei", "Petrov", "Quintana",
        "Rasmussen", "Sorensen", "Tanaka", "Umar", "Vasquez", "Winslow", "Yilmaz", "Zielinski",
        "Abernathy", "Bouchard", "Chamberlain", "Desrosiers", "Eldridge", "Fournier", "Goodwin",
        "Hartley", "Ibarra", "Jacobsen", "Kincaid", "Lambert", "Macomber", "Nadeau", "Oberg",
        "Pomeroy", "Quimby", "Rousseau", "Stinson", "Tremblay", "Underhill", "Vaillancourt",
        "Wentworth", "Yeaton", "Ziegler", "Blanchard", "Carrigan", "Dufresne"]

NOTE_POOL = ["Key under the blue planter", "Friendly dog, keep the gate shut", "Prefers Tuesdays",
             "No scented products, allergies", "Gate code on file", "Call before arriving",
             "Park on the street, not the driveway", "Cat stays in the bedroom", "Text when 20 min out",
             "Skip the basement", "Leave invoice on the counter", "Elderly parent at home, knock loudly",
             "Second floor only", "Uses our vacuum, not theirs", "Grandkids visit Fridays, avoid"]

COMMERCIAL = [
    # name, kind, neighborhood, crew for cleaning, base jobs per month in 2025, note
    ("Harbor Pointe Property Management", "property manager", "East End", "B", 30,
     "40-unit building on the Eastern Prom, unit turnovers and common areas, monthly invoice"),
    ("Casco Bay Realty Partners", "property manager", "Old Port", "A", 9,
     "Six rental buildings downtown, bills to the office"),
    ("Longfellow Square Properties", "property manager", "West End", "B", 7,
     "Turnovers plus hallway cleans, contact is Dale"),
    ("Munjoy Hill Rentals", "property manager", "Munjoy Hill", "B", 5,
     "Short-term rentals, same-day turnovers on weekends"),
    ("Seaside Dental Group", "dental office", "South Portland", "A", 6,
     "After-hours only, alarm code on file"),
    ("Fore River Physical Therapy", "clinic", "Libbytown", "A", 4,
     "Evenings after 6, wipe equipment with their spray"),
    ("Brightwater Yoga Studio", "studio", "Bayside", "B", 3,
     "Floors only, no chemicals on the cork"),
    ("Pell and Grange Law Office", "office", "Old Port", "A", 3,
     "Weekly, Thursdays after 5"),
    ("Tidewater Coworking", "office", "Bayside", "B", 4,
     "Two floors, kitchen is the priority"),
    ("Stonegate Veterinary Clinic", "clinic", "Westbrook", "A", 3,
     "Saturday afternoons after close"),
]


def poisson(lam):
    if lam <= 0:
        return 0
    L = math.exp(-lam)
    k, p = 0, 1.0
    while p > L:
        k += 1
        p *= rng.random()
    return k - 1


def pick(pairs):
    x, acc = rng.random(), 0.0
    for v, p in pairs:
        acc += p
        if x <= acc:
            return v
    return pairs[-1][0]


def days_in_month(d):
    nxt = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return (nxt - d).days


def next_month(d):
    return (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)


def hhmm(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# ---------------------------------------------------------------- customers
customers = []
cid = 1000

for name, kind, hood, crew, base, note in COMMERCIAL:
    cid += 1
    customers.append({
        "customer_id": f"C-{cid}", "customer_name": name, "customer_type": "commercial",
        "neighborhood": hood, "first_job_date": None, "preferred_crew": crew, "notes": note,
        "_kind": kind, "_base": base, "_start": None, "_legacy": True,
    })

used = set()
households = []
while len(households) < 290:
    nm = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    if nm in used or nm.endswith("Okafor"):
        continue  # only one Okafor household, the one Sofia mentions
    used.add(nm)
    households.append(nm)
# Mrs. Okafor is a real customer in the files
households[0] = "Grace Okafor"

# 11 households have their first job in September 2026 (Jordan's number)
sept_new = set(rng.sample(range(1, 290), 11))

for i, nm in enumerate(households):
    cid += 1
    side = rng.random() < 0.5
    hood = rng.choice(NEIGHBORHOODS_A if side else NEIGHBORHOODS_B)
    crew = "A" if side else "B"
    if nm == "Grace Okafor":
        hood, crew = "East End", "B"
    if i in sept_new:
        start = dt.date(2026, 9, rng.randint(1, 25))
        legacy = False
        plan = pick([("monthly", 0.3), ("occasional", 0.7)])
    elif rng.random() < 0.55:
        start = dt.date(rng.randint(2021, 2024), rng.randint(1, 12), rng.randint(1, 28))
        legacy = True
        plan = pick([("biweekly", 0.1), ("monthly", 0.18), ("occasional", 0.72)])
    else:
        start = dt.date(2025, 2, 1) + dt.timedelta(days=rng.randint(0, 570))
        legacy = False
        plan = pick([("biweekly", 0.05), ("monthly", 0.1), ("occasional", 0.85)])
    if nm == "Grace Okafor":
        start, legacy, plan = dt.date(2022, 5, 9), True, "monthly"
    base = {"biweekly": 2.0, "monthly": 1.0, "occasional": 0.1}[plan]
    note = rng.choice(NOTE_POOL) if rng.random() < 0.4 else ""
    if nm == "Grace Okafor":
        note = "Likes the same two cleaners each visit, calls the office rather than texting"
    customers.append({
        "customer_id": f"C-{cid}", "customer_name": nm, "customer_type": "household",
        "neighborhood": hood, "first_job_date": start.isoformat(), "preferred_crew": crew,
        "notes": note, "_kind": plan, "_base": base, "_start": start, "_legacy": legacy,
    })

# ---------------------------------------------------------------- jobs
def crew_on_time_rate(crew, d):
    if crew == "A":
        return 0.95
    if crew == "H":
        return 0.90
    return 0.71 if d >= dt.date(2026, 7, 1) else 0.94


def service_for(c):
    if c["customer_type"] == "commercial":
        if c["customer_name"].startswith("Harbor Pointe"):
            return pick([("standard clean", 0.6), ("deep clean", 0.12), ("move-out clean", 0.13),
                         ("handyman", 0.15)])
        if c["_kind"] == "property manager":
            return pick([("standard clean", 0.6), ("move-out clean", 0.2), ("handyman", 0.15),
                         ("window wash", 0.05)])
        return pick([("standard clean", 0.82), ("window wash", 0.1), ("handyman", 0.08)])
    if c["_kind"] == "occasional":
        return pick([("standard clean", 0.2), ("deep clean", 0.3), ("move-out clean", 0.17),
                     ("handyman", 0.23), ("window wash", 0.1)])
    return pick([("standard clean", 0.72), ("deep clean", 0.1), ("handyman", 0.1),
                 ("window wash", 0.06), ("move-out clean", 0.02)])


def price_for(service, c):
    if service == "standard clean":
        if c["customer_type"] == "commercial":
            return rng.randrange(150, 205, 5)
        return rng.randrange(140, 225, 5)
    if service == "deep clean":
        return rng.randrange(280, 425, 5)
    if service == "move-out clean":
        return rng.randrange(350, 605, 5)
    if service == "handyman":
        hours = pick([(1, 0.3), (2, 0.4), (3, 0.2), (4, 0.1)])
        return 95 * hours
    return rng.randrange(160, 305, 5)


def rating_for(crew, d, on_time):
    if rng.random() < (0.85 if False else 0.0):
        return ""
    if on_time:
        table = [(5, 0.66), (4, 0.26), (3, 0.06), (2, 0.015), (1, 0.005)]
        if crew == "B" and d >= dt.date(2026, 7, 1):
            table = [(5, 0.5), (4, 0.34), (3, 0.12), (2, 0.03), (1, 0.01)]
    else:
        table = [(5, 0.18), (4, 0.3), (3, 0.3), (2, 0.16), (1, 0.06)]
    return pick(table)


def make_job(c, d):
    service = service_for(c)
    crew = "H" if service == "handyman" else c["preferred_crew"]
    if c["customer_type"] == "commercial" and c["_kind"] in ("dental office", "clinic", "office", "studio"):
        start_h = rng.choice([7, 17, 17, 18])
    else:
        start_h = rng.choice([8, 8, 8, 9, 10, 10, 12, 13, 14])
    start_min = start_h * 60
    on_time = rng.random() < crew_on_time_rate(crew, d)
    if on_time:
        arrived = start_min + int(rng.triangular(0, 110, 20))
    else:
        late_by = int(rng.triangular(10, 95, 30))
        if crew == "B" and d >= dt.date(2026, 7, 1):
            late_by = int(rng.triangular(15, 140, 45))
        arrived = start_min + 120 + late_by
    quoted = price_for(service, c)
    invoiced = quoted
    if service == "handyman" and rng.random() < 0.15:
        invoiced += 95
    if not on_time and rng.random() < 0.5:
        invoiced -= 45  # one free hour credit for a missed window
    leave_blank = 0.85 if c["customer_type"] == "commercial" else 0.45
    rating = "" if rng.random() < leave_blank else rating_for(crew, d, on_time)
    return {
        "job_id": None, "date": d.isoformat(), "customer_id": c["customer_id"],
        "customer_name": c["customer_name"], "customer_type": c["customer_type"],
        "neighborhood": c["neighborhood"], "service": service, "crew": crew,
        "scheduled_window_start": hhmm(start_min), "arrived_at": hhmm(arrived),
        "on_time": "yes" if on_time else "no", "quoted_usd": quoted, "invoiced_usd": invoiced,
        "rating": rating,
    }


def pick_day(month, lo=1, hi=None):
    hi = hi or days_in_month(month)
    d = month.replace(day=rng.randint(lo, hi))
    if d.weekday() == 6:
        d += dt.timedelta(days=1)
    elif d.weekday() == 5 and rng.random() < 0.6:
        d += dt.timedelta(days=2)
    if d.month != month.month:
        d = month.replace(day=hi) if hi else d
        while d.weekday() == 6:
            d -= dt.timedelta(days=1)
    return d


jobs = []
month = START
while month <= dt.date(2026, 9, 1):
    partial = month == dt.date(2026, 9, 1)
    hi = 25 if partial else days_in_month(month)
    scale = SEASON[month.month] * (hi / days_in_month(month))
    for c in customers:
        base = c["_base"]
        if c["customer_type"] == "commercial":
            nm = c["customer_name"]
            if nm.startswith("Harbor Pointe"):
                base = 42 if month.year == 2026 else 32
                if month == dt.date(2026, 9, 1):
                    base = 30  # job count is down (Marcus mentions it, nobody says why)
            if nm == "Seaside Dental Group" and month > dt.date(2026, 4, 1):
                continue
            # commercial accounts are steady, so less noise than a Poisson draw
            n = int(round(base * scale * rng.uniform(0.92, 1.08)))
            for _ in range(n):
                jobs.append(make_job(c, pick_day(month, 1, hi)))
            continue
        start = c["_start"]
        if c["_legacy"] or start < month:
            n = poisson(base * scale)
            if c["_kind"] == "biweekly":
                n = pick([(1, 0.1), (2, 0.75), (3, 0.15)])
            elif c["_kind"] == "monthly":
                n = pick([(0, 0.08), (1, 0.84), (2, 0.08)])
            if c["_kind"] in ("biweekly", "monthly") and rng.random() < max(0.0, (SEASON[month.month] - 1.0) * 0.8):
                n += 1  # summer extras: windows, porches, a deep clean before guests
            for _ in range(n):
                jobs.append(make_job(c, pick_day(month, 1, hi)))
        elif start.year == month.year and start.month == month.month:
            # first job on the day they joined, then the regular rate for the rest of the month
            jobs.append(make_job(c, start))
            rest = (hi - start.day) / days_in_month(month)
            for _ in range(poisson(base * SEASON[month.month] * rest)):
                jobs.append(make_job(c, pick_day(month, start.day, hi)))
    month = next_month(month)

jobs = [j for j in jobs if dt.date.fromisoformat(j["date"]) <= TODAY]

# Week of September 21: Crew B misses exactly 4 windows (Marcus's number)
week = [j for j in jobs if j["crew"] == "B" and "2026-09-21" <= j["date"] <= "2026-09-25"]
rng.shuffle(week)
# if Mrs. Okafor had a visit that week, it is one of the misses
week.sort(key=lambda j: 0 if j["customer_name"] == "Grace Okafor" else 1)
for i, j in enumerate(week):
    start = int(j["scheduled_window_start"][:2]) * 60 + int(j["scheduled_window_start"][3:])
    if i < 4:
        j["on_time"] = "no"
        j["arrived_at"] = hhmm(start + 120 + int(rng.triangular(20, 120, 50)))
        if j["customer_type"] == "household":
            j["rating"] = rng.choice([2, 3, 3])
        if j["customer_name"] == "Grace Okafor":
            j["rating"] = 2
            j["invoiced_usd"] = j["quoted_usd"] - 45
    else:
        j["on_time"] = "yes"
        j["arrived_at"] = hhmm(start + int(rng.triangular(0, 110, 20)))
        j["invoiced_usd"] = j["quoted_usd"] if j["invoiced_usd"] == j["quoted_usd"] - 45 else j["invoiced_usd"]

# Mrs. Okafor's September visit was late and she rated it a 2
okafor = [j for j in jobs if j["customer_name"] == "Grace Okafor" and j["date"].startswith("2026-09")]
if not okafor:
    c = next(c for c in customers if c["customer_name"] == "Grace Okafor")
    jobs.append(make_job(c, dt.date(2026, 9, 16)))
    okafor = [jobs[-1]]
j = okafor[-1]
if not ("2026-09-21" <= j["date"] <= "2026-09-25"):
    start = int(j["scheduled_window_start"][:2]) * 60
    j["on_time"], j["arrived_at"], j["rating"] = "no", hhmm(start + 120 + 85), 2
    j["invoiced_usd"] = j["quoted_usd"] - 45

jobs.sort(key=lambda j: (j["date"], j["scheduled_window_start"], j["customer_id"]))
for n, j in enumerate(jobs, start=1):
    j["job_id"] = f"NW-{n:05d}"

# first_job_date for commercial accounts and any household whose plan produced an earlier job
first_seen = {}
for j in jobs:
    first_seen.setdefault(j["customer_id"], j["date"])
for c in customers:
    if c["customer_type"] == "commercial":
        legacy = {"Harbor Pointe Property Management": "2023-03-01", "Casco Bay Realty Partners": "2022-09-12",
                  "Longfellow Square Properties": "2024-04-15", "Munjoy Hill Rentals": "2024-06-03",
                  "Seaside Dental Group": "2023-11-06", "Fore River Physical Therapy": "2024-01-22",
                  "Brightwater Yoga Studio": "2024-08-19", "Pell and Grange Law Office": "2022-02-07",
                  "Tidewater Coworking": "2024-10-14", "Stonegate Veterinary Clinic": "2023-07-10"}
        c["first_job_date"] = legacy[c["customer_name"]]
    elif not c["_legacy"]:
        c["first_job_date"] = first_seen.get(c["customer_id"], c["first_job_date"])
    if c["customer_id"] not in first_seen and c["customer_type"] == "household":
        # every customer has at least one job in the export
        d = dt.date.fromisoformat(c["first_job_date"])
        if d < START:
            d = dt.date(2025, rng.randint(1, 12), rng.randint(1, 28))
        jobs.append(make_job(c, d))
        first_seen[c["customer_id"]] = d.isoformat()

jobs.sort(key=lambda j: (j["date"], j["scheduled_window_start"], j["customer_id"]))
for n, j in enumerate(jobs, start=1):
    j["job_id"] = f"NW-{n:05d}"

# ---------------------------------------------------------------- write
JOB_FIELDS = ["job_id", "date", "customer_id", "customer_name", "customer_type", "neighborhood",
              "service", "crew", "scheduled_window_start", "arrived_at", "on_time", "quoted_usd",
              "invoiced_usd", "rating"]
CUST_FIELDS = ["customer_id", "customer_name", "customer_type", "neighborhood", "first_job_date",
               "preferred_crew", "notes"]

(ROOT / "jobs").mkdir(parents=True, exist_ok=True)
(ROOT / "customers").mkdir(parents=True, exist_ok=True)
with open(ROOT / "jobs" / "jobs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=JOB_FIELDS)
    w.writeheader()
    w.writerows(jobs)
with open(ROOT / "customers" / "customers.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CUST_FIELDS)
    w.writeheader()
    w.writerows([{k: c[k] for k in CUST_FIELDS} for c in customers])

# ---------------------------------------------------------------- verify
def rate(rows):
    return (sum(1 for r in rows if r["on_time"] == "yes") / len(rows)) if rows else float("nan")


def avg_rating(rows):
    vals = [int(r["rating"]) for r in rows if r["rating"] != ""]
    return sum(vals) / len(vals) if vals else float("nan")


print(f"jobs.csv rows: {len(jobs)}   customers.csv rows: {len(customers)}")
print(f"date range: {jobs[0]['date']} to {jobs[-1]['date']}")
print()
print("Top 5 customers by 2026 job count:")
by_cust = Counter(j["customer_name"] for j in jobs if j["date"].startswith("2026"))
for name, n in by_cust.most_common(5):
    print(f"  {n:4d}  {name}")
hp_sept = sum(1 for j in jobs if j["customer_name"].startswith("Harbor Pointe") and j["date"].startswith("2026-09"))
hp_aug = sum(1 for j in jobs if j["customer_name"].startswith("Harbor Pointe") and j["date"].startswith("2026-08"))
print(f"  Harbor Pointe Aug 2026: {hp_aug}, Sept 2026 (through the 25th): {hp_sept}")
print()
print("On-time rate by crew, Jan-Jun 2026 vs Jul-Sep 2026 (and 2025 for reference):")
for crew in "ABH":
    h1 = [j for j in jobs if j["crew"] == crew and "2026-01-01" <= j["date"] <= "2026-06-30"]
    h2 = [j for j in jobs if j["crew"] == crew and j["date"] >= "2026-07-01"]
    y25 = [j for j in jobs if j["crew"] == crew and j["date"] < "2026-01-01"]
    print(f"  Crew {crew}: 2025 {rate(y25):.1%} ({len(y25)})   H1 2026 {rate(h1):.1%} ({len(h1)})   "
          f"since July 2026 {rate(h2):.1%} ({len(h2)})   change {rate(h2) - rate(h1):+.1%}")
print()
print("Average rating by crew, Jan-Jun 2026 vs Jul-Sep 2026:")
for crew in "ABH":
    h1 = [j for j in jobs if j["crew"] == crew and "2026-01-01" <= j["date"] <= "2026-06-30"]
    h2 = [j for j in jobs if j["crew"] == crew and j["date"] >= "2026-07-01"]
    print(f"  Crew {crew}: H1 2026 {avg_rating(h1):.2f}   since July 2026 {avg_rating(h2):.2f}")
print()
seaside = [j["date"] for j in jobs if j["customer_name"] == "Seaside Dental Group"]
print(f"Seaside Dental Group: {len(seaside)} jobs, first {min(seaside)}, last {max(seaside)}")
print()
print("Busiest month each year:")
by_month = Counter(j["date"][:7] for j in jobs)
for yr in ("2025", "2026"):
    months = {m: n for m, n in by_month.items() if m.startswith(yr)}
    top = max(months, key=months.get)
    ranked = ", ".join(f"{m[5:]}={n}" for m, n in sorted(months.items()))
    print(f"  {yr}: {top} with {months[top]} jobs   ({ranked})")
print()
wk = [j for j in jobs if j["crew"] == "B" and "2026-09-21" <= j["date"] <= "2026-09-25"]
print(f"Crew B week of Sept 21: {len(wk)} jobs, {sum(1 for j in wk if j['on_time'] == 'no')} missed windows")
new_h = sum(1 for c in customers if c["customer_type"] == "household" and c["first_job_date"].startswith("2026-09"))
print(f"New household customers with a first job in September 2026: {new_h}")
ok = [j for j in jobs if j["customer_name"] == "Grace Okafor" and j["date"].startswith("2026-09")]
print("Grace Okafor September 2026: " + "; ".join(f"{j['date']} crew {j['crew']} on_time={j['on_time']} rating={j['rating']}" for j in ok))
print(f"Jobs per crew: " + ", ".join(f"{c}={n}" for c, n in sorted(Counter(j['crew'] for j in jobs).items())))
