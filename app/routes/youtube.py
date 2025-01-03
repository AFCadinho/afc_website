from flask import Blueprint, redirect, url_for, request
from app.youtube_requests import get_latest_video
from app.models import LatestVideo
from datetime import datetime
from app import db
from app.utils import admin_required

bp = Blueprint('youtube', __name__)


@bp.route("/get_latest_video", methods=["POST"])
@admin_required
def latest_video():
    csrf_token = request.form.get("csrf_token")

    if not csrf_token:
        return redirect(url_for("general.index"))

    fetch_and_store_latest_video()

    return redirect(url_for("general.index"))


def fetch_and_store_latest_video():
    video_url, video_title = get_latest_video()
    
    if video_url:
        latest_video = LatestVideo.query.first()
        if latest_video:
            latest_video.video_id = video_url.split("/")[-1]
            latest_video.title = video_title
            latest_video.url = video_url
            latest_video.updated_at = datetime.now()
            print("EDITED NEW LATEST VIDEO")
        else:
            latest_video = LatestVideo(
                video_id=video_url.split("/")[-1],
                title=video_title,
                url=video_url
            )
            print("ADDED NEW LATEST VIDEO")
            db.session.add(latest_video)
        
        db.session.commit()