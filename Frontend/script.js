// --- 1. Textarea Auto-resize ---
const textarea = document.querySelector('.input-container textarea');
if (textarea) {
    const maxLines = 3;
    const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || (14 * 1.4);
    const paddingTop = parseFloat(getComputedStyle(textarea).paddingTop);
    const paddingBottom = parseFloat(getComputedStyle(textarea).paddingBottom);
    const maxHeight = (maxLines * lineHeight) + paddingTop + paddingBottom;

    function autoResize() {
        textarea.style.height = 'auto';
        const scrollHeight = textarea.scrollHeight;
        if (scrollHeight > maxHeight) {
            textarea.style.height = `${maxHeight}px`;
            textarea.style.overflowY = 'auto';
        } else {
            textarea.style.height = `${scrollHeight}px`;
            textarea.style.overflowY = 'hidden';
        }
    }

    textarea.addEventListener('input', autoResize);
    autoResize();
}

// --- 2. Slider Logic (ПОВЕРНУТО ПОВНІСТЮ) ---
document.addEventListener('DOMContentLoaded', () => {
    const wrapper = document.querySelector('.courses-wrapper');
    const dotsContainer = document.querySelector('.slider-dots');
    const dots = document.querySelectorAll('.slider-dots .dot');
    const cards = document.querySelectorAll('.course-card');
    const btnLeft = document.querySelector('.button_left');
    const btnRight = document.querySelector('.button_right');

    if (wrapper && dotsContainer && btnLeft && btnRight && cards.length > 0) {

        function updateActiveDot() {
            const scrollLeft = wrapper.scrollLeft;
            let closestIndex = 0;
            let minDiff = Infinity;

            cards.forEach((card, index) => {
                const diff = Math.abs(card.offsetLeft - scrollLeft);
                if (diff < minDiff) {
                    minDiff = diff;
                    closestIndex = index;
                }
            });

            dots.forEach((dot, index) => {
                dot.classList.toggle('active', index === closestIndex);
            });
        }

        function updateArrowStates() {
            const scrollLeft = wrapper.scrollLeft;
            const maxScroll = wrapper.scrollWidth - wrapper.clientWidth;
            btnLeft.disabled = scrollLeft < 10;
            btnRight.disabled = (scrollLeft + 10) > maxScroll;
        }

        btnRight.addEventListener('click', () => {
            const cardWidth = cards[0].offsetWidth;
            const gap = parseFloat(getComputedStyle(wrapper).gap);
            wrapper.scrollLeft += cardWidth + gap;
        });

        btnLeft.addEventListener('click', () => {
            const cardWidth = cards[0].offsetWidth;
            const gap = parseFloat(getComputedStyle(wrapper).gap);
            wrapper.scrollLeft -= cardWidth + gap;
        });

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                const targetCard = cards[index];
                if (targetCard) {
                    wrapper.scrollTo({
                        left: targetCard.offsetLeft,
                        behavior: 'smooth'
                    });
                }
            });
        });

        let scrollTimer;
        wrapper.addEventListener('scroll', () => {
            clearTimeout(scrollTimer);
            scrollTimer = setTimeout(() => {
                updateActiveDot();
                updateArrowStates();
            }, 50);
        });

        updateActiveDot();
        updateArrowStates();
    }
});

