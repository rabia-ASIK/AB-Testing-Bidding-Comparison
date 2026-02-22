"""
A/B Testing Case Study — Bidding Strategy Comparison (Maximum vs Average)

- Loads Control/Test sheets from ab_testing.xlsx
- Performs data quality checks + descriptive stats
- Checks assumptions: Shapiro (normality), Levene (variance homogeneity)
- Chooses the correct statistical test:
  - Independent t-test (equal variances) / Welch t-test (unequal variances)
  - Mann–Whitney U (if normality fails)
- Prints a clean console summary
- Writes a GitHub-friendly report.md

Advanced (portfolio upgrade):
- Effect size: Cohen's d
- Post-hoc power analysis (optional, requires statsmodels)

Author: Rabia
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from scipy.stats import shapiro, levene, ttest_ind, mannwhitneyu

# Optional dependency for power analysis
try:
    from statsmodels.stats.power import TTestIndPower
    STATS_MODELS_AVAILABLE = True
except Exception:
    STATS_MODELS_AVAILABLE = False


# =========================
# CONFIG
# =========================
FILE_PATH = "ab_testing.xlsx"
SHEET_CONTROL = "Control Group"
SHEET_TEST = "Test Group"
METRIC = "Purchase"
ALPHA = 0.05


# =========================
# TASK 1 — Load + EDA
# =========================
def load_data(file_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    control_df = pd.read_excel(file_path, sheet_name=SHEET_CONTROL)
    test_df = pd.read_excel(file_path, sheet_name=SHEET_TEST)
    return control_df, test_df


def validate_schema(control: pd.DataFrame, test: pd.DataFrame) -> None:
    if list(control.columns) != list(test.columns):
        raise ValueError("Control and Test sheets have different columns. Check Excel sheets.")
    if METRIC not in control.columns:
        raise ValueError(f"Metric column '{METRIC}' not found.")


def quick_profile(df: pd.DataFrame) -> Dict[str, object]:
    return {
        "shape": df.shape,
        "missing": df.isna().sum().to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
    }


def combine_groups(control: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    c = control.copy()
    t = test.copy()
    c["group"] = "control"
    t["group"] = "test"
    return pd.concat([c, t], ignore_index=True)


def purchase_means(df: pd.DataFrame) -> pd.Series:
    return df.groupby("group")[METRIC].mean()


# =========================
# TASK 3 — Assumptions
# =========================
@dataclass
class Assumptions:
    shapiro_control_p: float
    shapiro_test_p: float
    levene_p: float

    @property
    def normality_ok(self) -> bool:
        return self.shapiro_control_p > ALPHA and self.shapiro_test_p > ALPHA

    @property
    def equal_variances(self) -> bool:
        return self.levene_p > ALPHA


def check_assumptions(df: pd.DataFrame) -> Assumptions:
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


# =========================
# TASK 3 — Hypothesis Test
# =========================
@dataclass
class TestOutcome:
    test_name: str
    statistic: float
    p_value: float
    decision: str
    recommendation: str


def run_hypothesis_test(df: pd.DataFrame, a: Assumptions) -> TestOutcome:
    control_vals = df.loc[df["group"] == "control", METRIC]
    test_vals = df.loc[df["group"] == "test", METRIC]

    if a.normality_ok:
        if a.equal_variances:
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

    control_mean = float(control_vals.mean())
    test_mean = float(test_vals.mean())

    if reject:
        if test_mean > control_mean:
            recommendation = (
                "A statistically significant uplift exists for Average Bidding (test). "
                "Consider gradual rollout and validate by segments."
            )
        else:
            recommendation = (
                "Control outperforms significantly. Keep Maximum Bidding and investigate the cause."
            )
    else:
        recommendation = (
            "No statistically significant difference. Keep current approach. "
            "Consider longer test / larger sample and segment-based analysis."
        )

    return TestOutcome(
        test_name=test_name,
        statistic=stat,
        p_value=pval,
        decision=decision,
        recommendation=recommendation,
    )


# =========================
# ADVANCED — Cohen's d + Power
# =========================
def calculate_cohens_d(control_vals: pd.Series, test_vals: pd.Series) -> float:
    c = np.asarray(control_vals, dtype=float)
    t = np.asarray(test_vals, dtype=float)

    mean_c, mean_t = np.mean(c), np.mean(t)
    std_c, std_t = np.std(c, ddof=1), np.std(t, ddof=1)
    n_c, n_t = len(c), len(t)

    pooled = np.sqrt(((n_c - 1) * std_c**2 + (n_t - 1) * std_t**2) / (n_c + n_t - 2))
    if pooled == 0:
        return 0.0
    return (mean_t - mean_c) / pooled


def interpret_cohens_d(d: float) -> str:
    ad = abs(d)
    if ad < 0.2:
        return "Very small"
    if ad < 0.5:
        return "Small"
    if ad < 0.8:
        return "Medium"
    return "Large"


def calculate_posthoc_power(control_vals: pd.Series, test_vals: pd.Series) -> Tuple[float | None, str]:
    if not STATS_MODELS_AVAILABLE:
        return None, "statsmodels not installed → power analysis skipped"

    d = calculate_cohens_d(control_vals, test_vals)
    analysis = TTestIndPower()
    power = analysis.solve_power(
        effect_size=abs(d),
        nobs1=len(control_vals),
        alpha=ALPHA,
        ratio=len(test_vals) / len(control_vals),
        alternative="two-sided",
    )
    return float(power), "ok"


def interpret_power(power: float) -> str:
    if power < 0.5:
        return "Low"
    if power < 0.8:
        return "Moderate"
    return "Good"


# =========================
# REPORTING
# =========================
def print_console_summary(
    control_profile: Dict[str, object],
    test_profile: Dict[str, object],
    df: pd.DataFrame,
    means: pd.Series,
    a: Assumptions,
    outcome: TestOutcome,
    cohens_d: float,
    power: float | None,
    power_note: str,
) -> None:
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
    print(f"Shapiro p (control): {a.shapiro_control_p:.4f}")
    print(f"Shapiro p (test):    {a.shapiro_test_p:.4f}")
    print(f"Levene p:            {a.levene_p:.4f}")
    print(f"Normality OK?        {a.normality_ok}")
    print(f"Equal variances?     {a.equal_variances}")

    print("\n[Task 3 — Hypothesis Test]")
    print(f"Test used: {outcome.test_name}")
    print(f"Statistic: {outcome.statistic:.4f}")
    print(f"p-value:   {outcome.p_value:.4f}")
    print(f"Decision:  {outcome.decision}")

    print("\n[Advanced — Effect Size & Power]")
    print(f"Cohen's d: {cohens_d:.4f} ({interpret_cohens_d(cohens_d)} effect)")
    if power is None:
        print(f"Power:     N/A ({power_note})")
        print("Tip: Install statsmodels → pip install statsmodels")
    else:
        print(f"Power:     {power:.4f} ({interpret_power(power)})")

    print("\n[Task 4 — Recommendation]")
    print(outcome.recommendation)

    print("\n✅ report.md generated. Add it to your GitHub repository.")


def write_report_md(
    means: pd.Series,
    a: Assumptions,
    outcome: TestOutcome,
    cohens_d: float,
    power: float | None,
    power_note: str,
    out_path: str = "report.md",
) -> None:
    means_table = (
        "| group | mean_purchase |\n"
        "|------:|--------------:|\n"
        f"| control | {means.get('control', float('nan')):.6f} |\n"
        f"| test | {means.get('test', float('nan')):.6f} |\n"
    )

    power_line = (
        f"- Post-hoc power: **{power:.4f}** ({interpret_power(power)})"
        if power is not None
        else f"- Post-hoc power: **N/A** ({power_note}). Install statsmodels to enable."
    )

    md = f"""# A/B Test Report — Maximum Bidding vs Average Bidding

