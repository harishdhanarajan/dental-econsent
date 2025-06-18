// Registration success handling
document.addEventListener('DOMContentLoaded', function() {
    const consentForm = document.getElementById('consent-form');
    if (consentForm) {
        consentForm.addEventListener('submit', function(e) {

            if (!window.signaturePad || window.signaturePad.isEmpty()) {
                e.preventDefault();
                alert('Please provide a signature');
                return false;
            }
            const signatureData = document.getElementById('signature-data');
            if (signatureData) {
                signatureData.value = window.signaturePad.toDataURL();
            }
        });
    }
});

// Thank you modal function
function showThankYouModal() {
    // Create modal elements
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'modal-overlay';
    modalOverlay.style.position = 'fixed';
    modalOverlay.style.top = '0';
    modalOverlay.style.left = '0';
    modalOverlay.style.width = '100%';
    modalOverlay.style.height = '100%';
    modalOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modalOverlay.style.display = 'flex';
    modalOverlay.style.justifyContent = 'center';
    modalOverlay.style.alignItems = 'center';
    modalOverlay.style.zIndex = '9999';
    
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '30px';
    modalContent.style.borderRadius = '10px';
    modalContent.style.textAlign = 'center';
    modalContent.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.3)';
    modalContent.style.animation = 'fadeIn 0.5s ease-in-out';
    
    const modalIcon = document.createElement('div');
    modalIcon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="#28a745" viewBox="0 0 16 16"><path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-3.97-3.03a.75.75 0 0 0-1.08.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-.01-1.05z"/></svg>';
    
    const modalTitle = document.createElement('h2');
    modalTitle.textContent = 'Thanks for Registering!';
    modalTitle.style.margin = '20px 0';
    modalTitle.style.color = '#28a745';
    
    const modalMessage = document.createElement('p');
    modalMessage.textContent = 'Your information has been saved successfully.';
    modalMessage.style.fontSize = '18px';
    
    // Add elements to DOM
    modalContent.appendChild(modalIcon);
    modalContent.appendChild(modalTitle);
    modalContent.appendChild(modalMessage);
    modalOverlay.appendChild(modalContent);
    document.body.appendChild(modalOverlay);
    
    // Add animation style
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);
    
    // Remove modal after 5 seconds
    setTimeout(function() {
        modalOverlay.style.opacity = '0';
        modalOverlay.style.transition = 'opacity 0.5s ease';
        setTimeout(function() {
            document.body.removeChild(modalOverlay);
        }, 500);
    }, 4500);
}
