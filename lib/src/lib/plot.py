from matplotlib import pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.legend_handler import HandlerPatch
import numpy as np
import pandas as pd


def stacked_bar(x: int | float, series: pd.Series, ax=None, colors=None, **kwargs):
    if ax is None:
        ax = plt.subplot(111)
    if colors is None:
        colors = dict()
    offset = 0

    for id, value in series.items():
        color = colors.get(id)
        ax.bar(x, height=value, bottom=offset, color=color, **kwargs)
        offset += value
    return ax


def plot_grouped_bar(data, major, minor, stack, var_value, colors=None, ax=None, **kwargs):
    _data = data.copy()
    _data = _data.sort_values(by=[major, minor, stack])

    major_values = _data[major].unique()
    minor_values = _data[minor].unique()
    stack_values = _data[stack].unique()

    # prepare xtick locations
    def get_loc_minor(row):
        b = 0.3
        a = 0.2
        return row["id_major"] - b + a * row["id_minor"]

    # _data = _data.unstack(stack, sort=False).loc[:, var_value]
    _data = _data.pivot(index=[major, minor], columns=stack, values=var_value)

    index = pd.MultiIndex.from_product([major_values, minor_values], names=[major, minor])
    _data = _data.reindex(index, fill_value=0)

    loc_xticks = pd.DataFrame(
        [
            (id_major, id_minor)
            for id_major in range(len(major_values))
            for id_minor in range(len(minor_values))
        ],
        index=index,
        columns=["id_major", "id_minor"],
    )

    def get_loc_major(loc_xticks):
        def find_middle(group):
            id_mid = np.floor(len(group) / 2).astype(int)
            group["loc_major"] = group.iloc[id_mid].loc["loc_minor"]

            return group["loc_major"].unique()[0]

        loc_major = loc_xticks.groupby("id_major").apply(find_middle)
        return loc_major

    loc_xticks["loc_minor"] = loc_xticks.apply(get_loc_minor, 1)
    loc_xticks_major = get_loc_major(loc_xticks)

    # plot
    for id, df in _data.iterrows():
        loc = loc_xticks.loc[id, "loc_minor"]
        ax = stacked_bar(loc, df, ax=ax, colors=colors, **kwargs)

    # plot major ticks on ax
    major_xticks = loc_xticks_major
    major_xticklabels = _data.index.get_level_values(major).unique()

    ax.set_xticks(major_xticks)
    ax.set_xticklabels(major_xticklabels, rotation=0, ha="center")
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)

    # plot minor ticks on secax
    secax = ax.secondary_xaxis(location=0)

    minor_xticks = loc_xticks["loc_minor"]
    minor_xticklabels = loc_xticks.index.get_level_values(minor)

    secax.set_xticks(minor_xticks)
    secax.set_xticklabels(minor_xticklabels, rotation=45, ha="right")


def plot_pie_chart_on_centroids(data, regions, scaling, cmap, alpha=0, ax=None):
    assert all(data.index == regions.index), "Data and regions must have the same index."
    if ax is None:
        fig, ax = plt.subplots()

    centroids = regions.geometry.centroid

    # Define scaling factor for size of pie charts
    data_sums = data.sum(axis=1)

    for idx, centroid in centroids.items():
        region_data = data.loc[idx]
        colors = [cmap[techs] for techs in region_data.index]
        # don't plot if all zero
        if region_data.sum() == 0:
            continue

        area = data_sums.loc[idx] * scaling
        radius = np.sqrt(area / np.pi)
        plot_pie(ax, centroid.x, centroid.y, region_data, radius, colors, alpha)

    return ax


def plot_pie(ax, x, y, data, radius, color, alpha=1):
    # Normalize
    data = data / data.sum()

    # Draw pie chart
    start_angle = 0
    for value, color in zip(data, color):
        end_angle = start_angle + value * 360
        wedge = Wedge((x, y), radius, start_angle, end_angle, facecolor=color, alpha=alpha)
        ax.add_patch(wedge)
        start_angle = end_angle


def plot_network_of_pies(
    regions,
    links,
    col_regions,
    col_links,
    ax=None,
    c_pies=None,
    c_links="red",
    c_regions="grey",
    width_links=5,
    width_regions=0.4,
    size_pies=3,
):
    if ax is None:
        fig, ax = plt.subplots(figsize=(4, 4))

    links.plot(
        ax=ax,
        zorder=1,
        linewidth=links[col_links] * width_links,
        color=c_links,
        alpha=0.7,
        aspect=None,
    )

    regions.boundary.plot(
        ax=ax,
        zorder=0,
        color=c_regions,
        linewidth=width_regions,
        alpha=1,
        aspect=None,
    )

    plot_pie_chart_on_centroids(
        regions[col_regions],
        regions,
        scaling=size_pies,
        cmap=c_pies,
        alpha=1,
        ax=ax,
    )

    return ax


class HandlerCircle(HandlerPatch):
    """
    Legend Handler used to create circles for legend entries.

    This handler resizes the circles in order to match the same
    dimensional scaling as in the applied axis.
    """

    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ):
        # take minimum to protect against too uneven x- and y-axis extents
        # unit = min(np.diff(ax.transData.transform([(0, 0), (1, 1)]), axis=0)[0])

        radius = orig_handle.radius
        center = 5 - xdescent, 3 - ydescent
        p = plt.Circle(
            center,
            radius,
            facecolor=orig_handle.get_facecolor(),
            alpha=orig_handle.get_alpha(),
        )
        # self.update_prop(p, orig_handle, legend)
        # p.set_transform(trans)
        return [p]


def get_line_handles(widths, patch_kw=None):
    if patch_kw is None:
        patch_kw = {}
    return [plt.Line2D([0], [0], linewidth=w, **patch_kw) for w in widths]


def get_circle_handles(radiusses, patch_kw=None):
    if patch_kw is None:
        patch_kw = {}
    return [plt.Circle((0, 0), radius=s, **patch_kw) for s in radiusses]


def legend_network_of_pies(ax, pie_values, link_values, pie_labels, link_labels, legend_kw=None):
    if legend_kw is None:
        legend_kw = {
            "loc": "center",
            "ncols": ncols,
            "labelspacing": 1.0,
            "borderpad": 0,
            "frameon": False,
        }

    radius = get_scaling_factor(ax)

    handles_circle = get_circle_handles(
        [np.sqrt(value / np.pi) * 12 for value in pie_values],
        patch_kw={"color": "black", "alpha": 0.4},
    )
    handles_line = get_line_handles([value for value in link_values], patch_kw={"color": "red"})
    handles = handles_circle + handles_line
    labels = [*pie_labels, *link_labels]
    ncols = len(handles)
    draw_legend(
        ax,
        handles,
        labels=labels,
        legend_kw=legend_kw,
    )


def get_scaling_factor(ax):
    fig = ax.get_figure()
    unit = ax.transData.transform((1, 0))[0] - ax.transData.transform((0, 0))[0]
    scaling_factor = (72 / fig.dpi) * unit
    return scaling_factor


def draw_legend(ax, handles, labels, legend_kw=None):
    if legend_kw is None:
        legend_kw = {}
    legend = ax.legend(handles, labels, handler_map={plt.Circle: HandlerCircle()}, **legend_kw)
    ax.get_figure().add_artist(legend)
