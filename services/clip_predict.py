import clip
import numpy as np
import torch
import logging
from PIL import Image

# 🔹 Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CLIPpredictor:

    def __init__(self):
        self.text_descriptions = [
            "This is a photo of a cheap electronic device",
            "This is a photo of an expensive electronic device",
            "This is a photo of a medium-price electronic device",
        ]

        self.class_name = ["Cheap equipment", "Expensive equipment", "Medium-price equipment"]

        self.model, self.preprocess = clip.load("ViT-B/32", device="cpu")  # Убедимся, что модель загружается правильно
        self.model.eval()

    def preprocess_image(self, path):
        """Обрабатываем изображение перед подачей в модель"""
        image = Image.open(path)
        image = self.preprocess(image).unsqueeze(0)  # Исправлено: добавляем batch dimension
        return image

    def predict(self, pred_im):
        """Предсказание CLIP с максимальной отладкой"""
        try:
            image_input = self.preprocess_image(pred_im)
            text_tokens = clip.tokenize(self.text_descriptions)

            with torch.no_grad():
                image_features = self.model.encode_image(image_input).float()
                text_features = self.model.encode_text(text_tokens).float()
                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)

            text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            top_probs, top_labels = text_probs.cpu().topk(3, dim=-1)

            # 🔥 Проверяем, были ли созданы переменные
            if top_labels is None or top_labels.nelement() == 0:
                raise ValueError("Ошибка: `top_labels` пуст или не инициализирован!")

            # 🔹 Принудительно конвертируем в JSON-совместимый формат
            class_label = str(self.class_name[int(top_labels[0][0].item())])  # Теперь точно str
            confidence = round(float(top_probs[0][0].item()), 4)  # Теперь точно float
            full_probs = [round(float(p), 4) for p in text_probs.cpu().numpy()[0]]  # Принудительно list[float]

            # 🔥 Логируем после преобразования
            logger.info(f"✅ CLIP class_name: {class_label} (type: {type(class_label)})")
            logger.info(f"✅ CLIP confidence: {confidence} (type: {type(confidence)})")
            logger.info(f"✅ CLIP full_probs: {full_probs} (type: {type(full_probs)})")

            return {
                "class": class_label,
                "confidence": confidence,
                "full_probs": full_probs
            }

        except Exception as e:
            logger.error(f"❌ Ошибка в CLIP: {e}")
            return {"error": "Ошибка предсказания CLIP"}
