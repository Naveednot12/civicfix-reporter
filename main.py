from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import database
import geocoder
import email_sender
from PIL import Image
import io
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# --- 1. Initial Setup ---
# Create the database and tables when the app starts
database.create_db_and_tables()

# Create the main application instance
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')
# --- 2. Database Dependency ---
# This function creates a "session" (a conversation) with the database
# and makes sure it's closed correctly after the request is finished.
# We will use this to talk to our database inside the API endpoint.
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. The Main Reporting Endpoint ---
@app.post("/report")
async def create_report(
    lat: float = Form(...),
    lon: float = Form(...),
    issue_type: str = Form(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # --- Step A: Geocoding ---
    print(f"Received report for location: ({lat}, {lon})")
    address_info = geocoder.get_address_from_coords(lat, lon)
    if not address_info or not address_info.get("city"):
        # If we can't find the address, we can't proceed.
        raise HTTPException(status_code=400, detail="Could not determine address from coordinates.")

    city = address_info["city"]
    district = address_info["district"]
    print(f"Geocoded address: City={city}, District={district}")

    # --- Step B: Database Routing ---
    # Query the database to find a matching routing rule.
    # --- Step B: Database Routing with fallback ---

    routing_rule = (
        db.query(database.RoutingRule)
        .filter(
            database.RoutingRule.city == city,
            database.RoutingRule.district == district,
            database.RoutingRule.issue_type == issue_type
        )
        .first()
    )

# 2️⃣ Fallback: city + issue (ignore district)
    if not routing_rule:
        routing_rule = (
            db.query(database.RoutingRule)
            .filter(
                database.RoutingRule.city == city,
                database.RoutingRule.issue_type == issue_type
            )
            .first()
        )

# 3️⃣ Fallback: any city, any issue (global)
    if not routing_rule:
        routing_rule = (
            db.query(database.RoutingRule)
            .filter(database.RoutingRule.issue_type == issue_type)
            .first()
        )

# Final fallback: default email (never fail)
    if not routing_rule:
        target_email = "naveed12092004@gmail.com"
        print("No routing rule found. Using default email.")
    else:
        target_email = routing_rule.contact_email
        print(f"Found routing rule. Target email: {target_email}")



    if routing_rule:
        target_email = routing_rule.contact_email
        print(f"Found routing rule. Target email: {target_email}")
    else:
    # fallback email for any location / issue
        target_email = "naveed12092004@gmail.com"
        print("No routing rule found. Using fallback email.")


    # --- Step C: Image Processing ---
    # Read the uploaded photo into memory as bytes.
    photo_bytes = await photo.read()
    
    # Use Pillow to resize and compress the image to save space.
    try:
        image = Image.open(io.BytesIO(photo_bytes))
        image.thumbnail((800, 800)) # Resize to max 800x800 pixels
        
        # Save the resized image back into a byte buffer
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        processed_photo_bytes = buffer.getvalue()
        print("Image processed successfully.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file. Error: {e}")


    # --- Step D: Email Sending ---
    subject = f"New Civic Issue Report: {issue_type} in {city}"
    body = f"""
    <h1>New Civic Issue Report Received</h1>
    <p><b>Issue Type:</b> {issue_type}</p>
    <p><b>Location:</b> {city}, {district}</p>
    <p>A new report has been submitted via the CivicFix Reporter app.</p>
    <p>Approximate Location on Google Maps: <a href='https://www.google.com/maps?q={lat},{lon}'>Click Here</a></p>
    """

    email_sent = email_sender.send_report_email(
        to_email=target_email,
        subject=subject,
        body=body,
        photo_bytes=processed_photo_bytes
    )

    if not email_sent:
        # If Brevo fails to send the email, report an error.
        raise HTTPException(status_code=500, detail="Failed to send the report email.")

    # --- Step E: Success! ---
    return {"message": "Report submitted successfully!", "recipient": target_email}
