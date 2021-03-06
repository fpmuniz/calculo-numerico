import unittest

import numpy as np

from numerico import linalg


class LinalgTest(unittest.TestCase):
    def setUp(self):
        self.A = np.array([[1,5],[-2,15]])
        self.S = np.array([[1,2], [2,4]])
        self.L = np.array([[1,0], [2,4]])
        self.U = np.array([[1,1],[0,9]])
        self.A2 = np.array([[ 5, -1,  2],
                            [-1,  8,  4],
                            [ 2,  4,  10]])
        self.X = self.A @ self.A.T

    def test_gauss(self):
        b = np.array([ 3, -5, -8])
        x, det = linalg.gauss(self.A2, b)
        self.assertTrue((x == [1,0,-1]).all())

    def test_lu(self):
        dec = linalg.LU(self.A)
        self.assertEqual(dec.det, 25)
        self.assertTrue(((self.A @ dec.inv()).round(5) == np.identity(2)).all())

    def test_lu_refine(self):
        dec = linalg.LU(self.A2, precision=2)
        b = np.array([3, -5, -8])
        x0 = dec.solve(b)
        x = dec.refine(b, x0)
        self.assertTrue((x.round(2) == [1,0,-1]).all())

    def test_lu_singular_det(self):
        S = np.array([[ -3,   3,   4,   2,   7],
                      [  0,   7,  -3,  -5,   1],
                      [ -3,  -5,   5,   6,  -1],
                      [ -9, -14,  17,  19,   4],
                      [-15, -72,  50,  67,   2]])
        dec = linalg.LU(S)
        self.assertEqual(round(dec.det, 6), 0)

    def test_cholesky(self):
        dec = linalg.Cholesky(self.X)
        L = dec.L
        mult = (L @ L.T).round()
        self.assertTrue((mult == self.X).all())

    def test_cholesky_refine(self):
        dec = linalg.Cholesky(self.A2, precision=2)
        b = np.array([3, -5, -8])
        x0 = dec.solve(b)
        x = dec.refine(b, x0)
        self.assertTrue((x.round(2) == [1,0,-1]).all())

    def test_cholesky_det(self):
        dec = linalg.Cholesky(self.X)
        self.assertEqual(round(dec.det, 4), 625)

    def test_cholesky_solve(self):
        b = np.array([1,2])
        dec = linalg.Cholesky(self.X)
        x = dec.solve(b)
        r = (self.X @ x - b).round(4)
        self.assertEqual(r.sum(), 0)

    def test_cholesky_inv(self):
        dec = linalg.Cholesky(self.X)
        inv = dec.inv()
        e = np.identity(2)
        r = inv @ self.X - e
        r = r.round(4)
        self.assertEqual(r.sum(), 0)

    def test_is_lower_trig(self):
        self.assertTrue(linalg.is_lower_trig(self.L))
        self.assertFalse(linalg.is_lower_trig(self.A))
        self.assertFalse(linalg.is_lower_trig(self.U))

    def test_is_upper_trig(self):
        self.assertTrue(linalg.is_upper_trig(self.U))
        self.assertFalse(linalg.is_upper_trig(self.A))
        self.assertFalse(linalg.is_upper_trig(self.L))

    def test_successive_substitutions(self):
        b = np.array([1,10])
        x = linalg.successive_substitutions(self.L, b)
        self.assertTrue((x == [1,2]).all())

    def test_retroactive_substitutions(self):
        b = np.array([2,9])
        x = linalg.retroactive_substitutions(self.U, b)
        self.assertTrue((x == [1,1]).all())

    def test_ldlt(self):
        dec = linalg.LDLt(self.A2, precision=4)
        out = dec.ldlt
        expected = np.array([[ 5.,     -0.2,     0.4   ],
                             [-0.2,     7.8,     0.5641],
                             [ 0.4,     0.5641,  6.718 ]])
        self.assertTrue((out == expected).all())

    def test_ldlt_solve(self):
        b = np.array([1,2,3])
        dec = linalg.LDLt(self.A2)
        x = dec.solve(b)
        r = self.A2 @ x - b
        r = r.round(4)
        self.assertEqual(r.sum(), 0)

    def test_ldlt_inv(self):
        dec = linalg.LDLt(self.A2)
        inv = dec.inv()
        e = np.identity(3)
        r = e - inv @ self.A2
        r = r.round(4)
        self.assertEqual(r.sum(), 0)

    def test_ldlt_det(self):
        dec = linalg.LDLt(self.A2)
        self.assertEqual(round(dec.det), 262)

    def test_ldlt_refine(self):
        dec = linalg.LDLt(self.A2, precision=2)
        b = np.array([3, -5, -8])
        x0 = dec.solve(b)
        x = dec.refine(b, x0)
        self.assertTrue((x.round(2) == [1,0,-1]).all())

    def test_jacobi(self):
        jacobi = linalg.Jacobi(self.A2)
        x = jacobi.solve(np.array([3,-4,6]))
        self.assertTrue(jacobi.converges)
        self.assertTrue((x.round() == [0,-1,1]).all())

    def test_gauss_seidel(self):
        gs = linalg.GaussSeidel(self.A2)
        x = gs.solve(np.array([3,-4,6]))
        self.assertTrue(gs.converges)
        self.assertTrue((x.round() == [0,-1,1]).all())

    def test_sor(self):
        sor = linalg.SOR(self.A, omega=1.2)
        b = np.array([-5, -15])
        x = sor.solve(b)
        self.assertFalse(sor.converges)
        self.assertTrue((x.round() == [0, -1]).all())

    def test_krylov(self):
        coefs = linalg.krylov_poly(self.A)
        delta = (39)**0.5
        lambda1 = 8 - delta # autovalor 1
        lambda2 = 8 + delta # autovalor 2
        self.assertEqual(coefs(lambda1), 0)
        self.assertEqual(coefs(lambda2), 0)


if __name__ == '__main__':
    unittest.main()
