import random
import re

import sympy as sp

from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)


# =========================================================
# SYMPY SETUP
# =========================================================

x, t, y = sp.symbols(
    "x t y",
    real=True,
)

TRANSFORMATIONS = (
    standard_transformations
    + (
        implicit_multiplication_application,
        convert_xor,
    )
)

LOCAL_DICT = {
    "x": x,
    "t": t,
    "y": y,

    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,

    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,

    "sqrt": sp.sqrt,

    "exp": sp.exp,

    "e": sp.E,
    "E": sp.E,

    "ln": sp.log,
    "log": sp.log,

    "pi": sp.pi,
}


# =========================================================
# QUESTION BANK
# =========================================================

QUESTIONS = [

    # =====================================================
    # POWER RULE
    # =====================================================

    {
        "skill": "Differentiation",
        "topic": "Power Rule",
        "difficulty": 1,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y = 5x^3\).",

        "answers": [
            "15*x^2",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=15x^2",

        "hints": [
            r"Use the power rule \( \frac{d}{dx}(x^n)=nx^{n-1} \).",
            r"Multiply \(5\) by the exponent \(3\).",
            r"Reduce the exponent from \(3\) to \(2\).",
        ],

        "solution": [
            r"Start with \(y=5x^3\).",
            r"Using the power rule, \( \frac{d}{dx}(x^3)=3x^2 \).",
            r"Therefore \( \frac{dy}{dx}=5(3x^2)=15x^2 \).",
        ],
    },

    {
        "skill": "Differentiation",
        "topic": "Power Rule",
        "difficulty": 1,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y = 4x^5-3x^2+7\).",

        "answers": [
            "20*x^4-6*x",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=20x^4-6x",

        "hints": [
            r"Differentiate each term separately.",
            r"The derivative of the constant \(7\) is \(0\).",
            r"Use the power rule on \(4x^5\) and \(-3x^2\).",
        ],

        "solution": [
            r"The derivative of \(4x^5\) is \(20x^4\).",
            r"The derivative of \(-3x^2\) is \(-6x\).",
            r"The derivative of \(7\) is \(0\).",
            r"Therefore \( \frac{dy}{dx}=20x^4-6x \).",
        ],
    },


    # =====================================================
    # CHAIN RULE
    # =====================================================

    {
        "skill": "Differentiation",
        "topic": "Chain Rule",
        "difficulty": 2,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=(2x+1)^4\).",

        "answers": [
            "8*(2*x+1)^3",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=8(2x+1)^3",

        "hints": [
            r"Identify an outer function and an inner function.",
            r"Differentiate the outer power first.",
            r"Remember to multiply by the derivative of \(2x+1\).",
        ],

        "solution": [
            r"Let \(u=2x+1\), so \(y=u^4\).",
            r"Then \( \frac{dy}{du}=4u^3 \).",
            r"Also \( \frac{du}{dx}=2 \).",
            r"Therefore \( \frac{dy}{dx}=4(2x+1)^3(2)=8(2x+1)^3 \).",
        ],
    },

    {
        "skill": "Differentiation",
        "topic": "Chain Rule",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=(3x^2+1)^5\).",

        "answers": [
            "30*x*(3*x^2+1)^4",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=30x(3x^2+1)^4",

        "hints": [
            r"The inner function is \(3x^2+1\).",
            r"Differentiate the outer fifth power first.",
            r"The derivative of \(3x^2+1\) is \(6x\).",
        ],

        "solution": [
            r"Let \(u=3x^2+1\), so \(y=u^5\).",
            r"Then \( \frac{dy}{du}=5u^4 \).",
            r"Also \( \frac{du}{dx}=6x \).",
            r"Therefore \( \frac{dy}{dx}=5(3x^2+1)^4(6x) \).",
            r"Hence \( \frac{dy}{dx}=30x(3x^2+1)^4 \).",
        ],
    },


    # =====================================================
    # QUOTIENT RULE
    # =====================================================

    {
        "skill": "Differentiation",
        "topic": "Quotient Rule",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=\frac{x^2+1}{x}\).",

        "answers": [
            "1-1/x^2",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=1-\frac{1}{x^2}",

        "hints": [
            r"You can use the quotient rule or simplify first.",
            r"Rewrite the function as \(y=x+x^{-1}\).",
            r"Differentiate \(x\) and \(x^{-1}\) separately.",
        ],

        "solution": [
            r"Rewrite \( \frac{x^2+1}{x}=x+\frac{1}{x} \).",
            r"So \(y=x+x^{-1}\).",
            r"Differentiate to obtain \(1-x^{-2}\).",
            r"Therefore \( \frac{dy}{dx}=1-\frac{1}{x^2} \).",
        ],
    },

    {
        "skill": "Differentiation",
        "topic": "Quotient Rule",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=\frac{x+1}{x-1}\).",

        "answers": [
            "-2/(x-1)^2",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=-\frac{2}{(x-1)^2}",

        "hints": [
            r"Use the quotient rule.",
            r"For \(y=\frac{u}{v}\), use \( \frac{vu'-uv'}{v^2} \).",
            r"Here \(u=x+1\) and \(v=x-1\).",
        ],

        "solution": [
            r"Take \(u=x+1\) and \(v=x-1\).",
            r"Then \(u'=1\) and \(v'=1\).",
            r"So \(y'=\frac{(x-1)(1)-(x+1)(1)}{(x-1)^2}\).",
            r"The numerator simplifies to \(-2\).",
            r"Therefore \( \frac{dy}{dx}=-\frac{2}{(x-1)^2} \).",
        ],
    },


    # =====================================================
    # TRIGONOMETRIC DIFFERENTIATION
    # =====================================================

    {
        "skill": "Differentiation",
        "topic": "Trigonometric Differentiation",
        "difficulty": 2,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=\sin x\).",

        "answers": [
            "cos(x)",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=\cos x",

        "hints": [
            r"Recall the standard derivative of sine.",
            r"The derivative remains a trigonometric function.",
            r"The derivative of \(\sin x\) is \(\cos x\).",
        ],

        "solution": [
            r"Use the standard result \( \frac{d}{dx}(\sin x)=\cos x \).",
            r"Therefore \( \frac{dy}{dx}=\cos x \).",
        ],
    },

    {
        "skill": "Differentiation",
        "topic": "Trigonometric Differentiation",
        "difficulty": 2,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=\cos x\).",

        "answers": [
            "-sin(x)",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=-\sin x",

        "hints": [
            r"Recall the derivative of cosine.",
            r"Pay attention to the sign.",
            r"The derivative contains \(-\sin x\).",
        ],

        "solution": [
            r"Use \( \frac{d}{dx}(\cos x)=-\sin x \).",
            r"Therefore \( \frac{dy}{dx}=-\sin x \).",
        ],
    },

    {
        "skill": "Differentiation",
        "topic": "Trigonometric Differentiation",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=\sin(3x)\).",

        "answers": [
            "3*cos(3*x)",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=3\cos(3x)",

        "hints": [
            r"This requires the chain rule.",
            r"Differentiate \(\sin u\) first.",
            r"The derivative of the inner function \(3x\) is \(3\).",
        ],

        "solution": [
            r"Let \(u=3x\).",
            r"Then \( \frac{d}{dx}(\sin u)=\cos u\frac{du}{dx} \).",
            r"Since \(du/dx=3\), the result is \(3\cos(3x)\).",
        ],
    },


    # =====================================================
    # EXPONENTIAL DIFFERENTIATION
    # =====================================================

    {
        "skill": "Differentiation",
        "topic": "Exponential Differentiation",
        "difficulty": 2,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=e^{3x}\).",

        "answers": [
            "3*e^(3*x)",
            "3*exp(3*x)",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=3e^{3x}",

        "hints": [
            r"Use the chain rule.",
            r"The derivative of \(e^u\) is \(e^u u'\).",
            r"The derivative of \(3x\) is \(3\).",
        ],

        "solution": [
            r"Let \(u=3x\).",
            r"Then \( \frac{d}{dx}(e^u)=e^u\frac{du}{dx} \).",
            r"Since \(du/dx=3\), \( \frac{dy}{dx}=3e^{3x} \).",
        ],
    },

    {
        "skill": "Differentiation",
        "topic": "Exponential Differentiation",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=e^{x^2}\).",

        "answers": [
            "2*x*e^(x^2)",
            "2*x*exp(x^2)",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=2xe^{x^2}",

        "hints": [
            r"Use the chain rule.",
            r"The inner function is \(x^2\).",
            r"The derivative of \(x^2\) is \(2x\).",
        ],

        "solution": [
            r"Let \(u=x^2\).",
            r"Then \(dy/du=e^u\) and \(du/dx=2x\).",
            r"Therefore \( \frac{dy}{dx}=2xe^{x^2} \).",
        ],
    },


    # =====================================================
    # LOGARITHMS
    # =====================================================

    {
        "skill": "Differentiation",
        "topic": "Logarithmic Differentiation",
        "difficulty": 2,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=\ln x\).",

        "answers": [
            "1/x",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=\frac{1}{x}",

        "hints": [
            r"Recall the standard derivative of \(\ln x\).",
            r"The answer is a reciprocal.",
            r"The denominator is \(x\).",
        ],

        "solution": [
            r"Use \( \frac{d}{dx}(\ln x)=\frac{1}{x} \).",
            r"Therefore \( \frac{dy}{dx}=\frac{1}{x} \).",
        ],
    },

    {
        "skill": "Differentiation",
        "topic": "Logarithmic Differentiation",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=\ln(2x+1)\).",

        "answers": [
            "2/(2*x+1)",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=\frac{2}{2x+1}",

        "hints": [
            r"Use the chain rule.",
            r"For \(y=\ln u\), the derivative is \(u'/u\).",
            r"Here \(u=2x+1\) and \(u'=2\).",
        ],

        "solution": [
            r"Let \(u=2x+1\).",
            r"Then \( \frac{d}{dx}(\ln u)=\frac{u'}{u} \).",
            r"Therefore \( \frac{dy}{dx}=\frac{2}{2x+1} \).",
        ],
    },


    # =====================================================
    # INVERSE TRIGONOMETRIC
    # =====================================================

    {
        "skill": "Differentiation",
        "topic": "Inverse Trigonometric Differentiation",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=\sin^{-1}x\).",

        "answers": [
            "1/sqrt(1-x^2)",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=\frac{1}{\sqrt{1-x^2}}",

        "hints": [
            r"Recall the derivative of inverse sine.",
            r"The denominator contains a square root.",
            r"The expression inside the root is \(1-x^2\).",
        ],

        "solution": [
            r"Use the standard result for inverse sine.",
            r"\( \frac{d}{dx}(\sin^{-1}x)=\frac{1}{\sqrt{1-x^2}} \).",
        ],
    },

    {
        "skill": "Differentiation",
        "topic": "Inverse Trigonometric Differentiation",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"Differentiate \(y=\tan^{-1}x\).",

        "answers": [
            "1/(1+x^2)",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=\frac{1}{1+x^2}",

        "hints": [
            r"Recall the inverse tangent derivative.",
            r"The denominator contains \(1+x^2\).",
            r"No square root is required.",
        ],

        "solution": [
            r"Use the standard result \( \frac{d}{dx}(\tan^{-1}x)=\frac{1}{1+x^2} \).",
        ],
    },


    # =====================================================
    # PARAMETRIC
    # =====================================================

    {
        "skill": "Differentiation",
        "topic": "Parametric Differentiation",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"If \(x=t^2\) and \(y=t^3\), find \(\frac{dy}{dx}\).",

        "answers": [
            "3*t/2",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=\frac{3t}{2}",

        "hints": [
            r"Differentiate both \(x\) and \(y\) with respect to \(t\).",
            r"Use \( \frac{dy}{dx}=\frac{dy/dt}{dx/dt} \).",
            r"Here \(dy/dt=3t^2\) and \(dx/dt=2t\).",
        ],

        "solution": [
            r"\(dx/dt=2t\).",
            r"\(dy/dt=3t^2\).",
            r"Therefore \( \frac{dy}{dx}=\frac{3t^2}{2t}=\frac{3t}{2} \).",
        ],
    },

    {
        "skill": "Differentiation",
        "topic": "Parametric Differentiation",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"If \(x=2t+1\) and \(y=t^2\), find \(\frac{dy}{dx}\).",

        "answers": [
            "t",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=t",

        "hints": [
            r"Calculate \(dx/dt\) and \(dy/dt\).",
            r"Then divide \(dy/dt\) by \(dx/dt\).",
            r"You should obtain \(2t/2\).",
        ],

        "solution": [
            r"\(dx/dt=2\).",
            r"\(dy/dt=2t\).",
            r"Therefore \( \frac{dy}{dx}=\frac{2t}{2}=t \).",
        ],
    },


    # =====================================================
    # IMPLICIT DIFFERENTIATION
    # =====================================================

    {
        "skill": "Differentiation",
        "topic": "Implicit Differentiation",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"For \(x^2+y^2=25\), find \(\frac{dy}{dx}\).",

        "answers": [
            "-x/y",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=-\frac{x}{y}",

        "hints": [
            r"Differentiate both sides with respect to \(x\).",
            r"Remember that \(y\) depends on \(x\).",
            r"The derivative of \(y^2\) is \(2y\frac{dy}{dx}\).",
        ],

        "solution": [
            r"Differentiate to get \(2x+2y\frac{dy}{dx}=0\).",
            r"So \(2y\frac{dy}{dx}=-2x\).",
            r"Therefore \( \frac{dy}{dx}=-\frac{x}{y} \).",
        ],
    },


    # =====================================================
    # KINEMATICS
    # =====================================================

    {
        "skill": "Differentiation",
        "topic": "Kinematics",
        "difficulty": 2,
        "answer_type": "expression",

        "question":
            r"A particle has displacement \(s=4t^3-2t\). Find its velocity \(v(t)\).",

        "answers": [
            "12*t^2-2",
        ],

        "final_answer_latex":
            r"v(t)=12t^2-2",

        "hints": [
            r"Velocity is the derivative of displacement.",
            r"Use \(v=\frac{ds}{dt}\).",
            r"Differentiate each term with respect to \(t\).",
        ],

        "solution": [
            r"\(s=4t^3-2t\).",
            r"Differentiate with respect to \(t\).",
            r"\(v(t)=12t^2-2\).",
        ],
    },

    {
        "skill": "Differentiation",
        "topic": "Kinematics",
        "difficulty": 2,
        "answer_type": "expression",

        "question":
            r"A particle has velocity \(v=6t^2-4t+3\). Find its acceleration \(a(t)\).",

        "answers": [
            "12*t-4",
        ],

        "final_answer_latex":
            r"a(t)=12t-4",

        "hints": [
            r"Acceleration is the derivative of velocity.",
            r"Use \(a=\frac{dv}{dt}\).",
            r"Differentiate \(6t^2-4t+3\).",
        ],

        "solution": [
            r"\(v=6t^2-4t+3\).",
            r"Differentiate with respect to \(t\).",
            r"Therefore \(a(t)=12t-4\).",
        ],
    },


    # =====================================================
    # GRADIENT INTERPRETATION
    # =====================================================

    {
        "skill": "Gradient Interpretation",
        "topic": "Gradient Interpretation",
        "difficulty": 1,
        "answer_type": "text",

        "question":
            r"If \(f'(x)>0\), is the graph increasing or decreasing?",

        "answers": [
            "increasing",
            "rising",
            "going up",
        ],

        "final_answer_latex":
            r"\text{Increasing}",

        "hints": [
            r"Think about the sign of the gradient.",
            r"A positive derivative means a positive slope.",
            r"The graph rises as \(x\) increases.",
        ],

        "solution": [
            r"Since \(f'(x)>0\), the gradient is positive.",
            r"Therefore the graph is increasing.",
        ],
    },

    {
        "skill": "Gradient Interpretation",
        "topic": "Gradient Interpretation",
        "difficulty": 1,
        "answer_type": "text",

        "question":
            r"If \(f'(x)<0\), is the graph increasing or decreasing?",

        "answers": [
            "decreasing",
            "falling",
            "going down",
        ],

        "final_answer_latex":
            r"\text{Decreasing}",

        "hints": [
            r"A negative derivative means a negative slope.",
            r"The height decreases as \(x\) increases.",
            r"The graph is falling.",
        ],

        "solution": [
            r"Since \(f'(x)<0\), the gradient is negative.",
            r"Therefore the graph is decreasing.",
        ],
    },

    {
        "skill": "Gradient Interpretation",
        "topic": "Gradient Interpretation",
        "difficulty": 2,
        "answer_type": "number",

        "question":
            r"For \(y=x^2\), find the gradient when \(x=3\).",

        "answers": [
            "6",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=6",

        "hints": [
            r"Differentiate \(y=x^2\).",
            r"You should obtain \(dy/dx=2x\).",
            r"Now substitute \(x=3\).",
        ],

        "solution": [
            r"\(dy/dx=2x\).",
            r"At \(x=3\), \(dy/dx=2(3)=6\).",
        ],
    },


    # =====================================================
    # STATIONARY POINTS
    # =====================================================

    {
        "skill": "Stationary Points",
        "topic": "Stationary Points",
        "difficulty": 1,
        "answer_type": "number",

        "question":
            r"What is the value of \(f'(x)\) at a stationary point?",

        "answers": [
            "0",
        ],

        "final_answer_latex":
            r"f'(x)=0",

        "hints": [
            r"A stationary point has a horizontal tangent.",
            r"A horizontal tangent has zero gradient.",
            r"Therefore the derivative equals zero.",
        ],

        "solution": [
            r"At a stationary point the tangent is horizontal.",
            r"Hence its gradient is \(0\), so \(f'(x)=0\).",
        ],
    },

    {
        "skill": "Stationary Points",
        "topic": "Stationary Points",
        "difficulty": 2,
        "answer_type": "number",

        "question":
            r"For \(y=x^2-6x+5\), find the \(x\)-coordinate of the stationary point.",

        "answers": [
            "3",
        ],

        "final_answer_latex":
            r"x=3",

        "hints": [
            r"Differentiate the function.",
            r"Set the derivative equal to zero.",
            r"Solve \(2x-6=0\).",
        ],

        "solution": [
            r"\(dy/dx=2x-6\).",
            r"At a stationary point \(2x-6=0\).",
            r"Therefore \(x=3\).",
        ],
    },

    {
        "skill": "Stationary Points",
        "topic": "Stationary Points",
        "difficulty": 2,
        "answer_type": "text",

        "question":
            r"For \(y=-x^2+4x+1\), is the stationary point a maximum or minimum?",

        "answers": [
            "maximum",
            "max",
        ],

        "final_answer_latex":
            r"\text{Maximum}",

        "hints": [
            r"Look at the coefficient of \(x^2\).",
            r"The coefficient is negative.",
            r"The parabola therefore opens downward.",
        ],

        "solution": [
            r"The coefficient of \(x^2\) is negative.",
            r"The parabola opens downward.",
            r"Therefore its stationary point is a maximum.",
        ],
    },


    # =====================================================
    # PROJECTILE PHYSICS
    # =====================================================

    {
        "skill": "Projectile Physics",
        "topic": "Projectile Gradient",
        "difficulty": 2,
        "answer_type": "expression",

        "question":
            r"A projectile follows \(y=-0.05x^2+2x+1\). Find \(\frac{dy}{dx}\).",

        "answers": [
            "-0.1*x+2",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=-0.1x+2",

        "hints": [
            r"Differentiate the trajectory with respect to \(x\).",
            r"The derivative of \(-0.05x^2\) is \(-0.1x\).",
            r"The derivative of \(2x\) is \(2\).",
        ],

        "solution": [
            r"\(y=-0.05x^2+2x+1\).",
            r"Differentiate each term.",
            r"\(dy/dx=-0.1x+2\).",
        ],
    },

    {
        "skill": "Projectile Physics",
        "topic": "Projectile Gradient",
        "difficulty": 3,
        "answer_type": "number",

        "question":
            r"For \(y=-0.05x^2+2x+1\), find the gradient when \(x=10\).",

        "answers": [
            "1",
        ],

        "final_answer_latex":
            r"\left.\frac{dy}{dx}\right|_{x=10}=1",

        "hints": [
            r"Differentiate the trajectory first.",
            r"You should obtain \(dy/dx=-0.1x+2\).",
            r"Substitute \(x=10\).",
        ],

        "solution": [
            r"\(dy/dx=-0.1x+2\).",
            r"At \(x=10\), \(dy/dx=-0.1(10)+2\).",
            r"Therefore the gradient is \(1\).",
        ],
    },

    {
        "skill": "Projectile Physics",
        "topic": "Projectile Peak",
        "difficulty": 3,
        "answer_type": "number",

        "question":
            r"For \(y=-0.05x^2+2x+1\), find the \(x\)-coordinate of the maximum height.",

        "answers": [
            "20",
        ],

        "final_answer_latex":
            r"x=20",

        "hints": [
            r"At maximum height the trajectory has zero gradient.",
            r"Set \(dy/dx=-0.1x+2\) equal to zero.",
            r"Solve \(-0.1x+2=0\).",
        ],

        "solution": [
            r"\(dy/dx=-0.1x+2\).",
            r"At maximum height, \(dy/dx=0\).",
            r"So \(-0.1x+2=0\).",
            r"Therefore \(x=20\).",
        ],
    },

    {
        "skill": "Projectile Physics",
        "topic": "Projectile Interpretation",
        "difficulty": 2,
        "answer_type": "text",

        "question":
            r"If \(\frac{dy}{dx}>0\) on a projectile trajectory, is the projectile rising or falling?",

        "answers": [
            "rising",
            "going up",
            "increasing",
        ],

        "final_answer_latex":
            r"\text{Rising}",

        "hints": [
            r"A positive derivative means positive slope.",
            r"The height increases as horizontal distance increases.",
            r"The projectile is travelling upward.",
        ],

        "solution": [
            r"Since \(dy/dx>0\), the trajectory has positive gradient.",
            r"Therefore the projectile is rising.",
        ],
    },


    # =====================================================
    # COMPUTATIONAL THINKING
    # =====================================================

    {
        "skill": "Computational Thinking",
        "topic": "Code Interpretation",
        "difficulty": 2,
        "answer_type": "text",

        "question":
            "What mathematical operation should a program use "
            "to obtain instantaneous velocity from a position function?",

        "answers": [
            "differentiate",
            "differentiation",
            "derivative",
            "take the derivative",
        ],

        "final_answer_latex":
            r"\text{Differentiate the position function}",

        "hints": [
            r"Instantaneous velocity is a rate of change.",
            r"Think about \(v=\frac{ds}{dt}\).",
            r"The required operation is differentiation.",
        ],

        "solution": [
            r"Velocity is the instantaneous rate of change of displacement.",
            r"Therefore \(v=\frac{ds}{dt}\).",
            r"A program must differentiate the position function.",
        ],
    },

    {
        "skill": "Computational Thinking",
        "topic": "Calculus to Code",
        "difficulty": 3,
        "answer_type": "expression",

        "question":
            r"If a program models \(y=-0.1x^2+3x\), what expression should it use for the instantaneous gradient?",

        "answers": [
            "-0.2*x+3",
        ],

        "final_answer_latex":
            r"\frac{dy}{dx}=-0.2x+3",

        "hints": [
            r"The program needs the derivative of the trajectory.",
            r"Differentiate \(-0.1x^2\) using the power rule.",
            r"The derivative of \(3x\) is \(3\).",
        ],

        "solution": [
            r"Differentiate \(y=-0.1x^2+3x\).",
            r"The derivative of \(-0.1x^2\) is \(-0.2x\).",
            r"The derivative of \(3x\) is \(3\).",
            r"Therefore \(dy/dx=-0.2x+3\).",
        ],
    },
]


# =========================================================
# TEXT NORMALISATION
# =========================================================

def normalize_text(text):

    if text is None:
        return ""

    return (
        str(text)
        .strip()
        .lower()
        .replace("−", "-")
        .replace("–", "-")
        .replace("×", "*")
        .replace("÷", "/")
    )


# =========================================================
# CLEAN MATHEMATICAL INPUT
# =========================================================

def clean_math_input(text):

    text = normalize_text(text)

    # Remove common answer prefixes.
    prefixes = [
        "dy/dx=",
        "dydx=",
        "y'=",
        "f'(x)=",
        "v(t)=",
        "a(t)=",
        "x=",
    ]

    compact = text.replace(" ", "")

    for prefix in prefixes:

        if compact.startswith(prefix):
            compact = compact[len(prefix):]

    # Natural logarithm.
    compact = compact.replace(
        "ln(",
        "log(",
    )

    return compact


# =========================================================
# PARSE EXPRESSION
# =========================================================

def parse_math_expression(text):

    cleaned = clean_math_input(text)

    return parse_expr(
        cleaned,
        local_dict=LOCAL_DICT,
        transformations=TRANSFORMATIONS,
        evaluate=True,
    )


# =========================================================
# TEXT ANSWER CHECK
# =========================================================

def check_text_answer(
    student_answer,
    valid_answers,
):

    student = normalize_text(
        student_answer
    ).strip()

    for valid in valid_answers:

        correct = normalize_text(
            valid
        ).strip()

        if student == correct:
            return True

    return False


# =========================================================
# NUMERICAL ANSWER CHECK
# =========================================================

def check_number_answer(
    student_answer,
    valid_answers,
):

    try:

        student_expr = parse_math_expression(
            student_answer
        )

        student_value = float(
            sp.N(student_expr)
        )

    except Exception:
        return False

    for valid in valid_answers:

        try:

            correct_expr = parse_math_expression(
                valid
            )

            correct_value = float(
                sp.N(correct_expr)
            )

            if abs(
                student_value
                - correct_value
            ) < 1e-8:

                return True

        except Exception:
            continue

    return False


# =========================================================
# EXPRESSION ANSWER CHECK USING SYMPY
# =========================================================

def check_expression_answer(
    student_answer,
    valid_answers,
):

    try:

        student_expr = parse_math_expression(
            student_answer
        )

    except Exception:
        return False

    for valid in valid_answers:

        try:

            correct_expr = parse_math_expression(
                valid
            )

            difference = sp.simplify(
                student_expr
                - correct_expr
            )

            if difference == 0:
                return True

            # Additional symbolic equality check.
            if student_expr.equals(
                correct_expr
            ):
                return True

        except Exception:
            continue

    return False


# =========================================================
# MAIN ANSWER CHECK
# =========================================================

def check_answer(
    student_answer,
    question,
):

    answer_type = question.get(
        "answer_type",
        "expression",
    )

    valid_answers = question.get(
        "answers",
        [],
    )

    if answer_type == "text":

        return check_text_answer(
            student_answer,
            valid_answers,
        )

    if answer_type == "number":

        return check_number_answer(
            student_answer,
            valid_answers,
        )

    return check_expression_answer(
        student_answer,
        valid_answers,
    )


# =========================================================
# ADAPTIVE DIFFICULTY
# =========================================================

def appropriate_difficulty(
    mastery_score,
):

    if mastery_score < 40:
        return 1

    if mastery_score < 60:
        return 2

    if mastery_score < 80:
        return 3

    return 4


# =========================================================
# ADAPTIVE QUESTION SELECTION
# =========================================================

def choose_question(
    mastery,
    previous_topic=None,
):

    weighted_questions = []

    for question in QUESTIONS:

        skill = question["skill"]

        mastery_score = mastery.get(
            skill,
            50,
        )

        desired_level = appropriate_difficulty(
            mastery_score
        )

        # -------------------------------------------------
        # WEAKER SKILLS GET HIGHER PRIORITY
        # -------------------------------------------------

        weakness_weight = max(
            10,
            110 - mastery_score,
        )

        # -------------------------------------------------
        # DIFFICULTY MATCHING
        # -------------------------------------------------

        difficulty_gap = abs(
            question["difficulty"]
            - desired_level
        )

        if difficulty_gap == 0:

            difficulty_multiplier = 1.8

        elif difficulty_gap == 1:

            difficulty_multiplier = 1.0

        else:

            difficulty_multiplier = 0.35

        weight = (
            weakness_weight
            * difficulty_multiplier
        )

        # -------------------------------------------------
        # REDUCE IMMEDIATE TOPIC REPETITION
        # -------------------------------------------------

        if (
            previous_topic
            and question["topic"]
            == previous_topic
        ):

            weight *= 0.25

        # -------------------------------------------------
        # SMALL RANDOM REVIEW CHANCE
        # -------------------------------------------------

        weight += 5

        weighted_questions.extend(
            [question]
            * max(
                1,
                int(weight),
            )
        )

    return random.choice(
        weighted_questions
    )