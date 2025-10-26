"""
file: sankey.py
author: Alex K
description: A library for generating sankey diagrams
"""
import plotly.graph_objects as go
import pandas as pd

def code_mapping(df, src, targ):
    """map labels in src and targ columns to integers"""

    # get distinct labels in src and targ
    labels = list(set(df[src]).union(set(df[targ])))

    # generate list of integer codes
    codes = list(range(len(labels)))

    # create the label --> code mapping
    lc_map = dict(zip(labels, codes))

    # sub codes for the labels in the dataframe
    df[src]  = df[src].map(lc_map)
    df[targ] = df[targ].map(lc_map)

    print(labels, codes, lc_map, df)

    return df, labels

def show_sankey(df, *cols, vals=None, **kwargs):
    """ A wrapper to generate the sankey diagram
    df- dataframe
    cols - take all possible sources and targets and values
    kwargs - catchall for customizations """
    if vals:
        base_values = df[vals]
    else:
        base_values = [1] * len(df)

    label_set = set()
    for col in cols:
        label_set.update(df[col].unique())
    all_labels = sorted(label_set, key=str)
    label_map = {label: i for i, label in enumerate(all_labels)}

    sources = []
    targets = []
    weights = []

    for i in range(len(cols) - 1):
        src = cols[i]
        targ = cols[i + 1]

        temp_df = df[[src, targ]].copy()
        temp_df['value'] = base_values

        grouped = temp_df.groupby([src, targ], as_index=False).agg({'value': 'sum'})

        for _, row in grouped.iterrows():
            sources.append(label_map[row[src]])
            targets.append(label_map[row[targ]])
            weights.append(row['value'])

    padding = kwargs.get('padding', 50)
    thickness = kwargs.get('thickness', 25)
    width = kwargs.get('width', 800)
    height = kwargs.get('height', 600)

    link = {'source': sources, 'target': targets, 'value': weights}
    node = {'label': all_labels, 'pad': padding, 'thickness': thickness}

    sk = go.Sankey(link=link, node=node)
    fig = go.Figure(sk)
    fig.update_layout(
        autosize=False,
        width=width,
        height=height
    )
    return fig

