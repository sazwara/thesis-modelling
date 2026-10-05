# Franchising intensity and firm performance

Code supporting my MSc Business Economics thesis at the University of Amsterdam, examining the relationship between franchising intensity and financial performance among US fast-food franchisors.

The project combines empirical panel-data analysis in Stata with theoretical modelling and an interactive sensitivity explorer in Python.

**[Open the interactive dashboard](https://thesis-modelling-sensitivity-analysis.streamlit.app/)**

## Interactive sensitivity explorer

The Streamlit dashboard turns the thesis appendix’s sensitivity analysis into an interactive application. Users can adjust model assumptions and inspect how the relationship between franchising intensity and performance changes.

It implements three models:

| Model | Main assumption |
|---|---|
| Constant overhead | Company-operated outlets face a constant operating cost |
| Endogenous overhead | Operating costs depend on franchising intensity and outlet scale |
| Overhead and duplication | Maintaining company-operated and franchised structures incurs an additional duplication cost |

The dashboard includes:

- Controls for potential profit, operating costs, outlet scale, franchisee effort, effort effectiveness, and duplication costs.
- Interactive performance curves with best-performing franchising shares marked.
- A saved comparison scenario for inspecting parameter changes.
- Comparisons across multiple values of a selected parameter.
- An optional graph displaying all three models together.
- Downloads of curve data and parameter settings.
- Explanations of the equations, units, and assumptions.

The equations follow the thesis’s theoretical framework. Preset parameter values are illustrative. Performance is expressed in normalised units, and the application does not re-estimate the empirical regressions or forecast a particular firm.

## Empirical analysis

The Stata workflow covers:

- Preparing financial variables and polynomial terms.
- Producing descriptive statistics.
- Comparing pooled OLS, random-effects, and fixed-effects models.
- Absorbing firm and year fixed effects using `reghdfe`.
- Clustering standard errors at the firm level.
- Checking robustness across alternative financial outcomes.
- Examining heterogeneity by firm size and firm cluster.
- Testing quadratic relationships using the Lind–Mehlum U-test.
- Exporting regression tables in RTF format.

Return on assets is the main outcome.

## Where to start

For an interactive introduction, open the dashboard linked above.

For the Python implementation, inspect:

- [`franchising-dashboard/model.py`](franchising-dashboard/model.py): model equations, parameter validation, and analytical maxima and minima.
- [`franchising-dashboard/app.py`](franchising-dashboard/app.py): controls, graphs, comparisons, and downloads.

For the empirical analysis, open `Master Thesis Franchising .do file.do`. Its numbered sections follow the workflow from preparation through model comparison, robustness checks, heterogeneity analysis, and reporting.

## Repository contents

| File or folder | Purpose |
|---|---|
| `Master Thesis Franchising .do file.do` | Main Stata analysis |
| `Thesis_Dataset_Clustered2.xlsx` | Compiled empirical input workbook |
| `franchising-dashboard/` | Streamlit application, model functions, tests, and setup instructions |
| `dashboard` | Original exploratory draft |

## Running the dashboard locally

From the repository folder:

```bash
cd franchising-dashboard
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
