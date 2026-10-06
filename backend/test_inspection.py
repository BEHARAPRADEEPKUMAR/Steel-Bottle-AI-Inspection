from pathlib import Path

from inspection.inspection_service import inspect_video


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_VIDEO = BASE_DIR / "test_videos" / "mixerror.mp4"

OUTPUT_DIR = BASE_DIR / "test_output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_VIDEO = OUTPUT_DIR / "mixerror_test.mp4"


print("Starting inspection...")
print("Input:", INPUT_VIDEO)
print("Output:", OUTPUT_VIDEO)


summary = inspect_video(
    input_video=INPUT_VIDEO,
    output_video=OUTPUT_VIDEO,
)


print("\n==============================")
print("INSPECTION COMPLETE")
print("==============================")

print("Frames processed :", summary["frames_processed"])
print("Total bottles    :", summary["total_bottles"])
print("Accepted         :", summary["accepted"])
print("Rejected         :", summary["rejected"])

print("\nDefect summary:")

for defect, count in summary["defect_summary"].items():
    print(f"  {defect}: {count}")

print("\nOutput video:")
print(OUTPUT_VIDEO)