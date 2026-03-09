import numpy as np
import pandas as pd
import calliope
from collections import namedtuple
from lib.data_processing import rename_aggregate_by_label


model_specs = namedtuple("model_specs", ("method", "scenario", "path"))
model_tuple = namedtuple("model", ("method", "scenario", "model"))


def get_techs_by_base_tech(model: calliope.Model, base_tech: str) -> list:
    return model.inputs.techs.loc[model.inputs.base_tech == base_tech].to_series().tolist()


def get_from_to(model: calliope.Model) -> list[tuple]:
    """
    Get from/to for each transmission tech.

    This is a hacky implementation splitting the tech names.
    TODO Ideally, from/to should be read from the model definition.
    """
    transmission_techs = get_techs_by_base_tech(model, "transmission")
    from_to = {tech: tech.split("_to_") for tech in transmission_techs}
    from_to = pd.DataFrame.from_dict(from_to, orient="index", columns=["from", "to"])
    return from_to


def get_flow_cap(model: calliope.Model, rescale: float = 1) -> pd.DataFrame:
    transmission_techs = get_techs_by_base_tech(model, "transmission")

    flow_cap = (
        model.results.flow_cap.to_dataframe()
        .dropna()
        .reset_index()
        .replace({t: "transmission" for t in transmission_techs})
        .groupby(["nodes", "techs", "carriers"])
        .sum()
        .multiply(rescale)
        .reset_index()
    )

    return flow_cap


def get_flow_cap_max(model: calliope.Model, rescale: float = 1) -> pd.DataFrame:
    transmission_techs = get_techs_by_base_tech(model, "transmission")

    flow_cap_max = (
        model.inputs.flow_cap_max.drop_sel(techs=transmission_techs)
        .to_dataframe()
        .dropna()
        .multiply(rescale)
        .reset_index()
    )

    return flow_cap_max


def get_flow_cap_min(model: calliope.Model, rescale: float = 1) -> pd.DataFrame:
    transmission_techs = get_techs_by_base_tech(model, "transmission")

    flow_cap_min = (
        model.inputs.flow_cap_min.drop_sel(techs=transmission_techs)
        .to_dataframe()
        .dropna()
        .multiply(rescale)
        .reset_index()
    )

    return flow_cap_min


def get_flow_cap_links(model: calliope.Model, rescale: float = 1) -> pd.DataFrame:
    transmission_techs = get_techs_by_base_tech(model, "transmission")
    link_flow_cap = (
        model.results.flow_cap.sel(techs=transmission_techs)
        .to_dataframe()
        .dropna()
        .multiply(rescale)
        .reset_index()
    )

    return link_flow_cap


def get_storage_cap(model: calliope.Model, rescale: float = 1) -> pd.DataFrame:
    storage_cap = model.results.storage_cap.to_dataframe().dropna().multiply(rescale).reset_index()

    return storage_cap


def get_flow_out(model: calliope.Model, rescale: float = 1) -> pd.DataFrame:
    transmission_techs = get_techs_by_base_tech(model, "transmission")

    flow_out = (
        model.results.flow_out.sum("timesteps")
        .to_dataframe()
        .dropna()
        .reset_index()
        .replace({t: "transmission" for t in transmission_techs})
        .groupby(["nodes", "techs", "carriers"])
        .sum()
        .multiply(rescale)
        .reset_index()
    )

    return flow_out


def get_emissions(model, rescale=1):
    emissions = (
        model.results.cost.sel(costs="emissions")
        .to_dataframe()
        .dropna()
        .multiply(rescale)
        .reset_index()
    )
    return emissions


def get_area_use(model, rescale=1):
    area_use = model.results.area_use.to_dataframe().dropna().multiply(rescale).reset_index()
    return area_use


