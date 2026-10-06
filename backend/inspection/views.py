from pathlib import Path
from uuid import uuid4

from django.conf import settings

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .inspection_service import inspect_video


# ============================================================
# PREDEFINED DEMO VIDEOS
# ============================================================

DEMO_VIDEOS = {
    "mixerror": {
        "filename": "mixerror.mp4",
        "title": "Mixed Defects 01",
        "description": "Mixed bottle defect inspection scenario.",
    },

    "mixerror1": {
        "filename": "mixerror1.mp4",
        "title": "Mixed Defects 02",
        "description": "Multiple bottles with different defects.",
    },

    "mixerror2": {
        "filename": "mixerror2.mp4",
        "title": "Mixed Defects 03",
        "description": "Advanced mixed bottle inspection scenario.",
    },
}



# ============================================================
# COMMON RESPONSE
# ============================================================

def build_inspection_response(summary, output_name):
    return {
        "success": True,
        "message": "Inspection completed successfully.",
        "frames_processed": summary["frames_processed"],
        "total_bottles": summary["total_bottles"],
        "accepted": summary["accepted"],
        "rejected": summary["rejected"],
        "defect_summary": summary["defect_summary"],
        "results": summary["results"],
        "video_url": settings.MEDIA_URL + f"results/{output_name}",
    }


# ============================================================
# GET DEMO VIDEOS
# ============================================================

@api_view(["GET"])
def demo_videos_api(request):

    videos = []

    for demo_id, demo in DEMO_VIDEOS.items():

        video_path = (
            settings.DEMO_VIDEO_ROOT /
            demo["filename"]
        )

        if video_path.exists():

            videos.append({
                "id": demo_id,
                "title": demo["title"],
                "description": demo["description"],
                "filename": demo["filename"],
                "video_url": (
                    settings.DEMO_VIDEO_URL +
                    demo["filename"]
                ),
            })

    return Response({
        "success": True,
        "videos": videos,
    })


# ============================================================
# INSPECT VIDEO
#
# Accepts either:
#
# 1. Uploaded video
# 2. Predefined demo video
#
# Only ONE source is allowed at a time.
# ============================================================

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def inspect_video_api(request):

    uploaded_video = request.FILES.get("video")
    demo_video_id = request.data.get("demo_video")

    # --------------------------------------------------------
    # BOTH SOURCES SELECTED
    # --------------------------------------------------------

    if uploaded_video and demo_video_id:

        return Response(
            {
                "success": False,
                "message": (
                    "Please select either an uploaded video "
                    "or a demo video, not both."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # DEMO VIDEO
    # --------------------------------------------------------

    if demo_video_id:

        demo = DEMO_VIDEOS.get(demo_video_id)

        if not demo:

            return Response(
                {
                    "success": False,
                    "message": "Invalid demo video selected.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        input_path = (
            settings.DEMO_VIDEO_ROOT /
            demo["filename"]
        )

        if not input_path.exists():

            return Response(
                {
                    "success": False,
                    "message": "Demo video file not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        output_name = (
            f"{input_path.stem}_inspection_"
            f"{uuid4().hex[:8]}.mp4"
        )

        result_dir = (
            Path(settings.MEDIA_ROOT) /
            "results"
        )

        result_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = result_dir / output_name

    # --------------------------------------------------------
    # UPLOADED VIDEO
    # --------------------------------------------------------

    elif uploaded_video:

        allowed_extensions = {
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
        }

        extension = Path(
            uploaded_video.name
        ).suffix.lower()

        if extension not in allowed_extensions:

            return Response(
                {
                    "success": False,
                    "message": (
                        "Unsupported video format. "
                        "Use MP4, AVI, MOV or MKV."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload_dir = (
            Path(settings.MEDIA_ROOT) /
            "uploads"
        )

        result_dir = (
            Path(settings.MEDIA_ROOT) /
            "results"
        )

        upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        result_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Create unique filename
        unique_name = (
            f"{Path(uploaded_video.name).stem}_"
            f"{uuid4().hex[:8]}"
            f"{extension}"
        )

        input_path = upload_dir / unique_name

        with open(input_path, "wb+") as destination:

            for chunk in uploaded_video.chunks():
                destination.write(chunk)

        output_name = (
            f"{input_path.stem}_inspection.mp4"
        )

        output_path = result_dir / output_name

    # --------------------------------------------------------
    # NO VIDEO
    # --------------------------------------------------------

    else:

        return Response(
            {
                "success": False,
                "message": (
                    "Please upload a video or "
                    "select a demo video."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --------------------------------------------------------
    # RUN AI INSPECTION
    # --------------------------------------------------------

    try:

        summary = inspect_video(
            input_video=input_path,
            output_video=output_path,
        )

    except Exception as error:

        return Response(
            {
                "success": False,
                "message": "Inspection failed.",
                "error": str(error),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        build_inspection_response(
            summary,
            output_name,
        ),
        status=status.HTTP_200_OK,
    )