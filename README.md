# CivicFix Reporter 📍

A simple, mobile-first web application that allows citizens to instantly report local civic issues (like potholes, broken streetlights, or uncollected garbage) to the correct municipal authorities automatically.

---

### **Live Demo**

**You can try the live application here: [https://civicfix-reporter.vercel.app](https://civicfix-reporter.vercel.app)**

---

## Key Features

* **Simple Interface:** A clean, single-page form designed for quick use on a mobile phone.
* **Automatic Geolocation:** Uses the browser's GPS to get the user's exact coordinates.
* **Smart Routing:** The backend uses reverse geocoding to convert GPS coordinates into a specific administrative district.
* **Automated Reporting:** Automatically finds the correct contact email from a database and sends a professionally formatted report with the photo attached.
* **Image Optimization:** Resizes and compresses uploaded photos on the fly to ensure fast and reliable email delivery.

---

## Tech Stack

* **Backend:** Python with **FastAPI**
* **Database:** **PostgreSQL** (hosted on Neon)
* **Geocoding:** **Nominatim (OpenStreetMap)** via the `geopy` library
* **Email Service:** **Brevo API** for reliable transactional emails
* **Frontend:** Plain **HTML, CSS, and JavaScript**
* **Deployment:** Hosted on **Vercel** with continuous deployment from GitHub.

---

## Local Setup

To run this project locally:

1.  Clone the repository.
2.  Install the required packages: `pip install -r requirements.txt`
3.  Set up your environment variables for `BREVO_API_KEY` and `DATABASE_URL`.
4.  Run the application: `uvicorn main:app --reload`