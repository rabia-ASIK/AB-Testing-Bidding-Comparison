# A/B Test Report — Maximum Bidding vs Average Bidding

## Purchase Means
| group | mean_purchase |
|------:|--------------:|
| control | 550.894059 |
| test | 582.106097 |


## Assumption Checks (alpha=0.05)
- Shapiro p (control): 0.5891
- Shapiro p (test):    0.1541
- Levene p:            0.1083

## Hypothesis Test
- Test used: **Independent two-sample t-test (equal variances)**
- Statistic: -0.9416
- p-value: 0.3493
- Decision: **Fail to reject H0 (p ≥ 0.05) → no statistically significant difference**

## Advanced Analysis
- Cohen’s d: **0.2105** (Small effect)
- Post-hoc power: **0.1534** (Low)

## Recommendation
No statistically significant difference. Keep current approach. Consider longer test / larger sample and segment-based analysis.
