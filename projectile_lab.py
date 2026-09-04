import math

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


# =========================================================
# PROJECTILE EQUATIONS
# =========================================================

def projectile_height(x, a, b, c):
    """
    y = ax^2 + bx + c
    """
    return a * x**2 + b * x + c


def projectile_gradient(x, a, b):
    """
    dy/dx = 2ax + b
    """
    return 2 * a * x + b


def projectile_angle(gradient):
    """
    Converts trajectory gradient into an angle in degrees.
    """
    return math.degrees(
        math.atan(gradient)
    )


def projectile_peak(a, b, c):
    """
    Finds the stationary point of the parabola.
    dy/dx = 0
    """

    if a == 0:
        return None, None

    x_peak = -b / (2 * a)

    y_peak = projectile_height(
        x_peak,
        a,
        b,
        c,
    )

    return x_peak, y_peak


# =========================================================
# PROJECTILE LAB
# =========================================================

def render_projectile_lab(
    mission_number,
    a=-0.05,
    b=2.0,
    c=1.0,
):
    """
    Interactive CALSHOT projectile laboratory.
    """

    st.markdown("## 🚀 CALSHOT Projectile Lab")

    st.caption(
        "Use calculus to analyse the projectile before "
        "and after firing."
    )

    # -----------------------------------------------------
    # SESSION STATE FOR THIS MISSION
    # -----------------------------------------------------

    fired_key = f"projectile_fired_{mission_number}"

    if fired_key not in st.session_state:
        st.session_state[fired_key] = False


    # -----------------------------------------------------
    # TRAJECTORY INFORMATION
    # -----------------------------------------------------

    x_peak, y_peak = projectile_peak(
        a,
        b,
        c,
    )

    # We use a useful visual range.
    x_max = 40.0

    # Target is deliberately placed on the trajectory.
    target_x = 30.0

    target_y = projectile_height(
        target_x,
        a,
        b,
        c,
    )


    # -----------------------------------------------------
    # EQUATION DISPLAY
    # -----------------------------------------------------

    equation_col1, equation_col2 = st.columns(2)

    with equation_col1:

        st.markdown("#### Trajectory")

        st.latex(
            rf"y={a}x^2+{b}x+{c}"
        )

    with equation_col2:

        st.markdown("#### Gradient Function")

        st.latex(
            rf"\frac{{dy}}{{dx}}={2*a}x+{b}"
        )


    # -----------------------------------------------------
    # FIRE BUTTON
    # -----------------------------------------------------

    fire_col1, fire_col2 = st.columns([2, 1])

    with fire_col1:

        if not st.session_state[fired_key]:

            if st.button(
                "🔥 FIRE PROJECTILE",
                key=f"fire_{mission_number}",
                type="primary",
                use_container_width=True,
            ):

                st.session_state[fired_key] = True

                st.rerun()

        else:

            st.success(
                "🚀 Projectile launched! "
                "Use the scanner to investigate its path."
            )

    with fire_col2:

        if st.button(
            "↩️ Reset Shot",
            key=f"reset_shot_{mission_number}",
            use_container_width=True,
        ):

            st.session_state[fired_key] = False

            st.rerun()


    # -----------------------------------------------------
    # DERIVATIVE SCANNER
    # -----------------------------------------------------

    st.markdown("### 🔎 Derivative Scanner")

    scanner_x = st.slider(
        "Move the scanner along the horizontal distance x:",
        min_value=0.0,
        max_value=x_max,
        value=10.0,
        step=0.5,
        key=f"scanner_{mission_number}",
    )

    scanner_y = projectile_height(
        scanner_x,
        a,
        b,
        c,
    )

    scanner_gradient = projectile_gradient(
        scanner_x,
        a,
        b,
    )

    scanner_angle = projectile_angle(
        scanner_gradient
    )


    # -----------------------------------------------------
    # INTERPRET DIRECTION
    # -----------------------------------------------------

    if abs(scanner_gradient) < 0.01:

        motion_description = "Stationary / Peak"

    elif scanner_gradient > 0:

        motion_description = "Rising"

    else:

        motion_description = "Falling"


    # -----------------------------------------------------
    # SCANNER METRICS
    # -----------------------------------------------------

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:

        st.metric(
            "📍 x-position",
            f"{scanner_x:.1f}",
        )

    with metric2:

        st.metric(
            "📏 Height y",
            f"{scanner_y:.2f}",
        )

    with metric3:

        st.metric(
            "📐 Gradient dy/dx",
            f"{scanner_gradient:.2f}",
        )

    with metric4:

        st.metric(
            "🧭 Trajectory angle",
            f"{scanner_angle:.1f}°",
        )

    st.info(
        f"Scanner interpretation: **{motion_description}**"
    )


    # -----------------------------------------------------
    # CREATE TRAJECTORY GRAPH
    # -----------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    # Ground line.
    ax.axhline(
        y=0,
        linewidth=1,
    )

    # -----------------------------------------------------
    # BEFORE FIRING
    # -----------------------------------------------------

    if not st.session_state[fired_key]:

        ax.scatter(
            [0],
            [c],
            s=160,
            marker=">",
            label="Launcher",
        )

        ax.scatter(
            [target_x],
            [target_y],
            s=180,
            marker="X",
            label="Target",
        )

        ax.text(
            1,
            c + 1,
            "Launcher",
        )

        ax.text(
            target_x + 0.5,
            target_y + 1,
            "TARGET",
        )


    # -----------------------------------------------------
    # AFTER FIRING
    # -----------------------------------------------------

    else:

        x_values = np.linspace(
            0,
            x_max,
            300,
        )

        y_values = projectile_height(
            x_values,
            a,
            b,
            c,
        )

        # Only display trajectory above the ground.
        valid = y_values >= 0

        ax.plot(
            x_values[valid],
            y_values[valid],
            linewidth=2.5,
            label="Projectile trajectory",
        )


        # Launcher.
        ax.scatter(
            [0],
            [c],
            s=160,
            marker=">",
            label="Launcher",
        )


        # Target.
        ax.scatter(
            [target_x],
            [target_y],
            s=180,
            marker="X",
            label="Target",
        )


        # Scanner point.
        if scanner_y >= 0:

            ax.scatter(
                [scanner_x],
                [scanner_y],
                s=130,
                marker="o",
                label="Derivative Scanner",
            )


            # ---------------------------------------------
            # TANGENT LINE
            # ---------------------------------------------

            tangent_width = 4

            tangent_x = np.linspace(
                scanner_x - tangent_width,
                scanner_x + tangent_width,
                30,
            )

            tangent_y = (
                scanner_gradient
                * (tangent_x - scanner_x)
                + scanner_y
            )

            ax.plot(
                tangent_x,
                tangent_y,
                linestyle="--",
                linewidth=1.5,
                label="Tangent",
            )


        # -------------------------------------------------
        # PEAK
        # -------------------------------------------------

        if (
            x_peak is not None
            and 0 <= x_peak <= x_max
        ):

            ax.scatter(
                [x_peak],
                [y_peak],
                s=130,
                marker="*",
                label="Peak",
            )

            ax.annotate(
                "Peak: dy/dx = 0",
                xy=(x_peak, y_peak),
                xytext=(
                    x_peak + 2,
                    y_peak + 2,
                ),
                arrowprops={
                    "arrowstyle": "->"
                },
            )


    # -----------------------------------------------------
    # GRAPH FORMATTING
    # -----------------------------------------------------

    ax.set_xlim(
        0,
        x_max + 2,
    )

    y_limit = max(
        25,
        (y_peak or 20) + 6,
    )

    ax.set_ylim(
        0,
        y_limit,
    )

    ax.set_xlabel(
        "Horizontal distance, x"
    )

    ax.set_ylabel(
        "Height, y"
    )

    ax.set_title(
        "CALSHOT Projectile Trajectory"
    )

    ax.grid(
        True,
        alpha=0.25,
    )

    ax.legend(
        loc="upper right"
    )

    st.pyplot(
        fig,
        use_container_width=True,
    )

    plt.close(fig)


    # -----------------------------------------------------
    # CALCULUS ANALYSIS
    # -----------------------------------------------------

    if st.session_state[fired_key]:

        st.markdown(
            "### 🧠 Calculus Analysis"
        )

        analysis1, analysis2 = st.columns(2)

        with analysis1:

            st.write(
                "**At the scanner position:**"
            )

            st.latex(
                rf"x={scanner_x:.1f}"
            )

            st.latex(
                rf"y={scanner_y:.2f}"
            )

            st.latex(
                rf"\frac{{dy}}{{dx}}="
                rf"{scanner_gradient:.2f}"
            )

        with analysis2:

            st.write(
                "**Projectile interpretation:**"
            )

            if scanner_gradient > 0.01:

                st.success(
                    "The gradient is positive, "
                    "so the projectile is rising."
                )

            elif scanner_gradient < -0.01:

                st.warning(
                    "The gradient is negative, "
                    "so the projectile is falling."
                )

            else:

                st.info(
                    "The gradient is approximately zero. "
                    "The projectile is at its highest point."
                )


        # -------------------------------------------------
        # PEAK INFORMATION
        # -------------------------------------------------

        if x_peak is not None:

            with st.expander(
                "📐 Inspect stationary point"
            ):

                st.write(
                    "The maximum height occurs when:"
                )

                st.latex(
                    r"\frac{dy}{dx}=0"
                )

                st.latex(
                    rf"{2*a}x+{b}=0"
                )

                st.latex(
                    rf"x={x_peak:.2f}"
                )

                st.latex(
                    rf"y={y_peak:.2f}"
                )