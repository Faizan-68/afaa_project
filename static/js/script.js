document.addEventListener('DOMContentLoaded', function () {
  console.log("Script initialized: Dropdown and Menu");

  // Smooth typing animation for the hero section
  const animatedTypingElement = document.getElementById('animatedTyping');
  if (animatedTypingElement) {
    const text = "Afaa Elevate";
    let index = 0;

    function type() {
      if (index < text.length) {
        animatedTypingElement.textContent += text.charAt(index);
        index++;
        setTimeout(type, 150); // Adjust speed here (milliseconds)
      } else {
        // Reset and loop
        setTimeout(() => {
          animatedTypingElement.textContent = "";
          index = 0;
          type();
        }, 2000); // Pause before restarting
      }
    }
    type(); // Start the animation
  }

  // 1. Menu toggle for mobile navigation
  const menuToggle = document.getElementById('menuToggle');
  const navLinks = document.getElementById('navLinks');

  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', function () {
      navLinks.classList.toggle('active');
      menuToggle.classList.toggle('active');
    });
  }

  // Close mobile menu when clicking on navigation links
  if (navLinks) {
    const navLinksAll = navLinks.querySelectorAll('.nav-link');
    navLinksAll.forEach(link => {
      link.addEventListener('click', function() {
        if (navLinks.classList.contains('active')) {
          navLinks.classList.remove('active');
          if (menuToggle) {
            menuToggle.classList.remove('active');
          }
        }
      });
    });
  }

  // Close mobile menu when clicking outside
  document.addEventListener('click', function(e) {
    if (navLinks && menuToggle) {
      if (!navLinks.contains(e.target) && !menuToggle.contains(e.target)) {
        if (navLinks.classList.contains('active')) {
          navLinks.classList.remove('active');
          menuToggle.classList.remove('active');
        }
      }
    }
  });

  // 2. User Dashboard Dropdown Logic
  const userAvatar = document.getElementById('user-avatar');
  const userDropdown = document.getElementById('user-dropdown-menu');

  if (userAvatar && userDropdown) {
    userAvatar.addEventListener('click', function (e) {
      e.stopPropagation();
      userDropdown.classList.toggle('active');
    });
  }

  // 3. Close dropdown when clicking anywhere else on the page
  document.addEventListener('click', function (e) {
    if (userDropdown && userAvatar && !userAvatar.contains(e.target) && !userDropdown.contains(e.target)) {
      if (userDropdown.classList.contains('active')) {
        userDropdown.classList.remove('active');
      }
    }
  });

  // 4. Logout functionality
  const logoutButton = document.getElementById('logout-button');
  if (logoutButton) {
    logoutButton.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Show confirmation dialog
      if (confirm('Are you sure you want to logout?')) {
        // Create a form to submit logout request
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/accounts/logout/';
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
          const csrfInput = document.createElement('input');
          csrfInput.type = 'hidden';
          csrfInput.name = 'csrfmiddlewaretoken';
          csrfInput.value = csrfToken.value;
          form.appendChild(csrfInput);
        }
        
        document.body.appendChild(form);
        form.submit();
      }
    });
  }

  // CSRF Token Refresh Functionality
  // Refresh CSRF token every 30 minutes to prevent failures
  function refreshCSRFToken() {
    fetch('/csrf-refresh/', {
      method: 'GET',
      credentials: 'same-origin',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    })
    .then(response => {
      if (response.ok) {
        return response.json();
      }
      throw new Error('CSRF refresh failed');
    })
    .then(data => {
      if (data.csrf_token) {
        // Update all CSRF tokens on the page
        const csrfTokens = document.querySelectorAll('input[name="csrfmiddlewaretoken"]');
        csrfTokens.forEach(token => {
          token.value = data.csrf_token;
        });
        
        // Update meta tag if exists
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (csrfMeta) {
          csrfMeta.content = data.csrf_token;
        }
        
        console.log('CSRF token refreshed successfully');
      }
    })
    .catch(error => {
      console.warn('CSRF token refresh failed:', error);
    });
  }

  // Set up periodic CSRF token refresh (every 30 minutes)
  setInterval(refreshCSRFToken, 30 * 60 * 1000);
  
  // Also refresh on user activity after long inactivity
  let lastActivity = Date.now();
  const inactivityThreshold = 25 * 60 * 1000; // 25 minutes
  
  function updateActivity() {
    const now = Date.now();
    if (now - lastActivity > inactivityThreshold) {
      refreshCSRFToken();
    }
    lastActivity = now;
  }
  
  // Listen for user activity
  ['click', 'keypress', 'scroll', 'mousemove'].forEach(eventType => {
    document.addEventListener(eventType, updateActivity, { passive: true });
  });

});

// Toggle text function for course descriptions with smooth animation
function toggleText(id) {
  const element = document.getElementById('desc-' + id);
  const button = element.nextElementSibling;
  const fullText = element.getAttribute('data-full');
  const shortText = fullText.length > 100 ? fullText.substring(0, 100) + '...' : fullText;
  
  const isExpanded = element.getAttribute('data-expanded') === 'true';
  
  if (!isExpanded) {
    element.classList.add('expanded');
    setTimeout(() => {
      element.textContent = fullText;
    }, 50);
    button.textContent = 'See Less';
    element.setAttribute('data-expanded', 'true');
  } else {
    element.classList.remove('expanded');
    setTimeout(() => {
      element.textContent = shortText;
    }, 50);
    button.textContent = 'See More';
    element.setAttribute('data-expanded', 'false');
  }
}
