document.addEventListener("DOMContentLoaded", function () {

    const subjectRows = document.getElementById("subjectRows");
    const addSubjectBtn = document.getElementById("addSubjectBtn");
    const gradeForm = document.getElementById("gradeForm");
    const resetFormBtn = document.getElementById("resetFormBtn");

    if (!subjectRows || !addSubjectBtn || !gradeForm) {
        return;
    }


    // ==================================================
    // ADD SUBJECT
    // ==================================================

    addSubjectBtn.addEventListener("click", function () {

        const currentRows = subjectRows.querySelectorAll(".subject-row");

        if (currentRows.length >= 15) {
            alert("You can add a maximum of 15 subjects.");
            return;
        }

        const row = document.createElement("tr");

        row.className = "subject-row";

        row.innerHTML = `
            <td>
                <input
                    type="text"
                    name="subject_name[]"
                    placeholder="Enter subject name"
                    maxlength="100"
                    required
                >
            </td>

            <td>
                <input
                    type="number"
                    name="marks[]"
                    placeholder="Marks"
                    min="0"
                    max="100000"
                    step="any"
                    required
                >
            </td>

            <td>
                <input
                    type="number"
                    name="max_marks[]"
                    value="100"
                    min="0.01"
                    max="100000"
                    step="any"
                    required
                >
            </td>

            <td>
                <button
                    type="button"
                    class="remove-subject"
                    aria-label="Remove subject"
                >
                    ×
                </button>
            </td>
        `;

        subjectRows.appendChild(row);

        row.querySelector('input[name="subject_name[]"]').focus();

    });


    // ==================================================
    // REMOVE SUBJECT
    // ==================================================

    subjectRows.addEventListener("click", function (event) {

        const removeButton = event.target.closest(".remove-subject");

        if (!removeButton) {
            return;
        }

        const rows = subjectRows.querySelectorAll(".subject-row");

        if (rows.length <= 1) {
            alert("At least one subject is required.");
            return;
        }

        removeButton.closest(".subject-row").remove();

    });


    // ==================================================
    // FORM VALIDATION
    // ==================================================

    gradeForm.addEventListener("submit", function (event) {

        const rows = subjectRows.querySelectorAll(".subject-row");

        if (rows.length < 1 || rows.length > 15) {
            event.preventDefault();

            alert("Please enter between 1 and 15 subjects.");

            return;
        }

        for (let index = 0; index < rows.length; index++) {

            const row = rows[index];

            const name = row.querySelector(
                'input[name="subject_name[]"]'
            );

            const marksInput = row.querySelector(
                'input[name="marks[]"]'
            );

            const maxInput = row.querySelector(
                'input[name="max_marks[]"]'
            );

            const subjectName = name.value.trim();

            const marks = Number(marksInput.value);

            const maximum = Number(maxInput.value);

            if (!subjectName) {
                event.preventDefault();

                alert(`Please enter a name for subject ${index + 1}.`);

                name.focus();

                return;
            }

            if (
                marksInput.value.trim() === "" ||
                maxInput.value.trim() === "" ||
                !Number.isFinite(marks) ||
                !Number.isFinite(maximum)
            ) {
                event.preventDefault();

                alert(`Enter valid marks for subject ${index + 1}.`);

                marksInput.focus();

                return;
            }

            if (maximum <= 0 || maximum > 100000) {
                event.preventDefault();

                alert(
                    `Maximum marks for subject ${index + 1} must be greater than 0.`
                );

                maxInput.focus();

                return;
            }

            if (marks < 0 || marks > maximum) {
                event.preventDefault();

                alert(
                    `Marks for subject ${index + 1} must be between 0 and ${maximum}.`
                );

                marksInput.focus();

                return;
            }

        }

    });


    // ==================================================
    // RESET FORM
    // ==================================================

    if (resetFormBtn) {

        resetFormBtn.addEventListener("click", function () {

            window.setTimeout(function () {

                // Restore the original three subject rows.
                subjectRows.innerHTML = `
                    <tr class="subject-row">
                        <td>
                            <input
                                type="text"
                                name="subject_name[]"
                                value="English"
                                maxlength="100"
                                required
                            >
                        </td>

                        <td>
                            <input
                                type="number"
                                name="marks[]"
                                min="0"
                                max="100000"
                                step="any"
                                required
                            >
                        </td>

                        <td>
                            <input
                                type="number"
                                name="max_marks[]"
                                value="100"
                                min="0.01"
                                max="100000"
                                step="any"
                                required
                            >
                        </td>

                        <td>
                            <button
                                type="button"
                                class="remove-subject"
                                aria-label="Remove subject"
                            >×</button>
                        </td>
                    </tr>

                    <tr class="subject-row">
                        <td>
                            <input
                                type="text"
                                name="subject_name[]"
                                value="Tamil"
                                maxlength="100"
                                required
                            >
                        </td>

                        <td>
                            <input
                                type="number"
                                name="marks[]"
                                min="0"
                                max="100000"
                                step="any"
                                required
                            >
                        </td>

                        <td>
                            <input
                                type="number"
                                name="max_marks[]"
                                value="100"
                                min="0.01"
                                max="100000"
                                step="any"
                                required
                            >
                        </td>

                        <td>
                            <button
                                type="button"
                                class="remove-subject"
                                aria-label="Remove subject"
                            >×</button>
                        </td>
                    </tr>

                    <tr class="subject-row">
                        <td>
                            <input
                                type="text"
                                name="subject_name[]"
                                value="Computer Science"
                                maxlength="100"
                                required
                            >
                        </td>

                        <td>
                            <input
                                type="number"
                                name="marks[]"
                                min="0"
                                max="100000"
                                step="any"
                                required
                            >
                        </td>

                        <td>
                            <input
                                type="number"
                                name="max_marks[]"
                                value="100"
                                min="0.01"
                                max="100000"
                                step="any"
                                required
                            >
                        </td>

                        <td>
                            <button
                                type="button"
                                class="remove-subject"
                                aria-label="Remove subject"
                            >×</button>
                        </td>
                    </tr>
                `;

            }, 0);

        });

    }

});