// --- 3. Logic for Modals & Auth (З ПЕРЕНАПРАВЛЕННЯМ) ---
document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = "http://127.0.0.1:8000"; 

    // Кнопки хедеру
    const headerLoginBtn = document.getElementById('header-login-btn');
    const headerSignupBtn = document.getElementById('header-signup-btn');
    const loginModal = document.getElementById('login-modal');
    const signupModal = document.getElementById('signup-modal');

    // Елементи ЛОГІНУ
    const loginSubmitBtn = document.getElementById('login-submit-btn');
    const loginUserInput = document.getElementById('username');
    const loginUserError = document.getElementById('login-user-error');
    const loginPassInput = document.getElementById('password');
    const loginPassError = document.getElementById('login-pass-error');

    // Елементи РЕЄСТРАЦІЇ
    const signupBtn = document.getElementById('signup-btn');
    const regNameInput = document.getElementById('reg-name');
    const regNameError = document.getElementById('signup-name-error');
    const regEmailInput = document.getElementById('reg-email');
    const regEmailError = document.getElementById('signup-email-error');
    const regPassInput = document.getElementById('reg-password');
    const regPassError = document.getElementById('signup-pass-error');

    const confirmBlock = document.getElementById('confirm-password-block');
    const regConfirmInput = document.getElementById('reg-confirm-password');
    const regConfirmError = document.getElementById('signup-confirm-error');

    // === Допоміжні функції ===
    function openModal(modal) { if (modal) { modal.classList.add('modal-open'); document.body.style.overflow = 'hidden'; } }
    function closeModal(modal) { if (modal) { modal.classList.remove('modal-open'); document.body.style.overflow = ''; } }
    function showError(input, msgElement, message) { input.classList.add('error-input'); msgElement.innerText = message; msgElement.style.display = 'block'; }
    function clearError(input, msgElement) { input.classList.remove('error-input'); if (msgElement) msgElement.style.display = 'none'; }
    function isValidEmail(email) { return /\S+@\S+\.\S+/.test(email); }

    if (headerLoginBtn) headerLoginBtn.addEventListener('click', () => { openModal(loginModal); closeModal(signupModal); });
    if (headerSignupBtn) headerSignupBtn.addEventListener('click', () => { openModal(signupModal); closeModal(loginModal); });

    window.addEventListener('click', (event) => {
        if (event.target === loginModal) closeModal(loginModal);
        if (event.target === signupModal) closeModal(signupModal);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') { closeModal(loginModal); closeModal(signupModal); }
    });


    // === ЛОГІН ===
    if (loginSubmitBtn) {
        [loginUserInput, loginPassInput].forEach(input => {
            input.addEventListener('input', () => {
                clearError(input, input === loginUserInput ? loginUserError : loginPassError);
            });
        });

        loginSubmitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            let isValid = true;

            if (loginUserInput.value.trim() === "") {
                showError(loginUserInput, loginUserError, "Введіть email");
                isValid = false;
            }

            if (loginPassInput.value.trim() === "") {
                showError(loginPassInput, loginPassError, "Введіть пароль");
                isValid = false;
            }

            if (isValid) {
                const originalText = loginSubmitBtn.innerText;
                loginSubmitBtn.innerText = "Вхід...";
                loginSubmitBtn.disabled = true;

                fetch(`${API_BASE_URL}/auth/login/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        email: loginUserInput.value,
                        password: loginPassInput.value
                    })
                })
                .then(res => res.json().then(data => ({ status: res.status, body: data })))
                .then(obj => {
                    loginSubmitBtn.innerText = originalText;
                    loginSubmitBtn.disabled = false;

                    if (obj.status === 200) {
                        localStorage.setItem('accessToken', obj.body.token);
                        alert("Вхід успішний!");
                        closeModal(loginModal);
                        // ПЕРЕНАПРАВЛЕННЯ НА ПРОФІЛЬ
                        window.location.href = 'profile.html'; 
                    } else {
                        showError(loginPassInput, loginPassError, "Невірний email або пароль");
                    }
                })
                .catch(err => {
                    console.error(err);
                    loginSubmitBtn.innerText = originalText;
                    loginSubmitBtn.disabled = false;
                    alert("Помилка з'єднання");
                });
            }
        });
    }


    // === РЕЄСТРАЦІЯ ===
    if (signupBtn) {
        const regInputs = [
            { input: regNameInput, error: regNameError },
            { input: regEmailInput, error: regEmailError },
            { input: regPassInput, error: regPassError },
            { input: regConfirmInput, error: regConfirmError }
        ];

        regInputs.forEach(item => {
            if (item.input) {
                item.input.addEventListener('input', () => {
                    clearError(item.input, item.error);
                });
            }
        });

        signupBtn.addEventListener('click', function (e) {
            e.preventDefault();
            let isFormValid = true;

            if (regNameInput.value.trim() === "") {
                showError(regNameInput, regNameError, "Введіть ім'я");
                isFormValid = false;
            }

            if (regEmailInput.value.trim() === "") {
                showError(regEmailInput, regEmailError, "Введіть email");
                isFormValid = false;
            } else if (!isValidEmail(regEmailInput.value)) {
                showError(regEmailInput, regEmailError, "Некоректний формат email");
                isFormValid = false;
            }

            if (confirmBlock.style.display === 'none') {
                if (regPassInput.value.trim() === "") {
                    showError(regPassInput, regPassError, "Введіть пароль");
                    isFormValid = false;
                } else if (regPassInput.value.length < 6) {
                    showError(regPassInput, regPassError, "Пароль має бути мінімум 6 символів");
                    isFormValid = false;
                }

                if (isFormValid) {
                    confirmBlock.style.display = 'block';
                    signupBtn.innerText = 'Зареєструватися';
                    regConfirmInput.focus();
                }

            } else {
                if (regPassInput.value !== regConfirmInput.value) {
                    showError(regConfirmInput, regConfirmError, "Паролі не співпадають");
                    isFormValid = false;
                }

                if (isFormValid) {
                    const originalText = signupBtn.innerText;
                    signupBtn.innerText = 'Обробка...';
                    signupBtn.disabled = true;

                    fetch(`${API_BASE_URL}/auth/register/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: regNameInput.value,
                            email: regEmailInput.value,
                            password: regPassInput.value
                        })
                    })
                    .then(res => res.json().then(data => ({ status: res.status, body: data })))
                    .then(obj => {
                        signupBtn.innerText = originalText;
                        signupBtn.disabled = false;

                        if (obj.status === 201) {
                            localStorage.setItem('accessToken', obj.body.token);
                            alert("Реєстрація успішна!");
                            closeModal(signupModal);
                            // ПЕРЕНАПРАВЛЕННЯ НА ПРОФІЛЬ
                            window.location.href = 'profile.html';
                        } else {
                            if (obj.body.username) showError(regNameInput, regNameError, "Користувач з таким ім'ям існує");
                            if (obj.body.email) showError(regEmailInput, regEmailError, "Email вже використовується");
                            if (obj.body.password) showError(regPassInput, regPassError, obj.body.password[0]);
                            
                            if (!obj.body.username && !obj.body.email && !obj.body.password) {
                                alert("Сталася помилка: " + JSON.stringify(obj.body));
                            }
                        }
                    })
                    .catch(err => {
                        console.error(err);
                        signupBtn.innerText = originalText;
                        signupBtn.disabled = false;
                        alert("Помилка з'єднання.");
                    });
                }
            }
        });
    }
});