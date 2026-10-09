from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

import sqlite3
import json

from pathlib import Path
from datetime import datetime


# ==========================================================
# APPLICATION CONFIGURATION
# ==========================================================

app = Flask(__name__)

app.secret_key = "student-grade-calculator-pro-secret-key"

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "grades.db"


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            class_name TEXT NOT NULL,
            total_marks REAL NOT NULL,
            max_marks REAL NOT NULL,
            percentage REAL NOT NULL,
            grade TEXT NOT NULL,
            status TEXT NOT NULL,
            subjects_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


initialize_database()


# ==========================================================
# GRADE CALCULATION
# ==========================================================

def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    elif percentage >= 40:
        return "E"
    else:
        return "F"


def calculate_status(percentage):
    if percentage >= 40:
        return "Pass"

    return "Fail"


# ==========================================================
# HOME PAGE
# ==========================================================

@app.route("/")
def index():
    connection = get_db()

    total_students = connection.execute("""
        SELECT COUNT(*) AS total
        FROM results
    """).fetchone()["total"]

    average_percentage = connection.execute("""
        SELECT AVG(percentage) AS average
        FROM results
    """).fetchone()["average"]

    passed_students = connection.execute("""
        SELECT COUNT(*) AS total
        FROM results
        WHERE status = 'Pass'
    """).fetchone()["total"]

    recent_results = connection.execute("""
        SELECT *
        FROM results
        ORDER BY id DESC
        LIMIT 5
    """).fetchall()

    connection.close()

    average_percentage = average_percentage or 0

    return render_template(
        "index.html",
        total_students=total_students,
        average_percentage=round(average_percentage, 2),
        passed_students=passed_students,
        recent_results=recent_results
    )


# ==========================================================
# CALCULATE STUDENT RESULTS
# ==========================================================

