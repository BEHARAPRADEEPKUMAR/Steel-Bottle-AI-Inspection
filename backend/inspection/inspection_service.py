from pathlib import Path
from collections import defaultdict

import subprocess

import cv2
import imageio_ffmpeg
from ultralytics import YOLO


# ============================================================
# MODELS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"

BOTTLE_MODEL_PATH = MODELS_DIR / "bottle_detector_best.pt"
DEFECT_MODEL_PATH = MODELS_DIR / "defect_detector_best.pt"

bottle_model = YOLO(str(BOTTLE_MODEL_PATH))
defect_model = YOLO(str(DEFECT_MODEL_PATH))


# ============================================================
# CONFIGURATION
# ============================================================

BOTTLE_CONF = 0.40
DEFECT_CONF = 0.20

BOTTLE_IMGSZ = 512
DEFECT_IMGSZ = 640

DEFECT_CONFIRM_CONF = 0.45
HIGH_DEFECT_CONF = 0.70

MAX_CENTER_DISTANCE = 160
MAX_MISSED_FRAMES = 8
MIN_IOU = 0.05
EDGE_MARGIN = 15


DEFECT_NAMES = {
    "cap_defect",
    "coating_defect",
    "deformation",
    "dent",
    "rust",
    "scratch",
}


# ============================================================
# BASIC GEOMETRY
# ============================================================

def calculate_iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection_width = max(0, x2 - x1)
    intersection_height = max(0, y2 - y1)

    intersection_area = (
        intersection_width * intersection_height
    )

    area1 = (
        max(0, box1[2] - box1[0])
        * max(0, box1[3] - box1[1])
    )

    area2 = (
        max(0, box2[2] - box2[0])
        * max(0, box2[3] - box2[1])
    )

    union_area = area1 + area2 - intersection_area

    if union_area <= 0:
        return 0.0

    return intersection_area / union_area


def center_of_box(box):
    return (
        (box[0] + box[2]) / 2,
        (box[1] + box[3]) / 2,
    )


def center_distance(box1, box2):
    center1 = center_of_box(box1)
    center2 = center_of_box(box2)

    return (
        (center1[0] - center2[0]) ** 2
        + (center1[1] - center2[1]) ** 2
    ) ** 0.5


# ============================================================
# BOTTLE DETECTION
# ============================================================

def detect_bottles(frame):
    results = bottle_model.predict(
        source=frame,
        conf=BOTTLE_CONF,
        imgsz=BOTTLE_IMGSZ,
        verbose=False,
    )

    detections = []

    if not results:
        return detections

    result = results[0]

    if result.boxes is None:
        return detections

    for box in result.boxes:

        coordinates = box.xyxy[0].cpu().numpy()

        x1, y1, x2, y2 = map(
            int,
            coordinates,
        )

        confidence = float(
            box.conf[0].cpu().item()
        )

        detections.append(
            {
                "box": (x1, y1, x2, y2),
                "confidence": confidence,
            }
        )

    return detections


# ============================================================
# DEFECT DETECTION
# ============================================================

def detect_defects(crop):
    results = defect_model.predict(
        source=crop,
        conf=DEFECT_CONF,
        imgsz=DEFECT_IMGSZ,
        verbose=False,
    )

    detections = []

    if not results:
        return detections

    result = results[0]

    if result.boxes is None:
        return detections

    names = defect_model.names

    for box in result.boxes:

        class_id = int(
            box.cls[0].cpu().item()
        )

        confidence = float(
            box.conf[0].cpu().item()
        )

        defect_name = names[class_id]

        # GOOD is not a defect
        if defect_name == "good":
            continue

        # Ignore unexpected classes
        if defect_name not in DEFECT_NAMES:
            continue

        detections.append(
            {
                "defect": defect_name,
                "confidence": confidence,
            }
        )

    return detections


# ============================================================
# TRACK MATCHING
# ============================================================

def match_detection_to_track(
    detection,
    tracks,
    matched_track_ids=None,
):
    """
    Match one bottle detection to one existing
    internal track.

    A track can only be matched to ONE detection
    during the same frame.
    """

    if matched_track_ids is None:
        matched_track_ids = set()

    best_track_id = None
    best_score = float("inf")

    detection_box = detection["box"]

    for track_id, track in tracks.items():

        # Do not match the same track twice
        # in the same frame.
        if track_id in matched_track_ids:
            continue

        # Ignore tracks that have been missing too long.
        if track["missed"] > MAX_MISSED_FRAMES:
            continue

        previous_box = track["box"]

        distance = center_distance(
            detection_box,
            previous_box,
        )

        iou = calculate_iou(
            detection_box,
            previous_box,
        )

        if (
            distance <= MAX_CENTER_DISTANCE
            or iou >= MIN_IOU
        ):
            score = distance - (iou * 100)

            if score < best_score:
                best_score = score
                best_track_id = track_id

    return best_track_id


