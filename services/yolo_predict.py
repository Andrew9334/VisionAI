import csv
import os

from ultralytics import YOLO


def load_model(model_path="./best_real_estate.pt"):
    """Load the YOLO model."""
    return YOLO(model_path)


path = "models/best_real_estate.pt"
model = load_model(path)


def get_image_files(image_dir):
    """Retrieve all image file paths from the specified directory."""
    if not os.path.exists(image_dir):
        print(f"Error: Directory {image_dir} not found.")
        exit()

    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))]

    if not image_files:
        print("Error: No images found in the directory.")
        exit()

    return image_files


def predict_image(image_path, device="cpu"):
    """Perform prediction on a single image and return class name and confidence."""
    print(f"Пытаюсь предсказать изображение: {image_path}")

    results = model.predict(image_path, device=device, verbose=False)

    if not results or not hasattr(results[0], "probs"):
        print(f"Error: Failed to get predictions for {image_path}.")
        return "Prediction Error", ""

    class_probabilities = results[0].probs.data.tolist()
    class_index = class_probabilities.index(max(class_probabilities))
    class_name = model.names[class_index]
    confidence = max(class_probabilities)

    return class_name, confidence, class_probabilities


def save_results(output_file, image_files, model, image_dir):
    """Save prediction results to a CSV file."""
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["File", "Class", "Confidence"])

        for image_name in image_files:
            image_path = os.path.join(image_dir, image_name)
            class_name, confidence = predict_image(model, image_path)

            result_str = f"File: {image_name}, Class: {class_name}, Confidence: {confidence:.4f}"
            print(result_str)
            writer.writerow([image_name, class_name, confidence])
