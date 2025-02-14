fetch('http://localhost:8000/images')
    .then(response => response.json())
    .then(data => {
        const imagesContainer = document.getElementById('images');
        data.images.forEach(image => {
            const imageElement = document.createElement('img');
            imageElement.src = `/images/${image}`;
            imageElement.alt = image;
            imagesContainer.appendChild(imageElement);
        });
    })