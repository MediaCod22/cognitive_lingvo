# Manifest

## Методические файлы

- README.md — описание проекта, структура корпуса, методика ПРИЗМА, статистика.
- methodology.md — общая методология корпуса.
- source_selection.md — правила подбора источников.
- collection_rules.md — правила сбора медиаматериалов.
- LICENSE.md — лицензирование (CC BY 4.0 / MIT).

## Руководства по сегментам

- segment_guides/news.md
- segment_guides/analytics.md
- segment_guides/interviews.md
- segment_guides/opinion.md
- segment_guides/cultural_journalism.md
- segment_guides/popular_science.md
- segment_guides/regional.md
- segment_guides/canonical_layer.md

## Документация

- docs/codebook.md — кодбук разметки (14 категорий).
- docs/legal_policy.md — правовые и этические правила.
- docs/validation_rules.md — правила проверки качества.
- docs/assisted_annotation_protocol.md — протокол вспомогательной разметки.

## Схемы и шаблоны

- schemas/corpus_record.schema.json — JSON-схема записи корпуса.
- schemas/annotation_schema.json — JSON-схема аннотации.
- templates/corpus_record.template.json — шаблон записи.
- templates/corpus_metadata.template.csv — шаблон метаданных.
- templates/source_registry.template.csv — шаблон реестра источников.
- templates/annotation_review.template.json — шаблон экспертной проверки.

## Данные

- data/corpus_records.json — 200 записей корпуса в JSON-формате (единый файл).
- data/corpus_metadata.csv — плоская таблица метаданных.
- data/source_registry.csv — реестр источников.
- data/corpus_data_v1_legacy.csv — исходный CSV (обратная совместимость).
- data/records/ — 200 индивидуальных JSON-файлов записей.
- data/examples/example_record_news.json — пример новостной записи.
- data/examples/example_record_canon_media.json — пример записи канонического слоя.

## Промпты и скрипты

- prompts/cognitive_annotation_prompt.md — промт для ИИ-разметки.
- scripts/validate_record.py — скрипт валидации JSON-записей.
