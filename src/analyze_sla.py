#!/usr/bin/env python3
"""Analyze simulated support tickets for SLA performance. Requires pandas, numpy, matplotlib."""
from pathlib import Path
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

PRIORITIES = {"Low", "Medium", "High", "Critical"}
STATUS = {"Resolved", "Open"}

def load_data(path):
    df = pd.read_csv(path, parse_dates=["created_at", "resolved_at"])
    return df

def validate_data(df):
    checks = []
    def add(name, passed, details):
        checks.append({"check": name, "passed": bool(passed), "details": str(details)})
    add("required columns present", set(["ticket_id","created_at","priority","team","status","sla_hours","resolution_hours"]).issubset(df.columns),
        "Required analytical columns exist")
    add("ticket IDs unique", df["ticket_id"].is_unique, f"duplicates={int(df['ticket_id'].duplicated().sum())}")
    add("priority values valid", df["priority"].isin(PRIORITIES).all(), f"invalid={int((~df['priority'].isin(PRIORITIES)).sum())}")
    add("status values valid", df["status"].isin(STATUS).all(), f"invalid={int((~df['status'].isin(STATUS)).sum())}")
    add("team not blank", df["team"].fillna("").astype(str).str.strip().ne("").all(),
        f"blank={int(df['team'].fillna('').astype(str).str.strip().eq('').sum())}")
    add("resolution duration non-negative", df.loc[df["status"].eq("Resolved"), "resolution_hours"].dropna().ge(0).all(),
        f"negative={int(df['resolution_hours'].lt(0).sum())}")
    add("resolved tickets have duration", df.loc[df["status"].eq("Resolved"), "resolution_hours"].notna().all(),
        f"missing={int(df.loc[df['status'].eq('Resolved'),'resolution_hours'].isna().sum())}")
    return pd.DataFrame(checks)

def analyze(df):
    df = df.copy()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["resolved_at"] = pd.to_datetime(df["resolved_at"], errors="coerce")
    # Exclude records failing critical analytical fields; retain QA report separately.
    valid = df[
        df["ticket_id"].notna()
        & df["priority"].isin(PRIORITIES)
        & df["status"].isin(STATUS)
        & df["team"].fillna("").astype(str).str.strip().ne("")
        & df["sla_hours"].gt(0)
        & ((df["status"] != "Resolved") | (df["resolution_hours"].notna() & df["resolution_hours"].ge(0)))
    ].copy()
    valid = valid.drop_duplicates("ticket_id", keep="first")
    resolved = valid[valid["status"].eq("Resolved")].copy()
    resolved["sla_breached"] = resolved["resolution_hours"] > resolved["sla_hours"]
    resolved["created_month"] = resolved["created_at"].dt.to_period("M").astype(str)
    total = len(valid)
    resolved_n = len(resolved)
    breached_n = int(resolved["sla_breached"].sum())
    kpis = pd.DataFrame([
        ("Total valid tickets", total, "Count after critical quality filters"),
        ("Resolved tickets", resolved_n, "Resolved status"),
        ("Open tickets", int(valid["status"].eq("Open").sum()), "Still open; excluded from resolution-time/SLA rate denominator"),
        ("SLA breaches", breached_n, "Resolved tickets with resolution_hours > sla_hours"),
        ("SLA breach rate (%)", round(100*breached_n/resolved_n,2) if resolved_n else 0, "Breaches / resolved tickets"),
        ("Median resolution time (hours)", round(float(resolved["resolution_hours"].median()),2) if resolved_n else 0, "Median among resolved tickets"),
        ("Mean resolution time (hours)", round(float(resolved["resolution_hours"].mean()),2) if resolved_n else 0, "Mean among resolved tickets"),
    ], columns=["kpi","value","definition"])
    by_priority = resolved.groupby("priority", as_index=False).agg(
        resolved_tickets=("ticket_id","count"),
        median_resolution_hours=("resolution_hours","median"),
        sla_breaches=("sla_breached","sum"),
        sla_hours=("sla_hours","median")
    )
    by_priority["sla_breach_rate_pct"] = (100*by_priority["sla_breaches"]/by_priority["resolved_tickets"]).round(2)
    by_team = resolved.groupby("team", as_index=False).agg(
        resolved_tickets=("ticket_id","count"),
        median_resolution_hours=("resolution_hours","median"),
        sla_breaches=("sla_breached","sum")
    )
    by_team["sla_breach_rate_pct"] = (100*by_team["sla_breaches"]/by_team["resolved_tickets"]).round(2)
    by_category = resolved.groupby("category", as_index=False).agg(
        resolved_tickets=("ticket_id","count"),
        median_resolution_hours=("resolution_hours","median"),
        sla_breaches=("sla_breached","sum")
    )
    by_category["sla_breach_rate_pct"] = (100*by_category["sla_breaches"]/by_category["resolved_tickets"]).round(2)
    monthly = resolved.groupby("created_month", as_index=False).agg(
        resolved_tickets=("ticket_id","count"),
        sla_breaches=("sla_breached","sum"),
        median_resolution_hours=("resolution_hours","median")
    )
    monthly["sla_breach_rate_pct"] = (100*monthly["sla_breaches"]/monthly["resolved_tickets"]).round(2)
    return valid, resolved, kpis, by_priority, by_team, by_category, monthly

