"""
A/B Testing Case Study — Bidding Strategy Comparison (Maximum vs Average)

This script solves an end-to-end A/B testing case:
- Control group uses Maximum Bidding
- Test group uses Average Bidding
- Primary metric: Purchase

Project Tasks (mapped to code sections):
Task 1 — Data Preparation & Exploration
Task 2 — Hypothesis Definition
Task 3 — Assumption Checks + Statistical Testing
Task 4 — Interpretation + Business Recommendation

Outputs:
- Clean console summary
- report.md (GitHub-friendly report)

Author: Rabia
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import pandas as pd
from scipy.stats import shapiro, levene, ttest_ind, mannwhitneyu


# =========================
# CONFIG
# =========================
FILE_PATH = "ab_testing.xlsx"
SHEET_CONTROL = "Control Group"
SHEET_TEST = "Test Group"
METRIC = "Purchase"
ALPHA = 0.05


# =========================
# TASK 1 — Data Preparation & Exploration
# =========================
def load_data(file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load control and test group data from Excel sheets."""
    control_df = pd.read_excel(file_path, sheet_name=SHEET_CONTROL)
    test_df = pd.read_excel(file_path, sheet_name=SHEET_TEST)
    return control_df, test_df


def validate_schema(control: pd.DataFrame, test: pd.DataFrame) -> None:
    """Ensure both groups have the same schema and the metric exists."""
    if list(control.columns) != list(test.columns):
        raise ValueError(
            "Control and Test sheets have different columns. "
            "Please verify the Excel sheets."
        )
    if METRIC not in control.columns:
        raise ValueError(f"Metric column '{METRIC}' not found in the dataset.")


def quick_profile(df: pd.DataFrame) -> Dict[str, object]:
    """Lightweight EDA summary for reporting (shape, missing, dtypes, descriptives)."""
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "missing": df.isna().sum().to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "describe": df.describe().T,
    }


