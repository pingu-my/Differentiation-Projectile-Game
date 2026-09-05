import os
import time
import re
import base64
from datetime import datetime, timezone

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
# SUPABASE DATA HELPERS
# =========================================================

def create_student(player_name):
    """
    Create one participant record.

    Supabase/PostgreSQL generates students.id automatically.
    If the id column is an identity/bigserial primary key, the
    first participant is 1, then 2, 3, and so on.
    """
    response = (
        supabase
        .table("students")
        .insert(
            {
                "display_name": player_name,
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError("Student record was not created.")

    return response.data[0]["id"]


def create_game_session(student_id):
    """
    Create a fresh game session for one student.

    The database generates its own row id. CALSHOT also keeps a
    date-time session label in session_state so each play session
    can be identified by when it started.
    """
    session_label = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    response = (
        supabase
        .table("game_sessions")
        .insert(
            {
                "student_id": student_id,
                "total_score": 0,
                "questions_attempted": 0,
                "questions_correct": 0,
                "completed": False,
            }
        )
        .execute()
    )

    if not response.data:
        raise RuntimeError("Game session record was not created.")

    return response.data[0]["id"], session_label

def save_question_attempt(
    question,
    student_answer,
    is_correct,
    attempt_number,
    hints_used,
    response_time_seconds,
    points_earned,
):
    """
    Save one CALSHOT answer attempt to Supabase.
    """

    correct_answers = question.get("answers", [])

    if correct_answers:
        correct_answer = str(correct_answers[0])
    else:
        correct_answer = ""

    question_id = question.get(
        "id",
        f"Q{st.session_state.question_number}"
    )

    misconception = question.get(
        "misconception",
        ""
    )

    attempt_data = {
        "session_id": st.session_state.db_session_id,
        "student_id": st.session_state.student_id,
        "question_number": st.session_state.question_number,
        "question_id": str(question_id),
        "topic": question.get("topic", ""),
        "skill": question.get("skill", ""),
        "difficulty": question.get("difficulty", 1),
        "attempt_number": attempt_number,
        "student_answer": student_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "hint_used": hints_used > 0,
        "hints_used": hints_used,
        "misconception": misconception,
        "response_time_seconds": response_time_seconds,
        "points_earned": points_earned,
    }

    supabase.table(
        "question_attempts"
    ).insert(
        attempt_data
    ).execute()

def save_mastery_record():
    """
    Save the student's current CALSHOT mastery profile to Supabase.
    """

    mastery = st.session_state.mastery

    mastery_data = {
        "session_id": st.session_state.db_session_id,
        "student_id": st.session_state.student_id,
        "differentiation": mastery["Differentiation"],
        "gradient_interpretation": mastery["Gradient Interpretation"],
        "stationary_points": mastery["Stationary Points"],
        "projectile_physics": mastery["Projectile Physics"],
        "computational_thinking": mastery["Computational Thinking"],
    }

    response = (
        supabase
        .table("mastery_records")
        .insert(mastery_data)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Mastery record was not created.")


def complete_game_session():
    """
    Update the existing Supabase game_sessions row with
    the student's final CALSHOT results.
    """

    completion_time_seconds = int(
        time.time() - st.session_state.start_time
    )

    accuracy = (
        st.session_state.correct_answers
        / TOTAL_QUESTIONS
    ) * 100

    session_data = {
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "total_score": st.session_state.score,
        "questions_attempted": TOTAL_QUESTIONS,
        "questions_correct": st.session_state.correct_answers,
        "accuracy": round(accuracy, 2),
        "completion_time_seconds": completion_time_seconds,
        "final_streak": st.session_state.streak,
        "completed": True,
    }

    response = (
        supabase
        .table("game_sessions")
        .update(session_data)
        .eq("id", st.session_state.db_session_id)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Game session was not updated.")


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
    Adds the CALSHOT background as a full-screen fixed backdrop.

    The image is stretched to the browser viewport so the top CALSHOT /
    Swinburne area and the bottom-right design credit remain visible.
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
           CALSHOT FULL-SCREEN BACKGROUND
        ============================================= */

        .stApp {{
            background-image:
                linear-gradient(
                    rgba(255, 255, 255, 0.58),
                    rgba(255, 255, 255, 0.68)
                ),
                url("data:image/png;base64,{encoded_background}");

            /* Reserve a safe strip at the bottom so Streamlit's
               fixed "Manage app" control does not cover the
               "Designed by Amy Nyau" credit baked into the image. */
            background-size: 100vw calc(100vh - 92px);
            background-position: center top;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-color: #eef6ff;
        }}

        [data-testid="stHeader"] {{
            background: rgba(255, 255, 255, 0.22);
            backdrop-filter: blur(5px);
        }}

        .block-container {{
            max-width: 1500px;
            padding-top: 1.25rem;
            padding-bottom: 3rem;
        }}

        .calshot-login-spacer {{
            height: 14.5rem;
        }}

        /* Start-screen form styling:
           narrower controls, larger text, and shifted away from the hornbill. */
        .calshot-login-wrap {{
            max-width: 760px;
            margin-left: 16%;
        }}

        .calshot-login-wrap h2 {{
            font-size: 2.5rem !important;
            margin-bottom: 1rem !important;
        }}

        .calshot-login-wrap label {{
            font-size: 1.15rem !important;
            font-weight: 600 !important;
        }}

        .calshot-login-wrap [data-testid="stTextInput"] {{
            max-width: 620px;
        }}

        .calshot-login-wrap [data-testid="stTextInput"] input {{
            min-height: 54px;
            font-size: 1.2rem !important;
            padding-left: 18px !important;
        }}

        .calshot-login-wrap .stButton {{
            max-width: 620px;
        }}

        .calshot-login-wrap .stButton > button {{
            min-height: 54px;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
        }}

        h1,
        h2,
        h3 {{
            color: #17345f;
        }}

        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.84);
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid rgba(255, 255, 255, 0.92);
        }}

        [data-testid="stTextInput"] input {{
            background: rgba(255, 255, 255, 0.96);
            border-radius: 10px;
        }}

        .stButton > button {{
            border-radius: 10px;
        }}

        audio {{
            width: 190px !important;
            height: 32px !important;
        }}

        [data-testid="stAudio"] {{
            margin-top: -8px;
        }}

        @media (max-width: 900px) {{

            .stApp {{
                background-size: cover;
                background-position: center top;
            }}

            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}

            .calshot-login-spacer {{
                height: 12.5rem;
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
            autoplay=True,
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

if "student_id" not in st.session_state:
    st.session_state.student_id = None

# Human-readable date/time label for this play session.
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# Internal Supabase game_sessions primary-key id.
if "db_session_id" not in st.session_state:
    st.session_state.db_session_id = None

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
# START SCREEN
# =========================================================

if not st.session_state.started:

    # Leave the CALSHOT logo and tagline completely unobstructed.
    st.markdown(
        '<div class="calshot-login-spacer"></div>',
        unsafe_allow_html=True,
    )

    # Three-column layout:
    # - left spacer keeps the form away from the hornbill
    # - middle column keeps the form compact
    # - right spacer preserves the bridge, DUN building and feature cards
    left_space, login_area, right_space = st.columns(
        [0.20, 0.32, 0.48],
        gap="small",
    )

    with login_area:

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

            player_name = name.strip()

            if not player_name:

                st.warning(
                    "Please enter your name."
                )

            elif not SUPABASE_CONNECTED:

                st.error(
                    "The CALSHOT database is temporarily unavailable. "
                    "Please try again."
                )

            else:

                try:

                    student_id = create_student(
                        player_name
                    )

                    db_session_id, session_label = (
                        create_game_session(
                            student_id
                        )
                    )

                    reset_game()

                    st.session_state.student_name = (
                        player_name
                    )

                    st.session_state.student_id = (
                        student_id
                    )

                    st.session_state.session_id = (
                        session_label
                    )

                    st.session_state.db_session_id = (
                        db_session_id
                    )

                    st.session_state.started = True

                    st.session_state.start_time = (
                        time.time()
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "CALSHOT could not start the database session."
                    )

                    st.code(str(e))


# =========================================================
# MAIN GAME
# =========================================================

else:

    # Start the looping background music after the student
    # has clicked Start Game.
    render_music_player()

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

            student_id = (
                st.session_state.student_id
            )

            try:

                db_session_id, session_label = (
                    create_game_session(
                        student_id
                    )
                )

                reset_game()

                st.session_state.student_name = (
                    player_name
                )

                st.session_state.student_id = (
                    student_id
                )

                st.session_state.session_id = (
                    session_label
                )

                st.session_state.db_session_id = (
                    db_session_id
                )

                st.session_state.started = True

                st.session_state.start_time = (
                    time.time()
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "CALSHOT could not start a new game session."
                )

                print(
                    "CALSHOT Supabase replay error:",
                    repr(e),
                )

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

            attempt_start_time = time.time()

            st.session_state.attempts += 1

            correct = check_answer(
                student_answer=answer,
                question=q,
            )

            skill = q["skill"]

            attempt_number = (
                st.session_state.attempts
            )

            points_earned = 0

            # =================================================
            # CORRECT
            # =================================================

            if correct:

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

                points_earned = max(
                    40,
                    100
                    + streak_bonus
                    + difficulty_bonus
                    - attempt_penalty
                    - hint_penalty,
                )

                st.session_state.score += (
                    points_earned
                )

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
                    f"⭐ +{points_earned} points"
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

            # =================================================
            # SAVE ATTEMPT TO SUPABASE
            # =================================================

            response_time_seconds = round(
                time.time() - attempt_start_time,
                2,
            )

            try:

                save_question_attempt(
                    question=q,
                    student_answer=answer.strip(),
                    is_correct=correct,
                    attempt_number=attempt_number,
                    hints_used=(
                        st.session_state.hint_level
                    ),
                    response_time_seconds=(
                        response_time_seconds
                    ),
                    points_earned=points_earned,
                )

            except Exception as e:

                st.warning(
                    "Your answer was checked, "
                    "but CALSHOT could not save "
                    "this attempt to the database."
                )

                st.code(str(e))


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

            try:

                save_mastery_record()

            except Exception as e:

                st.warning(
                    "CALSHOT completed the mission, "
                    "but could not save the final mastery record."
                )

                st.code(str(e))

            try:

                complete_game_session()

            except Exception as e:

                st.warning(
                    "CALSHOT completed the mission, "
                    "but could not update the final game session."
                )

                st.code(str(e))

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