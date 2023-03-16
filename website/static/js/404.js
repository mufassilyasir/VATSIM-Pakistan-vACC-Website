

  (function() {
    "use strict";
  
    /**
     * Easy selector helper function
     */
    const select = (el, all = false) => {
      el = el.trim()
      if (all) {
        return [...document.querySelectorAll(el)]
      } else {
        return document.querySelector(el)
      }
    }
  
    /**
     * Easy event listener function
     */
    const on = (type, el, listener, all = false) => {
      let selectEl = select(el, all)
      if (selectEl) {
        if (all) {
          selectEl.forEach(e => e.addEventListener(type, listener))
        } else {
          selectEl.addEventListener(type, listener)
        }
      }
    }
  
    /**
     * Easy on scroll event listener 
     */
    const onscroll = (el, listener) => {
      el.addEventListener('scroll', listener)
    }
  
    /**
     * Navbar links active state on scroll
     */
    let navbarlinks = select('#navbar .scrollto', true)
    const navbarlinksActive = () => {
      let position = window.scrollY + 200
      navbarlinks.forEach(navbarlink => {
        if (!navbarlink.hash) return
        let section = select(navbarlink.hash)
        if (!section) return
        if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
          navbarlink.classList.add('active')
        } else {
          navbarlink.classList.remove('active')
        }
      })
    }
    window.addEventListener('load', navbarlinksActive)
    onscroll(document, navbarlinksActive)
  
    /**
     * Scrolls to an element with header offset
     */
    const scrollto = (el) => {
      let header = select('#header')
      let offset = header.offsetHeight
  
      let elementPos = select(el).offsetTop
      window.scrollTo({
        top: elementPos - offset,
        behavior: 'smooth'
      })
    }
  
    /**
     * Back to top button
     */
    let backtotop = select('.back-to-top')
    if (backtotop) {
      const toggleBacktotop = () => {
        if (window.scrollY > 100) {
          backtotop.classList.add('active')
        } else {
          backtotop.classList.remove('active')
        }
      }
      window.addEventListener('load', toggleBacktotop)
      onscroll(document, toggleBacktotop)
    }
  
    /**
     * Mobile nav toggle
     */
    on('click', '.mobile-nav-toggle', function(e) {
      select('#navbar').classList.toggle('navbar-mobile')
      this.classList.toggle('bi-list')
      this.classList.toggle('bi-x')
    })
  
    /**
     * Mobile nav dropdowns activate
     */
    on('click', '.navbar .dropdown > a', function(e) {
      if (select('#navbar').classList.contains('navbar-mobile')) {
        e.preventDefault()
        this.nextElementSibling.classList.toggle('dropdown-active')
      }
    }, true)
  
    /**
     * Scrool with ofset on links with a class name .scrollto
     */
    on('click', '.scrollto', function(e) {
      if (select(this.hash)) {
        e.preventDefault()
  
        let navbar = select('#navbar')
        if (navbar.classList.contains('navbar-mobile')) {
          navbar.classList.remove('navbar-mobile')
          let navbarToggle = select('.mobile-nav-toggle')
          navbarToggle.classList.toggle('bi-list')
          navbarToggle.classList.toggle('bi-x')
        }
        scrollto(this.hash)
      }
    }, true)
  
    /**
     * Scroll with ofset on page load with hash links in the url
     */
    window.addEventListener('load', () => {
      if (window.location.hash) {
        if (select(window.location.hash)) {
          scrollto(window.location.hash)
        }
      }
    });
  
    /**
     * Hero carousel indicators
     */
    let heroCarouselIndicators = select("#hero-carousel-indicators")
    let heroCarouselItems = select('#heroCarousel .carousel-item', true)
  
    heroCarouselItems.forEach((item, index) => {
      (index === 0) ?
      heroCarouselIndicators.innerHTML += "<li data-bs-target='#heroCarousel' data-bs-slide-to='" + index + "' class='active'></li>":
        heroCarouselIndicators.innerHTML += "<li data-bs-target='#heroCarousel' data-bs-slide-to='" + index + "'></li>"
    });
  
    /**
     * Porfolio isotope and filter
     */
    window.addEventListener('load', () => {
      let portfolioContainer = select('.portfolio-container');
      if (portfolioContainer) {
        let portfolioIsotope = new Isotope(portfolioContainer, {
          itemSelector: '.portfolio-item',
          layoutMode: 'fitRows'
        });
  
        let portfolioFilters = select('#portfolio-flters li', true);
  
        on('click', '#portfolio-flters li', function(e) {
          e.preventDefault();
          portfolioFilters.forEach(function(el) {
            el.classList.remove('filter-active');
          });
          this.classList.add('filter-active');
  
          portfolioIsotope.arrange({
            filter: this.getAttribute('data-filter')
          });
  
        }, true);
      }
  
    });
  
    /**
     * Initiate portfolio lightbox 
     */
    const portfolioLightbox = GLightbox({
      selector: '.portfolio-lightbox'
    });
  
    /**
     * Portfolio details slider
     */
    new Swiper('.portfolio-details-slider', {
      speed: 400,
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false
      },
      pagination: {
        el: '.swiper-pagination',
        type: 'bullets',
        clickable: true
      }
    });
  
  })()


  // jQuery.
