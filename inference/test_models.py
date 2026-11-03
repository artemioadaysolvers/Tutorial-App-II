import inspect
from pathlib import Path
import unittest
from engine import CATALOG, load, predict
from registry import MODELS

class ModelsTest(unittest.TestCase):
    def test_all_24_ids_sum_the_inputs(self):
        self.assertEqual(len(CATALOG), 24)
        for model_id in CATALOG:
            for inputs, total in [({'input1': 10, 'input2': -3, 'input3': .5}, 7.5),
                                  ({'input1': 0, 'input2': 0, 'input3': 0}, 0),
                                  ({'input1': -2, 'input2': -4, 'input3': -6}, -12)]:
                with self.subTest(model=model_id, inputs=inputs):
                    result = predict(model_id, inputs)
                    self.assertEqual(result['modelId'], model_id)
                    self.assertEqual(result['values'], [total])
                    self.assertEqual(result['unit'], 'unidades')
                    self.assertNotIn('dates', result)

    def test_each_model_has_its_own_file_under_its_area(self):
        paths = []
        declared_ids = []
        for model_id in MODELS:
            module = load(model_id)
            self.assertEqual(module.MODEL_ID, model_id)
            self.assertIs(type(module.MODEL_ID), int)
            self.assertTrue(10_000_000 <= module.MODEL_ID <= 99_999_999)
            declared_ids.append(module.MODEL_ID)
            path = Path(inspect.getsourcefile(module))
            self.assertEqual(path.parent.parent.name, 'modelos')
            self.assertEqual(path.parent.name, MODELS[model_id].split('.')[1])
            self.assertEqual(CATALOG[model_id]['archivo'],f'inference/modelos/{path.parent.name}/{path.name}')
            paths.append(path)
        self.assertEqual(len(set(paths)), 24)
        self.assertEqual(len(set(declared_ids)), 24)

    def test_rejects_unknown_ids_and_invalid_inputs(self):
        valid = {'input1': 1, 'input2': 2, 'input3': 3}
        for model_id in ['../../etc/passwd', 'modelos.inmobiliario.cart', 'desconocido']:
            with self.assertRaises(ValueError):
                predict(model_id, valid)
        for inputs in [{}, {**valid, 'email': 1}, {**valid, 'input1': True},
                       {**valid, 'input1': float('nan')}, {**valid, 'input2': float('inf')},
                       {**valid, 'input3': '3'}, {**valid, 'input1': None},
                       {**valid, 'input1': 1e13}]:
            with self.assertRaises(ValueError):
                predict(10000002, inputs)

if __name__ == '__main__':
    unittest.main()
