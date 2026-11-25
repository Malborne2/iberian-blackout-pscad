import inspect
import mhi.pscad as p

c = p.Canvas if hasattr(p, 'Canvas') else None
print('Canvas class:', c)
mods = [m for m in dir(p) if not m.startswith('_')]
print('module attrs:', mods)

main = p.connect().project('Spanish_grid_model').canvas('Main')
cls = type(main)
print('\ncanvas class', cls)
print(inspect.signature(cls.create_connection))
print(inspect.getdoc(cls.create_connection))
print('\n--- create_bus ---')
print(inspect.signature(cls.create_bus))
print(inspect.getdoc(cls.create_bus))
print('\n--- create_component ---')
print(inspect.signature(cls.create_component))
print(inspect.getdoc(cls.create_component)[:3000])
