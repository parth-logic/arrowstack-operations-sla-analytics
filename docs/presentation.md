# Demo / Presentation Outline — Operations SLA Analytics

## Slide 1 — Business question
How can a support operations manager identify ticket segments with slower resolution and higher SLA breach rates?

## Slide 2 — Dataset and assumptions
- 240 simulated support tickets.
- Priority-based SLA targets are assumptions: Critical 8h, High 24h, Medium 48h, Low 72h.
- Some deliberate quality defects are included for validation demonstration.

## Slide 3 — KPI definitions
Ticket volume, resolved/open counts, breach count/rate, median and mean resolution time.

## Slide 4 — Analysis
Use `results/sla_breach_by_priority.png`, `results/sla_breach_by_team.png`, and `results/monthly_sla_trend.png`.
Compare rates alongside resolved-ticket counts to avoid over-interpreting small segments.

## Slide 5 — Recommendations
- Review high-breach priority/team segments.
- Add escalation triggers for urgent tickets.
- Monitor monthly rate and volume together.
- Enforce data validation at ticket intake.

## Slide 6 — Limitations and next steps
Synthetic data only; thresholds are assumptions; descriptive patterns do not prove root causes. Validate against approved operational data and confirmed SLA policy before production use.
