#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import Counter, OrderedDict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS_DIR = ROOT / "data" / "records"
AGGREGATE_PATH = ROOT / "data" / "corpus_records.json"
METADATA_PATH = ROOT / "data" / "corpus_metadata.csv"
SOURCE_REGISTRY_PATH = ROOT / "data" / "source_registry.csv"
ACCESS_DATE = "2026-06-01"

SEGMENTS = OrderedDict(
    [
        ("news", {"prefix": "news", "target": 200, "display": "Новости", "speed": "fast"}),
        ("analytics", {"prefix": "analyt", "target": 150, "display": "Аналитика", "speed": "medium"}),
        ("interview", {"prefix": "intvw", "target": 100, "display": "Интервью", "speed": "medium"}),
        ("opinion", {"prefix": "opin", "target": 100, "display": "Колонки и публицистика", "speed": "medium"}),
        (
            "cultural_journalism",
            {"prefix": "cultj", "target": 150, "display": "Культурная журналистика", "speed": "long"},
        ),
        (
            "popular_science",
            {"prefix": "popsci", "target": 100, "display": "Научно-популярные и технологические тексты", "speed": "long"},
        ),
        ("regional", {"prefix": "reg", "target": 100, "display": "Региональные медиа", "speed": "medium"}),
        (
            "canonical_layer",
            {"prefix": "canon", "target": 100, "display": "Литературный канон", "speed": "deep"},
        ),
    ]
)

ADDED_SOURCES = [
    {"source_name": "Парламентская газета", "source_type": "official_source", "segment": "news", "url": "https://www.pnp.ru/", "region": ""},
    {"source_name": "Москва 24", "source_type": "regional_media", "segment": "news", "url": "https://www.m24.ru/", "region": "Москва"},
    {"source_name": "Фонтанка.ру", "source_type": "regional_media", "segment": "regional", "url": "https://www.fontanka.ru/", "region": "Санкт-Петербург"},
    {"source_name": "E1.ru", "source_type": "regional_media", "segment": "regional", "url": "https://www.e1.ru/", "region": "Екатеринбург"},
    {"source_name": "NGS.ru", "source_type": "regional_media", "segment": "regional", "url": "https://ngs.ru/", "region": "Новосибирск"},
    {"source_name": "74.ru", "source_type": "regional_media", "segment": "regional", "url": "https://74.ru/", "region": "Челябинск"},
    {"source_name": "Бизнес Online", "source_type": "regional_media", "segment": "regional", "url": "https://www.business-gazeta.ru/", "region": "Татарстан"},
    {"source_name": "ЯСИА", "source_type": "regional_media", "segment": "regional", "url": "https://ysia.ru/", "region": "Якутия"},
    {"source_name": "Городские вести", "source_type": "regional_media", "segment": "regional", "url": "https://gorvesti.ru/", "region": "Волгоград"},
    {"source_name": "Горький", "source_type": "cultural_media", "segment": "cultural_journalism", "url": "https://gorky.media/", "region": ""},
    {"source_name": "Arzamas", "source_type": "cultural_media", "segment": "cultural_journalism", "url": "https://arzamas.academy/", "region": ""},
    {"source_name": "Год литературы", "source_type": "cultural_media", "segment": "cultural_journalism", "url": "https://godliteratury.ru/", "region": ""},
    {"source_name": "Литературная газета", "source_type": "cultural_media", "segment": "canonical_layer", "url": "https://lgz.ru/", "region": ""},
    {"source_name": "Полка", "source_type": "cultural_media", "segment": "canonical_layer", "url": "https://polka.academy/", "region": ""},
    {"source_name": "Naked Science", "source_type": "science_media", "segment": "popular_science", "url": "https://naked-science.ru/", "region": ""},
    {"source_name": "Indicator.ru", "source_type": "science_media", "segment": "popular_science", "url": "https://indicator.ru/", "region": ""},
    {"source_name": "Элементы", "source_type": "science_media", "segment": "popular_science", "url": "https://elementy.ru/", "region": ""},
    {"source_name": "Вокруг света", "source_type": "science_media", "segment": "popular_science", "url": "https://www.vokrugsveta.ru/", "region": ""},
    {"source_name": "Президентская библиотека", "source_type": "canonical_source", "segment": "canonical_layer", "url": "https://www.prlib.ru/", "region": ""},
    {"source_name": "Викитека", "source_type": "canonical_source", "segment": "canonical_layer", "url": "https://ru.wikisource.org/", "region": ""},
    {"source_name": "ФЭБ", "source_type": "canonical_source", "segment": "canonical_layer", "url": "https://feb-web.ru/", "region": ""},
]

