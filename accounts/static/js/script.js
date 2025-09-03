document.addEventListener("DOMContentLoaded", function () {
  console.log("Script loaded successfully!");
  
  // Mobile menu toggle
  const menuToggle = document.getElementById("menuToggle");
  const navLinks = document.getElementById("navLinks");

  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", function () {
      navLinks.classList.toggle("active");
      menuToggle.classList.toggle("active");
    });
  }

  // User panel toggle
  const userAvatar = document.getElementById("userAvatar");
  const userPanel = document.getElementById("userPanel");

  if (userAvatar && userPanel) {
    userAvatar.addEventListener("click", function () {
      userPanel.classList.toggle("active");
    });

    // Close user panel when clicking outside
    document.addEventListener("click", function (event) {
      if (!userAvatar.contains(event.target)) {
        userPanel.classList.remove("active");
      }
    });
  }

  // Copy referral code functionality
  const copyRefBtn = document.getElementById("copyRefBtn");
  const refCode = document.getElementById("refCode");

  if (copyRefBtn && refCode) {
    copyRefBtn.addEventListener("click", function () {
      const textToCopy = refCode.textContent;
      
      // Create a temporary textarea to copy text
      const textarea = document.createElement("textarea");
      textarea.value = textToCopy;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      
      // Show feedback
      copyRefBtn.textContent = "Copied!";
      setTimeout(() => {
        copyRefBtn.textContent = "Copy";
      }, 2000);
    });
  }

  // Logout functionality
  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", function () {
      // Add logout logic here
      window.location.href = "/logout/";
    });
  }

  // Smooth scrolling for anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach(link => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const targetId = this.getAttribute("href");
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: "smooth",
          block: "start"
        });
      }
    });
  });

  // Invite friend button functionality
  const inviteFriendBtn = document.getElementById("inviteFriendBtn");
  console.log("Looking for invite button:", inviteFriendBtn);
  
  if (inviteFriendBtn) {
    inviteFriendBtn.addEventListener("click", function () {
      const msg = encodeURIComponent('Hey! Join me at Afaa Elevate Digital Academy for amazing courses. Use my referral code AFAA1234 to sign up: https://your-website.com');
      const url = `https://wa.me/?text=${msg}`;
      window.open(url, '_blank');
    });
  } else {
    console.log("Invite button not found!");
  }

  // Add active class to current nav link
  const currentPath = window.location.pathname;
  const navLinkElements = document.querySelectorAll(".nav-link");
  
  navLinkElements.forEach(link => {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });
});