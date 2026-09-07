/**
 * Nestlé Purina Confidential Access Gatekeeper
 * Protects H5N1 Risk Assessment and Monitoring Portals with Passcode Security.
 */
(function () {
    const VALID_PASSCODES = [
        'purina2026',
        'purinablayney',
        'blayney2026',
        'purina',
        'nestlepurina'
    ];

    const STORAGE_KEY = 'purina_h5n1_auth_token';
    const AUTH_VALUE = 'GRANTED_' + btoa('Purina2026_Nestle_BioSecurity');

    function isAuthorized() {
        return (
            sessionStorage.getItem(STORAGE_KEY) === AUTH_VALUE ||
            localStorage.getItem(STORAGE_KEY) === AUTH_VALUE
        );
    }

    function createAuthOverlay() {
        if (document.getElementById('purina-auth-gatekeeper')) return;

        // Detect language
        const isEnglish = document.documentElement.lang === 'en' ||
            window.location.pathname.includes('_en.html') ||
            document.title.toLowerCase().includes('english');

        const overlay = document.createElement('div');
        overlay.id = 'purina-auth-gatekeeper';
        overlay.style.cssText = `
            position: fixed;
            inset: 0;
            z-index: 999999;
            background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #f8fafc;
            backdrop-filter: blur(16px);
        `;

        const titleText = isEnglish
            ? 'Restricted Access Portal'
            : '內部機密專案情報系統';

        const subtitleText = isEnglish
            ? 'Supply Chain Biosecurity Telemetry & Quantitative Risk Model'
            : '跨國供應鏈生物安全動態遙測與進口風險決策模型';

        const descText = isEnglish
            ? 'This portal contains proprietary commercial risk evaluations and non-public epidemiological telemetry. Access is strictly limited to authorized personnel. Please enter your passcode to continue.'
            : '本系統包含商業機密與未公開流行病學遙測數據，僅限授權人員訪問。請輸入存取通行碼以繼續。';

        const placeholderText = isEnglish
            ? 'Enter Access Passcode'
            : '請輸入存取通行碼';

        const submitText = isEnglish ? 'Verify & Enter' : '驗證並進入系統';
        const rememberText = isEnglish ? 'Remember this browser (30 days)' : '記住此瀏覽器授權 (30 天內免重複輸入)';
        const errorText = isEnglish ? 'Invalid passcode. Please contact project administrator.' : '通行碼錯誤，請洽詢專案管理員';

        overlay.innerHTML = `
            <div id="purina-auth-card" style="
                background: rgba(15, 23, 42, 0.95);
                border: 1px solid rgba(56, 189, 248, 0.3);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 35px rgba(6, 182, 212, 0.2);
                border-radius: 20px;
                max-width: 460px;
                width: 100%;
                padding: 32px 28px;
                text-align: center;
                position: relative;
                animation: fadeInScale 0.3s ease-out;
            ">
                <!-- Lock Icon Badge -->
                <div style="
                    width: 64px;
                    height: 64px;
                    margin: 0 auto 16px;
                    background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(245, 158, 11, 0.2));
                    border: 1.5px solid #f59e0b;
                    border-radius: 18px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
                ">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                </div>

                <!-- Security Tag -->
                <div style="
                    display: inline-block;
                    background: #991b1b;
                    color: #fee2e2;
                    font-size: 11px;
                    font-weight: 800;
                    letter-spacing: 1.5px;
                    text-transform: uppercase;
                    padding: 4px 12px;
                    border-radius: 9999px;
                    margin-bottom: 12px;
                    border: 1px solid rgba(248, 113, 113, 0.4);
                ">
                    CONFIDENTIAL • RESTRICTED ACCESS
                </div>

                <h2 style="font-size: 20px; font-weight: 800; color: #ffffff; margin: 0 0 6px 0; letter-spacing: -0.5px;">
                    ${titleText}
                </h2>
                <div style="font-size: 12px; color: #38bdf8; font-weight: 600; margin-bottom: 12px;">
                    ${subtitleText}
                </div>
                <p style="font-size: 12px; color: #94a3b8; line-height: 1.5; margin: 0 0 22px 0;">
                    ${descText}
                </p>

                <!-- Passcode Input Form -->
                <form id="purina-auth-form" onsubmit="return false;" style="margin-bottom: 16px;">
                    <div style="position: relative; margin-bottom: 12px;">
                        <input type="password" id="purina-passcode-input" placeholder="${placeholderText}" autocomplete="current-password" style="
                            width: 100%;
                            box-sizing: border-box;
                            padding: 13px 44px 13px 16px;
                            background: #020617;
                            border: 1.5px solid #334155;
                            border-radius: 12px;
                            color: #ffffff;
                            font-size: 14px;
                            font-weight: 600;
                            outline: none;
                            transition: all 0.2s ease;
                        " />
                        <button type="button" id="purina-toggle-pwd" style="
                            position: absolute;
                            right: 12px;
                            top: 50%;
                            transform: translateY(-50%);
                            background: transparent;
                            border: none;
                            color: #64748b;
                            cursor: pointer;
                            padding: 4px;
                            font-size: 14px;
                        ">👁️</button>
                    </div>

                    <div id="purina-error-msg" style="
                        display: none;
                        color: #f87171;
                        font-size: 12px;
                        font-weight: 600;
                        margin-bottom: 12px;
                        background: rgba(239, 68, 68, 0.1);
                        border: 1px solid rgba(239, 68, 68, 0.3);
                        padding: 6px 12px;
                        border-radius: 8px;
                    ">${errorText}</div>

                    <div style="display: flex; align-items: center; justify-content: flex-start; gap: 8px; margin-bottom: 18px; font-size: 12px; color: #cbd5e1; cursor: pointer;">
                        <input type="checkbox" id="purina-remember-me" style="cursor: pointer; accent-color: #06b6d4; width: 15px; height: 15px;" />
                        <label for="purina-remember-me" style="cursor: pointer;">${rememberText}</label>
                    </div>

                    <button type="submit" id="purina-submit-btn" style="
                        width: 100%;
                        background: linear-gradient(135deg, #0284c7 0%, #06b6d4 100%);
                        color: #ffffff;
                        border: none;
                        padding: 13px;
                        border-radius: 12px;
                        font-size: 14px;
                        font-weight: 700;
                        cursor: pointer;
                        box-shadow: 0 4px 14px rgba(6, 182, 212, 0.4);
                        transition: all 0.2s ease;
                    ">${submitText}</button>
                </form>

                <div style="font-size: 11px; color: #64748b;">
                    Enterprise Biosecurity Management System • Restricted Access
                </div>
            </div>
        `;

        document.body.appendChild(overlay);
        document.body.style.overflow = 'hidden';

        // Focus input
        setTimeout(() => {
            const input = document.getElementById('purina-passcode-input');
            if (input) input.focus();
        }, 150);

        // Toggle password visibility
        const toggleBtn = document.getElementById('purina-toggle-pwd');
        const pwdInput = document.getElementById('purina-passcode-input');
        if (toggleBtn && pwdInput) {
            toggleBtn.addEventListener('click', () => {
                pwdInput.type = pwdInput.type === 'password' ? 'text' : 'password';
            });
        }

        // Form Submit
        const form = document.getElementById('purina-auth-form');
        form.addEventListener('submit', handleAuthSubmit);
    }

    function handleAuthSubmit() {
        const input = document.getElementById('purina-passcode-input');
        const remember = document.getElementById('purina-remember-me');
        const errorMsg = document.getElementById('purina-error-msg');
        const card = document.getElementById('purina-auth-card');

        if (!input) return;

        const val = input.value.trim().toLowerCase();
        if (VALID_PASSCODES.includes(val)) {
            // SUCCESS
            sessionStorage.setItem(STORAGE_KEY, AUTH_VALUE);
            if (remember && remember.checked) {
                localStorage.setItem(STORAGE_KEY, AUTH_VALUE);
            }

            const overlay = document.getElementById('purina-auth-gatekeeper');
            if (overlay) {
                overlay.style.transition = 'opacity 0.3s ease-out';
                overlay.style.opacity = '0';
                setTimeout(() => {
                    overlay.remove();
                    document.body.style.overflow = '';
                }, 300);
            }
        } else {
            // ERROR SHAKE
            if (errorMsg) errorMsg.style.display = 'block';
            input.style.borderColor = '#ef4444';
            input.style.boxShadow = '0 0 10px rgba(239, 68, 68, 0.4)';

            if (card) {
                card.style.animation = 'none';
                card.offsetHeight; // reflow
                card.style.animation = 'shakeCard 0.4s ease-in-out';
            }
        }
    }

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInScale {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        @keyframes shakeCard {
            0%, 100% { transform: translateX(0); }
            20%, 60% { transform: translateX(-8px); }
            40%, 80% { transform: translateX(8px); }
        }
    `;
    document.head.appendChild(style);

    // Global Logout Function
    window.purinaLogout = function () {
        sessionStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(STORAGE_KEY);
        location.reload();
    };

    // Auto-run check
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            if (!isAuthorized()) createAuthOverlay();
        });
    } else {
        if (!isAuthorized()) createAuthOverlay();
    }
})();
