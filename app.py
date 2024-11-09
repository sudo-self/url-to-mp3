from flask import Flask, request, send_file, jsonify
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_DIR = "/tmp"  # Directory to save the downloaded audio file
COOKIE_FILE_PATH = 'cookies.txt'  # Relative path to cookies.txt file in the same directory

@app.route('/convert', methods=['POST'])
def convert_url_to_mp3():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Check if the cookies file exists
    if not os.path.exists(COOKIE_FILE_PATH):
        return jsonify({"error": "Cookie file not found"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True, 
        'cookiefile': COOKIE_FILE_PATH  # Relative path to cookies.txt
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict).replace(info_dict["ext"], "mp3")
            
            # Ensure file exists before sending
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
            else:
                return jsonify({"error": "File not found after download."}), 500
            
    except yt_dlp.utils.DownloadError as e:
        if "Sign in to confirm" in str(e):
            return jsonify({"error": "This video requires authentication. Please try another URL."}), 403
        return jsonify({"error": f"Download failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
       
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port)