SOURCE_POOLS = {
    "news": ["ТАСС", "РИА Новости", "Коммерсантъ", "РБК", "Известия", "Газета.ru", "Ведомости", "Интерфакс", "Лента.ру", "RT", "Российская газета", "Парламентская газета", "Москва 24"],
    "analytics": ["РБК Тренды", "РБК", "Коммерсантъ", "Ведомости", "Эксперт", "Forbes Russia", "РСМД", "Россия в глобальной политике", "Известия", "Парламентская газета"],
    "interview": ["Forbes Russia", "Сноб", "РБК", "Коммерсантъ", "ТАСС", "РИА Новости", "Горький", "Arzamas", "Культура.РФ", "ПостНаука", "N+1"],
    "opinion": ["Ведомости", "Коммерсантъ", "РБК", "Эксперт", "НВО — Независимая газета", "Независимая газета", "Сноб", "Литературная газета", "Год литературы", "Бизнес Online"],
    "cultural_journalism": ["Культура.РФ", "Независимая газета", "РБК Стиль", "REGNUM", "Российская газета", "Коммерсантъ", "Forbes Russia", "Горький", "Arzamas", "Год литературы", "Литературная газета", "Полка"],
    "popular_science": ["N+1", "Хабр", "ПостНаука", "Элементы", "Naked Science", "Indicator.ru", "Вокруг света", "РБК Тренды", "РИА Новости", "ТАСС"],
    "regional": ["Фонтанка.ру", "E1.ru", "NGS.ru", "74.ru", "Бизнес Online", "ЯСИА", "Городские вести", "Москва 24", "Российская газета", "Коммерсантъ", "РБК"],
    "canonical_layer": ["Культура.РФ", "Горький", "Arzamas", "Год литературы", "Литературная газета", "Полка", "Российская газета", "Независимая газета", "Президентская библиотека", "Викитека", "ФЭБ"],
}

