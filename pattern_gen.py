def ship_search(period, x, y, dx, dy, symmetry, transform, nrange, pattern_file):
    """Generates a pattern file for a ship search"""

    origin_x = x  # Store original values
    origin_y = y

    x += nrange * 2  # Adding borders
    y += nrange * 2

    file = open(pattern_file, "w+")

    for t in range(period + 1):
        for i in range(nrange):  # Write in the border
            file.write("0 " * (x + dx) + "\n")

        num_vars = 0
        for i in range(y - nrange * 2 + dy):
            file.write("0 " * nrange)
            if (symmetry == "D2|" or symmetry == "D4+") and ((i > 0 and t == 0) or (i > dy and t == period)):
                num_vars += origin_x // 2 + 1

            if symmetry == "D2-" or symmetry == "D4+":
                if origin_y % 2:  # If odd
                    if i <= origin_y // 2:
                        num_vars = i * origin_x
                    elif i > origin_y // 2:
                        num_vars = (origin_y - i - 1) * origin_x
                else:  # If even
                    if i < origin_y // 2 - 1:
                        num_vars = i * origin_x
                    elif i > origin_y // 2 - 1:
                        num_vars = (origin_y - i - 1) * origin_x
            elif transform == "Flip|" and t == period:
                num_vars = (i + 1 - dy) * origin_x - 1

            for j in range(x - nrange * 2 + dx):
                if t == 0 and i < origin_y and j < origin_x:
                    if symmetry == "D2|" or symmetry == "D4+":
                        file.write(f"a{num_vars} ")
                        if origin_x % 2:  # If odd
                            num_vars += 1 if j < origin_x // 2 else -1
                        else:  # If even
                            if j < origin_x // 2 - 1:
                                num_vars += 1
                            elif j > origin_x // 2 - 1:
                                num_vars -= 1
                    else:
                        file.write(f"a{num_vars} ")
                        num_vars += 1
                elif t == period and i >= dy and j >= dx:
                    if symmetry == "D2|" or symmetry == "D4+":
                        file.write(f"a{num_vars} ")
                        if origin_x % 2:  # If odd
                            num_vars += 1 if j < origin_x // 2 else -1
                        else:  # If even
                            if j < origin_x // 2 - 1:
                                num_vars += 1
                            elif j > origin_x // 2 - 1:
                                num_vars -= 1
                    else:
                        file.write(f"a{num_vars} ")
                        if transform == "Flip|": num_vars -= 1
                        else: num_vars += 1
                elif t != 0 and t != period:
                    file.write("* ")
                else:
                    file.write("0 ")
            file.write("0 " * nrange + "\n")

        for i in range(nrange):  # Write in the border
            file.write("0 " * (x + dx) + "\n")
        file.write("\n")

    file.close()
