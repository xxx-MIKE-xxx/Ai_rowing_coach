import json

# Load keypoints data from JSON file
with open('keypoints.json', 'r') as f:
    data = json.load(f)

# Keypoint IDs (based on your sample data)
LEFT_HIP_ID = 11
RIGHT_HIP_ID = 12
LEFT_KNEE_ID = 13
RIGHT_KNEE_ID = 14
CONFIDENCE_THRESHOLD = 0.3  # Adjust as needed

def validate_hips(frame):
    """
    Check if hips are above their corresponding knees. If not, set hip values to -1.
    """
    keypoints = frame["keypoints"]
    
    # Find keypoints by ID
    left_hip = next((kp for kp in keypoints if kp["id"] == LEFT_HIP_ID), None)
    right_hip = next((kp for kp in keypoints if kp["id"] == RIGHT_HIP_ID), None)
    left_knee = next((kp for kp in keypoints if kp["id"] == LEFT_KNEE_ID), None)
    right_knee = next((kp for kp in keypoints if kp["id"] == RIGHT_KNEE_ID), None)

    # Validate left hip
    if left_hip and left_knee:
        if left_knee["confidence"] > CONFIDENCE_THRESHOLD:
            if left_hip["y"] > left_knee["y"]:
                left_hip.update({"x": -1, "y": -1, "confidence": -1})

    # Validate right hip
    if right_hip and right_knee:
        if right_knee["confidence"] > CONFIDENCE_THRESHOLD:
            if right_hip["y"] > right_knee["y"]:
                right_hip.update({"x": -1, "y": -1, "confidence": -1})

    return frame

# Process all frames
for frame in data:
    validate_hips(frame)

# Save modified data to a new file
with open('keypoints_filtered.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Hip validation complete. Results saved to keypoints_filtered.json.")