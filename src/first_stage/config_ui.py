import os


class Config:
    # Настройки окна приложения
    WINDOW_TITLE = 'Блок Разметки'
    WINDOW_GEOMETRY = (300, 250, 1300, 190)

    # Получаем текущую директорию
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Путь к иконке приложения
    ICON_PATH = os.path.join(BASE_DIR, 'icon.ico').replace(os.sep, '/')

    # Цвета
    BACKGROUND_COLOR = "#151D2C"
    TEXT_COLOR = "#ffffff"
    INPUT_BACKGROUND_COLOR = "#f0f0f0"
    HOVER_BORDER_COLOR = "#0078d7"

    BUTTON_COLOR = "#0078d7"
    BUTTON_HOVER_COLOR = "#0056a1"

    COMBOBOX_BACKGROUND_COLOR = '#0078d7'  # Цвет фона для выпадающих списков
    COMBOBOX_HOVER_COLOR = '#0056a1'

    CHECKBOX_BACKGROUND_COLOR = "#ffffff"
    CHECKBOX_CHECKED_COLOR = "#0078d7"
    CHECKBOX_HOVER_COLOR = "#e0e0e0"

    # Цвета для выпадающего меню
    DROPDOWN_PRIMARY_BG_COLOR = '#333A48'  # Основной цвет фона выпадающего меню
    DROPDOWN_PRIMARY_ITEM_BG_COLOR_DEFAULT = 'rgba(255,255,255,0)'  # Цвет фона для элементов по умолчанию
    DROPDOWN_PRIMARY_ITEM_BG_COLOR_HOVER = '#0056a1'  # Цвет фона для элементов при наведении
    DROPDOWN_PRIMARY_ITEM_BG_COLOR_SELECTED_DEFAULT = '#0056a1'  # Цвет фона для выбранных элементов
    DROPDOWN_PRIMARY_ITEMVALUE_COLOR_DEFAULT = '#E8E8EE'  # Цвет текста для элементов по умолчанию
    DROPDOWN_PRIMARY_ITEMVALUE_COLOR_SELECTED_DEFAULT = '#bb80ff'  # Цвет текста для выбранных элементов
    DROPDOWN_PRIMARY_HINT_COLOR_DEFAULT = '#9DA1AC'  # Цвет подсказок по умолчанию
    DROPDOWN_PRIMARY_TITLE_COLOR = '#9DA1AC'  # Цвет заголовков в выпадающем меню

    # Шрифты
    FONT_SIZE = 14  # Размер шрифта
    COMBOBOX_FONT_SIZE = 14  # Размер шрифта для выпадающих списков
    BUTTON_FONT_SIZE = 12
    LABEL_FONT_SIZE = 12
    CHECKBOX_FONT_SIZE = 12

    # Настройки для выпадающего меню
    DROPDOWN_BORDER_RADIUS = 5
    DROPDOWN_BORDER_WIDTH = 0  # Ширина рамки выпадающего меню
    DROPDOWN_ITEMLIST_PADDING_VERTICAL = 5
    DROPDOWN_ITEMLIST_PADDING_HORIZONTAL = 10
    DROPDOWN_ITEM_BORDER_RADIUS = 8  # Радиус скругления углов для элементов списка
    DROPDOWN_ITEM_PADDING_HORIZONTAL = 12  # Горизонтальные отступы для элементов списка
    DROPDOWN_ITEM_PADDING_VERTICAL = 8  # Вертикальные отступы для элементов списка
    DROPDOWN_ITEM_SPACING = 8  # Промежуток между элементами списка
    DROPDOWN_ITEMLIST_SPACING = 4  # Промежуток между элементами списка
    DROPDOWN_SELECTIONICON_PADDING_TOP = 2  # Отступ сверху для иконки выбора
    DROPDOWN_ICON_PADDING_TOP = 2  # Отступ сверху для иконки
    DROPDOWN_CONTENT_SPACING = 0  # Промежуток между содержимым выпадающего меню
    DROPDOWN_SUFFIX_SPACING = 8  # Промежуток между суффиксом и элементом

    # Иконки
    ARROW_COMBOBOX_ICON = "path/to/arrow_icon.png"
    ARROW_CHECKBOX_ICON = "path/to/checkbox_icon.png"

    # Выбранный элемент
    SELECTED_ITEM_COLOR = '#bb80ff'  # Цвет фона выбранного элемента в выпадающем списке
