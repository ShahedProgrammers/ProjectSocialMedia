// // API Base URL
// const API_BASE = 'http://localhost:8000/api';

// // Login Form Handler
// document.getElementById('login-form').addEventListener('submit', async (e) => {
//     e.preventDefault();

//     const formData = new FormData(e.target);
//     const data = {
//         identifier: formData.get('identifier'),
//         password: formData.get('password')
//     };

//     try {
//         const response = await fetch(`${API_BASE}/auth/login/`, {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(data)
//         });

//         const result = await response.json();

//         if (response.ok) {
//             // Store JWT tokens
//             localStorage.setItem('access_token', result.access);
//             localStorage.setItem('refresh_token', result.refresh);
//             localStorage.setItem('user_id', result.user_id);

//             // Redirect to main page
//             window.location.href = 'main.html';
//         } else {
//             alert(result.error || 'خطا در ورود. لطفاً اطلاعات را بررسی کنید.');
//         }
//     } catch (error) {
//         console.error('Login error:', error);
//         alert('خطا در برقراری ارتباط با سرور');
//     }
// });

// // Face Recognition Login
// let stream = null;

// function openFaceLogin() {
//     const modal = document.getElementById('face-modal');
//     const video = document.getElementById('face-video');

//     modal.classList.remove('hidden');

//     // Start camera
//     navigator.mediaDevices.getUserMedia({ video: true })
//         .then(mediaStream => {
//             stream = mediaStream;
//             video.srcObject = mediaStream;
//         })
//         .catch(err => {
//             alert('دسترسی به دوربین امکان‌پذیر نیست');
//             console.error(err);
//         });
// }

// function closeFaceLogin() {
//     const modal = document.getElementById('face-modal');
//     modal.classList.add('hidden');

//     if (stream) {
//         stream.getTracks().forEach(track => track.stop());
//     }
// }

// async function captureFace() {
//     const video = document.getElementById('face-video');
//     const canvas = document.getElementById('face-canvas');
//     const status = document.getElementById('face-status');

//     const context = canvas.getContext('2d');

//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;

//     context.drawImage(video, 0, 0, canvas.width, canvas.height);

//     const imageData = canvas.toDataURL('image/png');

//     status.innerText = "در حال بررسی چهره...";

//     try {
//         const response = await fetch(`${API_BASE}/auth/face-login/`, {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json"
//             },
//             body: JSON.stringify({ image: imageData })
//         });

//         const result = await response.json();

//         if (response.ok) {
//             localStorage.setItem('access_token', result.access);
//             localStorage.setItem('refresh_token', result.refresh);

//             window.location.href = "main.html";
//         } else {
//             status.innerText = "چهره شناسایی نشد";
//         }

//     } catch (error) {
//         status.innerText = "خطا در ارتباط با سرور";
//     }
// }




// =====================================================
// دیگر از API و JWT استفاده نمی‌کنیم.
// لاگین و ثبت‌نام با ارسال عادی فرم انجام می‌شوند.
// =====================================================

// --- بخش لاگین با فرم عادی (نیازی به JS نیست) ---
// فرم در HTML به صورت زیر تعریف شده است:
// <form method="POST" action="{% url 'login' %}">
//     {% csrf_token %}
//     ...
// </form>
// مرورگر خودش درخواست POST می‌زند و جنگو بعد از احراز هویت کاربر را redirect می‌کند.
// بنابراین شنوندهٔ submit را حذف کرده‌ایم.

// =====================================================
// Face Recognition Login (مودال)
// =====================================================
let stream = null;

function openFaceLogin() {
    const modal = document.getElementById('face-modal');
    const video = document.getElementById('face-video');

    modal.classList.remove('hidden');

    // Start camera
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(mediaStream => {
            stream = mediaStream;
            video.srcObject = mediaStream;
        })
        .catch(err => {
            alert('دسترسی به دوربین امکان‌پذیر نیست');
            console.error(err);
        });
}

function closeFaceLogin() {
    const modal = document.getElementById('face-modal');
    modal.classList.add('hidden');

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
}

async function captureFace() {
    const video = document.getElementById('face-video');
    const canvas = document.getElementById('face-canvas');
    const status = document.getElementById('face-status');

    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/png');

    status.innerText = "در حال بررسی چهره...";

    try {
        // ارسال تصویر به یک ویوی جنگو که کار تشخیص چهره را انجام می‌دهد.
        // این ویو سشن را تنظیم کرده و آدرس خانه را برمی‌گرداند.
        const response = await fetch('/face-login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // CSRF token را باید از کوکی یا یک تگ hidden دریافت کنید.
                'X-CSRFToken': getCookie('csrftoken') // تابع کمکی برای CSRF
            },
            body: JSON.stringify({ image: imageData })
        });

        const result = await response.json();

        if (response.ok && result.redirect) {
            // موفقیت: به صفحه خانه برو
            window.location.href = result.redirect;
        } else {
            status.innerText = result.error || "چهره شناسایی نشد";
        }
    } catch (error) {
        status.innerText = "خطا در ارتباط با سرور";
        console.error(error);
    }
}

// تابع کمکی برای دریافت مقدار CSRF از کوکی
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}