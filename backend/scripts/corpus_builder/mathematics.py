"""Mathematics Domain Knowledge Generator.
Comprehensive educational coverage of Arithmetic, Algebra, Geometry, Trigonometry, Probability, Statistics, Linear Algebra, and Calculus.
"""
from __future__ import annotations

def get_mathematics_documents() -> list[dict]:
    data = [
        # --- 1. ARITHMETIC & NUMBER THEORY ---
        ("math-arithmetic-primes", "Prime Numbers, Divisibility, and Fundamental Theorem of Arithmetic", "arithmetic",
         "A prime number is an integer strictly greater than 1 whose only positive divisors are 1 and itself (2, 3, 5, 7, 11...). The Fundamental Theorem of Arithmetic states that every integer n > 1 can be represented uniquely as a product of prime numbers (prime factorization), up to factor ordering. The Euclidean Algorithm computes the Greatest Common Divisor (GCD) of two integers via iterative modulo division: gcd(a, b) = gcd(b, a mod b)."),
        ("math-modular-arithmetic", "Modular Arithmetic and Congruences", "arithmetic",
         "Modular arithmetic performs arithmetic for integers where numbers 'wrap around' upon reaching a fixed modulus m. Two integers a and b are congruent modulo m (denoted a == b (mod m)) if their difference a - b is an integer multiple of m. Modular arithmetic underpins modern public-key cryptography (e.g., RSA, Diffie-Hellman key exchange) via Fermat's Little Theorem: if p is prime, a^(p-1) == 1 (mod p) for gcd(a, p) = 1."),

        # --- 2. ALGEBRA & FUNCTIONS ---
        ("math-algebra-linear-quadratic", "Linear Equations, Quadratic Equations, and Polynomials", "algebra",
         "A linear equation in one variable has the form ax + b = 0 with unique solution x = -b/a. A quadratic equation ax^2 + bx + c = 0 (with a != 0) has two roots given by the quadratic formula x = (-b +- sqrt(b^2 - 4ac)) / (2a). The discriminant Delta = b^2 - 4ac determines root character: Delta > 0 yields two distinct real roots, Delta = 0 yields one repeated real root, and Delta < 0 yields two complex conjugate roots. The Fundamental Theorem of Algebra states every n-degree complex polynomial has exactly n complex roots."),
        ("math-algebra-logarithms-exponents", "Exponents, Exponential Functions, and Logarithms", "algebra",
         "Exponentiation b^x represents repeated multiplication of base b by power x. The logarithm log_b(y) is the inverse operation, answering the question: to what power must base b be raised to produce y (i.e., b^x = y <=> log_b(y) = x). Essential logarithmic properties include log_b(x * y) = log_b(x) + log_b(y), log_b(x / y) = log_b(x) - log_b(y), and log_b(x^k) = k * log_b(x). The natural logarithm ln(x) uses Euler's constant e (approx 2.71828) as its base."),
        ("math-sequences-series", "Arithmetic and Geometric Sequences and Series", "algebra",
         "An arithmetic progression (AP) is a sequence where each term increases by a constant common difference d: a_n = a_1 + (n - 1) * d, with sum S_n = (n/2) * (2*a_1 + (n - 1)*d). A geometric progression (GP) is a sequence where each term is multiplied by a common ratio r: a_n = a_1 * r^(n - 1). For |r| < 1, an infinite geometric series converges to S_infinity = a_1 / (1 - r)."),

        # --- 3. GEOMETRY & TRIGONOMETRY ---
        ("math-geometry-euclidean", "Euclidean Geometry, Triangles, and Pythagorean Theorem", "geometry",
         "Euclidean geometry investigates geometric properties in flat two- and three-dimensional space. The sum of interior angles in any Euclidean triangle is always 180 degrees (pi radians). For any right-angled triangle with legs a, b and hypotenuse c, the Pythagorean Theorem states a^2 + b^2 = c^2. Circle geometry defines circumference C = 2 * pi * r and area A = pi * r^2, where pi is the mathematical ratio of a circle's circumference to its diameter."),
        ("math-trigonometry-functions", "Trigonometric Functions, Unit Circle, and Identities", "trigonometry",
         "Trigonometry studies angles and lengths of triangles. On the Cartesian unit circle centered at (0, 0) with radius 1, a ray at angle theta intersects the circle at coordinates (cos theta, sin theta). The tangent function is tan(theta) = sin(theta) / cos(theta). Fundamental trigonometric identities include the Pythagorean identity sin^2(theta) + cos^2(theta) = 1, double-angle formulas sin(2*theta) = 2*sin(theta)*cos(theta), and cos(2*theta) = cos^2(theta) - sin^2(theta)."),

        # --- 4. CALCULUS ---
        ("math-calculus-limits-derivatives", "Differential Calculus: Limits, Derivatives, and Rules", "calculus",
         "Differential calculus measures instantaneous rates of change. The derivative f'(x) of function f(x) is defined as the limit f'(x) = lim_{h -> 0} (f(x + h) - f(x)) / h, representing the geometric slope of the tangent line to the curve at x. Fundamental differentiation rules include: Power Rule d/dx[x^n] = n * x^(n-1), Product Rule d/dx[u * v] = u' * v + u * v', Quotient Rule d/dx[u / v] = (u' * v - u * v') / v^2, and Chain Rule d/dx[f(g(x))] = f'(g(x)) * g'(x)."),
        ("math-calculus-integrals", "Integral Calculus and Fundamental Theorem of Calculus", "calculus",
         "Integral calculus calculates the continuous accumulation of quantities, such as areas under curves, volumes of solids, and physical work. The definite integral int_a^b f(x) dx computes net signed area as the limit of Riemann sums. The Fundamental Theorem of Calculus links differentiation and integration: Part 1 states d/dx[ int_a^x f(t) dt ] = f(x); Part 2 states int_a^b f(x) dx = F(b) - F(a), where F'(x) = f(x) is the antiderivative of f."),
        ("math-calculus-multivariable", "Multivariable Calculus: Partial Derivatives, Gradients, and Jacobians", "calculus",
         "Multivariable calculus extends calculus to functions of multiple variables f(x1, x2, ..., xn). A partial derivative partial f / partial x_i measures change along a single coordinate axis while holding other variables constant. The Gradient vector grad(f) = [partial f / partial x1, ..., partial f / partial xn]^T points in the direction of steepest ascent with magnitude equal to the rate of increase. The Jacobian matrix contains all first-order partial derivatives of a vector-valued function, essential for neural network backpropagation."),

        # --- 5. LINEAR ALGEBRA ---
        ("math-linear-algebra-matrices", "Linear Algebra: Vectors, Matrices, and Matrix Operations", "linear_algebra",
         "Linear algebra studies linear equations, vector spaces, and linear transformations. A matrix A in R^(m x n) maps vectors from R^n to R^m. Matrix multiplication C = A * B requires the number of columns in A to match the rows in B, where entry C_{ij} = sum_k A_{ik} * B_{kj}. Transposition flips rows and columns: (A^T)_{ij} = A_{ji}. An identity matrix I acts as the multiplicative identity: A * I = A."),
        ("math-linear-algebra-eigenvalues", "Determinants, Matrix Inverses, and Eigenvalues", "linear_algebra",
         "The determinant det(A) of a square matrix A is a scalar reflecting how the matrix scales volume; A is invertible (non-singular) if and only if det(A) != 0. An eigenvector v (non-zero) and scalar eigenvalue lambda satisfy the characteristic equation A * v = lambda * v (or det(A - lambda * I) = 0). Eigendecomposition factorizes diagonalizable matrices as A = Q * Lambda * Q^(-1), fundamental in PCA, spectral graph theory, and quantum mechanics."),

        # --- 6. PROBABILITY & STATISTICS ---
        ("math-prob-axioms-bayes", "Probability Theory, Conditional Probability, and Bayes' Theorem", "probability_statistics",
         "Probability quantifies the likelihood of events in sample space Omega. Kolmogorov's axioms state: P(E) >= 0, P(Omega) = 1, and for mutually exclusive events, P(A U B) = P(A) + P(B). Conditional probability P(A|B) = P(A n B) / P(B) measures the probability of A given B. Bayes' Theorem updates prior belief P(A) with observed evidence B to compute posterior probability: P(A|B) = (P(B|A) * P(A)) / P(B)."),
        ("math-stats-distributions", "Statistical Distributions, Expectation, and Variance", "probability_statistics",
         "A random variable X has probability density function f(x). Expected value E[X] = mu measures the central probability-weighted mean; Variance Var(X) = sigma^2 = E[(X - mu)^2] measures dispersion, with standard deviation sigma = sqrt(Var(X)). The Normal (Gaussian) Distribution N(mu, sigma^2) has the bell-shaped curve f(x) = (1 / (sigma * sqrt(2*pi))) * e^(-(x-mu)^2 / (2*sigma^2)). The Central Limit Theorem proves the normalized sum of independent random variables approaches a normal distribution as n -> infinity."),

        # --- 7. DISCRETE MATHEMATICS & LOGIC ---
        ("math-discrete-set-theory-logic", "Set Theory, Propositional Logic, and Proof Techniques", "discrete_math",
         "Set theory provides the foundational language of mathematics: sets, subsets (A subseteq B), unions (A U B), intersections (A n B), set difference (A \\ B), and Cartesian products (A x B). Propositional logic evaluates truth values using boolean connectives: Conjunction (AND), Disjunction (OR), Negation (NOT), and Implication (P -> Q). Standard mathematical proof techniques include Direct Proof, Proof by Contradiction (reductio ad absurdum assuming not-P), and Mathematical Induction.")
    ]
    docs = []
    for doc_id, title, topic, text in data:
        docs.append({
            "document_id": doc_id,
            "passage_id": f"{doc_id}-1",
            "title": title,
            "domain": "mathematics",
            "topic": topic,
            "language": "en",
            "source_type": "curated",
            "keywords": [k.lower() for k in title.split()],
            "text": text
        })
    return docs