## Purchase Means
{means_table}

## Assumption Checks (alpha={ALPHA})
- Shapiro p (control): {a.shapiro_control_p:.4f}
- Shapiro p (test):    {a.shapiro_test_p:.4f}
- Levene p:            {a.levene_p:.4f}

## Hypothesis Test
- Test used: **{outcome.test_name}**
- Statistic: {outcome.statistic:.4f}
- p-value: {outcome.p_value:.4f}
- Decision: **{outcome.decision}**

## Advanced Analysis
- Cohen’s d: **{cohens_d:.4f}** ({interpret_cohens_d(cohens_d)} effect)
{power_line}

## Recommendation
{outcome.recommendation}
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)


# =========================
# MAIN
# =========================
def main() -> None:
    control, test = load_data(FILE_PATH)
    validate_schema(control, test)

    control_profile = quick_profile(control)
    test_profile = quick_profile(test)

    df = combine_groups(control, test)
    means = purchase_means(df)

    a = check_assumptions(df)
    outcome = run_hypothesis_test(df, a)

    control_vals = df.loc[df["group"] == "control", METRIC]
    test_vals = df.loc[df["group"] == "test", METRIC]

    cohens_d = calculate_cohens_d(control_vals, test_vals)
    power, power_note = calculate_posthoc_power(control_vals, test_vals)

    print_console_summary(
        control_profile, test_profile, df, means, a, outcome,
        cohens_d, power, power_note
    )
    write_report_md(means, a, outcome, cohens_d, power, power_note)

# =====================================================
    # VISUALIZATION FOR MEDIUM ARTICLE
    # =====================================================

    import matplotlib.pyplot as plt

    # Purchase değerlerini ayır
    control_purchase = df[df["group"] == "control"]["Purchase"]
    test_purchase = df[df["group"] == "test"]["Purchase"]

    # -------------------------
    # 1) Histogram: Distribution Comparison
    # -------------------------
    plt.figure(figsize=(8, 5))
    plt.hist(control_purchase, bins=15, alpha=0.6, label="Control (Max Bidding)")
    plt.hist(test_purchase, bins=15, alpha=0.6, label="Test (Average Bidding)")
    plt.title("Purchase Distribution: Control vs Test")
    plt.xlabel("Purchase")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # -------------------------
    # 2) Bar Chart: Mean Comparison
    # -------------------------
    means = df.groupby("group")["Purchase"].mean()

    plt.figure(figsize=(6, 4))
    means.plot(kind="bar")
    plt.title("Average Purchase by Bidding Strategy")
    plt.xlabel("Group")
    plt.ylabel("Average Purchase")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()
if __name__ == "__main__":
    main()

