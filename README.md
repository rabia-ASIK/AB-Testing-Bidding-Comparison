
# A/B Testing: Maximum Bidding vs Average Bidding
An end-to-end A/B testing case study with statistical rigor and business-focused insights.
## 📌 Project Overview

This project presents an end-to-end **A/B testing analysis** comparing two Facebook ad bidding strategies:
**Maximum Bidding** (control group) and **Average Bidding** (test group).

The objective is to evaluate whether the newly introduced **Average Bidding** strategy leads to a **statistically and practically significant improvement** in **Purchase** conversions.

The project is designed to reflect a **real-world data science workflow**, including data validation, statistical assumptions, hypothesis testing, effect size analysis, and business-oriented recommendations.

---

## 🧠 Business Problem

Facebook recently introduced **Average Bidding** as an alternative to the existing **Maximum Bidding** strategy.

A client company (*bombabomba.com*) conducted a **1-month A/B experiment** to understand whether switching to Average Bidding improves conversion performance.

The **primary success metric** is **Purchase**, representing completed purchases after ad interactions.

---

## 📊 Dataset

* **Source:** `ab_testing.xlsx`
* **Sheets:**

  * Control Group → Maximum Bidding
  * Test Group → Average Bidding
* **Observations:** 40 users per group

### Features

| Feature    | Description                      |
| ---------- | -------------------------------- |
| Impression | Number of ad impressions         |
| Click      | Number of ad clicks              |
| Purchase   | Number of completed purchases    |
| Earning    | Revenue generated from purchases |

---

## 🧪 Methodology

The analysis follows a structured and industry-standard A/B testing pipeline:

1. **Data Quality Validation**

   * Shape consistency
   * Missing value checks
   * Data type verification

2. **Exploratory Analysis**

   * Group-wise Purchase averages
   * Distributional comparison (visualized during analysis)

3. **Statistical Assumption Checks**

   * **Shapiro–Wilk Test** for normality
   * **Levene Test** for variance homogeneity

4. **Hypothesis Testing**

   * Independent two-sample t-test
   * Automatic fallback to Welch t-test or Mann–Whitney U if assumptions fail

5. **Advanced Statistical Evaluation**

   * Effect size estimation (Cohen’s d)
   * Post-hoc power analysis

6. **Business-Oriented Interpretation**

   * Actionable recommendations aligned with decision-making needs

---

## 📐 Hypotheses

* **H0 (Null Hypothesis):**
  The average Purchase values of the control and test groups are equal.

* **H1 (Alternative Hypothesis):**
  The average Purchase values of the control and test groups are different.

---

## 📈 Key Results (Purchase Metric)

* **Control Group Mean:** 550.89

* **Test Group Mean:** 582.11

* **p-value:** 0.3493 → *Not statistically significant*

* **Effect Size (Cohen’s d):** 0.21 → *Small practical effect*

* **Statistical Power:** 0.15 → *Low power*

---

## 📊 Interpretation of Visual Analysis (Summary)

Although graphical outputs are generated during analysis, the key insights are summarized below:

* **Purchase distributions** of both groups show substantial overlap, indicating similar user behavior.
* The **test group exhibits a slightly higher average Purchase**, but this difference is not strong enough to be statistically or practically meaningful.
* No visible separation in distributions suggests the observed difference is likely due to random variation rather than a true bidding effect.

---

## ✅ Conclusion

The A/B test results indicate **no statistically significant difference** between **Maximum Bidding** and **Average Bidding** strategies.

While the test group demonstrates a marginally higher Purchase average, the **small effect size** and **low statistical power** suggest insufficient evidence to justify a strategy change.

---

## 💡 Business Recommendation

* Continue using the **current Maximum Bidding strategy**.
* Re-run the experiment with:

  * A **larger sample size**
  * A **longer test duration**
* Perform **segment-level analysis** (e.g., device type, user category, traffic source) to uncover hidden effects.

These steps would improve decision confidence before committing to a bidding strategy transition.

---

## 🛠️ How to Run the Project

### 1) Clone the repository

```bash
git clone https://github.com/rabia-ASIK/AB-Testing-Bidding-Comparison.git
cd AB-Testing-Bidding-Comparison
```

### 2) Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Run the analysis

```bash
python ab_testing_analysis.py
```

Running the script will automatically:

* Perform the full A/B testing pipeline
* Print a structured console summary
* Generate a detailed **report.md** file with results and interpretations

---

## 📂 Project Structure

```
AB-Testing-Bidding-Comparison/
│
├── ab_testing_analysis.py   # Main analysis script
├── ab_testing.xlsx          # Dataset
├── report.md                # Auto-generated analysis report
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
└── .gitignore
```

---

## 🚀 Why This Project Matters

This project demonstrates:

* Practical application of statistical testing
* Correct assumption validation
* Business-aware interpretation of results
* Reproducible and production-ready Python workflow

It reflects how **data science decisions are made in real-world experimentation environments**, not just textbook scenarios.
This project emphasizes decision-making under uncertainty, a common challenge in real-world experimentation
