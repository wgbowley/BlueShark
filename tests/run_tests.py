import unittest
import unit_physics

loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Domain/Physics Tests
suite.addTests(loader.loadTestsFromTestCase(unit_physics.testMechanical))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.testElectrical))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.TestTransforms))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.TestRippleFunctions))
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)