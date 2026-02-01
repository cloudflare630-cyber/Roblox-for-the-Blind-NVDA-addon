# coding: utf-8
# robloxBrowser.py — Максимум для браузерной версии Roblox

import globalPluginHandler
import api
import ui
import tones
import controlTypes
from scriptHandler import script
import winUser
import logHandler

logger = logHandler.log.getLogger("RobloxBrowserMax")

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    def speak(self, text, freq=600, dur=80):
        ui.message(text)
        tones.beep(freq, dur)

    def event_gainFocus(self, obj, nextHandler):
        try:
            title = winUser.getWindowText(obj.windowHandle) or ""
            if "roblox" not in title.lower():
                return nextHandler()

            roleDesc = controlTypes.Role(obj.role).displayString if hasattr(controlTypes.Role, obj.role) else f"роль {obj.role}"
            name = obj.name or ""
            value = obj.value or ""
            text = f"Браузер Roblox — {roleDesc}"
            if name:
                text += f" — {name}"
            if value:
                text += f" → {value}"
            self.speak(text, 720, 90)

            # Canvas / игра
            if obj.role == controlTypes.Role.GRAPHIC or "canvas" in (name or "").lower():
                self.speak("ИГРОВОЙ CANVAS — browse mode отключён", 400, 60)
                obj.shouldReportAsTreeInterceptor = False
        except Exception as e:
            logger.error(f"Браузер ошибка: {e}")

        nextHandler()

    @script(gesture="kb:NVDA+shift+r", description="Максимум информации о Roblox в браузере", category="Roblox Browser Max")
    def script_maxInfo(self, gesture):
        obj = api.getFocusObject()
        if obj:
            title = winUser.getWindowText(obj.windowHandle) or "нет заголовка"
            role = controlTypes.Role(obj.role).displayString if hasattr(controlTypes.Role, obj.role) else "неизвестно"
            text = f"Roblox браузер: роль {role} | заголовок {title} | имя {obj.name or 'нет'} | значение {obj.value or 'нет'}"
            self.speak(text, 850, 130)
        else:
            self.speak("Нет фокуса в браузере", 200, 300)

    @script(gesture="kb:NVDA+control+shift+b", description="Проверить — Roblox ли в фокусе", category="Roblox Browser Max")
    def script_checkBrowser(self, gesture):
        obj = api.getFocusObject()
        if obj:
            title = winUser.getWindowText(obj.windowHandle) or ""
            if "roblox" in title.lower():
                self.speak("Да! Roblox в браузере — NVDA видит!", 1000, 180)
            else:
                self.speak("Это не Roblox окно", 350, 200)
