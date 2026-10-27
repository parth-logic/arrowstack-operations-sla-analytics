# Operations SLA Analytics — Arrowstack Task 2

## Project overview
Analyze support/operations tickets to understand ticket volume, resolution time, SLA breaches, and patterns by priority, team, category, and month.

**Important:** `data/simulated_support_tickets.csv` is synthetic, portfolio-demo data, not real company data. A few deliberate data-quality issues are included to demonstrate validation and filtering.

## Stakeholder and decision
**Stakeholder:** Support Operations Manager.  
**Decision supported:** Identify ticket segments that merit SLA-process review and prioritize improvements in triage, escalation, and data quality.

## KPIs
- **Total valid tickets:** rows remaining after critical quality filters and duplicate-ID removal.
- **Resolved tickets:** valid tickets whose status is `Resolved`.
- **SLA breach:** a resolved ticket with `resolution_hours > sla_hours`.
- **SLA breach rate:** breached resolved tickets / all resolved tickets × 100.
- **Median resolution time:** median hours among resolved tickets.
- **Open tickets:** tickets still open; excluded from resolution-time and breach-rate denominators.

Priority SLA thresholds in the simulated data: Critical 8h, High 24h, Medium 48h, Low 72h. These are project assumptions, not an external service standard.

## Files
- `data/simulated_support_tickets.csv` — input dataset.
- `src/analyze_sla.py` — reproducible analysis and chart generation.
- `results/` — KPI tables, segment analyses, validation evidence, charts and executive summary.
- `docs/requirements_and_method.md` — scope, assumptions, and method.
- `docs/presentation.md` — short demo/presentation outline.
- `tests/test_analysis.py` — automated checks.

## Run it
Python 3.10+ recommended.

```bash
pip install pandas numpy matplotlib
python src/analyze_sla.py --input data/simulated_support_tickets.csv --outdir results
python -m unittest discover -s tests -v
```

Run commands from the project root. Outputs are written to `results/`.

## Validation and quality
The analysis writes `results/validation_checks.csv`, which checks required columns, unique ticket IDs, allowed priorities/statuses, nonblank team, nonnegative resolution duration, and duration presence for resolved tickets. The report intentionally records input defects; the analysis filters critical invalid rows and removes duplicate IDs before KPI calculation. Review the QA output rather than assuming every raw row is clean.

## Interactive filters
The supplied outputs are CSV tables that can be opened in Excel. In Excel or Power BI, add slicers/filters for `priority`, `team`, `category`, `channel`, and `created_month`. The Python outputs provide pre-aggregated segment views.

## Limitations
- Synthetic data only; no real business conclusion should be inferred.
- Segment groups may have small counts; check `resolved_tickets` alongside rates.
- SLA thresholds are assumptions for this exercise.
- Descriptive segment differences do not prove causation.
- Open tickets are not counted as SLA breaches in this version.

## Next steps
Connect an approved real ticket export, confirm actual priority-specific SLA policies with the operations owner, add age-based SLA risk for open tickets, and publish a dashboard with interactive filters.
