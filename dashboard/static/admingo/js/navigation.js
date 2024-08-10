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

// Открытие/закрытие мобильной боковой панели.

const aside = document.getElementsByTagName("aside")[0];
const openMenuButton = document.getElementById("open-menu");

openMenuButton.addEventListener("click", function() {
  if (aside.classList.contains("hide-menu")) {
    aside.classList.remove("hide-menu");
  }
  aside.classList.add("show-menu");
})

const closeMenuButton = document.getElementById("close-menu");

closeMenuButton.addEventListener("click", function() {
  aside.classList.remove("show-menu");
  aside.classList.add("hide-menu");
})

// Открытие/закрытие мобильного поиска.

const searchButton = document.getElementById("top-search");
const searchForm = document.getElementsByClassName("search-top__form")[0]
const userWrapper = document.getElementsByClassName("user_wrapper")[0]
const menu = document.getElementById("open-menu")
const topNavigation = document.getElementsByClassName("top-navigation")[0]

searchButton.addEventListener("click", function() {
  if (searchButton.innerText === "search") {
    searchButton.innerText = "undo";
  }
  else {
    searchButton.innerText = "search";
  }
  topNavigation.classList.toggle("full_width");
  userWrapper.classList.toggle("hide");
  menu.classList.toggle("hide");
  searchForm.classList.toggle("show");
})
