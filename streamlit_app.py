import os
import time
import re
import base64

import streamlit as st
from supabase import create_client
from question_bank import (
    choose_question,
    check_answer,
)

from projectile_lab import render_projectile_lab


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CALSHOT",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# =========================================================
# SUPABASE CONNECTION
# =========================================================

@st.cache_resource
def get_supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


try:
    supabase = get_supabase_client()
    supabase.table("students").select("id").limit(1).execute()
    SUPABASE_CONNECTED = True
except Exception as e:
    supabase = None
    SUPABASE_CONNECTED = False
    SUPABASE_ERROR = str(e)

# =========================================================
# CONSTANTS
# =========================================================

TOTAL_QUESTIONS = 10
MAX_ATTEMPTS = 3

BACKGROUND_FILE = os.path.join(
    "assets",
    "calshot_background.png",
)

MUSIC_FILE = os.path.join(
    "assets",
    "background_music.mp3",
)

INITIAL_MASTERY = {
    "Differentiation": 50,
    "Gradient Interpretation": 50,
    "Stationary Points": 50,
    "Projectile Physics": 50,
    "Computational Thinking": 50,
}


# =========================================================
# BACKGROUND IMAGE
# =========================================================

@st.cache_data(show_spinner=False)
def image_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(
            image_file.read()
        ).decode()


