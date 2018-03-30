__author__ = "James Paul Mason"
__contact__ = "jmason86@gmail.com"


def latex_float(input_number):
    """Convert a floating point number to a LaTeX style scientific notation string. Useful for plot annotation.

    Inputs:
        input_number [float]: The number to be converted.

    Optional Inputs:
        None.

    Outputs:
        output_string [string]: The number represented in scientific notation in LaTeX style.

    Optional Outputs:
        None.

    Example:
        plt.annotate('t = ' + latex_float(1.39873934e9), xy=(0.8, 0.8), xycoords='axes fraction')
    """
    float_str = "{0:.2g}".format(input_number)
    if "e" in float_str:
        base, exponent = float_str.split("e")
        return r"${0} \times 10^{{{1}}}$".format(base, int(exponent))
    else:
        return float_str
