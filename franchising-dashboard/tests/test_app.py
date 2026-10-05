"""Interaction checks using the real Streamlit AppTest interface when installed."""
from pathlib import Path
import unittest
from model import PRESETS
try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest = None

APP = str(Path(__file__).parents[1]/'app.py')


@unittest.skipIf(AppTest is None,'Streamlit is not installed; install requirements.txt to run UI checks.')
class AppTests(unittest.TestCase):
    def run_app(self):
        app = AppTest.from_file(APP,default_timeout=20).run()
        self.assertFalse(app.exception)
        return app

    def test_all_examples_load_and_reset(self):
        app = self.run_app()
        for name in PRESETS:
            app.selectbox(key='preset').select(name).run()
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            app.slider(key='pi').set_value(1.6).run()
            self.assertFalse(app.exception)
            next(b for b in app.button if b.label=='Reset example').click().run()
            self.assertEqual(app.session_state['pi'],PRESETS[name][1].pi)
            self.assertFalse(app.exception)

    def test_saved_comparison_persists(self):
        app = self.run_app()
        app.slider(key='H').set_value(.9).run()
        next(b for b in app.button if b.label=='Save inputs as comparison').click().run()
        app.slider(key='H').set_value(.2).run()
        self.assertEqual(app.session_state['baseline_params']['H'],.9)
        self.assertFalse(app.exception)

    def test_invalid_sensitivity_and_recovery(self):
        app = self.run_app()
        app.text_input(key='sweep_values_H').input('oops, .3').run()
        self.assertTrue(app.error)
        self.assertFalse(app.exception)
        app.text_input(key='sweep_values_H').input('0.1, 0.35, 0.9').run()
        self.assertFalse(app.error)
        self.assertFalse(app.exception)

    def test_regime_comparison(self):
        app = self.run_app()
        app.selectbox(key='preset').select('Duplication costs · U shape').run()
        next(b for b in app.button if b.label=='Compare δ = 0, vN and 2vN').click().run()
        self.assertEqual(app.session_state['sweep_values_delta'],'0, 0.15, 0.3')
        self.assertFalse(app.exception)
        self.assertFalse(app.error)

    def test_boundaries_and_model_switches(self):
        app = self.run_app()
        app.slider(key='v').set_value(0.0).run()
        app.slider(key='a').set_value(0.0).run()
        self.assertFalse(app.exception)
        app.selectbox(key='model').select('duplication').run()
        app.slider(key='delta').set_value(0.0).run()
        self.assertFalse(app.exception)
        app.selectbox(key='model').select('baseline').run()
        self.assertFalse(app.exception)
        app.checkbox(key='show_other_models').check().run()
        self.assertFalse(app.exception)


if __name__ == '__main__':
    unittest.main()
