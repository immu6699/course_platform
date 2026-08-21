async function registerUser() {

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!name || !email || !password) {
        alert("Please fill all fields.");
        return;
    }

    console.log("Sending registration request...");

    try {

        const response = await fetch("/register", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })
        });

        console.log("Server response:", response.status);

        const data = await response.json();

        console.log("Server data:", data);

        alert(data.message);

        if (data.success) {
            window.location.href = "/login.html";
        }

    } catch (error) {

        console.error("REGISTER ERROR:", error);

        alert(
            "Cannot connect to Python server.\n\n" +
            "Make sure you opened the website using:\n" +
            "http://localhost:3000"
        );
    }
}


async function loginUser() {

    const email =
        document.getElementById("loginEmail").value.trim();

    const password =
        document.getElementById("loginPassword").value;

    if (!email || !password) {
        alert("Please enter email and password.");
        return;
    }

    try {

        const response = await fetch("/login", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        console.log("Login response:", data);

        alert(data.message);

        if (data.success) {

            localStorage.setItem(
                "user",
                JSON.stringify(data.user)
            );

            if (data.user.role === "admin") {

                window.location.href = "/admin.html";

            } else {

                window.location.href = "/course.html";

            }
        }

    } catch (error) {

        console.error("LOGIN ERROR:", error);

        alert("Cannot connect to Python server.");
    }
}


function logout() {

    localStorage.removeItem("user");

    window.location.href = "/login.html";
}

const cartStorageKey = "courseCart";

function getCart() {
    try {
        return JSON.parse(localStorage.getItem(cartStorageKey)) || [];
    } catch (error) {
        return [];
    }
}

function saveCart(cart) {
    localStorage.setItem(cartStorageKey, JSON.stringify(cart));
    renderCart();
}

function enrollCourse(courseName, price) {
    if (price === undefined) {
        const matchingCard = [...document.querySelectorAll(".course-card")]
            .find(card => card.querySelector("h2")?.textContent.trim() === courseName);
        const priceText = matchingCard?.querySelector(".price")?.textContent || "";
        price = Number(priceText.replace(/[^0-9.]/g, "")) || 0;
    }

    const cart = getCart();
    if (cart.some(course => course.title === courseName)) {
        alert("This course is already in your cart.");
        return;
    }

    cart.push({ title: courseName, price: Number(price) || 0 });
    saveCart(cart);
    alert("Course added to your cart.");
}

function removeFromCart(courseName) {
    saveCart(getCart().filter(course => course.title !== courseName));
}

function clearCart() {
    saveCart([]);
}

function renderCart() {
    const cartItems = document.getElementById("cartItems");
    const cartCount = document.getElementById("cartCount");
    const cartTotal = document.getElementById("cartTotal");
    if (!cartItems || !cartCount || !cartTotal) return;

    const cart = getCart();
    cartCount.textContent = cart.length;
    cartTotal.textContent = `₹${cart.reduce((total, course) => total + course.price, 0).toLocaleString("en-IN")}`;
    cartItems.innerHTML = cart.length
        ? cart.map(course => `
            <li>
                <span>${course.title}<strong>₹${course.price.toLocaleString("en-IN")}</strong></span>
                <button class="remove-cart" onclick="removeFromCart(${JSON.stringify(course.title)})">Remove</button>
            </li>`).join("")
        : "<li class=\"empty-cart\">Your cart is empty.</li>";
}

function checkoutCart() {
    const cart = getCart();
    if (!cart.length) {
        alert("Add a course before checkout.");
        return;
    }
    if (!localStorage.getItem("user")) {
        alert("Please log in before checkout.");
        window.location.href = "/login.html";
        return;
    }
    document.getElementById("checkoutModal")?.classList.add("is-open");
}

function closeCheckout() {
    document.getElementById("checkoutModal")?.classList.remove("is-open");
}

async function placeOrder(event) {
    event.preventDefault();
    const user = JSON.parse(localStorage.getItem("user") || "null");
    const form = event.target;
    const submitButton = form.querySelector("button[type=submit]");
    submitButton.disabled = true;

    try {
        const response = await fetch("/api/orders", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: user.id,
                items: getCart(),
                full_name: form.full_name.value.trim(),
                phone: form.phone.value.trim(),
                address: form.address.value.trim(),
                city: form.city.value.trim(),
                state: form.state.value.trim(),
                postal_code: form.postal_code.value.trim(),
                country: form.country.value.trim(),
                payment_method: form.payment_method.value
            })
        });
        const data = await response.json();
        if (!data.success) throw new Error(data.message);
        localStorage.removeItem(cartStorageKey);
        renderCart();
        form.reset();
        closeCheckout();
        alert(`${data.message} Your order number is ${data.order_number}.`);
    } catch (error) {
        alert(error.message || "Could not place your order.");
    } finally {
        submitButton.disabled = false;
    }
}

async function loadCourses() {
    const courseList = document.getElementById("courseList");
    if (!courseList) return;

    courseList.innerHTML = "<p>Loading courses...</p>";
    try {
        const response = await fetch("/api/courses");
        const data = await response.json();
        if (!data.success) throw new Error(data.message);
        courseList.innerHTML = data.courses.map(course => `
            <article class="course-card">
                <div class="course-image">${course.image ? `<img src="${course.image}" alt="">` : "📚"}</div>
                <div class="course-content">
                    <h2>${course.title}</h2>
                    <p>${course.description}</p>
                    <p><strong>Instructor:</strong> ${course.instructor}</p>
                    <p class="price">₹${Number(course.price).toLocaleString("en-IN")}</p>
                    <button onclick="enrollCourse(${JSON.stringify(course.title)}, ${Number(course.price)})">Add to Cart</button>
                </div>
            </article>`).join("");
    } catch (error) {
        courseList.innerHTML = "<p>Could not load courses. Please try again.</p>";
    }
}

async function uploadCourse() {
    const form = document.getElementById("courseForm");
    const response = await fetch("/api/admin/courses", {
        method: "POST",
        body: new FormData(form)
    });
    const data = await response.json();
    alert(data.message);
    if (data.success) form.reset();
}

document.addEventListener("DOMContentLoaded", renderCart);