def apply_background():
    """
    Adds the Sarawak CALSHOT image safely as the
    page background.

    Important:
    We do NOT place a giant white container over the app.
    """

    if not os.path.exists(BACKGROUND_FILE):
        return

    encoded_background = image_to_base64(
        BACKGROUND_FILE
    )

    st.markdown(
        f"""
        <style>

        /* =============================================
           CALSHOT PAGE BACKGROUND
        ============================================= */

        .stApp {{
            background-image:
                linear-gradient(
                    rgba(255, 255, 255, 0.76),
                    rgba(255, 255, 255, 0.82)
                ),
                url("data:image/png;base64,{encoded_background}");

            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}


        /* Keep Streamlit header subtle */

        [data-testid="stHeader"] {{
            background: rgba(255, 255, 255, 0.55);
            backdrop-filter: blur(8px);
        }}


        /* Main content remains visible */

        .block-container {{
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}


        /* Make headings easier to read */

        h1,
        h2,
        h3 {{
            color: #17345f;
        }}


        /* Metric cards */

        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.82);
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.9);
        }}


        /* Input field readability */

        [data-testid="stTextInput"] input {{
            background: rgba(255, 255, 255, 0.94);
            border-radius: 10px;
        }}


        /* Buttons */

        .stButton > button {{
            border-radius: 10px;
        }}


        /* =============================================
           COMPACT AUDIO PLAYER
        ============================================= */

        audio {{
            width: 190px !important;
            height: 32px !important;
        }}

        [data-testid="stAudio"] {{
            margin-top: -8px;
        }}


        /* =============================================
           MOBILE
        ============================================= */

        @media (max-width: 700px) {{

            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}

            audio {{
                width: 150px !important;
                height: 30px !important;
            }}

        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# Apply the background immediately
apply_background()


# =========================================================
# COMPACT MUSIC PLAYER
# =========================================================

def render_music_player():
    """
    Uses Streamlit's normal audio component rather than
    fixed-position custom HTML.

    This is much safer and will not cover the game.
    """

    if not os.path.exists(MUSIC_FILE):
        return

    left_space, music_area = st.columns(
        [5.5, 1.5]
    )

    with music_area:

        st.caption("🎵 Background music")

        st.audio(
            MUSIC_FILE,
            format="audio/mp3",
            loop=True,
        )


# =========================================================
# DISPLAY MATHEMATICS
# =========================================================

def display_math_text(text):
    """
    Displays text and mathematics enclosed by \\( ... \\).
    """

    if not text:
        return

    parts = re.split(
        r"(\\\(.*?\\\))",
        text
    )

    for part in parts:

        if not part:
            continue

        if (
            part.startswith(r"\(")
            and part.endswith(r"\)")
        ):

            equation = part[2:-2]

            st.latex(
                equation
            )

        elif part.strip():

            st.write(
                part.strip()
            )


# =========================================================
# RESET GAME
# =========================================================

def reset_game():
    """
    Reset all CALSHOT game data.
    """

    st.session_state.started = False
    st.session_state.student_name = ""

    st.session_state.score = 0
    st.session_state.start_time = None

    st.session_state.mastery = (
        INITIAL_MASTERY.copy()
    )

    st.session_state.current_question = None
    st.session_state.previous_topic = None

    st.session_state.question_number = 1

    st.session_state.hint_level = 0
    st.session_state.attempts = 0

    st.session_state.streak = 0
    st.session_state.correct_answers = 0

    st.session_state.answered_current_question = False
    st.session_state.show_final_answer = False

    st.session_state.game_over = False


# =========================================================
# START NEW ADAPTIVE QUESTION
# =========================================================

def start_new_question():

    st.session_state.current_question = (
        choose_question(
            st.session_state.mastery,
            st.session_state.previous_topic,
        )
    )

    st.session_state.hint_level = 0
    st.session_state.attempts = 0

    st.session_state.answered_current_question = False
    st.session_state.show_final_answer = False


# =========================================================
# SESSION STATE INITIALISATION
# =========================================================

if "started" not in st.session_state:
    st.session_state.started = False

if "student_name" not in st.session_state:
    st.session_state.student_name = ""

if "score" not in st.session_state:
    st.session_state.score = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "mastery" not in st.session_state:
    st.session_state.mastery = (
        INITIAL_MASTERY.copy()
    )

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "previous_topic" not in st.session_state:
    st.session_state.previous_topic = None

if "question_number" not in st.session_state:
    st.session_state.question_number = 1

if "hint_level" not in st.session_state:
    st.session_state.hint_level = 0

if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "streak" not in st.session_state:
    st.session_state.streak = 0

if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = 0

if "answered_current_question" not in st.session_state:
    st.session_state.answered_current_question = False

if "show_final_answer" not in st.session_state:
    st.session_state.show_final_answer = False

if "game_over" not in st.session_state:
    st.session_state.game_over = False


# =========================================================
# TOP RIGHT MUSIC PLAYER
# =========================================================

render_music_player()


# =========================================================
# CALSHOT HEADER
# =========================================================

st.title(
    "🚀 CALSHOT"
)

st.subheader(
    "Calculus in Mind, Physics in Motion, "
    "Excellence in Learning."
)

st.write(
    "Master differentiation through calculus, graphs, "
    "kinematics, computational thinking and projectile missions."
)


# =========================================================
# START SCREEN
# =========================================================

if not st.session_state.started:

    st.divider()

    st.markdown(
        "## 🎮 Enter the Mission"
    )

    st.write(
        "Aim. Analyse. Differentiate. "
        "Launch your way through CALSHOT."
    )

    name = st.text_input(
        "Student name",
        value=st.session_state.student_name,
        placeholder="Enter your name",
    )

    if st.button(
        "🚀 Start Game",
        type="primary",
        use_container_width=True,
    ):

        if not name.strip():

            st.warning(
                "Please enter your name first."
            )

        else:

            player_name = name.strip()

            reset_game()

            st.session_state.student_name = (
                player_name
            )

            st.session_state.started = True

            st.session_state.start_time = (
                time.time()
            )

            st.rerun()


# =========================================================
# MAIN GAME
# =========================================================

else:

    # =====================================================
    # TIMER
    # =====================================================

    elapsed_seconds = int(
        time.time()
        - st.session_state.start_time
    )

    minutes = (
        elapsed_seconds // 60
    )

    seconds = (
        elapsed_seconds % 60
    )


    # =====================================================
    # DASHBOARD
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "👤 Player",
            st.session_state.student_name,
        )

    with col2:

        st.metric(
            "⭐ Score",
            st.session_state.score,
        )

    with col3:

        st.metric(
            "🔥 Streak",
            st.session_state.streak,
        )

    with col4:

        st.metric(
            "⏱ Time",
            f"{minutes}:{seconds:02d}",
        )


    # =====================================================
    # PROGRESS
    # =====================================================

    progress = min(
        st.session_state.question_number
        / TOTAL_QUESTIONS,
        1.0,
    )

    st.progress(
        progress
    )

    st.caption(
        f"Mission "
        f"{st.session_state.question_number} "
        f"of {TOTAL_QUESTIONS}"
    )

    st.divider()


    # =====================================================
    # GAME OVER
    # =====================================================

    if st.session_state.game_over:

        st.markdown(
            "## 🏁 Mission Complete!"
        )

        accuracy = (
            st.session_state.correct_answers
            / TOTAL_QUESTIONS
        ) * 100

        average_mastery = (
            sum(
                st.session_state.mastery.values()
            )
            / len(
                st.session_state.mastery
            )
        )

        result1, result2, result3 = (
            st.columns(3)
        )

        with result1:

            st.metric(
                "🏆 Final Score",
                st.session_state.score,
            )

        with result2:

            st.metric(
                "🎯 Accuracy",
                f"{accuracy:.0f}%",
            )

        with result3:

            st.metric(
                "🧠 Average Mastery",
                f"{average_mastery:.0f}%",
            )

        st.divider()

        st.markdown(
            "### 🧠 Final Mastery Profile"
        )

        for skill, value in (
            st.session_state.mastery.items()
        ):

            st.write(
                f"**{skill}: {value}%**"
            )

            st.progress(
                value / 100
            )


        if accuracy >= 80:

            st.success(
                "🌟 Excellent mission performance!"
            )

        elif accuracy >= 60:

            st.info(
                "👍 Good work. Review your weaker "
                "skills and try again."
            )

        else:

            st.warning(
                "📚 Keep practising. CALSHOT will "
                "continue targeting your weaker skills."
            )


        st.write("")

        if st.button(
            "🔄 Play Again",
            type="primary",
            use_container_width=True,
        ):

            player_name = (
                st.session_state.student_name
            )

            reset_game()

            st.session_state.student_name = (
                player_name
            )

            st.session_state.started = True

            st.session_state.start_time = (
                time.time()
            )

            st.rerun()

        st.stop()


    # =====================================================
    # CREATE QUESTION
    # =====================================================

    if (
        st.session_state.current_question
        is None
    ):

        start_new_question()

    q = (
        st.session_state.current_question
    )


    # =====================================================
    # MISSION HEADER
    # =====================================================

    st.markdown(
        f"## 🎯 Mission "
        f"{st.session_state.question_number}"
    )

    info1, info2, info3 = st.columns(3)

    with info1:

        st.info(
            f"📘 Topic\n\n"
            f"{q['topic']}"
        )

    with info2:

        st.info(
            f"🧠 Skill\n\n"
            f"{q['skill']}"
        )

    with info3:

        st.info(
            f"⚡ Difficulty\n\n"
            f"Level {q['difficulty']}"
        )


    # =====================================================
    # PROJECTILE LAB
    # =====================================================

    if q["skill"] == "Projectile Physics":

        render_projectile_lab(
            mission_number=(
                st.session_state.question_number
            ),
            a=-0.05,
            b=2.0,
            c=1.0,
        )

        st.divider()


    # =====================================================
    # QUESTION
    # =====================================================

    st.markdown(
        "### Question"
    )

    display_math_text(
        q["question"]
    )


    # =====================================================
    # ANSWER INSTRUCTIONS
    # =====================================================

    answer_type = q.get(
        "answer_type",
        "expression",
    )

    if answer_type == "expression":

        st.caption(
            "You may enter normal mathematical notation. "
            "Examples: 6x, 2(x+1), x^2, sin(x), "
            "sqrt(1-x^2)."
        )

    elif answer_type == "number":

        st.caption(
            "Enter the numerical answer only. "
            "You may include x = if you wish."
        )

    elif answer_type == "text":

        st.caption(
            "Enter a short text answer."
        )


    # =====================================================
    # ANSWER INPUT
    # =====================================================

    answer = st.text_input(
        "✏️ Your answer",
        key=(
            f"answer_"
            f"{st.session_state.question_number}"
        ),
        disabled=(
            st.session_state
            .answered_current_question
        ),
    )


    # =====================================================
    # ATTEMPTS
    # =====================================================

    attempts_left = max(
        0,
        MAX_ATTEMPTS
        - st.session_state.attempts
    )

    st.caption(
        f"Attempts used: "
        f"{st.session_state.attempts}"
        f"/{MAX_ATTEMPTS}"
        f" • Attempts remaining: "
        f"{attempts_left}"
    )


    # =====================================================
    # BUTTONS
    # =====================================================

    button1, button2 = st.columns(2)

    with button1:

        submit_pressed = st.button(
            "✅ Submit Answer",
            type="primary",
            use_container_width=True,
            disabled=(
                st.session_state
                .answered_current_question
            ),
        )

    with button2:

        hint_pressed = st.button(
            "💡 Give Me a Hint",
            use_container_width=True,
            disabled=(
                st.session_state
                .answered_current_question
            ),
        )


    # =====================================================
    # MANUAL HINT
    # =====================================================

    if hint_pressed:

        if (
            st.session_state.hint_level
            < len(q["hints"])
        ):

            st.session_state.hint_level += 1

        else:

            st.info(
                "You have already seen "
                "all available hints."
            )


    # =====================================================
    # SUBMIT ANSWER
    # =====================================================

    if submit_pressed:

        if not answer.strip():

            st.warning(
                "Please enter an answer first."
            )

        else:

            st.session_state.attempts += 1

            correct = check_answer(
                student_answer=answer,
                question=q,
            )

            skill = q["skill"]


            # =================================================
            # CORRECT
            # =================================================

            if correct:

                attempt_number = (
                    st.session_state.attempts
                )

                st.success(
                    f"✅ Correct on attempt "
                    f"{attempt_number}!"
                )

                st.session_state.streak += 1

                st.session_state.correct_answers += 1


                attempt_penalty = (
                    attempt_number - 1
                ) * 20

                hint_penalty = (
                    st.session_state.hint_level
                    * 10
                )

                streak_bonus = (
                    st.session_state.streak
                    * 10
                )

                difficulty_bonus = (
                    q["difficulty"] - 1
                ) * 10


                points = max(
                    40,
                    100
                    + streak_bonus
                    + difficulty_bonus
                    - attempt_penalty
                    - hint_penalty,
                )


                st.session_state.score += points


                mastery_gain = max(
                    3,
                    9
                    - (
                        attempt_number - 1
                    ) * 2
                    - st.session_state.hint_level,
                )


                st.session_state.mastery[
                    skill
                ] = min(
                    100,
                    st.session_state.mastery[
                        skill
                    ] + mastery_gain,
                )


                st.session_state.answered_current_question = (
                    True
                )


                st.info(
                    f"⭐ +{points} points"
                    f" | 🔥 Streak bonus: "
                    f"+{streak_bonus}"
                    f" | ⚡ Difficulty bonus: "
                    f"+{difficulty_bonus}"
                )


            # =================================================
            # WRONG
            # =================================================

            else:

                st.session_state.streak = 0


                # ---------------------------------------------
                # WRONG ATTEMPT 1 OR 2
                # ---------------------------------------------

                if (
                    st.session_state.attempts
                    < MAX_ATTEMPTS
                ):

                    remaining = (
                        MAX_ATTEMPTS
                        - st.session_state.attempts
                    )

                    st.error(
                        f"❌ Not quite. "
                        f"You have {remaining} "
                        f"attempt(s) remaining."
                    )


                    st.session_state.mastery[
                        skill
                    ] = max(
                        0,
                        st.session_state.mastery[
                            skill
                        ] - 2,
                    )


                    if (
                        st.session_state.hint_level
                        < len(q["hints"])
                    ):

                        st.session_state.hint_level += 1


                # ---------------------------------------------
                # THIRD WRONG ATTEMPT
                # ---------------------------------------------

                else:

                    st.error(
                        "❌ Third attempt incorrect."
                    )


                    st.session_state.mastery[
                        skill
                    ] = max(
                        0,
                        st.session_state.mastery[
                            skill
                        ] - 5,
                    )


                    st.session_state.show_final_answer = (
                        True
                    )

                    st.session_state.answered_current_question = (
                        True
                    )


    # =====================================================
    # DISPLAY HINT
    # =====================================================

    if (
        st.session_state.hint_level > 0
        and not
        st.session_state.show_final_answer
    ):

        st.markdown(
            "### 💡 Hint"
        )

        hint_index = min(
            st.session_state.hint_level - 1,
            len(q["hints"]) - 1,
        )

        display_math_text(
            q["hints"][hint_index]
        )


    # =====================================================
    # THIRD-ATTEMPT FINAL ANSWER
    # =====================================================

    if (
        st.session_state.show_final_answer
    ):

        st.divider()

        st.warning(
            "You have used all three attempts. "
            "Review the solution before continuing."
        )

        st.markdown(
            "### 📘 Correct Answer"
        )

        if q.get(
            "final_answer_latex"
        ):

            st.latex(
                q["final_answer_latex"]
            )

        else:

            st.write(
                q["answers"][0]
            )


        st.markdown(
            "### 🧩 Worked Solution"
        )

        for step in q.get(
            "solution",
            [],
        ):

            display_math_text(
                step
            )


    # =====================================================
    # SUCCESS REVIEW
    # =====================================================

    if (
        st.session_state
        .answered_current_question
        and not
        st.session_state
        .show_final_answer
    ):

        st.markdown(
            "### ✅ Mission Solved"
        )

        if q.get(
            "final_answer_latex"
        ):

            st.latex(
                q["final_answer_latex"]
            )


    # =====================================================
    # NEXT MISSION
    # =====================================================

    st.write("")

    next_disabled = not (
        st.session_state
        .answered_current_question
    )


    if st.button(
        "➡️ Next Mission",
        use_container_width=True,
        disabled=next_disabled,
    ):

        st.session_state.previous_topic = (
            q["topic"]
        )


        if (
            st.session_state.question_number
            >= TOTAL_QUESTIONS
        ):

            st.session_state.game_over = True

            st.rerun()

        else:

            st.session_state.question_number += 1

            st.session_state.current_question = None

            st.session_state.hint_level = 0

            st.session_state.attempts = 0

            st.session_state.answered_current_question = (
                False
            )

            st.session_state.show_final_answer = (
                False
            )

            st.rerun()


    # =====================================================
    # MASTERY PROFILE
    # =====================================================

    st.divider()

    st.markdown(
        "## 🧠 Adaptive Mastery Profile"
    )

    st.caption(
        "CALSHOT gives greater priority to skills "
        "with lower mastery scores."
    )


    for skill, value in (
        st.session_state.mastery.items()
    ):

        st.write(
            f"**{skill}: {value}%**"
        )

        st.progress(
            value / 100
        )


    # =====================================================
    # RESTART GAME
    # =====================================================

    st.divider()

    if st.button(
        "🔄 Restart Game"
    ):

        reset_game()

        st.rerun()