def get_link_flows(model: calliope.Model, rescale=1) -> pd.DataFrame:
    """
    Prepares a DataFrame with columns `link_groups`, `timesteps` and `flow_out_link_group`
    """
    transmission_techs = get_techs_by_base_tech(model, "transmission")
    link_flow_out = (
        model.results.flow_out.sel(techs=transmission_techs).to_dataframe().dropna().reset_index()
    )

    # link_flow_out.columns.name = "var_name"
    # link_flow_out = link_flow_out.unstack(["nodes", "techs"])
    # link_flow_out.columns = link_flow_out.columns.droplevel(["var_name"])
    # link_flow_out.index = link_flow_out.index.droplevel("carriers")

    return link_flow_out



def _nonzero(df):
    df = df.loc[df != 0]
    # df.index = df.index.droplevel("costs")
    return df


def _aggregate_level(df, level):
    groupby = list(df.index.names)
    groupby.remove(level)
    df = df.groupby(groupby).sum()
    return df


def _get_costs(model):
    """
    Get the costs of a model.

    Returns
    -------
    cost: Sum of cost_investment_annualised and sum_t cost_operation_variable
    cost_investment_annualised: The installation costs of a technology, annualised.
    cost_investment_flow_cap: The investment costs associated with the nominal\rated capacity of a technology.
    cost_operation_variable: The operating costs per timestep of a technology (cost_flow_in, cost_flow_out, cost_export)
    """

    cost = _nonzero(model.results.cost.to_series().dropna())
    cost_investment = _nonzero(
        model.results[NAME_COST_INV].sel(costs="monetary").to_series().dropna()
    )
    cost_investment_flow_cap = _nonzero(model.results.cost_investment_flow_cap.to_series().dropna())
    cost_operation_variable = _nonzero(
        model.results[NAME_COST_VAR].sel(costs="monetary").to_series().dropna()
    )

    cost_operation_variable = _aggregate_level(cost_operation_variable, "timesteps")

    return cost, cost_investment, cost_investment_flow_cap, cost_operation_variable

NAME_COST_VAR = "cost_operation_variable"
NAME_COST_INV = "cost_investment_annualised"

def get_cost(model: calliope.Model, rescale=1, agg_transmission=True) -> pd.DataFrame:
    cost, cost_investment, _, cost_operation_variable = _get_costs(model)
    cost_investment = cost_investment.to_frame(NAME_COST_INV)
    cost_operation_variable = cost_operation_variable.to_frame(NAME_COST_VAR)
    result = cost_investment.join(cost_operation_variable)
    result *= rescale
    result = result.reset_index()

    transmission_techs = get_techs_by_base_tech(model, "transmission")
    result = rename_aggregate_by_label(
        result,
        "techs",
        transmission_techs,
        "transmission",
        [NAME_COST_INV, NAME_COST_VAR],
    )
    return result


def _outer_product(s1, s2):
    values = np.outer(s1.values, s2.values)
    outer_product = pd.DataFrame(values, columns=s2.index, index=s1.index)
    return outer_product


def get_power_potential(model: calliope.Model, rescale=1) -> pd.DataFrame:
    area = model.inputs.available_area.to_dataframe()
    area_use = model.inputs.area_use_per_flow_cap.to_dataframe().dropna()
    power_potential = _outer_product(area, 1 / area_use).stack()
    power_potential *= rescale
    power_potential = power_potential.to_frame(name="power_potential").reset_index()
    return power_potential


def get_flow_out_sum(model: calliope.Model, rescale=1) -> pd.DataFrame:
    """
    flow_out, summed over timesteps.
    """
    flow_out_sum = (
        model.results.flow_out.sum("timesteps")
        .to_dataframe()
        .dropna()
        .multiply(rescale)
        .reset_index()
    )

    return flow_out_sum


def get_flow_in_sum(model: calliope.Model, rescale=1) -> pd.DataFrame:
    """
    flow_in, summed over timesteps.
    """
    flow_in_sum = (
        model.results.flow_in.sum("timesteps")
        .to_dataframe()
        .dropna()
        .multiply(rescale)
        .reset_index()
    )

    return flow_in_sum