def make_charts(by_priority, by_team, monthly, outdir):
    outdir = Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    if not by_priority.empty:
        ax=by_priority.set_index("priority")["sla_breach_rate_pct"].plot(kind="bar")
        ax.set_title("SLA breach rate by priority"); ax.set_ylabel("Breach rate (%)"); ax.set_xlabel("Priority")
        plt.tight_layout(); plt.savefig(outdir/"sla_breach_by_priority.png", dpi=150); plt.close()
    if not by_team.empty:
        ax=by_team.set_index("team")["sla_breach_rate_pct"].plot(kind="bar")
        ax.set_title("SLA breach rate by team"); ax.set_ylabel("Breach rate (%)"); ax.set_xlabel("Team")
        plt.xticks(rotation=20, ha="right"); plt.tight_layout(); plt.savefig(outdir/"sla_breach_by_team.png", dpi=150); plt.close()
    if not monthly.empty:
        ax=monthly.set_index("created_month")["sla_breach_rate_pct"].plot(kind="line", marker="o")
        ax.set_title("Monthly SLA breach rate"); ax.set_ylabel("Breach rate (%)"); ax.set_xlabel("Ticket creation month")
        plt.tight_layout(); plt.savefig(outdir/"monthly_sla_trend.png", dpi=150); plt.close()

def run(input_path, outdir):
    outdir=Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    df=load_data(input_path)
    qa=validate_data(df)
    valid, resolved, kpis, by_priority, by_team, by_category, monthly=analyze(df)
    qa.to_csv(outdir/"validation_checks.csv", index=False)
    kpis.to_csv(outdir/"kpis.csv", index=False)
    by_priority.to_csv(outdir/"sla_by_priority.csv", index=False)
    by_team.to_csv(outdir/"sla_by_team.csv", index=False)
    by_category.to_csv(outdir/"sla_by_category.csv", index=False)
    monthly.to_csv(outdir/"monthly_sla_trend.csv", index=False)
    make_charts(by_priority, by_team, monthly, outdir)
    summary = [
        "# Executive Summary — Operations SLA Analytics",
        "",
        "> Dataset: simulated support tickets created for this portfolio project. These are not real company records.",
        "",
        f"- Valid tickets analyzed: **{len(valid)}**",
        f"- Resolved tickets: **{len(resolved)}**",
        f"- SLA breaches: **{int(resolved['sla_breached'].sum())}**",
        f"- SLA breach rate: **{(100*resolved['sla_breached'].mean()):.2f}%**" if len(resolved) else "- SLA breach rate: **N/A**",
        f"- Median resolution time: **{resolved['resolution_hours'].median():.2f} hours**" if len(resolved) else "- Median resolution time: **N/A**",
        "",
        "## Recommended actions",
        "1. Review the priority and team breakdowns to target coaching or workflow changes where breach rates are highest.",
        "2. Track monthly breach rate and ticket volume together; a rate alone can be misleading when volumes are small.",
        "3. Triage high-priority tickets early and define escalation triggers before the SLA deadline.",
        "4. Improve ticket-data quality at intake: enforce unique IDs, valid priority/status values, nonblank team, and nonnegative resolution time.",
        "",
        "## Interpretation limits",
        "- Simulated data demonstrates method only; findings must not be presented as actual company performance.",
        "- Open tickets are excluded from resolution-time and SLA-breach denominators.",
        "- SLA breach is defined as resolution time strictly greater than the priority SLA threshold.",
        "- The analysis is descriptive and does not establish causal root causes.",
    ]
    (outdir/"executive_summary.md").write_text("\n".join(summary), encoding="utf-8")
    return qa, kpis

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input", default="data/simulated_support_tickets.csv")
    parser.add_argument("--outdir", default="results")
    args=parser.parse_args()
    qa, kpis=run(args.input, args.outdir)
    print(f"Analysis complete. QA checks: {int(qa['passed'].sum())}/{len(qa)} passed. Outputs: {args.outdir}")
