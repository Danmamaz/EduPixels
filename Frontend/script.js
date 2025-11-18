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

// --- 2. Slider Logic ---
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

// --- 3. Logic for Modals & Full Validation ---
document.addEventListener('DOMContentLoaded', () => {
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

    function openModal(modal) {
        if (modal) {
            modal.classList.add('modal-open');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeModal(modal) {
        if (modal) {
            modal.classList.remove('modal-open');
            document.body.style.overflow = '';
        }
    }

    // Функція показу помилки
    function showError(input, msgElement, message) {
        input.classList.add('error-input');
        msgElement.innerText = message;
        msgElement.style.display = 'block';
    }

    // Функція очищення помилки
    function clearError(input, msgElement) {
        input.classList.remove('error-input');
        if (msgElement) msgElement.style.display = 'none';
    }

    // Функція перевірки email (Regex)
    function isValidEmail(email) {
        return /\S+@\S+\.\S+/.test(email);
    }

    // --- Event Listeners для Модалок ---
    if (headerLoginBtn) headerLoginBtn.addEventListener('click', () => { openModal(loginModal); closeModal(signupModal); });
    if (headerSignupBtn) headerSignupBtn.addEventListener('click', () => { openModal(signupModal); closeModal(loginModal); });

    window.addEventListener('click', (event) => {
        if (event.target === loginModal) closeModal(loginModal);
        if (event.target === signupModal) closeModal(signupModal);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') { closeModal(loginModal); closeModal(signupModal); }
    });


    // === ВАЛІДАЦІЯ ЛОГІНУ ===
    if (loginSubmitBtn) {
        // Очищення помилок при вводі
        [loginUserInput, loginPassInput].forEach(input => {
            input.addEventListener('input', () => {
                clearError(input, input === loginUserInput ? loginUserError : loginPassError);
            });
        });

        loginSubmitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            let isValid = true;

            // Перевірка імені
            if (loginUserInput.value.trim() === "") {
                showError(loginUserInput, loginUserError, "Введіть ім'я або email");
                isValid = false;
            }

            // Перевірка паролю
            if (loginPassInput.value.trim() === "") {
                showError(loginPassInput, loginPassError, "Введіть пароль");
                isValid = false;
            }

            if (isValid) {
                // Імітація успішного входу
                console.log("Login Success");
                alert("Вхід виконано!");
                closeModal(loginModal);
            }
        });
    }


    // === ВАЛІДАЦІЯ РЕЄСТРАЦІЇ ===
    if (signupBtn) {
        // Очищення помилок при вводі для всіх полів
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

            // 1. Валідація Імені
            if (regNameInput.value.trim() === "") {
                showError(regNameInput, regNameError, "Введіть ім'я");
                isFormValid = false;
            } else if (regNameInput.value.toLowerCase() === "admin") {
                showError(regNameInput, regNameError, "Користувач вже існує");
                isFormValid = false;
            }

            // 2. Валідація Email
            if (regEmailInput.value.trim() === "") {
                showError(regEmailInput, regEmailError, "Введіть email");
                isFormValid = false;
            } else if (!isValidEmail(regEmailInput.value)) {
                showError(regEmailInput, regEmailError, "Некоректний формат email");
                isFormValid = false;
            }

            // 3. Логіка появи другого пароля
            if (confirmBlock.style.display === 'none') {
                // Якщо блок ще закритий, перевіряємо перший пароль
                if (regPassInput.value.trim() === "") {
                    showError(regPassInput, regPassError, "Введіть пароль");
                    isFormValid = false;
                } else if (regPassInput.value.length < 6) {
                    showError(regPassInput, regPassError, "Пароль має бути мінімум 6 символів");
                    isFormValid = false;
                }

                // Якщо всі поля (Ім'я, Email, Пароль1) валіді - відкриваємо другий етап
                if (isFormValid) {
                    confirmBlock.style.display = 'block';

                    // --- ОСЬ ТУТ ЗМІНЮЄМО ТЕКСТ КНОПКИ ---
                    signupBtn.innerText = 'Зареєструватися';

                    regConfirmInput.focus();
                }

            } else {
                // Якщо блок ВЖЕ відкритий - перевіряємо підтвердження
                if (regPassInput.value !== regConfirmInput.value) {
                    showError(regConfirmInput, regConfirmError, "Паролі не співпадають");
                    isFormValid = false;
                }

                if (isFormValid) {
                    console.log("Registration Success");
                    alert("Реєстрація успішна!");
                    closeModal(signupModal);

                    // Опціонально: скидаємо форму після успіху
                    // signupBtn.innerText = 'Продовжити'; 
                    // confirmBlock.style.display = 'none';
                }
            }
        });
    }
});
