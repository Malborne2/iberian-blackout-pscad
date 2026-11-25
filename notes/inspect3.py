import mhi.pscad as p

app = p.connect()
pr = app.project('ieee_39_bus')
main = pr.canvas('Main')

print('--- TLine_1 canvas/params ---')
tl = pr.canvas('TLine_1')
print('params', tl.parameters())
print('components:')
for c in tl.components():
    print(' ', type(c).__name__, getattr(c, 'location', ''))
    if type(c).__name__ == 'UserCmp':
        print('   defn', c.definition.name)
        print('   pars', c.parameters())

print('--- psse defn ---')
ps = pr.canvas('psse')
for c in ps.components():
    print(' ', type(c).__name__, getattr(c, 'location', ''))
    if type(c).__name__ == 'UserCmp':
        print('   defn', c.definition.name, c.parameters())