$(function() {
	// Reference the tab links.
	const tabLinks = $('#tab-links li a');
	
	// Handle link clicks.
	tabLinks.click(function(event) {
		var $this = $(this);
		
		// Prevent default click behaviour.
		event.preventDefault();
		
		// Remove the active class from the active link and section.
		$('#tab-links a.active, section.active').removeClass('active');
		
		// Add the active class to the current link and corresponding section.
		$this.addClass('active');
		$($this.attr('href')).addClass('active');
	});
});


  function openGallery(id) {
    closeAll();
    const gallery = document.getElementById('gallery-' + id);
    const card = document.getElementById('card-' + id);
    gallery.classList.add('Gallery--active');
    card.classList.add('Card--active');
  }
  
  function closeAll() {
    const galleryActv = document.querySelector('.Gallery--active');
    const cardActv = document.querySelector('.Card--active');
    if (galleryActv) {
      galleryActv.classList.remove('Gallery--active');
    }
    if (cardActv) {
      cardActv.classList.remove('Card--active');
    }
  }
  var open01 = document.getElementById("open-popup-btn");
  var dismiss = document.getElementById("dismiss-popup-btn");
  var open1 = document.getElementById("open1-popup1-btn1");
  var dismiss1 = document.getElementById("dismiss1-popup1-btn1");
  var open2 = document.getElementById("open2-popup2-btn2");
  var dismiss2 = document.getElementById("dismiss2-popup2-btn2");

  if (open01) {
  document.getElementById("open-popup-btn").addEventListener("click",function(){
    document.getElementsByClassName("popup")[0].classList.add("active");
  });
  };

  if (dismiss){
  document.getElementById("dismiss-popup-btn").addEventListener("click",function(){
    document.getElementsByClassName("popup")[0].classList.remove("active");
  });
  };
  if (open1){
  document.getElementById("open1-popup1-btn1").addEventListener("click",function(){
    document.getElementsByClassName("popup1")[0].classList.add("active");
  });
  };

  if (dismiss1){
  document.getElementById("dismiss1-popup1-btn1").addEventListener("click",function(){
    document.getElementsByClassName("popup1")[0].classList.remove("active");
  });
  };

  if (open2){
  document.getElementById("open2-popup2-btn2").addEventListener("click",function(){
    document.getElementsByClassName("popup2")[0].classList.add("active");
  });
  };

  if (dismiss2){
  document.getElementById("dismiss2-popup2-btn2").addEventListener("click",function(){
    document.getElementsByClassName("popup2")[0].classList.remove("active");
  });
  };

  $(function() {
    var dimmerButton = $('.open1-popup1-btn1');
    var dimmer = $('.dimmer');
    var exit = $('.dismiss1-popup1-btn1');
    dimmerButton.on('click', function() {
      dimmer.show();
    });
    exit.on('click', function() {
      dimmer.hide();
    });
  });

  $(function() {
    var dimmerButton = $('.open2-popup2-btn2');
    var dimmer = $('.dimmer');
    var exit = $('.dismiss2-popup2-btn2');
    dimmerButton.on('click', function() {
      dimmer.show();
    });
    exit.on('click', function() {
      dimmer.hide();
    });
  });

  $(function() {
    var dimmerButton = $('.open-popup-btn');
    var dimmer = $('.dimmer');
    var exit = $('.dismiss-popup-btn');
    dimmerButton.on('click', function() {
      dimmer.show();
    });
    exit.on('click', function() {
      dimmer.hide();
    });
  });