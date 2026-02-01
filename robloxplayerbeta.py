# coding: utf-8
# robloxplayerbeta.py — расширенный модуль для Roblox Player (десктоп)
# Много событий, скриптов, звуков, проверок

import appModuleHandler
import api
import ui
import tones
import controlTypes
import speech
from scriptHandler import script, willSayAllResume
import globalPluginHandler
import logHandler
import time
import re

logger = logHandler.log.getLogger("RobloxAccessibility")

class AppModule(appModuleHandler.AppModule):
    sleepMode = True  # По умолчанию sleep mode включён — не мешаем игре
    lastChatMessage = ""  # Для предотвращения повторных объявлений
    chatSpamFilter = True  # Фильтр спама в чате
    announceMenuNavigation = True  # Объявлять навигацию по меню
    beepVolume = 70  # Громкость beep (0-100)
    languageDetection = True  # Пытаться определять язык чата

    def __init__(self, *args, **kwargs):
        super(AppModule, self).__init__(*args, **kwargs)
        logger.info("RobloxAccessibility: модуль загружен для RobloxPlayerBeta.exe")
        self.announce("Модуль Roblox Accessibility активирован (версия 0.5)")

    def announce(self, text, beepFreq=600, beepDur=80):
        """Удобная функция для объявления + beep"""
        if text:
            ui.message(text)
            tones.beep(beepFreq, beepDur)

    def event_gainFocus(self, obj, nextHandler):
        try:
            role = obj.role
            name = obj.name or ""
            value = obj.value or ""
            desc = obj.description or ""

            # Кнопки, ссылки, меню
            if role in (controlTypes.Role.BUTTON, controlTypes.Role.MENUITEM, controlTypes.Role.LINK, controlTypes.Role.TOGGLEBUTTON):
                state = ""
                if obj.isChecked is not None:
                    state = " (отмечено)" if obj.isChecked else " (не отмечено)"
                self.announce(f"{role.displayString}: {name or desc}{state}", 650, 70)

            # Текстовые поля и чат
            elif role == controlTypes.Role.EDITABLETEXT:
                if "chat" in name.lower() or "message" in name.lower() or "сообщ" in name.lower():
                    self.announce(f"Поле чата: {value}", 700, 90)
                else:
                    self.announce(f"Поле ввода: {value}", 550, 60)

            # Списки, таблицы, инвентарь
            elif role in (controlTypes.Role.LISTITEM, controlTypes.Role.TABLEROW, controlTypes.Role.TABLECELL):
                if self.announceMenuNavigation:
                    self.announce(f"Элемент списка: {name or value or desc}", 500, 50)

            # Чекбоксы, радиокнопки
            elif role in (controlTypes.Role.CHECKBOX, controlTypes.Role.RADIOBUTTON):
                state = "включено" if obj.isChecked else "выключено"
                self.announce(f"{name or role.displayString}: {state}", 720, 80)

            # Прогресс-бары (загрузка игры, Roblox)
            elif role == controlTypes.Role.PROGRESSBAR:
                self.announce(f"Прогресс: {value or name}", 400, 120)

            # Графика / Canvas (игра) — минимум объявлений
            elif role == controlTypes.Role.GRAPHIC:
                # Не спамим, только если есть имя
                if name:
                    self.announce(f"Графика: {name}", 300, 40)

            tones.beep(self.beepVolume + 200, 60)  # Общий beep при фокусе
        except Exception as e:
            logger.error(f"Ошибка в event_gainFocus: {e}")

        nextHandler()

    def event_valueChange(self, obj, nextHandler):
        try:
            if obj.role != controlTypes.Role.EDITABLETEXT:
                return nextHandler()

            value = obj.value or ""
            name = obj.name or ""

            # Фильтр спама чата
            if self.chatSpamFilter and value == self.lastChatMessage:
                return nextHandler()

            if "chat" in name.lower() or "message" in name.lower() or "сообщ" in name.lower():
                # Простой фильтр на повторяющиеся сообщения
                if len(value) > 3 and value != self.lastChatMessage:
                    prefix = ""
                    if self.languageDetection:
                        if re.search(r'[а-яА-Я]', value):
                            prefix = "Русский чат: "
                        elif re.search(r'[a-zA-Z]', value):
                            prefix = "English chat: "
                    self.announce(f"{prefix}{value}", 820, 100)
                    self.lastChatMessage = value
        except Exception as e:
            logger.error(f"Ошибка в event_valueChange: {e}")

        nextHandler()

    def event_nameChange(self, obj, nextHandler):
        # Изменение имени объекта (например, обновление заголовка окна или элемента)
        if obj.role in (controlTypes.Role.WINDOW, controlTypes.Role.FRAME):
            self.announce(f"Окно/вкладка: {obj.name}", 450, 120)
        nextHandler()

    @script(gesture="kb:NVDA+c", description="Прочитать текущий чат или фокус", category="Roblox")
    def script_readCurrent(self, gesture):
        obj = api.getFocusObject()
        if obj:
            parts = []
            if obj.name: parts.append(f"Имя: {obj.name}")
            if obj.value: parts.append(f"Значение: {obj.value}")
            if obj.description: parts.append(f"Описание: {obj.description}")
            text = " | ".join(parts) or "Нет информации"
            self.announce(f"Текущий: {text}", 850, 130)
        else:
            self.announce("Нет фокуса", 200, 200)

    @script(gesture="kb:NVDA+shift+c", description="Прочитать весь видимый чат (если возможно)", category="Roblox")
    def script_readFullChat(self, gesture):
        self.announce("Попытка прочитать чат... (ограничено доступностью Roblox)", 600, 150)
        # Здесь можно добавить логику поиска детей объекта чата, но пока заглушка

    @script(gesture="kb:NVDA+shift+s", description="Вкл/выкл sleep mode", category="Roblox")
    def script_toggleSleep(self, gesture):
        self.sleepMode = not self.sleepMode
        self.announce(f"Sleep mode {'включён' if self.sleepMode else 'выключен'}", 350 if self.sleepMode else 950, 180)

    @script(gesture="kb:NVDA+shift+m", description="Переключить объявление навигации по меню", category="Roblox")
    def script_toggleMenuAnnounce(self, gesture):
        self.announceMenuNavigation = not self.announceMenuNavigation
        self.announce(f"Объявление меню: {'вкл' if self.announceMenuNavigation else 'выкл'}", 500, 100)

    @script(gesture="kb:NVDA+shift+f", description="Прочитать версию Roblox и модуля", category="Roblox")
    def script_versionInfo(self, gesture):
        self.announce("Roblox Accessibility версия 0.5 | NVDA интеграция активна", 700, 120)

    def event_appModuleLose(self):
        logger.info("Модуль RobloxAccessibility выгружен")
        super(AppModule, self).event_appModuleLose()