import UITour from "./libs/uitour";
import trackEvent from "sumo/js/analytics";
import SwitchingDevicesWizardManager from "sumo/js/switching-devices-wizard-manager";
import "sumo/js/form-wizard";

document.addEventListener("DOMContentLoaded", function () {
  new SwitchingDevicesWizardManager(document.querySelector("#switching-devices-wizard"));
  kbTabsInit();
});


// This function initializes the tabs on the switching-devices page
// and adds click event listener
function kbTabsInit() {
  document.getElementById("kb-tab-all").style.display = "block";
  let tabItems = document.querySelectorAll('[data-event-category="link click"]');
  tabItems.forEach((item) => {
    item.addEventListener("click", (ev) => {
      toggleTabContent(ev);
    });
  });
}

// This function toggles the visibility of the tab content based on 
// clicked tab 
function toggleTabContent(ev) {
  let tabContent = document.getElementsByClassName("topic-list");
  [].forEach.call(tabContent, (el) => {
    el.style.display = "none";
  });

  let tabItems = document.getElementsByClassName("tabs--link");
  [].forEach.call(tabItems, (item) => {
    item.classList.remove("is-active");
  });

  ev.target.parentElement.classList.add("is-active");
  document.getElementById("tab-" + ev.target.parentElement.dataset.eventLabel).style.display = "block";
}