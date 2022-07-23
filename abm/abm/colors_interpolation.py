# -*- coding: utf-8 -*-

import plotly.colors


def get_continuous_color(colorscale, intermed):
    """
    Function to interpolate through the colors of a plotyl scale and return
    a color proportional to a value in the scale.

    Plotly continuous colorscales assign colors to the range [0, 1]. This
    function computes the intermediate color for any value in that range.
    Plotly doesn't make the colorscales directly accessible in a common format.
    Some are ready to use:
        colorscale = plotly.colors.PLOTLY_SCALES["Greens"]

    Others are just swatches that need to be constructed into a colorscale:
        viridis_colors, scale = plotly.colors.convert_colors_to_same_type(
            plotly.colors.sequential.Viridis
            )
        colorscale = plotly.colors.make_colorscale(viridis_colors, scale=scale)

    Code adapted from https://stackoverflow.com/questions/62710057/access-color-from-plotly-color-scale    
    Parameters
    ----------
    colorscale : 
        A plotly continuous colorscale defined with RGB string colors.
    intermed : float
        value in the range [0, 1]

    Returns
    -------
    str
        Color in hex string format.

    """
    if len(colorscale) < 1:
        raise ValueError("colorscale must have at least one color")

    if intermed <= 0 or len(colorscale) == 1:
        return colorscale[0][1]
    if intermed >= 1:
        return colorscale[-1][1]

    for cutoff, color in colorscale:
        if intermed > cutoff:
            low_cutoff, low_color = cutoff, color
        else:
            high_cutoff, high_color = cutoff, color
            break

    # noinspection PyUnboundLocalVariable
    color = plotly.colors.find_intermediate_color(
        lowcolor=low_color, highcolor=high_color,
        intermed=((intermed - low_cutoff) / (high_cutoff - low_cutoff)),
        colortype="rgb")
    # return color
    col_tuple = plotly.colors.convert_colors_to_same_type(
        color, colortype='tuple')[0][0]
    rounded_col_tuple = [int(round(el*255, 0)) for el in col_tuple]
    col_hex = '#%02x%02x%02x' % tuple(rounded_col_tuple)
    return col_hex
