import sieve

file = """C:\\Users\\kens0\\Downloads\\test.jpeg"""
confidence_threshold = 123.45
start_frame = 123
end_frame = 123
fps = 123.45

mediapipe_face_detector = sieve.function.get("kens091521-gmail-com/mediapipe_face_detector")
file_obj = sieve.File(path=file)
output = mediapipe_face_detector.run(
    file=file_obj,
    confidence_threshold = confidence_threshold,
    start_frame = start_frame,
    end_frame = end_frame,
    fps = fps
)
print(output)