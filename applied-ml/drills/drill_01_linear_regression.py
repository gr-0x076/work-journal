"""
Level 1 - Track A: First-Principles Drill 01
Linear Regression From Scratch (Pure NumPy)

Run this drill using:
    /home/mohith/.gemini/antigravity/scratch/venv/bin/python3 drill_01_linear_regression.py

Objectives:
1. Implement closed-form Normal Equations: w = (X^T X)^{-1} X^T y.
2. Implement vectorized Batch Gradient Descent.
3. Compare weights and predictions against Scikit-Learn's LinearRegression.
"""

import numpy as np
from typing import Tuple


class ScratchLinearRegression:
    def __init__(self):
        self.weights: np.ndarray = None  # shape: (D,)
        self.bias: float = 0.0           # scalar
        self.loss_history: list = []

    def fit_normal_equations(self, X: np.ndarray, y: np.ndarray) -> "ScratchLinearRegression":
        """
        Solves Ordinary Least Squares using the closed-form Normal Equations.
        
        Mathematical Formulation:
        Augment X with a column of 1s for the bias: X_aug = [X, 1].
        Then: theta = (X_aug^T X_aug)^{-1} X_aug^T y
        Where theta = [weights, bias].
        
        Requirements:
        - X shape: (N, D), y shape: (N,)
        - Use np.linalg.pinv() or np.linalg.inv() for matrix inversion.
        - Set self.weights to theta[:-1] and self.bias to theta[-1].
        """
        N = X.shape[0]

        X_aug = np.c_[X, np.ones(N)]

        theta = np.linalg.pinv(X_aug.T @ X_aug) @ X_aug.T @ y

        self.weights = theta[:-1]
        self.bias = theta[-1]
        return self


    def fit_gradient_descent(
        self, X: np.ndarray, y: np.ndarray, lr: float = 0.05, epochs: int = 1000
    ) -> "ScratchLinearRegression":
        """
        Fits weights and bias using vectorized Batch Gradient Descent.
        
        Loss: L = (1 / (2 * N)) * sum( (X w + b - y)^2 )
        Gradients:
            dL/dw = (1 / N) * X^T (y_pred - y)
            dL/db = (1 / N) * sum(y_pred - y)
            
        Requirements:
        - Zero loops across samples (vectorized).
        - Record MSE loss at each epoch into self.loss_history.
        """
        N,D = X.shape

        self.weights = np.zeros(D)
        self.bias = 0.0
        self.loss_history = []

        for epoch in range(epochs):
            y_pred = X @ self.weights + self.bias

            error = y_pred - y

            dw = (X.T @ error) / N
            db = np.mean(error)


                    # Update parameters
            self.weights -= lr * dw
            self.bias -= lr * db

            # Record MSE after update
            updated_pred = X @ self.weights + self.bias
            mse = np.mean((updated_pred - y) ** 2)

            self.loss_history.append(mse)

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return X @ self.weights + self.bias


# =====================================================================
# Verification Test Suite
# =====================================================================
def run_tests():
    print("=" * 60)
    print("Running Drill 01: Linear Regression From Scratch...")
    print("=" * 60)
    
    from sklearn.linear_model import LinearRegression
    np.random.seed(42)
    
    # Generate synthetic regression data: y = 3.5 * x1 - 2.0 * x2 + 1.2 + noise
    N, D = 200, 2
    X = np.random.randn(N, D)
    true_w = np.array([3.5, -2.0])
    true_b = 1.2
    y = X @ true_w + true_b + 0.05 * np.random.randn(N)
    
    # Scikit-Learn Ground Truth
    sk_model = LinearRegression().fit(X, y)
    
    # Test 1: Normal Equations
    print("\n[Test 1] Testing Normal Equations closed-form solution...")
    try:
        model_ne = ScratchLinearRegression().fit_normal_equations(X, y)
        preds_ne = model_ne.predict(X)
        
        assert np.allclose(model_ne.weights, sk_model.coef_, atol=1e-4), (
            f"Weights mismatch! Expected {sk_model.coef_}, got {model_ne.weights}"
        )
        assert np.isclose(model_ne.bias, sk_model.intercept_, atol=1e-4), (
            f"Bias mismatch! Expected {sk_model.intercept_:.4f}, got {model_ne.bias:.4f}"
        )
        print(">> Test 1 PASSED: Normal Equations match Scikit-Learn within 1e-4.")
    except NotImplementedError:
        print(">> Test 1 SKIPPED: fit_normal_equations not implemented yet.")
    except Exception as e:
        print(f">> Test 1 FAILED: {e}")

    # Test 2: Gradient Descent
    print("\n[Test 2] Testing Batch Gradient Descent...")
    try:
        model_gd = ScratchLinearRegression().fit_gradient_descent(X, y, lr=0.1, epochs=1500)
        preds_gd = model_gd.predict(X)
        
        assert len(model_gd.loss_history) == 1500, "Loss history not tracked per epoch!"
        assert model_gd.loss_history[-1] < model_gd.loss_history[0], "Loss did not decrease during gradient descent!"
        assert np.allclose(model_gd.weights, sk_model.coef_, atol=1e-2), (
            f"Weights mismatch! Expected {sk_model.coef_}, got {model_gd.weights}"
        )
        assert np.isclose(model_gd.bias, sk_model.intercept_, atol=1e-2), (
            f"Bias mismatch! Expected {sk_model.intercept_:.4f}, got {model_gd.bias:.4f}"
        )
        print(">> Test 2 PASSED: Gradient Descent converged cleanly to true parameters.")
    except NotImplementedError:
        print(">> Test 2 SKIPPED: fit_gradient_descent not implemented yet.")
    except Exception as e:
        print(f">> Test 2 FAILED: {e}")

    print("\n" + "=" * 60)
    print("End of Drill 01.")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
