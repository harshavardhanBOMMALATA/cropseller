const signupBtn = document.getElementById("signupBtn");

signupBtn.addEventListener("click", function (event) {
    event.preventDefault();

    const name = document.querySelector('input[name="name"]').value;
    const email = document.querySelector('input[name="email"]').value;
    const phone = document.querySelector('input[name="phone"]').value;
    const password = document.querySelector('input[name="password"]').value;
    const confirmPassword = document.querySelector('input[name="confirm_password"]').value;
        const address = document.querySelector('input[name="address"]').value;

    if (password !== confirmPassword) {
        document.getElementById("failuremessage").innerText="Passwords not matching";
        document.getElementById("failuremessage").style.color="red";
        return;
    }

    fetch('/database/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken' : getCSRFToken()

        },
        body: JSON.stringify({
            name: name,
            email: email,
            phone: phone,
            password: password,
            address:address,
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            showSuccessAndRedirect();
        } else {
            document.getElementById("failuremessage").innerText="User already existed";
            document.getElementById("failuremessage").style.color="red";
        }
    })
    .catch(() => {
        showMessage("Signup failed", "error");
    });
});

function showSuccessAndRedirect() {
    let msg = document.getElementById("signupMessage");

    if (!msg) {
        msg = document.createElement("div");
        msg.id = "signupMessage";
        msg.style.marginTop = "15px";
        msg.style.padding = "12px";
        msg.style.borderRadius = "6px";
        msg.style.fontSize = "14px";
        msg.style.textAlign = "center";
        msg.style.backgroundColor = "#e8f5e9";
        msg.style.color = "#2e7d32";
        document.querySelector(".login-container").appendChild(msg);
    }

    msg.innerText = "Account created successfully";

    setTimeout(() => {
        window.location.href = "/";
    }, 2000);
}


function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}