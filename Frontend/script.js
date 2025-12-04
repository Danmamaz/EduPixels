// ==========================================
// 1. TEXTAREA LOGIC (Auto-resize & Enter)
// ==========================================
const textarea = document.querySelector('.input-container textarea');
const generateBtn = document.getElementById('generate-course-btn');

if (textarea && generateBtn) {
    // Початковий стан - вимкнено
    generateBtn.disabled = true;

    const maxLines = 3;
    const lineHeight = parseFloat(getComputedStyle(textarea).lineHeight) || (18 * 1.5);
    const paddingTop = parseFloat(getComputedStyle(textarea).paddingTop);
    const paddingBottom = parseFloat(getComputedStyle(textarea).paddingBottom);
    const maxHeight = (maxLines * lineHeight) + paddingTop + paddingBottom;

    function handleInput() {
        // 1. Авто-розмір
        textarea.style.height = 'auto';
        const scrollHeight = textarea.scrollHeight;
        if (scrollHeight > maxHeight) {
            textarea.style.height = `${maxHeight}px`;
            textarea.style.overflowY = 'auto';
        } else {
            textarea.style.height = `${scrollHeight}px`;
            textarea.style.overflowY = 'hidden';
        }

        // 2. Логіка АКТИВНОЇ КНОПКИ (Біла)
        const text = textarea.value.trim();
        if (text.length > 0) {
            generateBtn.classList.add('active'); // Стає білою
            generateBtn.disabled = false;        // Стає клікабельною
        } else {
            generateBtn.classList.remove('active'); // Стає темною
            generateBtn.disabled = true;            // Блокується
        }
    }

    textarea.addEventListener('input', handleInput);

    // Обробка Enter
    textarea.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!generateBtn.disabled) {
                generateBtn.click();
            }
        }
    });

    handleInput(); // Запустити при завантаженні
}

// ==========================================
// 2. SLIDER LOGIC
// ==========================================
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
            // Додаємо невеликий допуск (10px) для точності
            btnLeft.disabled = scrollLeft < 10;
            btnRight.disabled = (scrollLeft + 10) > maxScroll;
        }

        btnRight.addEventListener('click', () => {
            const cardWidth = cards[0].offsetWidth;
            const gap = parseFloat(getComputedStyle(wrapper).gap) || 20;
            wrapper.scrollBy({ left: cardWidth + gap, behavior: 'smooth' });
        });

        btnLeft.addEventListener('click', () => {
            const cardWidth = cards[0].offsetWidth;
            const gap = parseFloat(getComputedStyle(wrapper).gap) || 20;
            wrapper.scrollBy({ left: -(cardWidth + gap), behavior: 'smooth' });
        });

        dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                const targetCard = cards[index];
                if (targetCard) {
                    // Центруємо картку або скролимо до її початку
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

        // Ініціалізація стану
        updateActiveDot();
        updateArrowStates();
    }
});

