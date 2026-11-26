document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#registro-form');
    const statusBox = document.querySelector('#registro-status');

    if (!form || !statusBox) return;

    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton ? submitButton.textContent : '';

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (!form.reportValidity()) return;

        statusBox.className = 'alert alert-info mt-3';
        statusBox.setAttribute('role', 'status');
        statusBox.textContent = 'Enviando tu registro…';
        form.setAttribute('aria-busy', 'true');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.textContent = 'Enviando…';
        }

        try {
            const response = await fetch(form.action || window.location.href, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            const result = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(result.message || 'No se pudo completar el registro. Revisa los datos e inténtalo de nuevo.');
            }

            form.reset();
            statusBox.className = 'alert alert-success mt-3';
            statusBox.setAttribute('role', 'status');
            statusBox.replaceChildren(document.createTextNode(`${result.message} `));
            if (result.login_url) {
                const loginLink = document.createElement('a');
                loginLink.href = result.login_url;
                loginLink.textContent = 'Iniciar sesión';
                statusBox.append(loginLink);
            }
        } catch (error) {
            statusBox.className = 'alert alert-danger mt-3';
            statusBox.setAttribute('role', 'alert');
            statusBox.textContent = error.message || 'No se pudo conectar con Canaco. Inténtalo de nuevo.';
        } finally {
            form.removeAttribute('aria-busy');
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = originalButtonText;
            }
        }
    });
});