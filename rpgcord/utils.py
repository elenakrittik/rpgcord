async def parse_state(i, rt=relict):
    async def spl(s, sp):
        sp_x = 0
        sb = lambda: s[sp_x]

        while sb() != sp:
            sp_x += 1

        fst = s[sp_x + 1 :]
        scnd = s[:sp_x]

        return fst, scnd

    i = i[4:]
    stt = rt()
    tl = {"int": int, "float": float}

    for p in i.split(" "):
        v, kt = await spl(p, "=")

        if ":" in kt:
            t, k = await spl(kt, ":")
            stt[k] = tl.get(t, str)(v)
        else:
            stt[kt] = v

    return stt
