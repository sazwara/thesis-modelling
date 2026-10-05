"""Independent equations and analytical boundary checks; uses unittest."""
from dataclasses import replace
import unittest
import numpy as np
from model import Parameters, performance, summarise, with_parameter


class ModelTests(unittest.TestCase):
    def test_direct_thesis_equations(self):
        p = Parameters(pi=1.2,c_op=.4,H=.2,v=.11,N=2.7,a=.43,theta=3.2,delta=.7)
        F = np.linspace(0,1,21)
        q = (1-np.exp(-p.theta*p.a))*p.pi - p.a**2/2
        base = (1-F)*(p.pi-p.c_op) + F*q
        overhead = (1-F)*(p.pi-p.H-p.v*(1-F)*p.N) + F*q
        np.testing.assert_allclose(performance(F,'baseline',p),base)
        np.testing.assert_allclose(performance(F,'overhead',p),overhead)
        np.testing.assert_allclose(performance(F,'duplication',p),overhead-p.delta*F*(1-F))

    def test_duplication_leaves_endpoints_unchanged(self):
        p = Parameters(delta=.83)
        np.testing.assert_allclose(performance([0,1],'duplication',p),performance([0,1],'overhead',p))
        self.assertAlmostEqual(performance(.5,'overhead',p)-performance(.5,'duplication',p),p.delta/4)

    def test_interior_maximum_matches_appendix_b(self):
        p = Parameters()
        expected = (p.H-p.pi+p.franchise_payoff+2*p.vN)/(2*p.vN)
        s = summarise('overhead',p)
        self.assertAlmostEqual(s.stationary_share,expected)
        self.assertEqual(s.stationary_kind,'maximum')
        np.testing.assert_allclose(s.maximisers,[expected])

    def test_convex_stationary_point_is_not_maximum(self):
        p = Parameters(delta=.5)
        s = summarise('duplication',p)
        self.assertEqual(s.stationary_kind,'minimum')
        np.testing.assert_allclose(s.minimisers,[s.stationary_share])
        self.assertEqual(s.maximisers,(1.0,))
        self.assertGreater(s.maximum,performance(s.stationary_share,'duplication',p))
        expected = (p.H-p.pi+p.franchise_payoff+2*p.vN-p.delta)/(2*(p.vN-p.delta))
        self.assertAlmostEqual(s.stationary_share,expected)

    def test_linear_threshold_and_zero_support(self):
        p = Parameters(delta=.15)
        s = summarise('duplication',p)
        self.assertAlmostEqual(s.curvature,0)
        self.assertIsNone(s.stationary_share)
        self.assertIn('Linear',s.shape)
        s = summarise('overhead',replace(p,v=0))
        self.assertIsNone(s.stationary_share)
        self.assertIn('Linear',s.shape)

    def test_flat_and_tied_endpoints(self):
        p = Parameters(pi=0,c_op=0,H=0,v=0,a=0,delta=0)
        s = summarise('baseline',p)
        self.assertTrue(s.all_shares_tied)
        self.assertEqual(s.maximum,0)
        s = summarise('duplication',replace(p,delta=.6))
        self.assertFalse(s.all_shares_tied)
        self.assertEqual(s.maximisers,(0.,1.))
        self.assertAlmostEqual(s.stationary_share,.5)

    def test_monotone_convex_is_not_called_u_shaped(self):
        p = Parameters(pi=1,H=1.5,v=.1,delta=.2)
        self.assertEqual(summarise('duplication',p).shape,'Convex, increasing')

    def test_analytic_extrema_against_dense_grid(self):
        rng = np.random.default_rng(901)
        grid = np.linspace(0,1,10001)
        for _ in range(80):
            p = Parameters(pi=rng.uniform(0,2),c_op=rng.uniform(0,2),H=rng.uniform(0,2),
                           v=rng.uniform(0,1),N=rng.uniform(.1,10),a=rng.uniform(0,1),
                           theta=rng.uniform(.1,10),delta=rng.uniform(0,1))
            for model in ('baseline','overhead','duplication'):
                s = summarise(model,p)
                ys = performance(grid,model,p)
                self.assertGreaterEqual(s.maximum,ys.max()-1e-11)
                self.assertLessEqual(s.minimum,ys.min()+1e-11)
                self.assertAlmostEqual(s.maximum,float(ys.max()),delta=1e-6)
                self.assertAlmostEqual(s.minimum,float(ys.min()),delta=1e-6)

    def test_support_product_sweep_holds_n_fixed(self):
        p = Parameters(N=2)
        new = with_parameter(p,'vN',.6)
        self.assertEqual(new.N,2)
        self.assertAlmostEqual(new.v,.3)
        self.assertAlmostEqual(new.vN,.6)
        self.assertEqual(new.franchise_payoff,p.franchise_payoff)

    def test_invalid_parameters(self):
        for kwargs in ({'a':1.1},{'N':0},{'theta':0},{'v':-1},{'delta':2},{'pi':float('nan')}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):
                Parameters(**kwargs)

    def test_invalid_domain(self):
        with self.assertRaises(ValueError):
            performance([-.1,.5],'baseline',Parameters())

    def test_unknown_model_and_parameter(self):
        with self.assertRaises(ValueError):
            performance(.5,'missing',Parameters())
        with self.assertRaises(ValueError):
            with_parameter(Parameters(),'missing',1)


if __name__ == '__main__':
    unittest.main()
