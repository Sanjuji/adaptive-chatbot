import unittest
from unittest.mock import patch
from src.intelligent_import_optimizer import IntelligentImportOptimizer, CircularDependency

class TestIntelligentImportOptimizer(unittest.TestCase):

    def test_circular_dependency_detection_fix(self):
        """
        Test that a simple 2-module circular dependency is detected correctly
        after the bug fix.
        """
        # We patch _analyze_project_imports to prevent it from running its own analysis
        with patch.object(IntelligentImportOptimizer, '_analyze_project_imports') as mock_analyze:
            optimizer = IntelligentImportOptimizer()
            mock_analyze.assert_called_once()

        # Manually create a simple circular dependency: A -> B -> A
        optimizer._import_graph = {
            'moduleA': {'moduleB'},
            'moduleB': {'moduleA'}
        }

        # Run the detection method
        optimizer._detect_circular_dependencies()

        # Check the detected circular dependencies
        self.assertEqual(len(optimizer._circular_dependencies), 1)
        detected_cycle = optimizer._circular_dependencies[0]

        # The correct cycle path is ['moduleA', 'moduleB', 'moduleA'], which has a length of 3.
        # The original bug reported a length of 4.
        self.assertEqual(len(detected_cycle.modules), 3, "The cycle path should be A -> B -> A")
        self.assertEqual(detected_cycle.modules, ['moduleA', 'moduleB', 'moduleA'])

        # Because the length is now correct (3), the severity should be 'LOW'.
        self.assertEqual(detected_cycle.severity, 'LOW')

if __name__ == '__main__':
    unittest.main()