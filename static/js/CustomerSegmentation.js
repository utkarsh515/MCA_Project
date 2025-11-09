// CustomerSegmentation.js
function handleSubmit(event) {
    event.preventDefault();

    var file = document.getElementById("file-upload").files[0];
    if (!file) {
        alert("Please select a file first.");
        return;
    }

    var formData = new FormData();
    formData.append("file", file);

    var spinner = document.getElementById("spinner");
    spinner.style.display = "block";

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/predict");

    xhr.send(formData);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            spinner.style.display = "none";
            
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                displayResults(response);
            } else {
                console.error("Error:", xhr.status, xhr.statusText);
                alert("An error occurred while processing your file. Please try again.");
            }
        }
    };
}

function displayResults(response) {
    // Show results section
    document.getElementById("results-section").style.display = "block";
    
    // Clear previous results
    const imageGrid = document.getElementById("image-grid");
    imageGrid.innerHTML = "";
    
    // Create image cards for each visualization
    const images = [
        { key: "amount_img", title: "Amount by Cluster" },
        { key: "freq_img", title: "Frequency by Cluster" },
        { key: "recency_img", title: "Recency by Cluster" },
        { key: "amount_pie", title: "Amount Distribution" },
        { key: "freq_pie", title: "Frequency Distribution" },
        { key: "recency_pie", title: "Recency Distribution" }
    ];
    
    images.forEach(img => {
        if (response[img.key]) {
            const imageCard = document.createElement("div");
            imageCard.className = "image-card";
            imageCard.innerHTML = `
                <img src="${response[img.key]}" alt="${img.title}" data-src="${response[img.key]}" data-title="${img.title}">
                <div class="card-body">
                    <h5>${img.title}</h5>
                    <button class="btn btn-sm btn-outline-primary view-btn">View Larger</button>
                </div>
            `;
            imageGrid.appendChild(imageCard);
        }
    });
    
    // Add event listeners to images and buttons
    document.querySelectorAll('.image-card img, .view-btn').forEach(element => {
        element.addEventListener('click', function() {
            let imgSrc, title;
            
            if (this.tagName === 'IMG') {
                imgSrc = this.getAttribute('data-src');
                title = this.getAttribute('data-title');
            } else {
                const imgElement = this.closest('.image-card').querySelector('img');
                imgSrc = imgElement.getAttribute('data-src');
                title = imgElement.getAttribute('data-title');
            }
            
            openModal(imgSrc, title);
        });
    });
    
    // Scroll to results section
    document.getElementById("results-section").scrollIntoView({ behavior: 'smooth' });
}

function openModal(imgSrc, title) {
    document.getElementById('modalImage').src = imgSrc;
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('downloadLink').href = imgSrc;
    $('#imageModal').modal('show');
}

// Add event listener to form when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('upload-form').addEventListener('submit', handleSubmit);
    
    // Add event listener for file input change to show file name
    document.getElementById('file-upload').addEventListener('change', function(e) {
        const fileName = e.target.files[0].name;
        const label = document.querySelector('.file-upload-label span');
        label.textContent = fileName;
    });
});