@app.route("/calculate", methods=["POST"])
def calculate():

    student_name = request.form.get(
        "student_name", ""
    ).strip()

    roll_number = request.form.get(
        "roll_number", ""
    ).strip()

    class_name = request.form.get(
        "class_name", ""
    ).strip()

    subject_names = request.form.getlist("subject_name[]")
    marks_values = request.form.getlist("marks[]")
    maximum_values = request.form.getlist("max_marks[]")

    # ------------------------------------------
    # Validate student information
    # ------------------------------------------

    if not student_name or not roll_number or not class_name:
        flash("Please complete all student information.", "error")
        return redirect(url_for("index"))

    if len(student_name) > 100:
        flash("Student name must be 100 characters or fewer.", "error")
        return redirect(url_for("index"))

    if len(roll_number) > 40:
        flash("Roll number must be 40 characters or fewer.", "error")
        return redirect(url_for("index"))

    if len(class_name) > 80:
        flash("Class name must be 80 characters or fewer.", "error")
        return redirect(url_for("index"))

    # ------------------------------------------
    # Validate subject rows
    # ------------------------------------------

    if not (
        len(subject_names) == len(marks_values) == len(maximum_values)
    ):
        flash("Invalid subject information. Please try again.", "error")
        return redirect(url_for("index"))

    if not 1 <= len(subject_names) <= 15:
        flash("Please enter between 1 and 15 subjects.", "error")
        return redirect(url_for("index"))

    subjects = []

    total_marks = 0.0
    total_maximum = 0.0

    # ------------------------------------------
    # Process each subject
    # ------------------------------------------

    for index, subject_name in enumerate(subject_names):

        subject_name = subject_name.strip()

        if not subject_name:
            flash(
                f"Please enter a name for subject {index + 1}.",
                "error"
            )
            return redirect(url_for("index"))

        if len(subject_name) > 100:
            flash(
                f"Subject {index + 1} must be 100 characters or fewer.",
                "error"
            )
            return redirect(url_for("index"))

        try:
            marks = float(marks_values[index])
            maximum = float(maximum_values[index])

        except (ValueError, TypeError):
            flash(
                f"Enter valid marks for subject {index + 1}.",
                "error"
            )
            return redirect(url_for("index"))

        if maximum <= 0 or maximum > 100000:
            flash(
                f"Maximum marks for subject {index + 1} must be greater than 0.",
                "error"
            )
            return redirect(url_for("index"))

        if marks < 0 or marks > maximum:
            flash(
                f"Obtained marks for subject {index + 1} must be between 0 and its maximum marks.",
                "error"
            )
            return redirect(url_for("index"))

        percentage = (marks / maximum) * 100

        grade = calculate_grade(percentage)
        status = calculate_status(percentage)

        subject = {
            "name": subject_name,
            "marks": marks,
            "max_marks": maximum,
            "percentage": round(percentage, 2),
            "grade": grade,
            "status": status
        }

        subjects.append(subject)

        total_marks += marks
        total_maximum += maximum

    # ------------------------------------------
    # Calculate overall performance
    # ------------------------------------------

    overall_percentage = (
        total_marks / total_maximum
    ) * 100

    overall_grade = calculate_grade(overall_percentage)

    # Student fails if any subject is below 40%.
    overall_status = (
        "Pass"
        if all(subject["percentage"] >= 40 for subject in subjects)
        else "Fail"
    )

    subjects_json = json.dumps(subjects)

    created_at = datetime.now().strftime(
        "%d %b %Y, %I:%M %p"
    )

    # ------------------------------------------
    # Save result to SQLite
    # ------------------------------------------

    connection = get_db()

    cursor = connection.execute("""
        INSERT INTO results (
            student_name,
            roll_number,
            class_name,
            total_marks,
            max_marks,
            percentage,
            grade,
            status,
            subjects_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_name,
        roll_number,
        class_name,
        total_marks,
        total_maximum,
        round(overall_percentage, 2),
        overall_grade,
        overall_status,
        subjects_json,
        created_at
    ))

    connection.commit()

    result_id = cursor.lastrowid

    connection.close()

    flash("Student result calculated successfully!", "success")

    return redirect(
        url_for("result", result_id=result_id)
    )


# ==========================================================
# RESULT DETAILS
# ==========================================================

@app.route("/result/<int:result_id>")
def result(result_id):

    connection = get_db()

    result_data = connection.execute("""
        SELECT *
        FROM results
        WHERE id = ?
    """, (result_id,)).fetchone()

    connection.close()

    if result_data is None:
        abort(404)

    result_data = dict(result_data)

    subjects = json.loads(result_data["subjects_json"])

    return render_template(
        "result.html",
        result=result_data,
        subjects=subjects
    )


# ==========================================================
# RESULT HISTORY
# ==========================================================

@app.route("/history")
def history():

    search_query = request.args.get("q", "").strip()

    connection = get_db()

    if search_query:

        results = connection.execute("""
            SELECT *
            FROM results
            WHERE student_name LIKE ?
               OR roll_number LIKE ?
               OR class_name LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search_query}%",
            f"%{search_query}%",
            f"%{search_query}%"
        )).fetchall()

    else:

        results = connection.execute("""
            SELECT *
            FROM results
            ORDER BY id DESC
        """).fetchall()

    connection.close()

    return render_template(
        "history.html",
        results=results,
        search_query=search_query
    )


# ==========================================================
# DELETE RESULT
# ==========================================================

@app.route("/delete/<int:result_id>", methods=["POST"])
def delete_result(result_id):

    connection = get_db()

    cursor = connection.execute("""
        DELETE FROM results
        WHERE id = ?
    """, (result_id,))

    connection.commit()

    deleted = cursor.rowcount

    connection.close()

    if deleted:
        flash("Result deleted successfully.", "success")
    else:
        flash("Result not found.", "error")

    return redirect(url_for("history"))


# ==========================================================
# ERROR PAGES
# ==========================================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)