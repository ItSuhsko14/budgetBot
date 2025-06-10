import re
from typing import List

def split_text_to_items(text: str) -> List[str]:
    """
    Розбиває вхідний текст на окремі елементи за роздільниками: коми, крапки з комою, крапки.
    
    Аргументи:
        text (str): Вхідний рядок тексту для обробки
        
    Повертає:
        List[str]: Список розділених та очищених елементів
    """
    if not text or not isinstance(text, str):
        return []
    
    # Розділяємо за комами, крапками з комою, крапками (з наступним пробілом або кінцем рядка)
    items = re.split(r'[;,.](?=\s|$)', text)
    
    # Видаляємо зайві пробіли на початку та в кінці кожного елемента
    cleaned_items = [item.strip() for item in items if item.strip()]
    
    return cleaned_items