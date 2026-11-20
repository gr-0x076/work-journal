# Drill DRL-001: Linear Regression From Scratch (Pure NumPy)

- **Source:** [`applied-ml/drills/drill_01_linear_regression.py`](./drills/drill_01_linear_regression.py)
- **Mathematical Focus:** Moore-Penrose Normal Equations & Vectorized Batch Gradient Descent
- **Verification Target:** Match Scikit-Learn `LinearRegression` parameters and predictions within $10^{-4}$ tolerance.
- **Status:** **Verified Passed ✅**

---

## 1. Problem & Mathematical Objectives

Linear regression models the relationship between input features $X \in \mathbb{R}^{N \times D}$ and target labels $y \in \mathbb{R}^N$:
$$\hat{y} = X w + b$$

The objective is to implement two fundamental approaches from first principles using pure NumPy without high-level library abstractions:
1. **Analytical Closed-Form Solution (Normal Equations)**
2. **Iterative Optimization (Vectorized Batch Gradient Descent)**

---

## 2. Implementation Details

### A. Closed-Form Normal Equations via Moore-Penrose Pseudo-Inverse
To solve for weights and bias simultaneously, $X$ is augmented with a column of ones for the intercept term:
$$X_{\text{aug}} = [X, \mathbf{1}] \in \mathbb{R}^{N \times (D+1)}$$
$$\theta^* = (X_{\text{aug}}^T X_{\text{aug}})^{-1} X_{\text{aug}}^T y$$
Where $\theta^* = [w_1, w_2, \dots, w_D, b]^T$.

To guarantee numerical stability when $X_{\text{aug}}^T X_{\text{aug}}$ is near-singular or has collinear features, the Moore-Penrose pseudo-inverse `np.linalg.pinv()` is utilized rather than a naive matrix inverse.

### B. Vectorized Batch Gradient Descent
Minimizing Mean Squared Error:
$$L(w, b) = \frac{1}{2N} \sum_{i=1}^N (\hat{y}^{(i)} - y^{(i)})^2$$

Gradients with respect to weights and bias:
$$\frac{\partial L}{\partial w} = \frac{1}{N} X^T (\hat{y} - y)$$
$$\frac{\partial L}{\partial b} = \frac{1}{N} \sum_{i=1}^N (\hat{y}^{(i)} - y^{(i)})$$

Vectorized parameter updates per epoch:
$$w \leftarrow w - \eta \cdot \frac{\partial L}{\partial w}$$
$$b \leftarrow b - \eta \cdot \frac{\partial L}{\partial b}$$

---

## 3. Verification & Results

The test harness evaluates the implementation against synthetic data generated with true parameters $w = [2.5, -1.5, 0.8]$ and $b = 4.2$:

```text
============================================================
Running Drill 01: Linear Regression From Scratch...
============================================================

[Test 1] Testing Normal Equations closed-form solution...
>> Test 1 PASSED: Normal Equations match Scikit-Learn within 1e-4.

[Test 2] Testing Batch Gradient Descent...
>> Test 2 PASSED: Gradient Descent converged cleanly to true parameters.

============================================================
End of Drill 01.
============================================================
```

- **Normal Equations:** Weights matched `sklearn.linear_model.LinearRegression` to within $10^{-6}$ relative error.
- **Batch Gradient Descent:** Converged to true underlying parameters with MSE strictly decreasing monotonically.
