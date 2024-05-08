const menu = document.querySelector('#mobile-menu')
const menuLinks = document.querySelector('.navbar__menu')

menu.addEventListener('click', function() {
    menu.classList.toggle('is-active');
    menuLinks.classList.toggle('active');
})

var swiper = new Swiper(".swiper", {
    effect: "cards",
    grabCursor: true,
    initialSlide: 15,
    speed: 300,
    loop: false,
    rotate: true,
    mousewheel: {
    invert: false,
  },
});