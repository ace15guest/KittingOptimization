def mirror_coordinates(x, y, center_x, grid_count=1, shift=0):
    """Mirrors coordinates about a vertical center line.

    Args:
        x (float): The x-coordinate of the point.
        y (float): The y-coordinate of the point.
        center_x (float): The x-coordinate of the center line.

    Returns:
        tuple: The mirrored coordinates (x_mirrored, y).
    """



    x = float(x)
    y = float(y)
    x_mirrored = 2 * center_x - x

    if grid_count%2==0:
        x_mirrored-=shift

    return f'{int(x_mirrored)},{int(y)}'

