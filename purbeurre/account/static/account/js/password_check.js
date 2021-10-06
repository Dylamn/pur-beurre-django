const password1 = document.querySelector('#id_password1')
const password2 = document.querySelector('#id_password2')

form = document.querySelector('#register_form')

form.addEventListener('submit', (ev) => {
    if (password1.value !== password2.value) {
        ev.preventDefault()
    }
})

password1.addEventListener('input', () => checkEquality(password1, password2))
password2.addEventListener('input', () => checkEquality(password1, password2))

/**
 * Check if the values of the password match and
 * add the validation class accordingly.
 *
 * @param {HTMLInputElement} first
 * @param {HTMLInputElement} second
 * @return void
 */
function checkEquality (first, second) {
    if (! first.value || ! second.value) {
        first.classList.remove('is-invalid', 'is-valid')
        second.classList.remove('is-invalid', 'is-valid')
        return
    }

    if (first.value === second.value) {
        first.classList.remove('is-invalid')
        second.classList.remove('is-invalid')
        first.classList.add('is-valid')
        second.classList.add('is-valid')
    } else {
        first.classList.remove('is-valid')
        second.classList.remove('is-valid')
        first.classList.add('is-invalid')
        second.classList.add('is-invalid')
    }
}
