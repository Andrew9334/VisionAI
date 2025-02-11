# Загружаем библиотеки
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import ImageDataGenerator

tf.autograph.set_verbosity(0)

# Загружаем файл модели
model_file = "models/petresnet50_model.keras"
weights_file = "models/model_weights.weights.h5"


model = tf.keras.models.load_model(model_file)
model.load_weights(weights_file)

# Параметры считывания изображения
img_size = (180, 180)
test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)


# Предсказание класса для одной модели
def predict_single_image(image_path):
    img = Image.open(image_path).resize(img_size)
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    prediction = model.predict(img_array)
    predicted_class_index = np.argmax(prediction, axis=1)[0]
    # Replace with your actual class mapping
    labels = {0: "low_income", 1: "middle_income", 2: "high_income"}
    predicted_class = labels[predicted_class_index]
    return predicted_class, max(prediction[0]), prediction[0]
