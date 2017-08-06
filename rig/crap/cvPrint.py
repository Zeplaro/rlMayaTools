def coord():
    i = mc.ls(sl=1, fl=1)
    cp = []
    for j in i:
        val = tuple(mc.xform(j, q=1, t=1, ws=True))
        cp.append(val)
    print('___________________________\n')
    cp = [tuple([round(x/2, 3) for x in j]) for j in cp]
    cp = str(cp)
    cp = cp.replace('.0)', ')')
    cp = cp.replace('.0,', ',')
    cp = cp.replace('-0)', '0)')
    cp = cp.replace('-0,', '0,')
    print(cp)
coord()