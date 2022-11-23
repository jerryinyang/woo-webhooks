const open_btn = document.querySelector(".open-btn")
const close_btn = document.querySelector(".close-btn")
const nav = document.querySelector(".nav")

if (open_btn){
  open_btn.addEventListener('click', () => {
      console.log('clicked')
      nav.classList.toggle('visible')
  })
}

if (close_btn){
  close_btn.addEventListener('click', () => nav.classList.toggle ('visible'))
}
