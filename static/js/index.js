// index.js
document.addEventListener('DOMContentLoaded', function() {
  // Handle flash messages
  handleFlashMessages();
  
  // Add animations to elements
  addAnimations();
  
  // Handle modal switching
  handleModalSwitching();
});

function handleFlashMessages() {
  const flashMessages = document.querySelectorAll('.flash-message');
  
  if (flashMessages.length > 0) {
    // Create alert container if it doesn't exist
    let alertContainer = document.getElementById('custom-alert-container');
    if (!alertContainer) {
      alertContainer = document.createElement('div');
      alertContainer.id = 'custom-alert-container';
      alertContainer.style.position = 'fixed';
      alertContainer.style.top = '100px';
      alertContainer.style.right = '20px';
      alertContainer.style.zIndex = '1050';
      document.body.appendChild(alertContainer);
    }
    
    // Process each flash message
    flashMessages.forEach(flash => {
      const category = flash.getAttribute('data-category');
      const message = flash.getAttribute('data-message');
      
      // Create alert element
      const alert = document.createElement('div');
      alert.className = `custom-alert alert alert-${category} alert-dismissible fade`;
      alert.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert">&times;</button>
      `;
      
      // Add to container
      alertContainer.appendChild(alert);
      
      // Show alert with animation
      setTimeout(() => {
        alert.classList.add('show');
      }, 100);
      
      // Auto dismiss after 5 seconds
      setTimeout(() => {
        if (alert.parentNode) {
          alert.classList.remove('show');
          setTimeout(() => {
            if (alert.parentNode) {
              alert.parentNode.removeChild(alert);
            }
          }, 500);
        }
      }, 5000);
    });
  }
}

function addAnimations() {
  // Animate feature cards on scroll
  const featureCards = document.querySelectorAll('.feature-card, .step-card');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });
  
  featureCards.forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(card);
  });
}

function handleModalSwitching() {
  // Handle login/register modal switching
  $('a[data-dismiss="modal"][data-toggle="modal"]').on('click', function() {
    const targetModal = $(this).data('target');
    $('.modal').modal('hide');
    setTimeout(() => {
      $(targetModal).modal('show');
    }, 500);
  });
}