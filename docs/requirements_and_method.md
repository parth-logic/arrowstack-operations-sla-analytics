# Requirements and Method

## Problem
Support leaders need visibility into ticket volume, resolution speed, SLA compliance, and segments that may need process review.

## Scope
Analyze a simulated ticket dataset. Report KPIs and breakdowns by priority, team, category, and ticket creation month. This is a descriptive analysis, not a causal investigation.

## Acceptance criteria
1. Reproducible script reads the supplied CSV and writes KPI/segment CSVs.
2. Data-quality checks cover key columns, IDs, priority/status values, team values, and resolution duration.
3. SLA breach definition and denominators are documented.
4. Charts show priority, team, and monthly trends.
5. Executive recommendations and limitations are recorded.
6. Automated tests verify core definitions and data handling.

## Data dictionary
- `ticket_id`: ticket identifier (synthetic).
- `created_at`, `resolved_at`: timestamps.
- `priority`: Low, Medium, High, Critical.
- `channel`: Email, Chat, Web, Phone.
- `team`: responsible support team.
- `category`: ticket issue category.
- `status`: Resolved or Open.
- `sla_hours`: assumed SLA target based on priority.
- `resolution_hours`: elapsed hours to resolution; blank for open tickets.

## Method
1. Load the CSV and parse timestamp fields.
2. Create a quality-check report on raw data.
3. Exclude records with invalid priority/status, blank team, missing required identifiers, invalid SLA target, or negative/missing resolved duration; deduplicate ticket IDs.
4. Calculate SLA breaches for resolved tickets where resolution duration is greater than the assigned SLA threshold.
5. Aggregate by priority, team, category, and creation month.
6. Export CSVs, charts, and an executive summary.

## Risk and privacy
All records are simulated. Do not replace them with customer-identifying data in a public repository. Use only authorized, sanitized datasets if adapting the project.
