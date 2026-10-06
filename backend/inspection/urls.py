from django.urls import path

from .views import (
    demo_videos_api,
    inspect_video_api,
)


urlpatterns = [

    path(
        "demo-videos/",
        demo_videos_api,
        name="demo-videos",
    ),

    path(
        "inspect/",
        inspect_video_api,
        name="inspect-video",
    ),

]