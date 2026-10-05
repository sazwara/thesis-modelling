# Franchising sensitivity explorer

An interactive Streamlit application for the theoretical models in Tahtia Sazwara's MSc Business Economics thesis at the University of Amsterdam. Visitors adjust model assumptions and inspect how franchising intensity affects performance.

The app implements three functions: constant company overhead, endogenous company overhead, and endogenous overhead with a duplication penalty. It compares current inputs with a saved scenario, finds global maxima and minima, and exports curve data. No firm dataset is needed.

## Start without installing anything

This is the simplest way to obtain a shareable website:

1. Unzip the supplied project folder.
2. Open your `sazwara/thesis-modelling` repository on GitHub.
3. Select **Add file → Upload files**. Drag the entire `franchising-dashboard` folder into the upload area. Check that GitHub shows `franchising-dashboard/app.py` and `franchising-dashboard/model.py`, then commit the upload. Do not upload a ZIP in place of the extracted files.
4. Open [Streamlit Community Cloud](https://share.streamlit.io/) and sign in with GitHub.
5. Choose **Create app**, then **Yup, I have an app**.
6. Select repository `sazwara/thesis-modelling`, your default branch (normally `main`), and main file path **`franchising-dashboard/app.py`**.
7. In advanced settings select Python **3.12**, then deploy.
8. Wait for installation to finish. The app will open at a public `streamlit.app` address. Add that address to your repository README and CV.

Streamlit discovers `requirements.txt` next to the app entrypoint. Keep `app.py`, `model.py` and `requirements.txt` together. The `.streamlit/config.toml` file controls appearance; for a nested app in this existing repository, move that configuration folder to the repository root if you want Community Cloud to apply it. The app runs correctly without the custom theme.

A GitHub repository stores the code. Community Cloud actually runs it. Uploading Python files alone does not create a running website.

## Run on a Mac

1. Unzip the folder somewhere convenient, such as Downloads.
2. Open Terminal using Spotlight: press Command+Space, type `Terminal`, press Return.
3. Type `cd `, including the space. Drag the extracted `franchising-dashboard` folder from Finder into Terminal and press Return. This puts Terminal in the right folder without typing its full path.
4. Paste this command and press Return:

   ```bash
   zsh START_HERE.command
   ```

5. Wait for packages to install, then open **http://localhost:8501** in a browser.
6. Leave Terminal open while using the app. Press **Control+C** in Terminal to stop it. To restart, run the same launcher command again.

The launcher creates an isolated `.venv` inside the folder and installs the project's dependencies. The first run requires internet access and Python 3.10 or later; Python 3.12 is recommended. If Python is missing, install it from [python.org](https://www.python.org/downloads/macos/).

You can also run the commands individually:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If port 8501 is already occupied:

```bash
.venv/bin/python -m streamlit run app.py --server.port 8502
```

Then use the address printed in Terminal.

## Using the explorer

- Choose an example to start from an increasing line, decreasing line, inverted U or U shape.
- Select a model and adjust its active controls. Grey controls do not enter that model.
- The main graph compares the current inputs with a saved set of inputs evaluated in the same model. Dots mark global maxima.
- **Save inputs as comparison** freezes the current parameters so you can change one assumption and compare the curves.
- **Reset example** restores the selected example and its comparison inputs.
- Inspect any chosen franchised share using the percentage control below the graph.
- Open **Compare parameter values** to enter two to six values for one parameter. For the duplication model, a button compares δ = 0, vN and 2vN where these values are feasible.
- Download curve data or the current parameter settings. Session inputs reset when a new browser session starts; downloaded JSON is a record, not an import feature.

## Equations and source mapping

Define `q = p(a)π − c(a)`, with `p(a) = 1 − exp(−θa)` and `c(a) = a²/2`.

| Component | Equation | Thesis source |
|---|---|---|
| Constant overhead | `P₀(F) = (1−F)(π−Cₒₚ) + Fq` | Theoretical framework, equation 1 |
| Endogenous overhead | `Cₒₚ(F) = H + v(1−F)N` | Theoretical framework; Appendix B |
| Second performance model | `P₁(F) = (1−F)[π−H−v(1−F)N] + Fq` | Equation 2; Appendix B |
| Duplication penalty | `D(F) = δF(1−F)` | Equation 3; Appendix D |
| Third performance model | `P₂(F) = P₁(F) − D(F)` | Equation 3; Appendix D |

The original draft's additional effort-cost coefficient is not used: this implementation follows the appendix's `a²/2`. Effort remains a user-selected assumption, not an optimised contract solution. The app does not re-estimate the thesis's empirical regressions.

### Units and illustrative examples

All profit and cost terms are in consistent normalised units. H is the base overhead **per company outlet** in the implemented equation, not an unscaled total HQ budget. N is labelled **outlet scale** because Appendix C compares fractional N values, including 0.3. It is not displayed as a literal restaurant count.

Default parameters are `π=1`, `Cₒₚ=0.35`, `H=0.35`, `v=0.15`, `N=1`, `a=0.5`, `θ=2.4`, `δ=0.10`. These are chosen to illustrate the equations and are not fitted coefficients or recovered values for every appendix figure. The U-shaped example changes δ to 0.50. Linear examples change Cₒₚ to 0.55 and 0.15.

The H, N, v, vN and δ sweep lists transcribe the varied values visible in the appendix figures. Captions do not state every fixed parameter, so the app does **not** claim exact numerical reproduction of those figures. All other assumptions use the current controls.

For a vN comparison, N is held fixed and v changes to obtain the chosen product. This avoids adding an independent parameter that contradicts v and N.

### Maxima, minima and flat cases

For `P(F)=A+BF+CF²`, the stationary point is `−B/(2C)` when `C ≠ 0`. The app evaluates both endpoints and any stationary point in `(0,1)` and compares their values.

The curvature of P₁ is `−2vN`. The curvature of P₂ is `2(δ−vN)`. When δ exceeds vN, an interior turning point is a **minimum**, so the maximum must be found by comparing endpoints. When δ equals vN, the curve is linear and the app avoids division by zero. It preserves tied endpoints and reports every share as optimal for a flat curve.

Some convex or concave curves are monotone on `[0,1]`; the app calls them U shaped or inverted U only when the turning point lies inside the interval.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit controls, plots, explanatory text and downloads |
| `model.py` | Validated parameters, thesis equations and analytical extrema |
| `requirements.txt` | Runtime dependencies |
| `START_HERE.command` | Mac setup and launch script |
| `.streamlit/config.toml` | Optional visual theme |
| `tests/test_model.py` | Numerical and boundary checks |
| `tests/test_app.py` | Interaction checks through Streamlit AppTest |
| `VALIDATION.md` | Checks completed during development and execution limits |

## Checks

From the project folder, with dependencies installed:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The model checks compare the implementation with independently evaluated equations, test convex minima, endpoint ties and linear thresholds, and compare analytical extrema against dense grids for randomly selected inputs. AppTest checks examples, resets, saved comparisons, model switches and invalid sensitivity entries.

## Deployment documentation

- [Streamlit installation](https://docs.streamlit.io/get-started/installation/command-line)
- [Deploying from GitHub](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Dependency file placement](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization)