# ============================================================
# TRACK UPDATE
# ============================================================

def update_track(
    track,
    detection,
    defects,
    frame_number,
):
    """
    Accumulate defect evidence for one bottle.

    Once a confirmed defect is found,
    the bottle permanently remains REJECTED.
    """

    track["box"] = detection["box"]
    track["missed"] = 0
    track["last_frame"] = frame_number

    for defect in defects:

        defect_name = defect["defect"]
        confidence = defect["confidence"]

        track["defect_history"][defect_name].append(
            confidence
        )

        # Confirm defect
        if confidence >= DEFECT_CONFIRM_CONF:

            # Permanent rejection
            track["status"] = "REJECTED"

            if confidence >= HIGH_DEFECT_CONF:
                track["severity"] = "HIGH"
            else:
                track["severity"] = "MEDIUM"

            # Keep strongest detected defect
            if confidence > track["best_confidence"]:

                track["best_confidence"] = confidence
                track["primary_defect"] = defect_name

    return track


# ============================================================
# CREATE TRACK
# ============================================================

def create_track(
    track_id,
    detection,
    frame_number,
):
    return {
        "track_id": track_id,

        "box": detection["box"],

        "missed": 0,

        "first_frame": frame_number,

        "last_frame": frame_number,

        "status": "ACCEPTED",

        "primary_defect": None,

        "severity": None,

        "best_confidence": 0.0,

        "defect_history": defaultdict(list),
    }


# ============================================================
# FINALIZE TRACK
# ============================================================

def finalize_track(track):

    if track["status"] == "REJECTED":

        return {
            "status": "REJECTED",
            "quality": "DEFECTIVE",
            "defect": track["primary_defect"],
            "confidence": round(
                track["best_confidence"],
                4,
            ),
            "severity": track["severity"],
        }

    return {
        "status": "ACCEPTED",
        "quality": "GOOD",
        "defect": None,
        "confidence": None,
        "severity": None,
    }


# ============================================================
# DRAW RESULT
# ============================================================

