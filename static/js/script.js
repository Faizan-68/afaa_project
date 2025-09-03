// Prevent multiple script execution
if (window.scriptLoaded) {
  console.log("Script already loaded, skipping...");
} else {
  window.scriptLoaded = true;
  
  document.addEventListener("DOMContentLoaded", function () {
    console.log("Script.js loaded");
    
    // Menu toggle functionality
    const menuToggle = document.getElementById("menuToggle");
    const navLinks = document.getElementById("navLinks");

    if (menuToggle && navLinks) {
      // Remove any existing event listeners to prevent duplicates
      const newMenuToggle = menuToggle.cloneNode(true);
      menuToggle.parentNode.replaceChild(newMenuToggle, menuToggle);
      
      newMenuToggle.addEventListener("click", function () {
        console.log("Menu toggle clicked");
        navLinks.classList.toggle("active");
        newMenuToggle.classList.toggle("active");
      });
    }

    // User panel dropdown logic
    const avatar = document.getElementById("userAvatar");
    const panel = document.getElementById("userPanel");
    if (avatar && panel) {
      avatar.addEventListener("click", function (e) {
        e.stopPropagation();
        panel.classList.toggle("active");
      });
      document.addEventListener("click", function (e) {
        if (!avatar.contains(e.target)) {
          panel.classList.remove("active");
        }
      });
    }
    
    // Copy referral code logic
    const copyRefBtn = document.getElementById("copyRefBtn");
    if (copyRefBtn) {
      copyRefBtn.addEventListener("click", function () {
        const code = document.getElementById("refCode").textContent;
        navigator.clipboard.writeText(code);
        this.textContent = "Copied!";
        setTimeout(() => {
          this.textContent = "Copy";
        }, 1200);
      });
    }
    
    // Logout button logic
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
      logoutBtn.onclick = function () {
        window.location.href = "login.html";
      };
    }
    
    // Invite friend button logic
    const inviteFriendBtn = document.getElementById("inviteFriendBtn");
    if (inviteFriendBtn) {
      inviteFriendBtn.onclick = function () {
        const msg = encodeURIComponent(
          "Hey! Join me at Afaa Elevate Digital Academy for amazing courses. Use my referral code AFAA1234 to sign up: https://your-website.com"
        );
        window.open("https://wa.me/?text=" + msg, "_blank");
      };
    }

    // See More button functionality (for courses page and user dashboard)
    const seeMoreBtns = document.querySelectorAll('.see-more-btn');
    if (seeMoreBtns.length > 0) {
      console.log('Found', seeMoreBtns.length, 'see more buttons');
      
      seeMoreBtns.forEach((btn, index) => {
        btn.addEventListener('click', function () {
          console.log('Button clicked:', index);
          const desc = this.previousElementSibling;
          if (desc && desc.classList.contains('course-description')) {
            desc.classList.toggle('expanded');
            this.textContent = desc.classList.contains('expanded') ? 'See Less' : 'See More';
            console.log('Description expanded:', desc.classList.contains('expanded'));
          } else {
            console.log('Description element not found or wrong class');
          }
        });
      });
    }

    // Payment method selection and form toggle (for payments page)
    const visaBox = document.getElementById('visaBox');
    const mcBox = document.getElementById('mcBox');
    const visaForm = document.getElementById('visaForm');
    const mcForm = document.getElementById('mcForm');
    
    if (visaBox && mcBox && visaForm && mcForm) {
      // Remove selected from all
      function clearSelected() {
        visaBox.classList.remove('selected');
        mcBox.classList.remove('selected');
        visaForm.style.display = 'none';
        mcForm.style.display = 'none';
      }
      
      visaBox.addEventListener('click', function() {
        if (!visaBox.classList.contains('selected')) {
          clearSelected();
          visaBox.classList.add('selected');
          visaForm.style.display = 'block';
        } else {
          clearSelected();
        }
      });
      
      mcBox.addEventListener('click', function() {
        if (!mcBox.classList.contains('selected')) {
          clearSelected();
          mcBox.classList.add('selected');
          mcForm.style.display = 'block';
        } else {
          clearSelected();
        }
      });
      
      // Prevent form submit (demo only)
      document.querySelectorAll('.card-form form').forEach(f => {
        f.addEventListener('submit', function(e) {
          e.preventDefault();
          alert('This is a demo. Payment processing is not implemented.');
        });
      });
    }
  });
}
