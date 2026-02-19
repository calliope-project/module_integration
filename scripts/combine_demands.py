# %%
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
from pathlib import Path
import yaml


def read_yaml(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def read_timeseries(file_path, tech):
    df = pd.read_parquet(
        file_path,
    )
    df.index = pd.to_datetime(df.index)

    # TODO this can go as soon as the rest of the script can do without multiindex
    df.columns = pd.MultiIndex.from_product([[tech], df.columns], names=['techs', 'nodes'])

    return df



def combine_demands(*demands):
    """Combine electricity and heat demand into a single DataFrame."""
    # Ensure all demands have the same nodes
    all_nodes = set()
    for demand in demands:
        all_nodes.update(demand.columns.get_level_values("nodes"))

    for i, demand in enumerate(demands):
        demand_nodes = set(demand.columns.get_level_values("nodes"))
        missing_nodes = all_nodes.difference(demand_nodes)
        assert not missing_nodes, f"Missing nodes in demand {i}: {missing_nodes}"

        # Ensure all demands have the same index
        # assert demands[i].index.equals(demands[0].index), f"Index mismatch between demands {i} and 0."

    # Combine demands
    combined_demand = pd.concat(
        [*demands],
        axis=1,
    )

    return combined_demand


def sum_sectorial_demands(demand):
    _demand = demand.copy()
    _demand.columns = _demand.columns.get_level_values("nodes")
    _demand = _demand.groupby(level=0, axis=1).sum()
    _demand.columns = pd.MultiIndex.from_product(
        [["demand_electricity"], _demand.columns]
    )
    return _demand


def get_demand_annual(demand):
    """Aggregate demand to annual values."""
    demand_annual = demand.sum(axis=0)
    demand_annual = demand_annual.unstack("techs")
    return demand_annual


def create_demand_scenarios(demand_heat, demand_electricity, demand_transport):
    demand_scenarios = {}
    for scenario in ["base", "res_50", "res_75", "res_90"]:
        scale_heat = snakemake.config["demand_scenario"][scenario]["demand_heat_scaler"]
        scale_electricity = snakemake.config["demand_scenario"][scenario][
            "demand_electricity_scaler"
        ]
        scale_transport = snakemake.config["demand_scenario"][scenario][
            "demand_transport_scaler"
        ]

        # scale demands
        demand_heat_scaled = demand_heat * scale_heat
        demand_electricity_scaled = demand_electricity * scale_electricity
        demand_transport_scaled = demand_transport * scale_transport

        columns_to_drop = [col for col in demand_heat_scaled.columns if "GBR" in col[1]]
        demand_heat_scaled = demand_heat_scaled.drop(columns=columns_to_drop)

        columns_to_drop = [
            col for col in demand_transport_scaled.columns if "GBR" in col[1]
        ]
        demand_transport_scaled = demand_transport_scaled.drop(columns=columns_to_drop)

        # combine
        demand_combined = combine_demands(
            demand_heat_scaled,
            demand_electricity_scaled,
            demand_transport_scaled,
        )

        demand_combined_sum = sum_sectorial_demands(demand_combined)

        demand_combined_annual = get_demand_annual(demand_combined)

        demand_scenarios[scenario] = {
            "demand_combined": demand_combined,
            "demand_combined_sum": demand_combined_sum,
            "demand_combined_annual": demand_combined_annual,
        }

    return demand_scenarios


def plot_demand_assumptions(demand_scenarios):
    colors = {
        "demand_electricity": "#69c8ffff",
        "demand_heat": "#fd6b6bff",
        "demand_transport": "#68447cff",
        "demand_hydrogen": "#a4e9ffff",
    }

    fig = plt.figure(figsize=(7, 3.5))
    gs = fig.add_gridspec(
        4, 2, width_ratios=[1.5, 1], height_ratios=[1, 1, 1, 2], wspace=0.16, hspace=0.4
    )
    ax1 = fig.add_subplot(gs[:3, 1])
    ax_ts4 = fig.add_subplot(gs[3, 0])
    ax_ts3 = fig.add_subplot(gs[2, 0], sharex=ax_ts4)
    ax_ts2 = fig.add_subplot(gs[1, 0], sharex=ax_ts4)
    ax_ts1 = fig.add_subplot(gs[0, 0], sharex=ax_ts4)

    # Plot timeseries
    for ax, label in zip(
        [ax_ts1, ax_ts2, ax_ts3],
        ["demand_electricity", "demand_heat", "demand_transport"],
    ):
        df = demand_scenarios["res_90"]["demand_combined"].iloc[:, 0]
        ax.plot(
            df.index,
            df,
            alpha=0.3,
            color=colors[label],
            zorder=2,
        )
        df_resample = df.resample("24h").mean()
        ax.plot(
            df_resample.index,
            df_resample,
            alpha=1,
            color=colors[label],
            zorder=2,
        )
        ax.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)

    ### total demand
    df = demand_scenarios["res_90"]["demand_combined_sum"].iloc[:, 0]
    ax_ts4.plot(
        df.index,
        df,
        alpha=0.3,
        color="grey",
        zorder=2,
    )
    df_resample = df.resample("24h").mean()
    ax_ts4.plot(
        df_resample.index,
        df_resample,
        alpha=1,
        color="grey",
        zorder=2,
    )
    ax_ts4.grid(axis="y", linestyle="--", alpha=0.4, zorder=0)
    ###

    ax_ts1.set_xticks([])
    ax_ts1.set_xticks([], minor=True)
    ax_ts1.set_title("Demand Profile Spain")
    ax_ts1.set_yticks([0e3, 15e3, 30e3, 45e3])
    ax_ts1.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x * 1e-3:.0f} GW")
    )

    ax_ts2.set_yticks([0e3, 15e3, 30e3, 45e3])
    ax_ts2.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x * 1e-3:.0f} GW")
    )

    ax_ts3.set_yticks([0e3, 15e3, 30e3, 45e3])
    ax_ts3.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x * 1e-3:.0f} GW")
    )

    ax_ts4.set_yticks([0e3, 15e3, 30e3, 45e3, 60e3, 75e3, 90e3])
    ax_ts4.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{x * 1e-3:.0f} GW")
    )
    ax_ts4.set_xticks(
        [
            pd.Timestamp("2018-01-01"),
            pd.Timestamp("2018-04-01"),
            pd.Timestamp("2018-07-01"),
            pd.Timestamp("2018-10-01"),
            pd.Timestamp("2019-01-01"),
        ]
    )
    ax_ts4.set_xticklabels(
        ["Jan", "Apr", "Jul", "Oct", "Jan"],
        rotation=0,
    )

    # Plot annual demand
    demand_combined_annual_scenarios = {
        scenario: data["demand_combined_annual"]
        for scenario, data in demand_scenarios.items()
    }
    demand_combined_annual_scenarios = pd.concat(
        demand_combined_annual_scenarios.values(),
        axis=1,
        keys=demand_combined_annual_scenarios.keys(),
    )
    demand_combined_annual_scenarios.columns.names = ["scenario", "techs"]
    demand_combined_annual_scenarios_sum = demand_combined_annual_scenarios.sum(
        axis=0
    ).unstack("techs")

    c = [
        colors[col]
        for col in demand_combined_annual_scenarios_sum.columns
        if col in colors
    ]
    demand_combined_annual_scenarios_sum.plot.bar(
        ax=ax1, stacked=True, width=0.8, zorder=2, color=c, legend=False
    )

    ax1.yaxis.tick_right()
    ax1.grid(axis="y", linestyle="--", alpha=0.7, zorder=0)
    handles, labels = ax1.get_legend_handles_labels()

    handles.append(mpatches.Patch(color="grey", label="Total demand"))
    labels.append("Total demand")
    ax1.set_ylabel("Annual demand (TWh)")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x * 1e-6:.0f} TWh"))
    labels = [label.replace("demand_", "").capitalize() for label in labels]
    ax1.legend(
        handles,
        labels,
        loc="lower right",
        bbox_to_anchor=(1, -1.1),
        ncol=4,
        frameon=False,
    )
    ax1.xaxis.get_label().set_visible(False)
    ax1.set_title("Annual Demand Europe")


def main(
    path_demand_electricity,
    path_demand_heat,
    path_demand_transport,
    path_scenarios,
    path_plot,
):

    demand_electricity = read_timeseries(path_demand_electricity, tech="demand_electricity")  # in MW
    demand_heat = read_timeseries(path_demand_heat, tech="demand_heat")  # in MW
    demand_transport = read_timeseries(path_demand_transport, tech="demand_transport")  # in MW

    demand_scenarios = create_demand_scenarios(
        demand_heat, demand_electricity, demand_transport
    )

    plot_demand_assumptions(demand_scenarios)
    plt.savefig(path_plot, bbox_inches="tight", dpi=300)

    # Save demand scenarios
    path_scenarios = Path(path_scenarios)
    for scenario, data in demand_scenarios.items():
        df = data["demand_combined_sum"]

        # TODO this can go as soon as the rest of the script can do without multiindex
        df.columns = df.columns.get_level_values("nodes")
        df.to_parquet(
            path_scenarios / f"demand_combined_sum_{scenario}.parquet"
        )


if __name__ == "__main__":
    main(
        snakemake.input.demand_electricity,
        snakemake.input.demand_heat,
        snakemake.input.demand_transport,
        snakemake.output.scenarios,
        snakemake.output.plot,
    )
