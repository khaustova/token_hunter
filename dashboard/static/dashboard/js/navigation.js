'use strict'; 

// Открытие/закрытие выпадающего меню пользователя.

const mainMenu = document.getElementById("user-menu");
const userMenu = document.getElementById("expand-user-menu");

const username = document.getElementsByClassName("user__name")[0]
username.addEventListener("click", function() {
  mainMenu.classList.toggle("open");
  userMenu.innerHTML = !mainMenu.classList.contains("open")
  ? "expand_more"
  : "close";
})

// Закрытие административного сообщения.

const closeMessageButton = document.getElementsByClassName("message_close")[0];

if (closeMessageButton) {
  closeMessageButton.addEventListener("click", function() {
    const message = document.getElementsByClassName("message")[0];
    message.classList.add("hide");
  });
}