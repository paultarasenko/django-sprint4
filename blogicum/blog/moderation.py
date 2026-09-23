"""Проверка комментариев на токсичность моделью rubert-tiny-toxicity.

Модель только считает оценку токсичности текста — решение о том,
сохранять комментарий или нет, принимает форма приложения
(см. `blog.forms.CommentForm.clean_text`). Это продуктовое правило
«Блогикума», а не часть самой ML-модели.
"""
import functools

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from core.constants import TOXICITY_THRESHOLD

MODEL_NAME = 'cointegrated/rubert-tiny-toxicity'


@functools.cache
def _get_tokenizer_and_model():
    """Лениво загрузить токенизатор и модель (только при первом вызове)."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def get_toxicity_score(text: str) -> float:
    """Вернуть оценку токсичности от 0 до 1."""
    tokenizer, model = _get_tokenizer_and_model()
    with torch.inference_mode():
        inputs = tokenizer(text, return_tensors='pt', truncation=True)
        proba = torch.sigmoid(model(**inputs).logits).numpy()[0]
    # Первый класс модели — «not toxic», последний — «dangerous».
    # Итоговая токсичность — это вероятность «не токсичного» класса,
    # дополнительно уменьшенная на вероятность «опасного».
    return 1 - proba[0] * (1 - proba[-1])


def is_toxic(text: str) -> bool:
    """Определить, достигла ли оценка заданного порога."""
    return get_toxicity_score(text) >= TOXICITY_THRESHOLD
