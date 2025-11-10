# Biography Video Prompt Generator

[English](#english) | [Русский](#русский)

---

<a name="english"></a>
## English

### Description

Biography Video Prompt Generator is a modular Python application designed to analyze biographical texts (12,000-15,000 words) and automatically generate image prompts using AI providers (OpenRouter, OpenAI, Gemini, Anthropic). The tool creates structured, cinematically compelling prompts suitable for video production.

### Features

#### AI Integration
- ✅ **4 AI Providers**: OpenRouter (20 req/min), OpenAI (50 req/min), Gemini (15 req/min), Anthropic (10 req/min)
- ✅ **Automatic Rate Limiting**: Respects provider-specific limits
- ✅ **Retry with Exponential Backoff**: Up to 5 retry attempts
- ✅ **HTTP 429 Handling**: Graceful rate limit exceeded handling

#### Text Processing
- ✅ **Text Chunking**: Splits large texts by ~1000 words
- ✅ **Scene Splitting**: Divides into 5-7 second scenes
- ✅ **Timeline Calculation**: Calculates timestamps for each prompt
- ✅ **Character Consistency**: Optional character profile maintenance

#### Scene Analysis
- **Shot Type**: Wide shot, medium shot, close-up, tracking shot, etc.
- **Emotions**: Rage, joy, melancholy, anxiety, determination (with intensity)
- **Objects**: Documents, furniture, clothing, weapons, nature, architecture
- **Time of Day**: Dawn, morning, afternoon, golden hour, night
- **Weather**: Clear, sunny, rainy, foggy, overcast, snowy

#### 12-Element Prompt Structure
1. **SHOT TYPE**: Camera angle and framing
2. **SUBJECT**: Characters with physical appearance
3. **ACTION**: Activities and micro-emotions
4. **SETTING**: Location, architecture, time period
5. **COMPOSITION**: Visual arrangement (rule of thirds, etc.)
6. **LIGHTING**: Source, direction, quality, color
7. **MOOD**: Atmosphere and emotional tone
8. **KEY DETAILS**: Objects, textures, effects
9. **COLOR PALETTE**: Specific colors and relationships
10. **STYLE**: Visual style (historical, photorealistic, etc.)
11. **TECHNICAL**: Quality descriptors (8k, cinematic, etc.)
12. **CHARACTER APPEARANCE**: Consistent character descriptions

#### Output Formats
- ✅ **JSON**: Primary format with full metadata
- ✅ **TXT**: Human-readable text format
- ✅ **CSV**: Spreadsheet-compatible format

#### GUI Features (CustomTkinter)
- ✅ **Dark Theme**: Modern dark interface
- ✅ **Folder Selection**: Easy input/output folder browsing
- ✅ **AI Provider Selection**: Choose from 4 providers
- ✅ **Model Selection**: Provider-specific model options
- ✅ **API Key Management**: Secure key storage
- ✅ **Video Settings**:
  - Frame interval (3-30 sec, default 6)
  - Narration speed (100-200 wpm, default 150)
  - Visual style (dropdown selection)
- ✅ **Processing Options**:
  - Dense mode (detailed prompts)
  - Character consistency
- ✅ **Progress Tracking**: Real-time progress bar and status
- ✅ **Logs**: Live processing logs
- ✅ **Estimated Images**: Automatic calculation

### Installation

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

#### Steps

1. **Clone the repository**:
```bash
git clone https://github.com/nikolayegarev-arch/biography-video-prompt-generator.git
cd biography-video-prompt-generator
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure API keys**:

Option A - Using `.env` file (recommended):
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Option B - Using `config.txt`:
```bash
cp config.txt.example config.txt
# Edit config.txt and add your API keys
```

### API Keys

You'll need at least one API key from the following providers:

#### OpenRouter
- Website: https://openrouter.ai/keys
- Key format: `sk-or-...`
- Rate limit: 20 requests/minute

#### OpenAI
- Website: https://platform.openai.com/api-keys
- Key format: `sk-...`
- Rate limit: 50 requests/minute

#### Google Gemini
- Website: https://makersuite.google.com/app/apikey
- Key format: `AIza...`
- Rate limit: 15 requests/minute

#### Anthropic
- Website: https://console.anthropic.com/
- Key format: `sk-ant-...`
- Rate limit: 10 requests/minute

### Usage

#### GUI Mode (Recommended)

1. **Start the application**:
```bash
python main.py
```

2. **Configure settings**:
   - Select input folder (containing `.txt` files)
   - Select output folder (for generated prompts)
   - Choose AI provider and set API key
   - Select model
   - Adjust frame interval and narration speed
   - Choose visual style
   - Enable optional features (dense mode, character consistency)

3. **Start processing**:
   - Click "Start Processing"
   - Monitor progress in real-time
   - Results saved automatically

#### Workflow

1. Place biographical text files (`.txt`) in the `texts_to_process/` folder
2. Run `python main.py`
3. Select AI provider and enter API key
4. Configure parameters (interval, speed, style)
5. Click "Start Processing"
6. Results are saved in `video_prompts/`:
   - `filename.video_prompts.json` - Primary output
   - `filename.video_prompts.txt` - Text format
   - `filename.video_prompts.csv` - Spreadsheet format
   - `filename.partial.json` - Temporary (deleted on success)

### Output Structure

#### JSON Output
```json
{
  "metadata": {
    "total_prompts": 800,
    "total_duration_seconds": 4800,
    "frame_interval_seconds": 6.0,
    "narration_speed_wpm": 150,
    "visual_style": "historical illustration",
    "character_profiles": {},
    "source_word_count": 12000,
    "total_chunks": 12,
    "processed_chunks": 12,
    "dense_mode": false,
    "character_consistency": false
  },
  "scenes": [
    {
      "id": "scene_0_0",
      "timestamp": 0.0,
      "prompt": "Medium shot of Queen Victoria...",
      "chunk": 0,
      "scene": 0,
      "word_index": 0,
      "shot_type": "medium shot",
      "emotions": {"determination": "high"},
      "objects": ["crown", "letter", "desk"],
      "time_of_day": "morning",
      "weather": "clear"
    }
  ]
}
```

### Error Handling & Resilience

- ✅ **Partial Saves**: Progress saved after each chunk
- ✅ **Resume Capability**: Continues from last successful chunk
- ✅ **Atomic File Writes**: Uses tempfile + rename for safety
- ✅ **Graceful Degradation**: Handles API errors elegantly
- ✅ **Detailed Logging**: Full processing logs

### Project Structure

```
biography-video-prompt-generator/
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── config.txt.example         # Config file template
├── main.py                    # Application entry point
├── config.py                  # Configuration classes
├── exceptions.py              # Custom exceptions
├── api/
│   ├── __init__.py
│   └── api_manager.py         # Unified API manager
├── processing/
│   ├── __init__.py
│   ├── story_processor.py     # Main processor
│   ├── prompt_templates.py    # Prompt templates
│   ├── scene_analyzer.py      # Scene analysis
│   └── text_processor.py      # Text processing
├── utils/
│   ├── __init__.py
│   ├── retry_handler.py       # Retry logic
│   ├── file_ops.py            # File operations
│   └── config_loader.py       # Config loading
├── gui/
│   ├── __init__.py
│   ├── main_window.py         # Main window
│   ├── api_key_dialog.py      # API key dialog
│   └── settings.py            # Settings management
├── texts_to_process/          # Input folder
│   └── .gitkeep
└── video_prompts/             # Output folder
    └── .gitkeep
```

### Troubleshooting

#### API Key Issues
- Verify key format matches provider requirements
- Check key validity on provider website
- Ensure key has sufficient credits/quota

#### Rate Limiting
- Application automatically handles rate limits
- If persistent issues, reduce processing frequency
- Consider upgrading provider plan

#### Processing Errors
- Check `biography_generator.log` for detailed errors
- Verify input text file encoding (UTF-8)
- Ensure sufficient disk space for output files

#### GUI Issues
- Update CustomTkinter: `pip install --upgrade customtkinter`
- Check Python version (3.8+ required)
- Try running from terminal to see error messages

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### License

This project is open source. See LICENSE file for details.

---

<a name="русский"></a>
## Русский

### Описание

Biography Video Prompt Generator — это модульное Python-приложение для анализа биографических текстов (12,000-15,000 слов) и автоматической генерации промптов для изображений с использованием AI (OpenRouter, OpenAI, Gemini, Anthropic). Инструмент создает структурированные, кинематографически убедительные промпты, подходящие для видеопроизводства.

### Возможности

#### Интеграция AI
- ✅ **4 провайдера**: OpenRouter (20 зап/мин), OpenAI (50 зап/мин), Gemini (15 зап/мин), Anthropic (10 зап/мин)
- ✅ **Автоматический rate limiting**: Учитывает лимиты каждого провайдера
- ✅ **Retry с exponential backoff**: До 5 попыток
- ✅ **Обработка HTTP 429**: Корректная обработка превышения лимитов

#### Обработка текста
- ✅ **Chunking**: Разделение больших текстов по ~1000 слов
- ✅ **Scene splitting**: Деление на сцены по 5-7 секунд
- ✅ **Расчет timeline**: Временные метки для каждого промпта
- ✅ **Консистентность персонажей**: Опциональное сохранение описаний

#### Анализ сцен
- **Shot Type**: Общий план, средний план, крупный план, tracking shot и т.д.
- **Эмоции**: Ярость, радость, меланхолия, тревога, решительность (с интенсивностью)
- **Объекты**: Документы, мебель, одежда, оружие, природа, архитектура
- **Время суток**: Рассвет, утро, день, золотой час, ночь
- **Погода**: Ясно, солнечно, дождь, туман, облачно, снег

#### 12-элементная структура промпта
1. **SHOT TYPE**: Угол и кадрирование камеры
2. **SUBJECT**: Персонажи с физическим описанием
3. **ACTION**: Действия и микроэмоции
4. **SETTING**: Локация, архитектура, исторический период
5. **COMPOSITION**: Визуальная композиция (правило третей и т.д.)
6. **LIGHTING**: Источник, направление, качество, цвет
7. **MOOD**: Атмосфера и эмоциональный тон
8. **KEY DETAILS**: Объекты, текстуры, эффекты
9. **COLOR PALETTE**: Конкретные цвета и отношения
10. **STYLE**: Визуальный стиль (исторический, фотореалистичный и т.д.)
11. **TECHNICAL**: Технические дескрипторы (8k, cinematic и т.д.)
12. **CHARACTER APPEARANCE**: Последовательные описания персонажей

#### Форматы вывода
- ✅ **JSON**: Основной формат с полными метаданными
- ✅ **TXT**: Человекочитаемый текстовый формат
- ✅ **CSV**: Формат для электронных таблиц

#### Функции GUI (CustomTkinter)
- ✅ **Темная тема**: Современный темный интерфейс
- ✅ **Выбор папок**: Простой выбор папок ввода/вывода
- ✅ **Выбор AI провайдера**: Выбор из 4 провайдеров
- ✅ **Выбор модели**: Модели для каждого провайдера
- ✅ **Управление API ключами**: Безопасное хранение ключей
- ✅ **Настройки видео**:
  - Интервал кадров (3-30 сек, по умолчанию 6)
  - Скорость дикторского текста (100-200 слов/мин, по умолчанию 150)
  - Визуальный стиль (выпадающий список)
- ✅ **Опции обработки**:
  - Dense mode (детальные промпты)
  - Консистентность персонажей
- ✅ **Отслеживание прогресса**: Прогресс-бар и статус в реальном времени
- ✅ **Логи**: Логи обработки в реальном времени
- ✅ **Оценка изображений**: Автоматический расчет

### Установка

#### Требования
- Python 3.8 или выше
- pip (менеджер пакетов Python)

#### Шаги

1. **Клонируйте репозиторий**:
```bash
git clone https://github.com/nikolayegarev-arch/biography-video-prompt-generator.git
cd biography-video-prompt-generator
```

2. **Установите зависимости**:
```bash
pip install -r requirements.txt
```

3. **Настройте API ключи**:

Вариант A - Используя файл `.env` (рекомендуется):
```bash
cp .env.example .env
# Отредактируйте .env и добавьте свои API ключи
```

Вариант B - Используя `config.txt`:
```bash
cp config.txt.example config.txt
# Отредактируйте config.txt и добавьте свои API ключи
```

### API Ключи

Вам понадобится хотя бы один API ключ от следующих провайдеров:

#### OpenRouter
- Сайт: https://openrouter.ai/keys
- Формат ключа: `sk-or-...`
- Лимит: 20 запросов/минута

#### OpenAI
- Сайт: https://platform.openai.com/api-keys
- Формат ключа: `sk-...`
- Лимит: 50 запросов/минута

#### Google Gemini
- Сайт: https://makersuite.google.com/app/apikey
- Формат ключа: `AIza...`
- Лимит: 15 запросов/минута

#### Anthropic
- Сайт: https://console.anthropic.com/
- Формат ключа: `sk-ant-...`
- Лимит: 10 запросов/минута

### Использование

#### Режим GUI (Рекомендуется)

1. **Запустите приложение**:
```bash
python main.py
```

2. **Настройте параметры**:
   - Выберите папку ввода (содержащую файлы `.txt`)
   - Выберите папку вывода (для сгенерированных промптов)
   - Выберите AI провайдер и установите API ключ
   - Выберите модель
   - Настройте интервал кадров и скорость дикторского текста
   - Выберите визуальный стиль
   - Включите опциональные функции (dense mode, консистентность персонажей)

3. **Запустите обработку**:
   - Нажмите "Start Processing"
   - Отслеживайте прогресс в реальном времени
   - Результаты сохраняются автоматически

#### Рабочий процесс

1. Поместите биографические текстовые файлы (`.txt`) в папку `texts_to_process/`
2. Запустите `python main.py`
3. Выберите AI провайдер и введите API ключ
4. Настройте параметры (интервал, скорость, стиль)
5. Нажмите "Start Processing"
6. Результаты сохраняются в `video_prompts/`:
   - `filename.video_prompts.json` - Основной вывод
   - `filename.video_prompts.txt` - Текстовый формат
   - `filename.video_prompts.csv` - Формат электронной таблицы
   - `filename.partial.json` - Временный (удаляется при успехе)

### Структура вывода

#### JSON вывод
```json
{
  "metadata": {
    "total_prompts": 800,
    "total_duration_seconds": 4800,
    "frame_interval_seconds": 6.0,
    "narration_speed_wpm": 150,
    "visual_style": "historical illustration",
    "character_profiles": {},
    "source_word_count": 12000,
    "total_chunks": 12,
    "processed_chunks": 12,
    "dense_mode": false,
    "character_consistency": false
  },
  "scenes": [
    {
      "id": "scene_0_0",
      "timestamp": 0.0,
      "prompt": "Medium shot of Queen Victoria...",
      "chunk": 0,
      "scene": 0,
      "word_index": 0,
      "shot_type": "medium shot",
      "emotions": {"determination": "high"},
      "objects": ["crown", "letter", "desk"],
      "time_of_day": "morning",
      "weather": "clear"
    }
  ]
}
```

### Обработка ошибок и устойчивость

- ✅ **Частичные сохранения**: Прогресс сохраняется после каждого чанка
- ✅ **Возможность возобновления**: Продолжение с последнего успешного чанка
- ✅ **Атомарная запись файлов**: Использует tempfile + rename для безопасности
- ✅ **Graceful degradation**: Корректная обработка ошибок API
- ✅ **Детальное логирование**: Полные логи обработки

### Структура проекта

```
biography-video-prompt-generator/
├── README.md                   # Этот файл
├── requirements.txt            # Зависимости Python
├── .env.example               # Шаблон переменных окружения
├── .gitignore                 # Правила игнорирования Git
├── config.txt.example         # Шаблон файла конфигурации
├── main.py                    # Точка входа приложения
├── config.py                  # Классы конфигурации
├── exceptions.py              # Кастомные исключения
├── api/
│   ├── __init__.py
│   └── api_manager.py         # Унифицированный API менеджер
├── processing/
│   ├── __init__.py
│   ├── story_processor.py     # Основной процессор
│   ├── prompt_templates.py    # Шаблоны промптов
│   ├── scene_analyzer.py      # Анализ сцен
│   └── text_processor.py      # Обработка текста
├── utils/
│   ├── __init__.py
│   ├── retry_handler.py       # Логика повторных попыток
│   ├── file_ops.py            # Файловые операции
│   └── config_loader.py       # Загрузка конфигурации
├── gui/
│   ├── __init__.py
│   ├── main_window.py         # Основное окно
│   ├── api_key_dialog.py      # Диалог API ключа
│   └── settings.py            # Управление настройками
├── texts_to_process/          # Папка ввода
│   └── .gitkeep
└── video_prompts/             # Папка вывода
    └── .gitkeep
```

### Решение проблем

#### Проблемы с API ключами
- Проверьте формат ключа в соответствии с требованиями провайдера
- Проверьте действительность ключа на сайте провайдера
- Убедитесь, что у ключа достаточно кредитов/квоты

#### Rate Limiting
- Приложение автоматически обрабатывает лимиты
- При постоянных проблемах уменьшите частоту обработки
- Рассмотрите возможность обновления плана провайдера

#### Ошибки обработки
- Проверьте `biography_generator.log` для детальных ошибок
- Проверьте кодировку входного текстового файла (UTF-8)
- Убедитесь в наличии достаточного дискового пространства для выходных файлов

#### Проблемы GUI
- Обновите CustomTkinter: `pip install --upgrade customtkinter`
- Проверьте версию Python (требуется 3.8+)
- Попробуйте запустить из терминала, чтобы увидеть сообщения об ошибках

### Вклад

Вклад приветствуется! Пожалуйста, не стесняйтесь отправлять Pull Request.

### Лицензия

Этот проект имеет открытый исходный код. Подробности см. в файле LICENSE.
