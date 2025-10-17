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
    formData.append('photo', photoInput.files[0]);

    // --- Send data to the backend ---
    try {
        const response = await fetch('/report', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

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