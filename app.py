from flask import Flask, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import os
import atexit
import ffmpeg
import json

app = Flask(__name__)

# Configuration
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
UPLOAD_FOLDER = 'uploads'

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists at startup
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:
            return {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
    except Exception as e:
        print(f"Error getting EXIF data: {e}")
    return None

def dms_to_decimal(dms):
    if not dms:
        return None
    degrees, minutes, seconds = dms
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

def get_gps_coordinates_from_image(exif_data):
    gps_info = exif_data.get('GPSInfo') if exif_data else None
    if gps_info:
        gps_coords = {GPSTAGS.get(key, key): value for key, value in gps_info.items()}
        lat = gps_coords.get('GPSLatitude')
        lon = gps_coords.get('GPSLongitude')

        if lat and lon:
            latitude = dms_to_decimal(lat)
            longitude = dms_to_decimal(lon)
            if gps_coords.get('GPSLatitudeRef') == 'S':
                latitude = -latitude
            if gps_coords.get('GPSLongitudeRef') == 'W':
                longitude = -longitude
            return latitude, longitude
    return None, None

def get_video_metadata(video_path):
    try:
        metadata = ffmpeg.probe(video_path, v='error', select_streams='v:0',
                                show_entries='stream=codec_name,width,height,r_frame_rate,duration', format='json')
        metadata = json.loads(metadata)
        video_stream = metadata.get('streams', [])[0]
        return {
            'width': video_stream.get('width'),
            'height': video_stream.get('height'),
            'duration': video_stream.get('duration')
        }
    except Exception as e:
        print(f"Error extracting video metadata: {e}")
    return None

def cleanup_uploads():
    folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(folder):
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

atexit.register(cleanup_uploads)

@app.route("/", methods=["GET", "POST"])
def index():
    file_url = None
    if request.method == "POST":
        uploaded_file = request.files.get('file')
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            file_url = url_for('uploaded_file', filename=filename)

            if allowed_image_file(filename):
                exif_data = get_exif_data(file_path)
                if exif_data:
                    gps_lat, gps_lon = get_gps_coordinates_from_image(exif_data)
                    if gps_lat and gps_lon:
                        google_maps_url = f"https://www.google.com/maps?q={gps_lat},{gps_lon}"
                        return render_template("index.html", exif_data=exif_data, gps_lat=gps_lat, gps_lon=gps_lon, google_maps_url=google_maps_url, file_url=file_url)
                    return render_template("index.html", exif_data=exif_data, error="No GPS data found.", file_url=file_url)
                return render_template("index.html", error="No EXIF data found.", file_url=file_url)

            elif allowed_video_file(filename):
                video_metadata = get_video_metadata(file_path)
                if video_metadata:
                    return render_template("index.html", video_metadata=video_metadata, file_url=file_url)
                return render_template("index.html", error="No video metadata found.", file_url=file_url)

            return render_template("index.html", error="Invalid file format.", file_url=file_url)

    return render_template("index.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
