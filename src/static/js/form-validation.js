// Form validation script
document.addEventListener('DOMContentLoaded', function() {
    // Get all forms with class needs-validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Find all invalid fields and add animation
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.classList.add('input-error');
                    
                    // Remove the animation class after animation completes
                    setTimeout(() => {
                        field.classList.remove('input-error');
                    }, 500);
                });
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Add page transition effect when navigating
    const navButtons = document.querySelectorAll('.nav-button');
    navButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Don't apply to form submission buttons that need validation
            if (this.type === 'submit' && this.form && this.form.classList.contains('needs-validation')) {
                return;
            }
            
            e.preventDefault();
            const targetUrl = this.getAttribute('href') || this.getAttribute('formaction');
            
            // Add fade-out effect
            document.querySelector('main').style.opacity = '0';
            document.querySelector('main').style.transform = 'translateY(20px)';
            document.querySelector('main').style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            
            // Navigate after animation completes
            setTimeout(() => {
                window.location.href = targetUrl;
            }, 300);
        });
    });
    
    // Add page entrance animation
    document.querySelector('main').classList.add('page-transition');
});

// Signature pad functionality
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('signature-pad');
    if (!canvas) return;
    
    const signaturePad = new SignaturePad(canvas, {
        backgroundColor: 'rgba(255, 255, 255, 0)',
        penColor: 'black'
    });
    
    // Set canvas dimensions
    function resizeCanvas() {
        const ratio = Math.max(window.devicePixelRatio || 1, 1);
        canvas.width = canvas.offsetWidth * ratio;
        canvas.height = canvas.offsetHeight * ratio;
        canvas.getContext("2d").scale(ratio, ratio);
        signaturePad.clear(); // Otherwise isEmpty() might return incorrect value
    }
    
    window.addEventListener("resize", resizeCanvas);
    resizeCanvas();
    
    // Clear signature button
    document.getElementById('clear-signature').addEventListener('click', function() {
        signaturePad.clear();
    });
    
    // Form submission - save signature data
    document.querySelector('form').addEventListener('submit', function(e) {
        if (signaturePad.isEmpty()) {
            e.preventDefault();
            alert('Please provide a signature');
            return false;
        }
        
        const signatureData = document.getElementById('signature-data');
        signatureData.value = signaturePad.toDataURL();
    });
});
