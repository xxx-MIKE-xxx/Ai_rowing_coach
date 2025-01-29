import cv2
import tensorflow as tf
import numpy as np

CONF_THRESHOLD = 0.2
SMOOTH_ALPHA = 0.3

def load_movenet_model(model_path):
    return tf.saved_model.load(model_path)

def estimate_pose(movenet, frame):
    # Preprocess
    resized = tf.image.resize(frame, (256, 256))
    resized = tf.cast(resized, dtype=tf.int32)
    input_tensor = tf.expand_dims(resized, axis=0)
    
    # Inference
    outputs = movenet.signatures["serving_default"](input=input_tensor)
    # Shape: (1, 1, 17, 3) => [y, x, confidence]
    keypoints = outputs["output_0"].numpy()
    return keypoints[0, 0, :, :]  # shape (17, 3)

def draw_keypoints(frame, keypoints, threshold=CONF_THRESHOLD):
    h, w, _ = frame.shape
    for i, (ky, kx, conf) in enumerate(keypoints):
        if conf >= threshold:
            cv2.circle(frame, (int(kx * w), int(ky * h)), 5, (0,255,0), -1)

def main():
    model_path = "./movenet_thunder"
    movenet = load_movenet_model(model_path)
    
    cap = cv2.VideoCapture("input_video.mp4")
    if not cap.isOpened():
        print("Error opening video")
        return
    
    # For output video
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # If rotating 90° clockwise => output dimension is swapped
    out_width, out_height = original_height, original_width
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_video = cv2.VideoWriter("output_video.mp4", fourcc, fps, (out_width, out_height))
    
    previous_keypoints = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Rotate physically rotated video frame
        rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(rotated_frame, cv2.COLOR_BGR2RGB)
        
        # Pose estimation
        keypoints = estimate_pose(movenet, rgb_frame)
        
        # Simple smoothing
        if previous_keypoints is None:
            smoothed_keypoints = keypoints
        else:
            smoothed_keypoints = SMOOTH_ALPHA * previous_keypoints + (1 - SMOOTH_ALPHA) * keypoints
        
        # Draw on frame
        draw_keypoints(rotated_frame, smoothed_keypoints, threshold=CONF_THRESHOLD)
        
        cv2.imshow("Pose Estimation", rotated_frame)
        out_video.write(rotated_frame)
        
        previous_keypoints = smoothed_keypoints
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    out_video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