// ==========================================
// 3. MAIN LOGIC (Auth, Modals, Generation)
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = "http://127.0.0.1:8000";

    // --- Елементи UI ---
    const headerLoginBtn = document.getElementById('header-login-btn');
    const headerSignupBtn = document.getElementById('header-signup-btn');
    const loginModal = document.getElementById('login-modal');
    const signupModal = document.getElementById('signup-modal');
    const authButtons = document.getElementById('auth-buttons');
    const userProfile = document.getElementById('user-profile');

    // --- Елементи ЛОГІНУ ---
    const loginSubmitBtn = document.getElementById('login-submit-btn');
    const loginUserInput = document.getElementById('username');
    const loginUserError = document.getElementById('login-user-error');
    const loginPassInput = document.getElementById('password');
    const loginPassError = document.getElementById('login-pass-error');

    // --- Елементи РЕЄСТРАЦІЇ ---
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

    // --- Генерація курсу ---
    const generateCourseBtn = document.getElementById('generate-course-btn');
    const coursePromptInput = document.getElementById('course-prompt');

    // === Перевірка авторизації ===
    const token = localStorage.getItem('accessToken');
    if (token) {
        if (authButtons) authButtons.style.display = 'none';
        if (userProfile) userProfile.style.display = 'flex';
    } else {
        if (authButtons) authButtons.style.display = 'flex';
        if (userProfile) userProfile.style.display = 'none';
    }

    // === Допоміжні функції (Модалки) ===
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

    // === ГЕНЕРАЦІЯ КУРСУ ===
    if (generateCourseBtn) {
        generateCourseBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            const prompt = coursePromptInput.value.trim();
            if (!prompt) {
                alert("Будь ласка, введіть тему курсу");
                return;
            }

            const token = localStorage.getItem('accessToken');
            if (!token) {
                alert("Спочатку увійдіть в акаунт");
                openModal(loginModal);
                return;
            }

            // 1. Зберігаємо оригінальний контент
            const originalContent = generateCourseBtn.innerHTML;

            // 2. Вмикаємо анімацію (Спінер)
            // Використовуємо класи .loader та .btn-loader з CSS
            generateCourseBtn.innerHTML = '<div class="loader btn-loader" style="width: 24px; height: 24px; border-width: 3px;"></div>';
            generateCourseBtn.disabled = true;

            try {
                const response = await fetch(`${API_BASE_URL}/courses/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ prompt: prompt })
                });

                if (response.status === 401) {
                    localStorage.removeItem('accessToken');
                    alert("Сесія закінчилась. Увійдіть знову");
                    window.location.reload();
                    return;
                }

                if (response.ok) {
                    const data = await response.json();
                    // alert(`Курс створено!`); 
                    window.location.href = `topics.html?id=${data.id}`;
                } else {
                    const errorData = await response.json();
                    alert("Помилка: " + (errorData.error || "Не вдалося створити курс"));
                    // Повертаємо кнопку в початковий стан при помилці
                    generateCourseBtn.innerHTML = originalContent;
                    generateCourseBtn.disabled = false;
                }
            } catch (error) {
                console.error(error);
                alert("Помилка з'єднання з сервером");
                generateCourseBtn.innerHTML = originalContent;
                generateCourseBtn.disabled = false;
            }
        });
    }

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
                // Анімація спінера
                loginSubmitBtn.innerHTML = '<div class="loader"></div>';
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
                        if (obj.status === 200) {
                            localStorage.setItem('accessToken', obj.body.token);
                            // alert("Вхід успішний!");
                            closeModal(loginModal);
                            window.location.href = 'profile.html';
                        } else {
                            showError(loginPassInput, loginPassError, "Невірний email або пароль");
                            // Повертаємо текст кнопки
                            loginSubmitBtn.innerText = originalText;
                            loginSubmitBtn.disabled = false;
                        }
                    })
                    .catch(err => {
                        console.error(err);
                        alert("Помилка з'єднання");
                        loginSubmitBtn.innerText = originalText;
                        loginSubmitBtn.disabled = false;
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
                    // Анімація спінера
                    signupBtn.innerHTML = '<div class="loader"></div>';
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
                            if (obj.status === 201) {
                                localStorage.setItem('accessToken', obj.body.token);
                                // alert("Реєстрація успішна!");
                                closeModal(signupModal);
                                window.location.href = 'profile.html';
                            } else {
                                if (obj.body.username) showError(regNameInput, regNameError, "Користувач з таким ім'ям існує");
                                if (obj.body.email) showError(regEmailInput, regEmailError, "Email вже використовується");
                                if (obj.body.password) showError(regPassInput, regPassError, obj.body.password[0]);

                                if (!obj.body.username && !obj.body.email && !obj.body.password) {
                                    alert("Сталася помилка: " + JSON.stringify(obj.body));
                                }
                                // Повертаємо текст кнопки
                                signupBtn.innerText = originalText;
                                signupBtn.disabled = false;
                            }
                        })
                        .catch(err => {
                            console.error(err);
                            alert("Помилка з'єднання.");
                            signupBtn.innerText = originalText;
                            signupBtn.disabled = false;
                        });
                }
            }
        });
    }

    // === BACKEND STATUS CHECK ===
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');

    if (statusText && statusDot) {
        const checkBackend = async () => {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 3000);

                await fetch(API_BASE_URL + '/auth/login/', {
                    method: 'OPTIONS',
                    signal: controller.signal,
                    headers: { 'Accept': 'application/json' }
                });
                clearTimeout(timeoutId);

                statusText.innerText = "Online";
                statusText.style.color = "#4ade80";
                statusDot.style.background = "#4ade80";
                statusDot.style.boxShadow = "0 0 10px #4ade80";
            } catch (err) {
                console.error("Backend connection check failed:", err);
                statusText.innerText = "Offline";
                statusText.style.color = "#f87171";
                statusDot.style.background = "#f87171";
                statusDot.style.boxShadow = "0 0 10px #f87171";
            }
        };

        // Check every 5 seconds
        checkBackend();
        setInterval(checkBackend, 5000);
    }
});