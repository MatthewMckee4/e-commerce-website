document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#registration-form");
    const usernameField = form.querySelector("#username");
    const usernameError = document.querySelector("#username-error");

    const emailField = form.querySelector("#email");
    const emailError = document.querySelector("#email-error");

    const passwordField = form.querySelector("#password");
    const passwordError = document.querySelector("#password-error");

    const confirmPasswordField = form.querySelector("#confirm_password");
    const confirmPasswordError = document.querySelector(
        "#confirm-password-error"
    );

    form.addEventListener("submit", function (event) {
        let isValid = true;

        // Username validation
        if (usernameField.value.length < 2) {
            usernameError.textContent =
                "Username must be at least 2 characters long.";
            usernameError.style.display = "block";
            isValid = false;
        } else {
            usernameError.style.display = "none";
        }

        // Email validation (using simple pattern)
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailField.value)) {
            emailError.textContent = "Please enter a valid email address.";
            emailError.style.display = "block";
            isValid = false;
        } else {
            emailError.style.display = "none";
        }

        // Password validation
        const passwordValue = passwordField.value;
        const confirmPasswordValue = confirmPasswordField.value;

        if (passwordValue.length < 7) {
            passwordError.textContent =
                "Password must be at least 7 characters long.";
            passwordError.style.display = "block";
            isValid = false;
        } else {
            passwordError.style.display = "none";
        }

        const containsCapitalLetter = /[A-Z]/.test(passwordValue);
        const containsLowerCaseLetter = /[a-z]/.test(passwordValue);
        const containsDigit = /\d/.test(passwordValue);
        const containsSpecialChar = /[._!-]/.test(passwordValue);

        if (
            !(
                containsCapitalLetter &&
                containsLowerCaseLetter &&
                containsDigit &&
                containsSpecialChar
            )
        ) {
            passwordError.textContent =
                "Password must meet all requirements: at least one capital letter, one lowercase letter, one digit, and one special character (._-!).";
            passwordError.style.display = "block";
            isValid = false;
        } else {
            passwordError.style.display = "none";
        }

        if (passwordValue !== confirmPasswordValue) {
            confirmPasswordError.textContent = "Passwords do not match.";
            confirmPasswordError.style.display = "block";
            isValid = false;
        } else {
            confirmPasswordError.style.display = "none";
        }

        // If any validation failed, prevent form submission
        if (!isValid) {
            event.preventDefault();
        }
    });
});
function showConfirmationDialog(event) {
    event.preventDefault();

    const dialog = document.getElementById("confirmation-dialog");
    dialog.style.display = "block";

    const cancelButton = document.getElementById("cancel-delete");
    cancelButton.addEventListener("click", function () {
        dialog.style.display = "none";
    });
}
