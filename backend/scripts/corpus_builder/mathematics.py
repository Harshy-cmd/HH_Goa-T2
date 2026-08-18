"""Mathematics Domain Knowledge Generator.
Comprehensive educational coverage of Arithmetic, Algebra, Geometry, Trigonometry, Probability, Statistics, and Calculus.
"""
from __future__ import annotations

def get_mathematics_documents() -> list[dict]:
    data = [
        ("math-arithmetic-primes", "Prime Numbers and Fundamental Theorem of Arithmetic", "arithmetic",
         "A prime number is a natural number strictly greater than 1 that cannot be formed by multiplying two smaller natural numbers. The Fundamental Theorem of Arithmetic states that every integer greater than 1 either is a prime itself or can be uniquely represented as a product of prime numbers, up to the order of the factors."),
        ("math-algebra-equations", "Algebraic Equations and Polynomials", "algebra",
         "Algebra studies mathematical symbols and the rules for manipulating these symbols in equations. Linear equations (ax + b = 0) represent straight lines, while quadratic equations (ax^2 + bx + c = 0) are solved using the quadratic formula x = (-b +- sqrt(b^2 - 4ac)) / (2a). The Fundamental Theorem of Algebra guarantees that every non-zero single-variable polynomial of degree n with complex coefficients has exactly n complex roots."),
        ("math-geometry-euclidean", "Euclidean Geometry and the Pythagorean Theorem", "geometry",
         "Euclidean geometry investigates flat space relations involving points, lines, angles, and surfaces. For any right-angled triangle with legs of length a and b and hypotenuse c, the Pythagorean Theorem states that a^2 + b^2 = c^2. Circle geometry relates circumference (C = 2*pi*r) and area (A = pi*r^2) to radius r."),
        ("math-trigonometry", "Trigonometric Functions and the Unit Circle", "trigonometry",
         "Trigonometry studies relationships between side lengths and angles of triangles. The primary trigonometric functions—sine, cosine, and tangent—are defined geometrically on the Cartesian unit circle where a point at angle theta has coordinates (cos theta, sin theta). Fundamental identities include sin^2(theta) + cos^2(theta) = 1 and tan(theta) = sin(theta) / cos(theta)."),
        ("math-calculus-derivatives", "Differential Calculus and Derivatives", "calculus",
         "Differential calculus is the mathematical study of the rates at which quantities change. The derivative of a function f(x) measures the instantaneous rate of change and slope of the tangent line at x, formally defined as the limit of (f(x + h) - f(x)) / h as h approaches 0. Essential differentiation rules include the Power Rule, Product Rule, Quotient Rule, and Chain Rule."),
        ("math-calculus-integrals", "Integral Calculus and Fundamental Theorem of Calculus", "calculus",
         "Integral calculus studies the accumulation of quantities, such as areas under curves, volumes, and total displacements. Definite integrals compute accumulated sums via Riemann sums. The Fundamental Theorem of Calculus links differentiation and integration, stating that integration can be reversed by differentiation."),
        ("math-linear-algebra-matrices", "Linear Algebra, Vectors, and Matrices", "linear_algebra",
         "Linear algebra is the branch of mathematics concerning vector spaces, linear transformations, matrices, and systems of linear equations. A matrix represents a linear transformation between coordinate spaces. Core concepts include matrix multiplication, determinants, matrix inverses, and eigenvalues lambda satisfying A*v = lambda*v for eigenvector v."),
        ("math-prob-stats", "Probability Theory, Bayes' Theorem, and Statistics", "probability_statistics",
         "Probability theory quantifies the likelihood of random events occurring on a scale from 0 (impossible) to 1 (certain). Bayes' Theorem computes conditional probability: P(A|B) = (P(B|A) * P(A)) / P(B). Descriptive statistics summarizes data distributions using measures of central tendency (mean, median, mode) and dispersion (variance, standard deviation)."),
        ("math-set-theory", "Set Theory and Propositional Logic", "discrete_math",
         "Set theory is the fundamental mathematical language concerning collections of objects called sets. Basic set operations include union (A U B), intersection (A n B), set difference (A \\ B), and Cartesian products. Propositional logic uses truth tables and logical connectives (AND, OR, NOT, IMPLIES) to establish valid deductive reasoning.")
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
