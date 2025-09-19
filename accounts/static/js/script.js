document.addEventListener('DOMContentLoaded', function () {
  console.log("Script initialized: Dropdown and Menu");

  // 1. Menu toggle for mobile navigation
  const menuToggle = document.getElementById('menuToggle');
  const navLinks = document.getElementById('navLinks');

  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', function () {
      navLinks.classList.toggle('active');
      menuToggle.classList.toggle('active');
    });
  }

  // 2. User Dashboard Dropdown Logic
  const userAvatar = document.getElementById('user-avatar');
  const userDropdown = document.getElementById('user-dropdown-menu');

  if (userAvatar && userDropdown) {
    userAvatar.addEventListener('click', function (e) {
      e.stopPropagation(); // Prevent the document click from firing immediately
      console.log("Avatar clicked, toggling dropdown");
      userDropdown.classList.toggle('active');
    });
  }

  // 3. Close dropdown when clicking anywhere else on the page
  document.addEventListener('click', function (e) {
    // Check if the dropdown exists and if the click was outside of it
    if (userDropdown && !userAvatar.contains(e.target) && !userDropdown.contains(e.target)) {
      // Only remove the class if it's currently active
      if (userDropdown.classList.contains('active')) {
        console.log("Clicked outside, closing dropdown");
        userDropdown.classList.remove('active');
      }
    }
  });

});

// Toggle text function for course descriptions with smooth animation
function toggleText(id) {
  const element = document.getElementById('desc-' + id);
  const button = element.nextElementSibling;
  const fullText = element.getAttribute('data-full');
  const shortText = fullText.length > 100 ? fullText.substring(0, 100) + '...' : fullText;
  
  // Check if currently expanded using data attribute
  const isExpanded = element.getAttribute('data-expanded') === 'true';
  
  if (!isExpanded) {
    // Expand - Show full text with animation
    element.classList.add('expanded');
    setTimeout(() => {
      element.textContent = fullText;
    }, 50); // Small delay for smooth transition
    button.textContent = 'See Less';
    element.setAttribute('data-expanded', 'true');
  } else {
    // Collapse - Show short text with animation
    element.classList.remove('expanded');
    setTimeout(() => {
      element.textContent = shortText;
    }, 50); // Small delay for smooth transition
    button.textContent = 'See More';
    element.setAttribute('data-expanded', 'false');
  }
}
