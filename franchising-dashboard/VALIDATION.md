# Development validation

Checks completed on 5 October 2026:

- Read the source thesis's theoretical framework and Appendices B–E, including the embedded sensitivity figures.
- Checked the structured Word equations rather than relying only on flattened equation text. In particular, Appendix D's stationary-point denominator is `2(vN−δ)`.
- Passed 12 model tests using Python 3.10 and NumPy 1.23.4 already available in the development environment.
- Compared analytical extrema with dense grids for 80 random parameter sets in each of the three models, covering 240 curves.
- Checked Python 3.10 syntax for the application and model, and shell syntax for the Mac launcher.

For the default parameters, the endogenous-overhead model has a maximum at `F=0.7460192936`, with `P₁=0.5834817180`. Its two endpoints are `P₁(0)=0.5` and `P₁(1)=0.5738057881`.

For the U-shaped example, δ is 0.50. Its interior turning point is a minimum, while the global maximum occurs at the fully franchised endpoint. The implementation explicitly compares endpoints and stationary points instead of clipping a minimum and labelling it a maximum.

## Execution limits

The development environment could not download Python packages from the package index. Streamlit and Plotly were therefore not installed, and the Streamlit interface has not been launched or visually verified. Five real Streamlit AppTest interaction tests are included, but were skipped because Streamlit was unavailable.

The full test command, after installing `requirements.txt`, is:

```bash
python -m unittest discover -s tests -v
```

A successful full verification should report **17 tests, no failures and no skips**. Model tests alone passed; this does not imply that interface tests passed.

The app has not been deployed. Community Cloud deployment is described in README.md. Requirements permit compatible package updates rather than claiming a pinned, fully tested dependency environment.
