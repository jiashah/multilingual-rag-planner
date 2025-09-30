"""
Multilingual Translation Support
Uses Google Translate API and language detection
"""

import os
import streamlit as st
from typing import Dict, List, Optional, Any
from googletrans import Translator as GoogleTranslator
from langdetect import detect, detect_langs
from utils.logger import setup_logger

logger = setup_logger("translator")

class Translator:
    def __init__(self):
        self.google_translator = GoogleTranslator()
        self.supported_languages = {
            "en": "English",
            "es": "Español", 
            "fr": "Français",
            "de": "Deutsch",
            "it": "Italiano",
            "pt": "Português",
            "zh": "中文",
            "ja": "日本語",
            "ko": "한국어",
            "hi": "हिंदी",
            "ar": "العربية",
            "ru": "Русский",
            "nl": "Nederlands",
            "sv": "Svenska",
            "no": "Norsk",
            "da": "Dansk",
            "fi": "Suomi",
            "pl": "Polski",
            "tr": "Türkçe",
            "th": "ไทย"
        }
        
        # UI text translations for common interface elements
        self.ui_translations = self._load_ui_translations()
    
    def _load_ui_translations(self) -> Dict[str, Dict[str, str]]:
        """Load UI text translations for common interface elements"""
        return {
            "en": {
                "dashboard": "Dashboard",
                "goal_planner": "Goal Planner", 
                "task_manager": "Task Manager",
                "settings": "Settings",
                "login": "Login",
                "logout": "Logout",
                "signup": "Sign Up",
                "create_goal": "Create Goal",
                "create_task": "Create Task",
                "today": "Today",
                "tomorrow": "Tomorrow",
                "this_week": "This Week",
                "completed": "Completed",
                "pending": "Pending",
                "in_progress": "In Progress",
                "priority": "Priority",
                "due_date": "Due Date",
                "progress": "Progress",
                "description": "Description",
                "title": "Title",
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "edit": "Edit",
                "view": "View",
                "search": "Search",
                "filter": "Filter",
                "all": "All",
                "active": "Active",
                "category": "Category",
                "ai_insights": "AI Insights",
                "generate_tasks": "Generate Tasks",
                "loading": "Loading..."
            },
            "es": {
                "dashboard": "Tablero",
                "goal_planner": "Planificador de Objetivos",
                "task_manager": "Gestor de Tareas",
                "settings": "Configuración",
                "login": "Iniciar Sesión",
                "logout": "Cerrar Sesión",
                "signup": "Registrarse",
                "create_goal": "Crear Objetivo",
                "create_task": "Crear Tarea",
                "today": "Hoy",
                "tomorrow": "Mañana",
                "this_week": "Esta Semana",
                "completed": "Completado",
                "pending": "Pendiente",
                "in_progress": "En Progreso",
                "priority": "Prioridad",
                "due_date": "Fecha Límite",
                "progress": "Progreso",
                "description": "Descripción",
                "title": "Título",
                "save": "Guardar",
                "cancel": "Cancelar",
                "delete": "Eliminar",
                "edit": "Editar",
                "view": "Ver",
                "search": "Buscar",
                "filter": "Filtrar",
                "all": "Todos",
                "active": "Activo",
                "category": "Categoría",
                "ai_insights": "Insights de IA",
                "generate_tasks": "Generar Tareas",
                "loading": "Cargando..."
            },
            "fr": {
                "dashboard": "Tableau de Bord",
                "goal_planner": "Planificateur d'Objectifs",
                "task_manager": "Gestionnaire de Tâches",
                "settings": "Paramètres",
                "login": "Se Connecter",
                "logout": "Se Déconnecter",
                "signup": "S'inscrire",
                "create_goal": "Créer un Objectif",
                "create_task": "Créer une Tâche",
                "today": "Aujourd'hui",
                "tomorrow": "Demain",
                "this_week": "Cette Semaine",
                "completed": "Terminé",
                "pending": "En Attente",
                "in_progress": "En Cours",
                "priority": "Priorité",
                "due_date": "Date Limite",
                "progress": "Progrès",
                "description": "Description",
                "title": "Titre",
                "save": "Sauvegarder",
                "cancel": "Annuler",
                "delete": "Supprimer",
                "edit": "Modifier",
                "view": "Voir",
                "search": "Rechercher",
                "filter": "Filtrer",
                "all": "Tous",
                "active": "Actif",
                "category": "Catégorie",
                "ai_insights": "Insights IA",
                "generate_tasks": "Générer des Tâches",
                "loading": "Chargement..."
            },
            "de": {
                "dashboard": "Dashboard",
                "goal_planner": "Ziel-Planer",
                "task_manager": "Aufgaben-Manager",
                "settings": "Einstellungen",
                "login": "Anmelden",
                "logout": "Abmelden",
                "signup": "Registrieren",
                "create_goal": "Ziel Erstellen",
                "create_task": "Aufgabe Erstellen",
                "today": "Heute",
                "tomorrow": "Morgen",
                "this_week": "Diese Woche",
                "completed": "Abgeschlossen",
                "pending": "Ausstehend",
                "in_progress": "In Bearbeitung",
                "priority": "Priorität",
                "due_date": "Fälligkeitsdatum",
                "progress": "Fortschritt",
                "description": "Beschreibung",
                "title": "Titel",
                "save": "Speichern",
                "cancel": "Abbrechen",
                "delete": "Löschen",
                "edit": "Bearbeiten",
                "view": "Ansehen",
                "search": "Suchen",
                "filter": "Filtern",
                "all": "Alle",
                "active": "Aktiv",
                "category": "Kategorie",
                "ai_insights": "KI-Einblicke",
                "generate_tasks": "Aufgaben Generieren",
                "loading": "Laden..."
            },
            "zh": {
                "dashboard": "仪表板",
                "goal_planner": "目标规划器",
                "task_manager": "任务管理器",
                "settings": "设置",
                "login": "登录",
                "logout": "登出",
                "signup": "注册",
                "create_goal": "创建目标",
                "create_task": "创建任务",
                "today": "今天",
                "tomorrow": "明天",
                "this_week": "本周",
                "completed": "已完成",
                "pending": "待处理",
                "in_progress": "进行中",
                "priority": "优先级",
                "due_date": "截止日期",
                "progress": "进度",
                "description": "描述",
                "title": "标题",
                "save": "保存",
                "cancel": "取消",
                "delete": "删除",
                "edit": "编辑",
                "view": "查看",
                "search": "搜索",
                "filter": "筛选",
                "all": "全部",
                "active": "活跃",
                "category": "类别",
                "ai_insights": "AI洞察",
                "generate_tasks": "生成任务",
                "loading": "加载中..."
            }
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of given text
        
        Args:
            text (str): Text to detect language for
            
        Returns:
            str: Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            if not text or len(text.strip()) < 3:
                return "en"  # Default to English for short texts
            
            detected = detect(text)
            
            # Validate detected language is in our supported list
            if detected in self.supported_languages:
                return detected
            else:
                logger.warning(f"Detected language {detected} not supported, defaulting to English")
                return "en"
                
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "en"  # Default to English on error
    
    def get_language_confidence(self, text: str) -> List[Dict[str, Any]]:
        """
        Get language detection confidence scores
        
        Args:
            text (str): Text to analyze
            
        Returns:
            List of dictionaries with language and probability
        """
        try:
            if not text or len(text.strip()) < 3:
                return [{"lang": "en", "prob": 1.0}]
            
            detected_langs = detect_langs(text)
            results = []
            
            for lang in detected_langs:
                if lang.lang in self.supported_languages:
                    results.append({
                        "lang": lang.lang,
                        "language_name": self.supported_languages[lang.lang],
                        "prob": lang.prob
                    })
            
            return results[:3]  # Return top 3 results
            
        except Exception as e:
            logger.error(f"Language confidence detection failed: {e}")
            return [{"lang": "en", "language_name": "English", "prob": 1.0}]
    
    def translate_text(self, text: str, target_lang: str, source_lang: str = "auto") -> str:
        """
        Translate text to target language
        
        Args:
            text (str): Text to translate
            target_lang (str): Target language code
            source_lang (str): Source language code (auto-detect if "auto")
            
        Returns:
            str: Translated text
        """
        try:
            if not text or not text.strip():
                return text
            
            # Don't translate if source and target are the same
            if source_lang == target_lang:
                return text
            
            # Auto-detect source language if needed
            if source_lang == "auto":
                source_lang = self.detect_language(text)
                if source_lang == target_lang:
                    return text
            
            # Validate target language
            if target_lang not in self.supported_languages:
                logger.warning(f"Target language {target_lang} not supported")
                return text
            
            # Perform translation
            result = self.google_translator.translate(text, dest=target_lang, src=source_lang)
            
            if result and hasattr(result, 'text'):
                return result.text
            else:
                logger.warning("Translation result is empty")
                return text
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original text on error
    
    def translate_goal(self, goal_data: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """
        Translate goal data to target language
        
        Args:
            goal_data (dict): Goal data to translate
            target_lang (str): Target language code
            
        Returns:
            dict: Translated goal data
        """
        try:
            translated_goal = goal_data.copy()
            
            # Translate title and description
            if goal_data.get("title"):
                translated_goal["title"] = self.translate_text(
                    goal_data["title"], target_lang
                )
            
            if goal_data.get("description"):
                translated_goal["description"] = self.translate_text(
                    goal_data["description"], target_lang
                )
            
            # Store original language if not already set
            if "original_language" not in translated_goal:
                detected_lang = self.detect_language(goal_data.get("title", ""))
                translated_goal["original_language"] = detected_lang
            
            # Set current language
            translated_goal["language"] = target_lang
            
            return translated_goal
            
        except Exception as e:
            logger.error(f"Goal translation failed: {e}")
            return goal_data
    
    def translate_task(self, task_data: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
        """
        Translate task data to target language
        
        Args:
            task_data (dict): Task data to translate
            target_lang (str): Target language code
            
        Returns:
            dict: Translated task data
        """
        try:
            translated_task = task_data.copy()
            
            # Translate title and description
            if task_data.get("title"):
                translated_task["title"] = self.translate_text(
                    task_data["title"], target_lang
                )
            
            if task_data.get("description"):
                translated_task["description"] = self.translate_text(
                    task_data["description"], target_lang
                )
            
            # Translate completion notes if present
            if task_data.get("completion_notes"):
                translated_task["completion_notes"] = self.translate_text(
                    task_data["completion_notes"], target_lang
                )
            
            # Set language
            translated_task["language"] = target_lang
            
            return translated_task
            
        except Exception as e:
            logger.error(f"Task translation failed: {e}")
            return task_data
    
    def translate_bulk_tasks(self, tasks: List[Dict[str, Any]], target_lang: str) -> List[Dict[str, Any]]:
        """
        Translate multiple tasks efficiently
        
        Args:
            tasks (list): List of task dictionaries
            target_lang (str): Target language code
            
        Returns:
            list: List of translated tasks
        """
        translated_tasks = []
        
        for task in tasks:
            translated_task = self.translate_task(task, target_lang)
            translated_tasks.append(translated_task)
        
        return translated_tasks
    
    def get_ui_text(self, key: str, language: str = None) -> str:
        """
        Get translated UI text
        
        Args:
            key (str): Text key to look up
            language (str): Language code (uses session language if None)
            
        Returns:
            str: Translated text or original key if not found
        """
        if not language:
            language = st.session_state.get("language", "en")
        
        # Get translations for the language, fallback to English
        translations = self.ui_translations.get(language, self.ui_translations.get("en", {}))
        
        return translations.get(key, key)  # Return key if translation not found
    
    def translate_ai_response(self, response: str, target_lang: str) -> str:
        """
        Translate AI-generated response to target language
        
        Args:
            response (str): AI response to translate
            target_lang (str): Target language code
            
        Returns:
            str: Translated response
        """
        try:
            if not response or target_lang == "en":
                return response
            
            # For AI responses, we want to maintain structure while translating content
            return self.translate_text(response, target_lang)
            
        except Exception as e:
            logger.error(f"AI response translation failed: {e}")
            return response
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names"""
        return self.supported_languages.copy()
    
    def is_rtl_language(self, lang_code: str) -> bool:
        """Check if language is right-to-left"""
        rtl_languages = {"ar", "he", "fa", "ur"}
        return lang_code in rtl_languages
    
    def format_date_for_language(self, date_str: str, lang_code: str) -> str:
        """
        Format date string appropriately for language
        
        Args:
            date_str (str): Date string in YYYY-MM-DD format
            lang_code (str): Language code
            
        Returns:
            str: Formatted date string
        """
        try:
            from datetime import datetime
            
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Format based on language conventions
            if lang_code in ["en", "en-US"]:
                return date_obj.strftime("%B %d, %Y")  # January 15, 2024
            elif lang_code in ["de", "fr", "it"]:
                return date_obj.strftime("%d %B %Y")   # 15 Januar 2024
            elif lang_code in ["zh", "ja", "ko"]:
                return date_obj.strftime("%Y年%m月%d日")  # 2024年01月15日
            else:
                return date_obj.strftime("%d/%m/%Y")   # 15/01/2024
                
        except Exception as e:
            logger.error(f"Date formatting failed: {e}")
            return date_str
    
    def create_language_prompt(self, base_prompt: str, target_lang: str) -> str:
        """
        Create a language-specific prompt for AI operations
        
        Args:
            base_prompt (str): Base English prompt
            target_lang (str): Target language code
            
        Returns:
            str: Language-specific prompt
        """
        if target_lang == "en":
            return base_prompt
        
        lang_name = self.supported_languages.get(target_lang, "the target language")
        
        language_instruction = f"Please respond in {lang_name} ({target_lang}). "
        return language_instruction + base_prompt

# Global translator instance
translator = Translator()