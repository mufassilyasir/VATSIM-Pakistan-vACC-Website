
const showModal = (openButton, modalContent) =>{
    const openBtn = document.getElementById(openButton),
    modalContainer = document.getElementById(modalContent)
    
    if(openBtn && modalContainer){
        openBtn.addEventListener('click', ()=>{
            modalContainer.classList.add('show-modal')
        })
    }
}
showModal('open-modal','modal-container')

/*=============== CLOSE MODAL ===============*/
const closeBtn = document.querySelectorAll('.close-modal')

function closeModal(){
    const modalContainer = document.getElementById('modal-container')
    modalContainer.classList.remove('show-modal')
}
closeBtn.forEach(c => c.addEventListener('click', closeModal))




document.getElementById("open-popup-btn").addEventListener("click",function(){
    document.getElementsByClassName("popup")[0].classList.add("active");
  });
  
  document.getElementById("dismiss-popup-btn").addEventListener("click",function(){
    document.getElementsByClassName("popup")[0].classList.remove("active");
  });

  $(function() {
    var dimmerButton = $('.open-popup-btn');
    console.log(1)
    var dimmer = $('.dimmer');
    var exit = $('.dismiss-popup-btn');
    dimmerButton.on('click', function() {
      dimmer.show();
      console.log(2)
    });
    exit.on('click', function() {
      dimmer.hide();
      console.log(3)
    });
  });