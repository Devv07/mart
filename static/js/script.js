document.addEventListener('mousemove', (e) => {
    const heroVisual = document.querySelector('.hero-visual');
    const xAxis = (window.innerWidth / 2 - e.pageX) / 25;
    const yAxis = (window.innerHeight / 2 - e.pageY) / 25;
    
    if (heroVisual) {
        heroVisual.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
    }
});

const productCards = document.querySelectorAll('.product-card');
productCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const xAxis = (card.clientWidth / 2 - e.offsetX) / 25;
        const yAxis = (card.clientHeight / 2 - e.offsetY) / 25;
        card.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg) translateY(-10px)`;
    });
    
    card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(-10px)';
    });
});

const aiToggle = document.querySelector('.ai-toggle');
if (aiToggle) {
    aiToggle.addEventListener('click', () => {
        alert('AI shopping assistant activated. How can I help you today?');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('JavaScript loaded');
    // Add to cart
    document.querySelectorAll('.action-icon form').forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            const productId = this.action.split('/').slice(-2)[0];
            fetch(`/user/add-to-cart/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new FormData(this)
            })
            .then(response => response.json())
            .then(data => alert(data.message))
            .catch(error => console.error('Error:', error));
        });
    });
    // Add to wishlist
    document.querySelectorAll('.action-icon[href*="add_to_wishlist"]').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const productId = this.href.split('/').slice(-2)[0];
            fetch(`/user/add-to-wishlist/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                const heart = this.querySelector('i.fas.fa-heart');
                heart.style.color = heart.style.color === 'rgb(255, 77, 77)' ? '#ccc' : '#ff4d4d';
            })
            .catch(error => console.error('Error:', error));
        });
    });
    // Check session status periodically
    function checkSession() {
        fetch('/check-session/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (!data.is_authenticated) {
                window.location.href = '/login/';
            }
        })
        .catch(error => console.error('Session check error:', error));
    }
    setInterval(checkSession, 30000); // Check every 30 seconds
});