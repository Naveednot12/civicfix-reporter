// --- 1. Get references to our HTML elements ---
const form = document.getElementById('report-form');
const issueTypeSelect = document.getElementById('issue-type');
const photoInput = document.getElementById('photo-input');
const fileNameSpan = document.getElementById('file-name');
const getLocationBtn = document.getElementById('get-location-btn');
const locationStatus = document.getElementById('location-status');
const submitBtn = document.getElementById('submit-btn');
const feedbackArea = document.getElementById('feedback-area');
const feedbackMessage = document.getElementById('feedback-message');
const spinner = document.querySelector('.spinner');

// Store the user's location coordinates
let userLatitude = null;
let userLongitude = null;

function preparePhoto(file) {
    return new Promise((resolve, reject) => {
        const image = new Image();
        const objectUrl = URL.createObjectURL(file);

        image.onload = () => {
            URL.revokeObjectURL(objectUrl);
            const scale = Math.min(1, 1200 / Math.max(image.width, image.height));
            const canvas = document.createElement('canvas');
            canvas.width = Math.round(image.width * scale);
            canvas.height = Math.round(image.height * scale);
            canvas.getContext('2d').drawImage(image, 0, 0, canvas.width, canvas.height);
            canvas.toBlob((blob) => {
                if (blob) {
                    resolve(new File([blob], 'issue_report.jpg', { type: 'image/jpeg' }));
                } else {
                    reject(new Error('Could not process the photo.'));
                }
            }, 'image/jpeg', 0.8);
        };
        image.onerror = () => {
            URL.revokeObjectURL(objectUrl);
            reject(new Error('Could not read the photo.'));
        };
        image.src = objectUrl;
    });
}

// --- 2. Event Listeners ---

// Update the file name when a user chooses a photo
photoInput.addEventListener('change', () => {
    if (photoInput.files.length > 0) {
        fileNameSpan.textContent = photoInput.files[0].name;
    } else {
        fileNameSpan.textContent = 'No file chosen';
    }
});

// Get the user's GPS location
getLocationBtn.addEventListener('click', () => {
    if (!navigator.geolocation) {
        locationStatus.textContent = 'Geolocation is not supported by your browser.';
        return;
    }

    locationStatus.textContent = 'Getting location...';

    navigator.geolocation.getCurrentPosition(
        (position) => {
            userLatitude = position.coords.latitude;
            userLongitude = position.coords.longitude;
            locationStatus.textContent = '✅ Location acquired!';
            getLocationBtn.classList.add('success');
        },
        () => {
            locationStatus.textContent = 'Unable to retrieve your location.';
        }
    );
});

// Handle the form submission
form.addEventListener('submit', async (event) => {
    event.preventDefault(); // Stop the default browser refresh

    // --- Validation ---
    if (!userLatitude || !userLongitude) {
        alert('Please get your location before submitting.');
        return;
    }
    if (photoInput.files.length === 0) {
        alert('Please upload a photo of the issue.');
        return;
    }

    // --- UI feedback ---
    submitBtn.disabled = true;
    feedbackArea.classList.remove('hidden');
    feedbackMessage.textContent = 'Submitting your report...';
    feedbackMessage.className = '';
    spinner.style.display = 'block';

    // --- Prepare data for sending ---
    const formData = new FormData();
    formData.append('lat', userLatitude);
    formData.append('lon', userLongitude);
    formData.append('issue_type', issueTypeSelect.value);
    try {
        formData.append('photo', await preparePhoto(photoInput.files[0]));
    } catch (error) {
        feedbackMessage.textContent = error.message;
        feedbackMessage.classList.add('error');
        submitBtn.disabled = false;
        spinner.style.display = 'none';
        return;
    }

    // --- Send data to the backend ---
    try {
        const response = await fetch('/report', {
            method: 'POST',
            body: formData,
        });

        const responseText = await response.text();
        let result = {};
        try {
            result = responseText ? JSON.parse(responseText) : {};
        } catch {
            result.detail = `Server returned HTTP ${response.status}.`;
        }

        if (response.ok) {
            feedbackMessage.textContent = 'Report submitted successfully! Thank you.';
            feedbackMessage.classList.add('success');
            form.reset();
            fileNameSpan.textContent = 'No file chosen';
            locationStatus.textContent = 'Location not set';
            getLocationBtn.classList.remove('success');
            // Hide the feedback message after a few seconds
            setTimeout(() => {
                feedbackArea.classList.add('hidden');
            }, 4000); // Hide after 4 seconds
        } else {
            // Check for our specific geocoding error
            if (result.detail && result.detail.includes("determine address")) {
                feedbackMessage.textContent = "Error: Could not find a street address. Please move to a main road and try getting your location again.";
            } else {
                // Display other errors from the backend
                 feedbackMessage.textContent = `Error: ${result.detail || 'An unknown error occurred.'}`;
    }
    feedbackMessage.classList.add('error');
}
    } catch (error) {
        feedbackMessage.textContent = 'A network error occurred. Please try again.';
        feedbackMessage.classList.add('error');
    } finally {
        // Always re-enable the submit button and hide the spinner
        submitBtn.disabled = false;
        spinner.style.display = 'none';
    }
});