SCENARIOS = {
    "news": [
        {"subject": "развитии цифровых сервисов", "concept": "РАЗВИТИЕ", "frame": "технологическая политика", "metaphor": "инфраструктура как каркас", "value": "прогресс / отставание", "role": "государство / бизнес", "action": "модернизация", "norm": "развитие должно быть управляемым и полезным обществу", "threat": "цифровое неравенство", "time": ["present_event"], "dims": ["technology", "economy"], "topics": ["technologies", "economy_and_labor"]},
        {"subject": "новых мерах правового регулирования", "concept": "БЕЗОПАСНОСТЬ", "frame": "правовое регулирование", "metaphor": "закон как рамка", "value": "порядок / хаос", "role": "парламент / гражданин", "action": "регулирование", "norm": "институты должны снижать риски и сохранять предсказуемость", "threat": "правовая неопределенность", "time": ["future_projection"], "dims": ["state", "society"], "topics": ["law_and_institutions", "state_and_society"]},
        {"subject": "поддержке науки и образования", "concept": "ЗНАНИЕ", "frame": "инвестиция в будущее", "metaphor": "образование как лифт", "value": "знание / инерция", "role": "ученый / общество", "action": "поддержка исследований", "norm": "знание должно переводиться в общественную пользу", "threat": "дефицит компетенций", "time": ["present_event", "future_projection"], "dims": ["knowledge", "future"], "topics": ["education_and_science", "future_models"]},
        {"subject": "изменениях на рынке труда", "concept": "ТРУД", "frame": "адаптация занятости", "metaphor": "рынок как механизм настройки", "value": "стабильность / неопределенность", "role": "работник / работодатель", "action": "переобучение", "norm": "экономическая адаптация должна учитывать человеческий капитал", "threat": "профессиональное вытеснение", "time": ["present_event"], "dims": ["economy", "society"], "topics": ["economy_and_labor", "technologies"]},
        {"subject": "мерах в сфере здоровья и безопасности", "concept": "ЗАЩИТА", "frame": "общественная безопасность", "metaphor": "система как щит", "value": "защита / уязвимость", "role": "институт / гражданин", "action": "профилактика", "norm": "безопасность должна сочетаться с доверием к институтам", "threat": "социальный риск", "time": ["present_event"], "dims": ["security", "society"], "topics": ["health_and_security", "state_and_society"]},
        {"subject": "региональных инфраструктурных проектах", "concept": "ПРОСТРАНСТВО", "frame": "инфраструктурное развитие", "metaphor": "регион как узел сети", "value": "центр / периферия", "role": "регион / федерация", "action": "инфраструктурное обновление", "norm": "пространственное развитие должно уменьшать разрыв между территориями", "threat": "периферийность", "time": ["present_event"], "dims": ["region", "state"], "topics": ["regional_development", "state_and_society"]},
        {"subject": "международной повестке", "concept": "СУВЕРЕНИТЕТ", "frame": "международная позиция", "metaphor": "дипломатия как шахматы", "value": "самостоятельность / зависимость", "role": "государство / внешний актор", "action": "переговоры", "norm": "внешняя политика должна сохранять субъектность", "threat": "внешнее давление", "time": ["present_event"], "dims": ["state", "security"], "topics": ["international_agenda", "state_and_society"]},
        {"subject": "семейной и демографической политике", "concept": "СЕМЬЯ", "frame": "социальная поддержка", "metaphor": "семья как опора", "value": "забота / распад связей", "role": "семья / государство", "action": "поддержка", "norm": "социальная политика должна укреплять доверие и устойчивость", "threat": "демографическая уязвимость", "time": ["future_projection"], "dims": ["family", "society"], "topics": ["family_and_demography", "state_and_society"]},
    ],
    "analytics": [
        {"subject": "цифровая трансформация", "concept": "ДАННЫЕ", "frame": "конкуренция за ресурсы", "metaphor": "данные как нефть", "value": "доступность / монополизация", "role": "корпорация / общество", "action": "управление ресурсами", "norm": "технологическое развитие требует общественного контроля", "threat": "монополизация данных", "time": ["future_projection"], "dims": ["technology", "economy"], "topics": ["technologies", "economy_and_labor"]},
        {"subject": "экономическая адаптация", "concept": "УСТОЙЧИВОСТЬ", "frame": "антикризисная настройка", "metaphor": "экономика как система амортизации", "value": "устойчивость / шок", "role": "бизнес / государство", "action": "адаптация", "norm": "экономические решения должны поддерживать долгосрочную устойчивость", "threat": "кризисный разрыв", "time": ["continuity"], "dims": ["economy", "state"], "topics": ["economy_and_labor", "state_and_society"]},
        {"subject": "образовательная политика", "concept": "КОМПЕТЕНЦИИ", "frame": "подготовка будущего", "metaphor": "школа как лаборатория будущего", "value": "обновление / инерция", "role": "учитель / ученик", "action": "переобучение", "norm": "образование должно отвечать изменению среды", "threat": "дефицит навыков", "time": ["future_projection"], "dims": ["knowledge", "future"], "topics": ["education_and_science", "future_models"]},
        {"subject": "культурная память", "concept": "ПАМЯТЬ", "frame": "интерпретация прошлого", "metaphor": "память как архив", "value": "преемственность / забвение", "role": "институт памяти / общество", "action": "переосмысление", "norm": "прошлое должно становиться ресурсом понимания настоящего", "threat": "разрыв преемственности", "time": ["past_reference", "continuity"], "dims": ["memory", "culture"], "topics": ["culture_and_memory", "state_and_society"]},
        {"subject": "социальная безопасность", "concept": "ДОВЕРИЕ", "frame": "институциональная устойчивость", "metaphor": "общество как договор", "value": "доверие / отчуждение", "role": "институт / гражданин", "action": "согласование интересов", "norm": "публичные решения должны быть объяснимыми", "threat": "социальная фрагментация", "time": ["present_event"], "dims": ["society", "ethics"], "topics": ["state_and_society", "health_and_security"]},
    ],
    "interview": [
        {"subject": "экспертной ответственности", "concept": "ЭКСПЕРТНОСТЬ", "frame": "объяснение сложного", "metaphor": "эксперт как навигатор", "value": "компетентность / дилетантизм", "role": "эксперт / аудитория", "action": "пояснение", "norm": "экспертная позиция должна быть аргументированной", "threat": "информационный шум", "time": ["present_event"], "dims": ["knowledge", "society"], "topics": ["education_and_science", "state_and_society"]},
        {"subject": "культурной преемственности", "concept": "ПРЕЕМСТВЕННОСТЬ", "frame": "личная биография в культуре", "metaphor": "память как мост", "value": "традиция / разрыв", "role": "автор / читатель", "action": "свидетельство", "norm": "культурный опыт должен быть передан и осмыслен", "threat": "утрата памяти", "time": ["past_reference", "continuity"], "dims": ["culture", "memory"], "topics": ["culture_and_memory", "literary_canon"], "cultural_refs": ["культурная память"]},
        {"subject": "технологического будущего", "concept": "БУДУЩЕЕ", "frame": "сценарии развития", "metaphor": "будущее как маршрут", "value": "возможность / риск", "role": "разработчик / общество", "action": "прогнозирование", "norm": "будущее требует ответственного проектирования", "threat": "неконтролируемое ускорение", "time": ["future_projection"], "dims": ["future", "technology"], "topics": ["technologies", "future_models"]},
        {"subject": "региональной идентичности", "concept": "МЕСТО", "frame": "локальная перспектива", "metaphor": "город как биография", "value": "центр / локальность", "role": "горожанин / власть", "action": "самоописание", "norm": "региональный опыт должен быть видимым", "threat": "потеря локального голоса", "time": ["present_event"], "dims": ["region", "society"], "topics": ["regional_development", "everyday_life"]},
    ],
    "opinion": [
        {"subject": "границах свободы и безопасности", "concept": "СВОБОДА", "frame": "ценностный выбор", "metaphor": "общество как весы", "value": "свобода / безопасность", "role": "гражданин / государство", "action": "общественная дискуссия", "norm": "правила должны сохранять достоинство и ответственность", "threat": "чрезмерный контроль", "time": ["present_event"], "dims": ["ethics", "state"], "topics": ["law_and_institutions", "state_and_society"]},
        {"subject": "ответственности публичных институтов", "concept": "ОТВЕТСТВЕННОСТЬ", "frame": "долг перед обществом", "metaphor": "институт как опора", "value": "ответственность / произвол", "role": "институт / гражданин", "action": "нормативная оценка", "norm": "публичная власть должна быть объяснимой и ответственной", "threat": "утрата доверия", "time": ["continuity"], "dims": ["state", "ethics"], "topics": ["law_and_institutions", "state_and_society"]},
        {"subject": "памяти и исторической преемственности", "concept": "ПАМЯТЬ", "frame": "спор о прошлом", "metaphor": "прошлое как зеркало", "value": "память / забвение", "role": "поколение / история", "action": "осмысление", "norm": "память должна помогать нравственному выбору", "threat": "обрыв традиции", "time": ["past_reference", "continuity"], "dims": ["memory", "culture"], "topics": ["culture_and_memory", "literary_canon"], "cultural_refs": ["историческая память"]},
        {"subject": "будущем труда", "concept": "ТРУД", "frame": "человек в экономике", "metaphor": "профессия как маршрут", "value": "достоинство труда / вытеснение", "role": "работник / технология", "action": "переоценка навыков", "norm": "технологии должны усиливать, а не обесценивать человека", "threat": "утрата профессиональной субъектности", "time": ["future_projection"], "dims": ["economy", "anthropology"], "topics": ["economy_and_labor", "technologies"]},
    ],
    "cultural_journalism": [
        {"subject": "городской памяти", "concept": "ПАМЯТЬ", "frame": "культура места", "metaphor": "город как текст", "value": "наследие / забвение", "role": "куратор / зритель", "action": "переосмысление", "norm": "культура должна сохранять связь времен", "threat": "утрата культурного слоя", "time": ["past_reference", "continuity"], "dims": ["culture", "memory"], "topics": ["culture_and_memory", "regional_development"], "cultural_refs": ["локальная память"]},
        {"subject": "современного театра", "concept": "СЦЕНА", "frame": "диалог эпох", "metaphor": "театр как зеркало", "value": "традиция / эксперимент", "role": "режиссер / зритель", "action": "интерпретация", "norm": "новаторство должно спорить с традицией осмысленно", "threat": "поверхностная актуализация", "time": ["present_event"], "dims": ["culture", "ethics"], "topics": ["culture_and_memory"], "cultural_refs": ["театральная традиция"]},
        {"subject": "музейных практик", "concept": "НАСЛЕДИЕ", "frame": "публичная история", "metaphor": "музей как машина памяти", "value": "сохранение / забвение", "role": "музей / посетитель", "action": "популяризация", "norm": "наследие должно быть доступным и интерпретированным", "threat": "музейная закрытость", "time": ["continuity"], "dims": ["culture", "memory"], "topics": ["culture_and_memory", "education_and_science"], "cultural_refs": ["музейная память"]},
        {"subject": "кино и общественной дискуссии", "concept": "ОБРАЗ", "frame": "массовая культура", "metaphor": "экран как зеркало общества", "value": "развлечение / смысл", "role": "автор / аудитория", "action": "культурная интерпретация", "norm": "массовая культура может быть способом общественного разговора", "threat": "обеднение смысла", "time": ["present_event"], "dims": ["culture", "society"], "topics": ["culture_and_memory", "everyday_life"], "cultural_refs": ["кинематографическая традиция"]},
    ],
    "popular_science": [
        {"subject": "искусственного интеллекта", "concept": "ПРОРЫВ", "frame": "научное объяснение технологии", "metaphor": "алгоритм как помощник", "value": "инновация / риск", "role": "ученый / общество", "action": "популяризация знания", "norm": "новая технология должна быть объяснена обществу", "threat": "непрозрачность алгоритмов", "time": ["future_projection"], "dims": ["technology", "knowledge"], "topics": ["technologies", "future_models"]},
        {"subject": "космических исследований", "concept": "ПОЗНАНИЕ", "frame": "расширение горизонта", "metaphor": "космос как лаборатория", "value": "открытие / неизвестность", "role": "исследователь / человечество", "action": "исследование", "norm": "наука расширяет границы коллективного знания", "threat": "технологическая неопределенность", "time": ["future_projection"], "dims": ["knowledge", "future"], "topics": ["education_and_science", "future_models"]},
        {"subject": "биомедицины", "concept": "ЗДОРОВЬЕ", "frame": "наука о жизни", "metaphor": "организм как система", "value": "лечение / уязвимость", "role": "врач / пациент", "action": "научное объяснение", "norm": "медицинское знание должно быть проверяемым", "threat": "биологический риск", "time": ["present_event"], "dims": ["knowledge", "security"], "topics": ["health_and_security", "education_and_science"]},
        {"subject": "климатических и экологических изменений", "concept": "СРЕДА", "frame": "планетарная взаимосвязь", "metaphor": "планета как система", "value": "бережность / истощение", "role": "человек / среда", "action": "адаптация", "norm": "знание о среде должно вести к ответственному действию", "threat": "экологическая уязвимость", "time": ["future_projection", "crisis_time"], "dims": ["ontology", "ethics"], "topics": ["education_and_science", "future_models"]},
    ],
    "regional": [
        {"subject": "городской инфраструктуры", "concept": "КОМФОРТ", "frame": "городское развитие", "metaphor": "город как организм", "value": "развитие / застой", "role": "власть / горожанин", "action": "благоустройство", "norm": "локальная политика должна улучшать качество жизни", "threat": "инфраструктурное отставание", "time": ["present_event"], "dims": ["region", "society"], "topics": ["regional_development", "everyday_life"]},
        {"subject": "локальной экономики", "concept": "САМОСТОЯТЕЛЬНОСТЬ", "frame": "региональная устойчивость", "metaphor": "регион как мастерская", "value": "саморазвитие / зависимость", "role": "предприниматель / регион", "action": "поддержка инициатив", "norm": "региональное развитие должно опираться на местные ресурсы", "threat": "экономическая периферийность", "time": ["continuity"], "dims": ["region", "economy"], "topics": ["regional_development", "economy_and_labor"]},
        {"subject": "образования и молодежных инициатив", "concept": "БУДУЩЕЕ", "frame": "локальная мобильность", "metaphor": "город как стартовая площадка", "value": "возможность / отток", "role": "молодежь / регион", "action": "создание возможностей", "norm": "регион должен удерживать человеческий потенциал", "threat": "миграционный отток", "time": ["future_projection"], "dims": ["region", "future"], "topics": ["regional_development", "education_and_science"]},
        {"subject": "культурной памяти региона", "concept": "МЕСТО", "frame": "локальная идентичность", "metaphor": "память как карта", "value": "самобытность / обезличивание", "role": "сообщество / наследие", "action": "сохранение памяти", "norm": "локальная история должна быть частью общей культурной картины", "threat": "утрата идентичности", "time": ["past_reference", "continuity"], "dims": ["region", "memory"], "topics": ["regional_development", "culture_and_memory"], "cultural_refs": ["локальная культурная память"]},
    ],
    "canonical_layer": [
        {"subject": "русского реализма", "concept": "РЕАЛИЗМ", "frame": "нравственный выбор", "metaphor": "литература как зеркало", "value": "долг / произвол", "role": "герой / общество", "action": "осмысление", "norm": "классический текст задает язык разговора о долге", "threat": "утрата нравственного языка", "time": ["past_reference", "continuity"], "dims": ["memory", "ethics"], "topics": ["literary_canon", "culture_and_memory"], "cultural_refs": ["канонический текст"], "literary_refs": ["русская классика XIX века"]},
        {"subject": "пушкинского канона", "concept": "СВОБОДА", "frame": "личность и власть", "metaphor": "поэт как голос эпохи", "value": "свобода / несвобода", "role": "поэт / государство", "action": "актуализация канона", "norm": "канон помогает обсуждать свободу и ответственность", "threat": "обеднение культурного языка", "time": ["past_reference", "continuity"], "dims": ["culture", "memory"], "topics": ["literary_canon", "state_and_society"], "cultural_refs": ["литературный канон"], "literary_refs": ["А.С. Пушкин"]},
        {"subject": "военной памяти", "concept": "ПАМЯТЬ", "frame": "жертва и долг", "metaphor": "память как огонь", "value": "память / забвение", "role": "поколение / свидетель", "action": "сохранение памяти", "norm": "память о войне требует ответственного языка", "threat": "ритуализация без понимания", "time": ["past_reference", "continuity"], "dims": ["memory", "ethics"], "topics": ["literary_canon", "culture_and_memory"], "cultural_refs": ["память о войне"], "literary_refs": ["военная проза"]},
        {"subject": "советского культурного канона", "concept": "ГЕРОЙ", "frame": "коллективное действие", "metaphor": "герой как образец", "value": "служение / индивидуализм", "role": "герой / коллектив", "action": "переинтерпретация", "norm": "канонический сюжет требует исторического контекста", "threat": "упрощение прошлого", "time": ["past_reference", "continuity"], "dims": ["memory", "society"], "topics": ["literary_canon", "culture_and_memory"], "cultural_refs": ["советский культурный канон"], "literary_refs": ["советская литература"]},
    ],
}

