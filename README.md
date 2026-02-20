# A/B Testing: Bidding Strategy Comparison

This project presents an end-to-end A/B testing analysis comparing **Maximum Bidding** and **Average Bidding** strategies using real campaign data.

## Business Problem
Facebook recently introduced **Average Bidding** as an alternative to the existing **Maximum Bidding** model.  
The objective is to evaluate whether the new bidding strategy leads to higher conversions.

The primary success metric is **Purchase**.

## Dataset
The dataset consists of two groups stored in separate Excel sheets:
- **Control Group** → Maximum Bidding
- **Test Group** → Average Bidding

### Features
- **Impression**: Number of ad impressions  
- **Click**: Number of ad clicks  
- **Purchase**: Number of purchases after clicking ads  
- **Earning**: Revenue generated from purchases  

## Methodology
1. Data loading and quality checks  
2. Exploratory data analysis (EDA)  
3. Hypothesis formulation (H0 / H1)  
4. Assumption checks:
   - Shapiro-Wilk test (normality)
   - Levene test (variance homogeneity)
5. Hypothesis testing:
   - Independent two-sample t-test
6. Business interpretation and recommendation

## Results
- Both groups satisfy normality and variance homogeneity assumptions
- Independent two-sample t-test was applied
- No statistically significant difference was found between bidding strategies at a 95% confidence level

## Conclusion
Based on the A/B test results, **Average Bidding does not provide a statistically significant improvement** over Maximum Bidding.  
It is recommended to continue with the current strategy and consider re-running the experiment with a larger sample size or longer duration.

## Technologies
- Python
- Pandas
- SciPy
- A/B Testing

