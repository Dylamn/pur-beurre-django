const ratingInput = document.getElementById('review_rating')
const ratingGauge = document.getElementById('rating_input_gauge')

const regex = /rating-[1-5]/i

ratingInput.addEventListener('change', e => {
    ratingGauge.className = ratingGauge.className.replace(regex, `rating-${e.target.value}`)
})
