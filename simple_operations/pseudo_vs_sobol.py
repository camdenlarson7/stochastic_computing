import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# Config
# -----------------------------
PRNG_CSV = Path("all_stochastic_results.csv")   # pseudo-random results
SOBOL_CSV = Path("all_sobol_results.csv")       # sobol results

OUT_ABS = Path("absolute_error_comparison.png")
OUT_PCT = Path("percent_error_comparison.png")

# -----------------------------
# Loader
# -----------------------------
def load_results(path: Path, label: str) -> pd.DataFrame:
    """Load one CSV and return a clean DataFrame."""
    df = pd.read_csv(path)

    # Confirm required columns exist
    expected_cols = {
        "Run ID", "Timestamp", "a", "b",
        "Number of Bits", "Expected Result", "Stochastic Result",
        "Percent Error (%)", "Absolute Error"
    }
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"{path.name} is missing expected columns: {missing}")

    # Normalize schema
    out = pd.DataFrame({
        "Method": label,
        "Run ID": df["Run ID"],
        "Timestamp": pd.to_datetime(df["Timestamp"]),
        "a": df["a"],
        "b": df["b"],
        "Number of Bits": df["Number of Bits"],
        "Expected": df["Expected Result"],
        "Estimate": df["Stochastic Result"],
        "Absolute Error": df["Absolute Error"].abs(),   # ensure positive
        "Percent Error (%)": df["Percent Error (%)"].abs()
    })

    return out

# -----------------------------
# Plotting helper
# -----------------------------
def plot_comparisons(all_df: pd.DataFrame,
                     out_abs: Path,
                     out_pct: Path,
                     out_abs_mean: Path = Path("absolute_error_means.png"),
                     out_pct_mean: Path = Path("percent_error_means.png")):
    """Create and save comparison plots (per trial and mean per bit length)."""
    all_df.sort_values(by=["Number of Bits", "Method"], inplace=True)

    # -------------------------------
    # 1. Absolute Error per trial
    # -------------------------------
    plt.figure(figsize=(9, 5))
    for method, dfm in all_df.groupby("Method"):
        plt.plot(dfm["Number of Bits"], dfm["Absolute Error"],
                 marker="o", linestyle="-", label=method)
    plt.xscale("log", base=2)
    plt.xlabel("Number of Bits (log₂ scale)")
    plt.ylabel("Absolute Error")
    plt.title("Absolute Error per Trial: Pseudo-Random vs Sobol")
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_abs, dpi=160)
    plt.close()

    # -------------------------------
    # 2. Percent Error per trial
    # -------------------------------
    plt.figure(figsize=(9, 5))
    for method, dfm in all_df.groupby("Method"):
        plt.plot(dfm["Number of Bits"], dfm["Percent Error (%)"],
                 marker="o", linestyle="-", label=method)
    plt.xscale("log", base=2)
    plt.xlabel("Number of Bits (log₂ scale)")
    plt.ylabel("Percent Error (%)")
    plt.title("Percent Error per Trial: Pseudo-Random vs Sobol")
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_pct, dpi=160)
    plt.close()

    # -------------------------------
    # 3. Mean Absolute Error per bit length
    # -------------------------------
    mean_abs = (all_df.groupby(["Method", "Number of Bits"])["Absolute Error"]
                .agg(['mean', 'std'])
                .reset_index())

    plt.figure(figsize=(9, 5))
    for method, dfm in mean_abs.groupby("Method"):
        plt.errorbar(dfm["Number of Bits"], dfm["mean"], yerr=dfm["std"],
                     marker="o", linestyle="-", capsize=3, label=f"{method} (±1σ)")
    plt.xscale("log", base=2)
    plt.xlabel("Number of Bits (log₂ scale)")
    plt.ylabel("Mean Absolute Error")
    plt.title("Mean Absolute Error vs Bit Length")
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_abs_mean, dpi=160)
    plt.close()

    # -------------------------------
    # 4. Mean Percent Error per bit length
    # -------------------------------
    mean_pct = (all_df.groupby(["Method", "Number of Bits"])["Percent Error (%)"]
                .agg(['mean', 'std'])
                .reset_index())

    plt.figure(figsize=(9, 5))
    for method, dfm in mean_pct.groupby("Method"):
        plt.errorbar(dfm["Number of Bits"], dfm["mean"], yerr=dfm["std"],
                     marker="o", linestyle="-", capsize=3, label=f"{method} (±1σ)")
    plt.xscale("log", base=2)
    plt.xlabel("Number of Bits (log₂ scale)")
    plt.ylabel("Mean Percent Error (%)")
    plt.title("Mean Percent Error vs Bit Length")
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_pct_mean, dpi=160)
    plt.close()

    # -------------------------------
    # 5. Table graphic: mean absolute error for each bit length and method
    abs_table = mean_abs.pivot(index="Number of Bits", columns="Method", values="mean")
    fig, ax = plt.subplots(figsize=(8, 0.5 + 0.4 * len(abs_table)))
    ax.axis('off')
    tbl = ax.table(
        cellText=abs_table.round(8).values,
        rowLabels=abs_table.index,
        colLabels=abs_table.columns,
        cellLoc='center',
        loc='center',
        colColours=['#dbeafe']*len(abs_table.columns)
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(12)
    tbl.scale(1.2, 1.5)
    plt.title('Mean Absolute Error by Bit Length and Method', pad=20)
    plt.tight_layout()
    table_path = Path("absolute_error_table.png")
    plt.savefig(table_path, dpi=160)
    plt.close()
    print(f"Saved plots:\n - {out_abs}\n - {out_pct}\n - {out_abs_mean}\n - {out_pct_mean}\n - {table_path}")


# -----------------------------
# Main
# -----------------------------
def main():
    prng = load_results(PRNG_CSV, "Pseudo-Random")
    sobol = load_results(SOBOL_CSV, "Sobol")

    all_df = pd.concat([prng, sobol], ignore_index=True)

    plot_comparisons(all_df, OUT_ABS, OUT_PCT)
    print(f"Saved plots:\n - {OUT_ABS}\n - {OUT_PCT}")

if __name__ == "__main__":
    main()

