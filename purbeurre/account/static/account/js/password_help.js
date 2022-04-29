(() => {
    const new_password = document.getElementById('new_password')
    const password_help = document.getElementById('password_help')
    const varietyRegex = /[^A-Za-z]/

    if (new_password && password_help) {
        const length_check = document.getElementById('password_length_check')
        const variety_check = document.getElementById('password_variety_check')

        new_password.addEventListener('focus', () => {
            password_help.classList.remove('d-none')
        })
        new_password.addEventListener('blur', () => {
            password_help.classList.add('d-none')
        })

        new_password.addEventListener('keyup', (e) => {
            const value = e.target.value.trim()

            length_check.className = value.length >= 8 ? 'checked' : 'unchecked'
            variety_check.className = varietyRegex.test(value) ? 'checked' : 'unchecked'
        })
    }
})()