def draw_result(
    frame,
    box,
    result,
):
    x1, y1, x2, y2 = box

    if result["status"] == "REJECTED":

        # BGR = red
        color = (
            50,
            50,
            210,
        )

        defect_name = result["defect"]

        if defect_name:
            label = (
                f"REJECTED | "
                f"{defect_name}"
            )
        else:
            label = "REJECTED"

    else:

        # BGR = green
        color = (
            50,
            180,
            70,
        )

        label = "ACCEPTED | GOOD"

    # Bottle bounding box
    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        color,
        3,
    )

    text_y = max(
        y1 - 10,
        25,
    )

    # Label background
    cv2.rectangle(
        frame,
        (
            x1,
            text_y - 25,
        ),
        (
            x1 + 300,
            text_y + 5,
        ),
        color,
        -1,
    )

    # Label text
    cv2.putText(
        frame,
        label,
        (
            x1 + 5,
            text_y - 3,
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )


# ============================================================
# CONVERT VIDEO TO BROWSER-COMPATIBLE MP4
# ============================================================

def convert_to_browser_mp4(
    input_video,
    output_video,
):
    """
    Convert OpenCV-generated AVI/video into
    browser-compatible H.264 MP4.
    """

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    input_video = Path(input_video)
    output_video = Path(output_video)

    output_video.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        ffmpeg_path,

        "-y",

        "-i",
        str(input_video),

        "-c:v",
        "libx264",

        "-preset",
        "fast",

        "-crf",
        "23",

        "-pix_fmt",
        "yuv420p",

        "-movflags",
        "+faststart",

        str(output_video),
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return output_video


# ============================================================
# MAIN INSPECTION
# ============================================================

def inspect_video(
    input_video,
    output_video,
):

    input_video = Path(input_video)
    output_video = Path(output_video)

    output_video.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Temporary OpenCV output
    # --------------------------------------------------------

    temporary_video = (
        output_video.parent
        / f"{output_video.stem}_opencv.avi"
    )

    cap = cv2.VideoCapture(
        str(input_video)
    )

    if not cap.isOpened():
        raise RuntimeError(
            f"Unable to open video: {input_video}"
        )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:
        fps = 30.0

    width = int(
        cap.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        cap.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    fourcc = cv2.VideoWriter_fourcc(
        *"XVID"
    )

    writer = cv2.VideoWriter(
        str(temporary_video),
        fourcc,
        fps,
        (width, height),
    )

    if not writer.isOpened():

        cap.release()

        raise RuntimeError(
            "Unable to create temporary output video."
        )

    # --------------------------------------------------------
    # Tracking state
    # --------------------------------------------------------

    tracks = {}

    next_track_id = 1

    completed_results = []

    frames_processed = 0

    # --------------------------------------------------------
    # Frame processing
    # --------------------------------------------------------

    while True:

        success, frame = cap.read()

        if not success:
            break

        frames_processed += 1

        detections = detect_bottles(
            frame
        )

        matched_track_ids = set()

        current_track_ids = set()

        # ----------------------------------------------------
        # Process every detected bottle
        # ----------------------------------------------------

        for detection in detections:

            x1, y1, x2, y2 = detection["box"]

            # Keep coordinates inside frame
            x1 = max(
                0,
                x1,
            )

            y1 = max(
                0,
                y1,
            )

            x2 = min(
                width,
                x2,
            )

            y2 = min(
                height,
                y2,
            )

            if x2 <= x1 or y2 <= y1:
                continue

            crop = frame[
                y1:y2,
                x1:x2,
            ]

            if crop.size == 0:
                continue

            # Detect defects inside bottle crop
            defects = detect_defects(
                crop
            )

            # ------------------------------------------------
            # Match bottle to existing track
            # ------------------------------------------------

            track_id = match_detection_to_track(
                detection,
                tracks,
                matched_track_ids,
            )

            # ------------------------------------------------
            # Create new track
            # ------------------------------------------------

            if track_id is None:

                track_id = next_track_id

                next_track_id += 1

                tracks[track_id] = create_track(
                    track_id,
                    detection,
                    frames_processed,
                )

            # ------------------------------------------------
            # Update matched track
            # ------------------------------------------------

            matched_track_ids.add(
                track_id
            )

            current_track_ids.add(
                track_id
            )

            tracks[track_id] = update_track(
                tracks[track_id],
                detection,
                defects,
                frames_processed,
            )

            # ------------------------------------------------
            # Draw current decision
            # ------------------------------------------------

            current_result = finalize_track(
                tracks[track_id]
            )

            draw_result(
                frame,
                detection["box"],
                current_result,
            )

        # ----------------------------------------------------
        # Update missed tracks
        # ----------------------------------------------------

        for track_id in list(
            tracks.keys()
        ):

            if track_id not in current_track_ids:

                tracks[track_id]["missed"] += 1

            if (
                tracks[track_id]["missed"]
                > MAX_MISSED_FRAMES
            ):

                final_result = finalize_track(
                    tracks[track_id]
                )

                completed_results.append(
                    final_result
                )

                del tracks[track_id]

        # ----------------------------------------------------
        # Write processed frame
        # ----------------------------------------------------

        writer.write(frame)

    # --------------------------------------------------------
    # Cleanup video resources
    # --------------------------------------------------------

    cap.release()
    writer.release()

    # --------------------------------------------------------
    # Finalize remaining tracks
    # --------------------------------------------------------

    for track in tracks.values():

        final_result = finalize_track(
            track
        )

        completed_results.append(
            final_result
        )

    # --------------------------------------------------------
    # Final results
    # --------------------------------------------------------

    results = completed_results

    # --------------------------------------------------------
    # Count results
    # --------------------------------------------------------

    accepted = sum(
        1
        for result in results
        if result["status"] == "ACCEPTED"
    )

    rejected = sum(
        1
        for result in results
        if result["status"] == "REJECTED"
    )

    # --------------------------------------------------------
    # Defect summary
    # --------------------------------------------------------

    defect_summary = defaultdict(int)

    for result in results:

        defect = result.get(
            "defect"
        )

        if defect:
            defect_summary[defect] += 1

    # --------------------------------------------------------
    # Convert AVI -> H.264 MP4
    # --------------------------------------------------------

    convert_to_browser_mp4(
        temporary_video,
        output_video,
    )

    # --------------------------------------------------------
    # Remove temporary AVI
    # --------------------------------------------------------

    try:
        temporary_video.unlink()
    except FileNotFoundError:
        pass

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    summary = {
        "frames_processed": frames_processed,

        "total_bottles": len(results),

        "accepted": accepted,

        "rejected": rejected,

        "defect_summary": dict(
            defect_summary
        ),

        "results": results,

        "output_video": str(
            output_video
        ),
    }

    return summary