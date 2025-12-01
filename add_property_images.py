#!/usr/bin/env python3

"""
Property Image Upload Script
File: add_property_images.py

This script helps you add sample images to your accommodations.
Run with: python add_property_images.py
"""
import os
import django
import sys

# 1. Point to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_platform.settings')

django.setup()

import django
from pathlib import Path
import requests
from urllib.parse import urlparse

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booking_platform.settings')

try:
    django.setup()
    from accommodations.models import Accommodation, AccommodationImage
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage
except ImportError as e:
    print(f"❌ Error importing Django: {e}")
    print("Make sure you're running this from your project directory")
    sys.exit(1)

def download_image(url, filename):
    """Download image from URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return None

def add_sample_images():
    """Add sample images to accommodations using Unsplash"""
    
    print("🖼️ Adding sample images to properties...")
    
    # Create media directory if it doesn't exist
    media_dir = Path('media/accommodation_images')
    media_dir.mkdir(parents=True, exist_ok=True)
    
    # Unsplash sample image URLs (these are free to use)
    # Format: {accommodation_title_keyword: [image_urls]}
    sample_images = {
        'Luxury Downtown Apartment': [
            'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80',  # Modern apartment
            'https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800&q=80',  # City view
            'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80',   # Luxury interior
        ],
        'Charming Victorian House': [
            'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80',  # Victorian house
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80',  # Beach house
            'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&q=80',  # House exterior
        ],
        'Modern Villa with Private Pool': [
            'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&q=80',  # Villa with pool
            'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&q=80',  # Modern villa
            'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800&q=80',  # Pool area
        ],
        'Cozy Studio in Arts District': [
            'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&q=80',  # Studio apartment
            'https://images.unsplash.com/photo-1565623833408-d77e39b88af6?w=800&q=80',  # Cozy interior
            'https://images.unsplash.com/photo-1522050212171-61b01dd24579?w=800&q=80',  # Arts district
        ],
        'Family-Friendly Cottage': [
            'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&q=80',  # Family cottage
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80',  # Cottage exterior
            'https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?w=800&q=80',  # Garden area
        ],
        'Industrial Loft with Smart Home': [
            'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800&q=80',  # Industrial loft
            'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&q=80',    # Loft interior
            'https://images.unsplash.com/photo-1521747116042-5a810fda9664?w=800&q=80',  # Smart home
        ],
        'Penthouse Suite with Panoramic': [
            'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&q=80',  # Penthouse
            'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&q=80',    # City view
            'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80',  # Luxury suite
        ],
        'Rustic Mountain Cabin': [
            'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80',  # Mountain cabin
            'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',  # Cabin exterior
            'https://images.unsplash.com/photo-1602343168117-bb8ffe3e2e9f?w=800&q=80',  # Hot tub
        ],
        'Beachfront Apartment with Ocean': [
            'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',  # Beach view
            'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=800&q=80',  # Beachfront
            'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80',    # Ocean apartment
        ],
        'Historic Brownstone in Greenwich': [
            'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80',  # Historic building
            'https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800&q=80',  # Brownstone
            'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&q=80',  # Historic interior
        ]
    }
    
    accommodations = Accommodation.objects.all()
    images_added = 0
    
    for accommodation in accommodations:
        print(f"🏠 Processing: {accommodation.title}")
        
        # Find matching images for this accommodation
        matching_images = None
        for key, urls in sample_images.items():
            if key.lower() in accommodation.title.lower():
                matching_images = urls
                break
        
        if not matching_images:
            print(f"⚠️  No matching images found for: {accommodation.title}")
            continue
        
        # Download and add images
        for i, image_url in enumerate(matching_images):
            try:
                print(f"📥 Downloading image {i+1}/3...")
                image_content = download_image(image_url, f"image_{i+1}.jpg")
                
                if image_content:
                    # Create AccommodationImage
                    filename = f"{accommodation.id}_image_{i+1}.jpg"
                    
                    acc_image = AccommodationImage(
                        accommodation=accommodation,
                        caption=f"{accommodation.title} - Image {i+1}",
                        order=i+1,
                        is_primary=(i == 0)
                    )
                    
                    acc_image.image.save(
                        filename,
                        ContentFile(image_content),
                        save=False
                    )
                    acc_image.save()
                    
                    images_added += 1
                    print(f"✅ Added image {i+1} to {accommodation.title}")
                
            except Exception as e:
                print(f"❌ Error adding image {i+1} to {accommodation.title}: {e}")
                continue
    
    print(f"\n🎉 Successfully added {images_added} images to properties!")
    print("\n📋 Next Steps:")
    print("1. Start your server: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000/accommodations/")
    print("3. Check that property images are displaying correctly")
    print("4. If needed, add more images via admin panel or host dashboard")

def show_manual_instructions():
    """Show manual image upload instructions"""
    print("""
🖼️ MANUAL IMAGE UPLOAD INSTRUCTIONS

If the automatic download doesn't work, here's how to add images manually:

1. 📁 CREATE MEDIA FOLDER:
   mkdir -p media/accommodation_images

2. 📥 DOWNLOAD SAMPLE IMAGES:
   - Visit: unsplash.com, pexels.com, or pixabay.com
   - Search for property types (e.g., "luxury apartment", "mountain cabin")
   - Download 3-5 images per property type
   - Save them in media/accommodation_images/

3. 🌐 UPLOAD VIA DASHBOARD:
   - Start server: python manage.py runserver
   - Login as host: john.host@example.com / password123
   - Go to: http://127.0.0.1:8000/dashboard/host/
   - Click "Edit" on each property
   - Upload images using the image upload section

4. 🛡️ UPLOAD VIA ADMIN:
   - Login as admin: admin@bookingplatform.com / admin123
   - Go to: http://127.0.0.1:8000/admin/
   - Navigate to: Accommodations > Accommodation images
   - Add new images and assign to accommodations

5. ✅ VERIFY:
   - Visit property pages to confirm images display
   - Check that primary images show on listings
""")

def main():
    """Main function"""
    print("🖼️ Property Image Upload Script")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        show_manual_instructions()
        return
    
    try:
        # Check if we have accommodations
        if not Accommodation.objects.exists():
            print("❌ No accommodations found!")
            print("Please run: python manage.py populate_data")
            return
        
        # Check if images already exist
        existing_images = AccommodationImage.objects.count()
        if existing_images > 0:
            print(f"ℹ️  Found {existing_images} existing images")
            response = input("Do you want to add more images? (y/n): ")
            if response.lower() != 'y':
                print("👍 Skipping image addition")
                return
        
        # Add sample images
        add_sample_images()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're in your Django project directory")
        print("2. Activate your virtual environment")
        print("3. Install requests: pip install requests")
        print("4. Run: python add_property_images.py --manual")

if __name__ == "__main__":
    main()
