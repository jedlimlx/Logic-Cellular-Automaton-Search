import gen_trans


def b0_lyser(rulestring, rulespace, bsconditions, s_max):
    """Generates the relevant alternating rule for a B0 rule.
    Uses method specified at http://golly.sourceforge.net/Help/Algorithms/QuickLife.html"""
    if rulespace == "Single State" and bsconditions == "Outer Totalistic":
        new_birth, new_survival = [], []
        birth, survival = gen_trans.outer_totalistic_gen(rulestring)

        for i in range(len(birth)):
            if 0 not in birth[i]:  # Add in normal transitions if no B0
                new_birth += [birth[i]]
                new_survival += [survival[i]]
                continue

            if s_max[i] in survival[i]:  # Check for Smax
                new_birth += [[x for x in range(s_max[i] + 1) if x not in birth[i]]]
                new_survival += [[x for x in range(s_max[i] + 1) if x not in survival[i]]]
            else:
                new_birth += [[x for x in range(s_max[i] + 1) if x not in birth[i]],
                              [s_max[i] - x for x in survival[i]]]
                new_survival += [[x for x in range(s_max[i] + 1) if x not in survival[i]],
                                 [s_max[i] - x for x in birth[i]]]

        return [",".join([str(y) for y in new_survival[x]]) + "/" + ",".join([str(y) for y in new_birth[x]])
                for x in range(len(new_birth))]

    raise NotImplementedError("This rulespace does not support B0!")


if __name__ == "__main__":
    print(b0_lyser(["9/0-3"], "Single State", "Outer Totalistic", [12]))
