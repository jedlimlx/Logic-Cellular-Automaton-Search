def ship_search(period, x, y, dx, dy, symmetry, nrange, pattern_file):
    """Generates a pattern file for a ship search"""

    x += nrange * 2  # Adding borders
    y += nrange * 2

    num_vars_origin = 0
    num_vars_period = 0

    file = open(pattern_file, "w+")

    print(symmetry)
    for t in range(period + 1):
        for i in range(nrange):  # Write in the border
            file.write("0 " * (x + dx) + "\n")

        for i in range(y - nrange * 2 + dy):
            file.write("0 " * nrange)
            for j in range(x - nrange * 2 + dx):
                if t == 0 and i < y - nrange * 2 and j < x - nrange * 2:
                    if symmetry == "D2|":
                        if j > (x - nrange * 2 + dx) // 2 - 2:
                            file.write(f"a{num_vars_origin} ")
                            num_vars_origin -= 1
                        else:
                            file.write(f"a{num_vars_origin} ")
                            num_vars_origin += 1
                    else:
                        file.write(f"a{num_vars_origin} ")
                        num_vars_origin += 1
                elif t == period and i >= dy and j >= dx:
                    if symmetry == "D2|":
                        if j > (x - nrange * 2 + dx) // 2 - 2:
                            file.write(f"a{num_vars_period} ")
                            num_vars_period -= 1
                        else:
                            file.write(f"a{num_vars_period} ")
                            num_vars_period += 1
                    else:
                        file.write(f"a{num_vars_period} ")
                        num_vars_period += 1
                elif t != 0 and t != period:
                    file.write("* ")
                else:
                    file.write("0 ")
            file.write("0 " * nrange + "\n")

        for i in range(nrange):  # Write in the border
            file.write("0 " * (x + dx) + "\n")
        file.write("\n")

    file.close()