def combine_groups(control: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    """Add group labels and concatenate into one dataframe."""
    c = control.copy()
    t = test.copy()
    c["group"] = "control"
    t["group"] = "test"
    return pd.concat([c, t], ignore_index=True)


def purchase_means(df: pd.DataFrame) -> pd.Series:
    """Compute mean Purchase by group."""
    return df.groupby("group")[METRIC].mean()


# =========================
# TASK 3 — Assumptions + Test Selection
# =========================
@dataclass
class Assumptions:
    shapiro_control_p: float
    shapiro_test_p: float
    levene_p: float

    @property
    def normality_ok(self) -> bool:
        return (self.shapiro_control_p > ALPHA) and (self.shapiro_test_p > ALPHA)

    @property
    def equal_variances(self) -> bool:
        return self.levene_p > ALPHA


def check_assumptions(df: pd.DataFrame) -> Assumptions:
    """Shapiro-Wilk normality test (per group) + Levene variance homogeneity."""
    control_vals = df.loc[df["group"] == "control", METRIC]
    test_vals = df.loc[df["group"] == "test", METRIC]

    sh_c = shapiro(control_vals)
    sh_t = shapiro(test_vals)
    lev = levene(control_vals, test_vals)

    return Assumptions(
        shapiro_control_p=float(sh_c.pvalue),
        shapiro_test_p=float(sh_t.pvalue),
        levene_p=float(lev.pvalue),
    )


@dataclass
class TestOutcome:
    test_name: str
    statistic: float
    p_value: float
    decision: str
    recommendation: str


def run_hypothesis_test(df: pd.DataFrame, assumptions: Assumptions) -> TestOutcome:
    """
    TASK 2 + TASK 3
    Hypotheses:
      H0: mean(Purchase_control) = mean(Purchase_test)
      H1: mean(Purchase_control) != mean(Purchase_test)

    Select test based on assumptions:
      - Independent two-sample t-test if normality OK and variances equal
      - Welch t-test if normality OK and variances unequal
      - Mann–Whitney U if normality fails
    """
    control_vals = df.loc[df["group"] == "control", METRIC]
    test_vals = df.loc[df["group"] == "test", METRIC]

    if assumptions.normality_ok:
        if assumptions.equal_variances:
            res = ttest_ind(control_vals, test_vals, equal_var=True)
            test_name = "Independent two-sample t-test (equal variances)"
        else:
            res = ttest_ind(control_vals, test_vals, equal_var=False)
            test_name = "Welch t-test (unequal variances)"
        stat = float(res.statistic)
        pval = float(res.pvalue)
    else:
        res = mannwhitneyu(control_vals, test_vals, alternative="two-sided")
        test_name = "Mann–Whitney U test (non-parametric)"
        stat = float(res.statistic)
        pval = float(res.pvalue)

    reject = pval < ALPHA
    if reject:
        decision = f"Reject H0 (p < {ALPHA}) → statistically significant difference"
    else:
        decision = f"Fail to reject H0 (p ≥ {ALPHA}) → no statistically significant difference"

    # TASK 4 — Business recommendation
    control_mean = float(control_vals.mean())
    test_mean = float(test_vals.mean())

    if reject:
        if test_mean > control_mean:
            recommendation = (
                "A statistically significant improvement was detected in the Test group. "
                "Consider gradually rolling out Average Bidding, and validate the uplift across key segments "
                "(e.g., device, geography, new vs returning users)."
            )
        else:
            recommendation = (
                "A statistically significant improvement was detected in the Control group. "
                "Continue with Maximum Bidding and investigate why Average Bidding underperformed."
            )
    else:
        recommendation = (
            "No statistically significant difference was detected between bidding strategies. "
            "Maintain the current approach. To strengthen confidence, rerun the experiment with a larger sample "
            "and/or longer duration, and perform segment-level analysis."
        )

    return TestOutcome(
        test_name=test_name,
        statistic=stat,
        p_value=pval,
        decision=decision,
        recommendation=recommendation,
    )


# =========================
# REPORTING (Console + Markdown)
# =========================
def print_console_summary(
    control_profile: Dict[str, object],
    test_profile: Dict[str, object],
    df: pd.DataFrame,
    means: pd.Series,
    assumptions: Assumptions,
    outcome: TestOutcome,
) -> None:
    """Recruiter-friendly console summary."""
    print("\n" + "=" * 72)
    print("A/B TEST — CONSOLE SUMMARY")
    print("=" * 72)

    print("\n[Task 1 — Data Quality]")
    print(f"Control shape: {control_profile['shape']} | Test shape: {test_profile['shape']}")
    print(f"Missing values (control): {control_profile['missing']}")
    print(f"Missing values (test):    {test_profile['missing']}")
    print("Group counts:")
    print(df["group"].value_counts())

    print("\n[Task 2 — Purchase Means]")
    print(means)

    print("\n[Task 3 — Assumption Checks]")
    print(f"Shapiro p (control): {assumptions.shapiro_control_p:.4f}")
    print(f"Shapiro p (test):    {assumptions.shapiro_test_p:.4f}")
    print(f"Levene p:            {assumptions.levene_p:.4f}")
    print(f"Normality OK?        {assumptions.normality_ok}")
    print(f"Equal variances?     {assumptions.equal_variances}")

    print("\n[Task 3 — Hypothesis Test]")
    print(f"Test used: {outcome.test_name}")
    print(f"Statistic: {outcome.statistic:.4f}")
    print(f"p-value:   {outcome.p_value:.4f}")
    print(f"Decision:  {outcome.decision}")

    print("\n[Task 4 — Recommendation]")
    print(outcome.recommendation)

    print("\n✅ report.md generated. Add it to your GitHub repository.")


def write_report_md(
    control_profile: Dict[str, object],
    test_profile: Dict[str, object],
    means: pd.Series,
    assumptions: Assumptions,
    outcome: TestOutcome,
    out_path: str = "report.md",
) -> None:
    """Write a clean Markdown report for GitHub."""
    means_md = means.to_frame("mean").to_markdown()

    h0 = "H0: mean(Purchase_control) = mean(Purchase_test)"
    h1 = "H1: mean(Purchase_control) != mean(Purchase_test)"

    md = f"""# A/B Test Report — Maximum Bidding vs Average Bidding

## Business Problem
Facebook introduced **Average Bidding** as an alternative to **Maximum Bidding**.  
This project evaluates whether Average Bidding improves **{METRIC}** for an e-commerce A/B test.

## Project Scope & Tasks
**Task 1 — Data Preparation & Exploration**
- Loaded control/test data from Excel, validated schema, checked missing values and descriptive stats.

**Task 2 — Hypothesis Definition**
- {h0}  
- {h1}

**Task 3 — Assumptions & Statistical Testing (alpha={ALPHA})**
- Shapiro–Wilk normality test per group
- Levene variance homogeneity test
- Test selection based on assumptions (t-test / Welch / Mann–Whitney)

**Task 4 — Interpretation & Recommendation**
- Business-friendly interpretation and actionable recommendation.

## Data Quality
- Control shape: {control_profile['shape']}
- Test shape: {test_profile['shape']}
- Missing (control): {control_profile['missing']}
- Missing (test): {test_profile['missing']}

## Purchase Means
{means_md}

## Assumption Checks
- Shapiro p (control): {assumptions.shapiro_control_p:.4f}
- Shapiro p (test):    {assumptions.shapiro_test_p:.4f}
- Levene p-value:      {assumptions.levene_p:.4f}

Derived:
- Normality OK?    {assumptions.normality_ok}
- Equal variances? {assumptions.equal_variances}

## Hypothesis Test
- Test used: **{outcome.test_name}**
- Statistic: {outcome.statistic:.4f}
- p-value: {outcome.p_value:.4f}
- Decision: **{outcome.decision}**

## Recommendation
{outcome.recommendation}
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)


# =========================
# ENTRY POINT
# =========================
def main() -> None:
    pd.set_option("display.max_columns", None)
    pd.set_option("display.expand_frame_repr", False)

    # Task 1 — Load + Validate + Profile
    control, test = load_data(FILE_PATH)
    validate_schema(control, test)
    control_profile = quick_profile(control)
    test_profile = quick_profile(test)

    # Task 1 — Combine groups
    df = combine_groups(control, test)

    # Task 2 — Means
    means = purchase_means(df)

    # Task 3 — Assumptions + Test
    assumptions = check_assumptions(df)
    outcome = run_hypothesis_test(df, assumptions)

    # Reporting
    print_console_summary(control_profile, test_profile, df, means, assumptions, outcome)
    write_report_md(control_profile, test_profile, means, assumptions, outcome, out_path="report.md")


if __name__ == "__main__":
    main()