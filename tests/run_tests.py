import unittest
import unit_physics
import unit_generation

loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Domain/Physics Tests
suite.addTests(loader.loadTestsFromTestCase(unit_physics.TestMechanical))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.TestElectrical))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.TestTransforms))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.TestRippleFunctions))
suite.addTest(loader.loadTestsFromTestCase(unit_physics.TestDisplacementCommutation))

# Domain/Generation Tests
suite.addTest(loader.loadTestsFromTestCase(unit_generation.NumberTurns))
suite.addTest(loader.loadTestsFromTestCase(unit_generation.GetCenteroid))
suite.addTest(loader.loadTestsFromTestCase(unit_generation.TestOriginPoints))

runner = unittest.TextTestRunner(verbosity=2)

if __name__ == "__main__":
    result = runner.run(suite)