const forms = document.getElementsByClassName('delete-review-form')

for (let i = 0; i < forms.length; i++) {
    forms[i].addEventListener('submit', e => {
        e.preventDefault()
        const confirmed = confirm('Voulez-vous vraiment supprimer votre avis ?')

        if (confirmed) {
            forms[i].submit()
        }
    })
}