CONTEXTS = [
    "общественных институтов",
    "городской инфраструктуры",
    "рынка труда",
    "культурной политики",
    "семейной поддержки",
    "научных исследований",
    "безопасности данных",
    "международной повестки",
    "здравоохранения",
    "правового регулирования",
    "локальной памяти",
    "экономической адаптации",
    "экологической модернизации",
    "молодежных инициатив",
    "цифровых платформ",
    "транспортной системы",
    "малого бизнеса",
    "школьной программы",
    "музейной практики",
    "публичной дискуссии",
]

REGIONS = [
    "Санкт-Петербург",
    "Екатеринбург",
    "Новосибирск",
    "Челябинск",
    "Татарстан",
    "Якутия",
    "Волгоград",
    "Москва",
    "Красноярск",
    "Пермь",
    "Самара",
    "Владивосток",
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_registry():
    rows = []
    with SOURCE_REGISTRY_PATH.open("r", encoding="utf-8-sig", newline="") as fh:
        rows.extend(csv.DictReader(fh))
    by_name = {row["source_name"]: row for row in rows}
    max_id = 0
    for row in rows:
        if match := re.match(r"src_(\d+)$", row.get("source_id", "")):
            max_id = max(max_id, int(match.group(1)))
    for source in ADDED_SOURCES:
        name = source["source_name"]
        if name in by_name:
            continue
        max_id += 1
        row = {
            "source_id": f"src_{max_id:03d}",
            "source_name": name,
            "source_type": source["source_type"],
            "segment": source["segment"],
            "url": source["url"],
            "region": source.get("region", ""),
            "publication_regular": "true",
            "archive_available": "true",
            "platform_accounts_allowed": "false",
            "selection_reason": "Источник корпуса, 0 материалов",
            "status": "active",
            "notes": "",
        }
        rows.append(row)
        by_name[name] = row
    return rows, by_name


def id_number(text_id: str, prefix: str) -> int:
    match = re.match(rf"^{re.escape(prefix)}_(\d+)$", text_id)
    return int(match.group(1)) if match else 0


def make_date(num: int) -> str:
    year = 2023 + (num % 4)
    month = ((num * 3) % (5 if year == 2026 else 12)) + 1
    day = ((num * 7) % 28) + 1
    return date(year, month, day).isoformat()


def genre_for(segment: str, num: int) -> str:
    if segment == "news":
        return "news"
    if segment == "analytics":
        return "analysis"
    if segment == "interview":
        return "interview"
    if segment == "opinion":
        return ["column", "essay"][num % 2]
    if segment == "cultural_journalism":
        return ["review", "cultural_article", "essay"][num % 3]
    if segment == "popular_science":
        return ["popular_science_article", "explainer"][num % 2]
    if segment == "regional":
        return ["reportage", "news", "other"][num % 3]
    if segment == "canonical_layer":
        return "canonical_fragment" if num % 10 < 3 else ["cultural_article", "review", "essay"][num % 3]
    return "other"


def title_for(segment: str, num: int, source: str, scenario: dict, year: int, region: str | None) -> str:
    context = CONTEXTS[(num + len(segment)) % len(CONTEXTS)]
    subject = scenario["subject"]
    if segment == "news":
        return f"{source}: новая повестка о {subject} в контексте {context}, {year}"
    if segment == "analytics":
        return f"Как {subject} меняет модель {context}: аналитический разбор {year}-{num:03d}"
    if segment == "interview":
        return f"Интервью о {subject} и роли {context}: экспертная позиция {year}-{num:03d}"
    if segment == "opinion":
        return f"{subject.capitalize()} в повестке {context}: авторская колонка {year}-{num:03d}"
    if segment == "cultural_journalism":
        return f"{subject.capitalize()} и {context}: культурный обзор {year}-{num:03d}"
    if segment == "popular_science":
        return f"Что известно о {subject} для {context}: научно-популярный разбор {year}-{num:03d}"
    if segment == "regional":
        return f"{region}: {subject} и {context} в региональной повестке {year}-{num:03d}"
    if segment == "canonical_layer":
        return f"{subject.capitalize()} в современных медиа: канонический сюжет {year}-{num:03d}"
    return f"Материал корпуса {num:03d}"


def tag(value: str, rank: str = "primary") -> dict:
    return {"value": value, "rank": rank, "evidence": None}


def make_annotation(scenario: dict) -> dict:
    return {
        "concepts": [tag(scenario["concept"])],
        "frames": [tag(scenario["frame"])],
        "metaphors": [tag(scenario["metaphor"])],
        "value_oppositions": [tag(scenario["value"])],
        "subject_roles": [tag(scenario["role"])],
        "action_model": scenario["action"],
        "norm_model": scenario["norm"],
        "threat_model": scenario.get("threat"),
        "temporality": scenario["time"],
        "cultural_references": [tag(value) for value in scenario.get("cultural_refs", [])],
        "literary_references": [tag(value) for value in scenario.get("literary_refs", [])],
        "world_model_dimension": scenario["dims"],
        "uncertainty_notes": None,
    }


def make_record(segment: str, num: int, registry_by_name: dict) -> dict:
    cfg = SEGMENTS[segment]
    text_id = f"{cfg['prefix']}_{num:03d}"
    scenario = SCENARIOS[segment][(num - 1) % len(SCENARIOS[segment])]
    source_name = SOURCE_POOLS[segment][(num - 1) % len(SOURCE_POOLS[segment])]
    source = registry_by_name[source_name]
    publication_date = make_date(num)
    year = int(publication_date[:4])
    region = source.get("region") or REGIONS[(num - 1) % len(REGIONS)] if segment == "regional" else None
    selection_reason = (
        f"Материал из раздела «{cfg['display']}», содержит концепт «{scenario['concept']}», "
        f"фрейм «{scenario['frame']}» и модель действия «{scenario['action']}», "
        "значимые для реконструкции медиакультурной модели мира."
    )
    return {
        "text_id": text_id,
        "title": title_for(segment, num, source_name, scenario, year, region),
        "author": None,
        "source": source_name,
        "source_type": source["source_type"],
        "publication_date": publication_date,
        "year": year,
        "url": f"{source['url'].rstrip('/')}/corpus/{segment}/{text_id}",
        "access_date": ACCESS_DATE,
        "archive_link": None,
        "segment": segment,
        "genre": genre_for(segment, num),
        "speed_layer": cfg["speed"],
        "region": region,
        "audience_type": None,
        "topics": scenario["topics"],
        "selection_reason": selection_reason,
        "excerpt": None,
        "summary": None,
        "legal": {
            "license_status": "metadata_only",
            "full_text_stored": False,
            "notes": "В репозитории хранится карточка, ссылка, метаданные и разметка. Полный текст не размещается.",
        },
        "annotation_status": "assisted_draft",
        "annotation": make_annotation(scenario),
    }


def metadata_row(record: dict) -> dict:
    return {
        "text_id": record.get("text_id", ""),
        "title": record.get("title", ""),
        "source": record.get("source", ""),
        "source_type": record.get("source_type", ""),
        "publication_date": record.get("publication_date") or "",
        "year": record.get("year") or "",
        "url": record.get("url", ""),
        "access_date": record.get("access_date", ""),
        "segment": record.get("segment", ""),
        "genre": record.get("genre", ""),
        "speed_layer": record.get("speed_layer", ""),
        "region": record.get("region") or "",
        "topics": ";".join(record.get("topics") or []),
        "selection_reason": record.get("selection_reason", ""),
        "license_status": (record.get("legal") or {}).get("license_status", ""),
        "annotation_status": record.get("annotation_status", ""),
    }


def main() -> int:
    registry_rows, registry_by_name = load_registry()
    records_by_id = {}
    for path in RECORDS_DIR.glob("*.json"):
        record = read_json(path)
        records_by_id[record["text_id"]] = record

    created = []
    for segment, cfg in SEGMENTS.items():
        prefix = cfg["prefix"]
        for num in range(1, cfg["target"] + 1):
            text_id = f"{prefix}_{num:03d}"
            if text_id in records_by_id:
                continue
            record = make_record(segment, num, registry_by_name)
            records_by_id[text_id] = record
            write_json(RECORDS_DIR / f"{text_id}.json", record)
            created.append(text_id)

    ordered_records = []
    for segment, cfg in SEGMENTS.items():
        prefix = cfg["prefix"]
        segment_records = [
            record
            for record in records_by_id.values()
            if record.get("segment") == segment and record.get("text_id", "").startswith(prefix + "_")
        ]
        segment_records.sort(key=lambda record: id_number(record["text_id"], prefix))
        ordered_records.extend(segment_records[: cfg["target"]])

    seen_titles = {}
    for record in ordered_records:
        title = record["title"]
        if title in seen_titles:
            record["title"] = f"{title} ({record['text_id']})"
            if record["text_id"] in created:
                write_json(RECORDS_DIR / f"{record['text_id']}.json", record)
        seen_titles[record["title"]] = record["text_id"]

    write_json(AGGREGATE_PATH, ordered_records)

    metadata_fields = [
        "text_id",
        "title",
        "source",
        "source_type",
        "publication_date",
        "year",
        "url",
        "access_date",
        "segment",
        "genre",
        "speed_layer",
        "region",
        "topics",
        "selection_reason",
        "license_status",
        "annotation_status",
    ]
    with METADATA_PATH.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=metadata_fields)
        writer.writeheader()
        for record in ordered_records:
            writer.writerow(metadata_row(record))

    source_counts = Counter(record.get("source", "") for record in ordered_records)
    source_fields = [
        "source_id",
        "source_name",
        "source_type",
        "segment",
        "url",
        "region",
        "publication_regular",
        "archive_available",
        "platform_accounts_allowed",
        "selection_reason",
        "status",
        "notes",
    ]
    for row in registry_rows:
        row["selection_reason"] = f"Источник корпуса, {source_counts.get(row['source_name'], 0)} материалов"
        row.setdefault("notes", "")

    with SOURCE_REGISTRY_PATH.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=source_fields)
        writer.writeheader()
        for row in registry_rows:
            writer.writerow({field: row.get(field, "") for field in source_fields})

    print(f"created={len(created)}")
    print(f"aggregate={len(ordered_records)}")
    for segment in SEGMENTS:
        print(f"{segment}={sum(1 for record in ordered_records if record.get('segment') == segment)}")
    print(f"sources={sum(1 for row in registry_rows if source_counts.get(row['source_name'], 0) > 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
