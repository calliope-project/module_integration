# %%
import pandas as pd
from pathlib import Path
from lib.templater import parametrise_template


def prepare_cost_slack(cost):
    total_cost = (
        cost.drop(columns=["nodes", "techs"])
        .groupby(["scenario", "method"])
        .sum()
        .sum(axis=1)
        .to_frame(name="total_cost")
        .reset_index()
    )

    cost_slack = total_cost.loc[total_cost["method"] == "min_cost"]
    cost_slack = cost_slack.drop(columns=["method"])
    cost_slack["cost_slack_01"] = cost_slack["total_cost"] * 1.01
    cost_slack["cost_slack_05"] = cost_slack["total_cost"] * 1.05
    cost_slack["cost_slack_10"] = cost_slack["total_cost"] * 1.1

    return cost_slack


# if __name__ == "__main__":
path_to_template = Path("../notebooks/Deliverable/sensitivities/sensitivities.yaml")
cost = pd.read_csv("../results/models/postprocess_combined/cost.csv", index_col=0)

cost_slack_total = prepare_cost_slack(cost)
cost_slack_total = cost_slack_total.set_index("scenario")

slacks = ["cost_slack_01", "cost_slack_05", "cost_slack_10"]


# %%
RESOLUTION1 = "NUTS0"
SCENARIOS = ["base", "res_50", "res_75", "res_90"]
BASEPATH = Path(__file__).parent.parent

destinations = [
    BASEPATH
    / f"results/models/{RESOLUTION1}/min_area_use/{scenario}/construct/overrides/sensitivities_alternative_objective.yaml"
    for scenario in SCENARIOS
]
for destination in destinations:
    parametrise_template(path_to_template, destination, data=cost_slack_total)

# %%
