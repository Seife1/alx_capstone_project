let modal = document.querySelector(".modal");
let btn = document.querySelector(".delete_modal");

btn.addEventListener("click", () => {
  modal.style.display = "block";
});

function hideModal() {
  modal.style.display = "none";
}

window.onclick = function(event) {
  if (event.target == modal) {
    hideModal();
  }
};