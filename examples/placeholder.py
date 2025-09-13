# examples/__init__.py

from blueshark.domain.material_manager.manager import MaterialManager

manager = MaterialManager()

material = manager.use_material("Air")
print(material)

print(manager.materials["material"])