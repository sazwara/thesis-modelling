# Franchising intensity and firm performance

Code supporting my MSc Business Economics thesis at the University of Amsterdam, examining the relationship between franchising intensity and financial performance among US fast-food franchisors.

The project combines empirical panel-data analysis with a theoretical model of franchising and profit. The empirical analysis compares linear and non-linear specifications, while the appendix explores how the theoretical model responds to changes in its parameters.

## Empirical analysis

The Stata workflow covers:

- Preparing financial variables and polynomial terms.
- Producing descriptive statistics.
- Comparing pooled OLS, random-effects, and fixed-effects models.
- Absorbing firm and year fixed effects using `reghdfe`.
- Clustering standard errors at the firm level.
- Checking robustness across alternative financial outcomes.
- Examining heterogeneity by firm size and firm cluster.
- Testing the quadratic relationship using the Lind–Mehlum U-test.
- Exporting regression tables in RTF format.

Return on assets is the main outcome. Alternative outcomes include profit margins, turnover measures, advertising intensity, leverage, and liquidity ratios.

## Where to start

Open `Master Thesis Franchising .do file.do`.

The numbered sections follow the empirical workflow from preparation through estimation and reporting:

- Sections 1–2: variable preparation and descriptive statistics.
- Sections 3–4: main model comparisons.
- Sections 5–7: robustness, heterogeneity, and U-shape tests.
- Section 8: extended tables.

## Interactive sensitivity explorer — in development

The Streamlit draft is intended to turn the thesis appendix’s sensitivity analysis into an interactive application.

Users would adjust model parameters and see the corresponding profit curves update. The prototype includes controls for operating costs, headquarters overhead, outlet count, franchisee effort and efficiency, effort costs, and a duplication penalty.

This component visualises the theoretical model; it does not re-estimate the empirical regressions when parameters change. The current draft requires preparation before it can run as a Streamlit application.

## Repository contents

| File | Purpose |
|---|---|
| `Master Thesis Franchising .do file.do` | Main empirical analysis |
| `Thesis_Dataset_Clustered2.xlsx` | Compiled input workbook |
| `dashboard` | Draft Python/Streamlit sensitivity explorer |

## Running the empirical analysis

1. Download the repository.
2. Open the main do-file in Stata.
3. Update the working-directory path near the beginning.
4. Confirm that the input workbook is in that directory.
5. Run the do-file from the beginning.

The script checks for and installs `reghdfe`, `ftools`, `estout`, and `utest` when needed. Package installation requires internet access.

Generated tables are saved in `tables/`. Figures are displayed in Stata.

## Interpretation

The empirical analysis uses observational firm data. Fixed effects and clustered standard errors do not, by themselves, establish a causal effect of franchising intensity.
