from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import unicodedata

def quitar_acentos(texto: str) -> str:
    """
    Normaliza y elimina los caracteres diacríticos (acentos) de una cadena.
    Por ejemplo, convierte 'programación' a 'programacion'.
    """
    try:
        texto = texto.decode('utf-8')
    except (UnicodeDecodeError, AttributeError):
        pass
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    return str(texto)

# Base de datos simulada de cursos. Las claves están sin acentos
# para poder coincidir con el texto normalizado del usuario.
cursos_data = {
    "ofimatica": {
        "microsoft word basico": {"precio": "$50", "link": "https://tucurso.com/word-basico"},
        "excel basico": {"precio": "$80", "link": "https://tucurso.com/excel-basico"},
        "excel intermedio": {"precio": "$80", "link": "https://tucurso.com/excel-intermedio"},
        "excel avanzado": {"precio": "$80", "link": "https://tucurso.com/excel-avanzado"},
        "powerpoint para presentaciones": {"precio": "$65", "link": "https://tucurso.com/powerpoint"},
    },
    "programacion": {
        "python basico": {"precio": "$100", "link": "https://tucurso.com/python-basico"},
        "python intermedio": {"precio": "$100", "link": "https://tucurso.com/python-intermedio"},
        "python avanzado": {"precio": "$100", "link": "https://tucurso.com/python-avanzado"},
        "desarrollo web con javascript": {"precio": "$150", "link": "https://tucurso.com/js-web"},
        "bases de datos sql": {"precio": "$100", "link": "https://tucurso.com/sql-db"},
        "c# basico": {"precio": "$100", "link": "https://tucurso.com/csharp-basico"},
        "c# intermedio": {"precio": "$100", "link": "https://tucurso.com/csharp-intermedio"},
        "c# avanzado": {"precio": "$100", "link": "https://tucurso.com/csharp-avanzado"},
    },
    "diseno grafico": {
        "photoshop basico": {"precio": "$90", "link": "https://tucurso.com/photoshop-basico"},
        "illustrator": {"precio": "$95", "link": "https://tucurso.com/illustrator"},
    },
    "edicion de video": {
        "adobe premiere": {"precio": "$90", "link": "https://tucurso.com/premier"},
        "after effects": {"precio": "$90", "link": "https://tucurso.com/after-effects"},
    },
    "videojuegos": {
        "unity 2d": {"precio": "$90", "link": "https://tucurso.com/unity2d"},
        "unity 3d": {"precio": "$90", "link": "https://tucurso.com/unity3d"},
        "godot basico": {"precio": "$90", "link": "https://tucurso.com/godot-basico"},
        "godot avanzado": {"precio": "$90", "link": "https://tucurso.com/godot-avanzado"},
    },
}

class ActionConsultarCategorias(Action):
    def name(self) -> Text:
        return "action_consultar_categorias"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Las categorías se muestran con mayúscula inicial para una mejor presentación
        categorias_disponibles = ", ".join([cat.capitalize() for cat in cursos_data.keys()])
        dispatcher.utter_message(text=f"Ofrecemos cursos en las siguientes categorías: {categorias_disponibles}.")
        return []

class ActionConsultarCursosPorCategoria(Action):
    def name(self) -> Text:
        return "action_consultar_cursos_por_categoria"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        categoria = tracker.get_slot("categoria")
        nombre_curso = tracker.get_slot("nombre_curso")

        # Prioriza la búsqueda por nombre de curso si se encuentra
        if nombre_curso:
            nombre_curso_limpio = quitar_acentos(nombre_curso.lower())
            found_courses = []

            # Itera sobre todas las categorías para encontrar coincidencias de cursos
            for cursos_en_categoria in cursos_data.values():
                for nombre_curso_key in cursos_en_categoria.keys():
                    # Comprueba si el nombre del curso del usuario es parte del nombre del curso en la base de datos
                    if nombre_curso_limpio in nombre_curso_key:
                        found_courses.append(nombre_curso_key)
            
            if found_courses:
                nombres_cursos_formateados = [nombre.title() for nombre in found_courses]
                dispatcher.utter_message(text=f"Hemos encontrado los siguientes cursos relacionados con '{nombre_curso.title()}': {', '.join(nombres_cursos_formateados)}.")
            else:
                dispatcher.utter_message(response="utter_no_course_found", nombre_curso=nombre_curso)

        # Si no se encontró un nombre de curso, busca por categoría
        elif categoria:
            # Normalizamos la entrada del usuario: minúsculas y sin acentos
            categoria_limpia = quitar_acentos(categoria.lower())
            
            if categoria_limpia in cursos_data:
                cursos_en_categoria = cursos_data[categoria_limpia]
                nombres_cursos = [nombre.title() for nombre in cursos_en_categoria.keys()]
                dispatcher.utter_message(text=f"En la categoría de {categoria.capitalize()} tenemos los siguientes cursos: {', '.join(nombres_cursos)}.")
            else:
                dispatcher.utter_message(response="utter_no_category_found", categoria=categoria)
        
        # Si no se encontró ni nombre de curso ni categoría, pide la categoría
        else:
            dispatcher.utter_message(response="utter_ask_category_name")
            
        return []

class ActionConsultarPrecioCurso(Action):
    def name(self) -> Text:
        return "action_consultar_precio_curso"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nombre_curso = tracker.get_slot("nombre_curso")
        if nombre_curso:
            nombre_curso_limpio = quitar_acentos(nombre_curso.lower())
            found_price = None

            # Busca el curso en todas las categorías
            for categoria, cursos_en_categoria in cursos_data.items():
                if nombre_curso_limpio in cursos_en_categoria:
                    found_price = cursos_en_categoria[nombre_curso_limpio]["precio"]
                    break # Salir del bucle una vez que se encuentra el curso

            if found_price:
                dispatcher.utter_message(text=f"El curso de {nombre_curso.title()} tiene un precio de {found_price}.")
            else:
                dispatcher.utter_message(response="utter_no_course_found", nombre_curso=nombre_curso)
        else:
            dispatcher.utter_message(response="utter_ask_course_name")
        return []

class ActionConsultarLinkCurso(Action):
    def name(self) -> Text:
        return "action_consultar_link_curso"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nombre_curso = tracker.get_slot("nombre_curso")
        if nombre_curso:
            nombre_curso_limpio = quitar_acentos(nombre_curso.lower())
            found_link = None

            # Busca el curso en todas las categorías
            for categoria, cursos_en_categoria in cursos_data.items():
                if nombre_curso_limpio in cursos_en_categoria:
                    found_link = cursos_en_categoria[nombre_curso_limpio]["link"]
                    break

            if found_link:
                dispatcher.utter_message(text=f"Puedes encontrar más información sobre el curso de {nombre_curso.title()} en este enlace: {found_link}")
            else:
                dispatcher.utter_message(response="utter_no_course_found", nombre_curso=nombre_curso)
        else:
            dispatcher.utter_message(response="utter_ask_course_name")
        return []

class ActionConsultarInfoCurso(Action):
    def name(self) -> Text:
        return "action_consultar_info_curso"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nombre_curso = tracker.get_slot("nombre_curso")
        if nombre_curso:
            nombre_curso_limpio = quitar_acentos(nombre_curso.lower())
            found_course_info = None

            # Busca el curso en todas las categorías
            for categoria, cursos_en_categoria in cursos_data.items():
                if nombre_curso_limpio in cursos_en_categoria:
                    found_course_info = cursos_en_categoria[nombre_curso_limpio]
                    break

            if found_course_info:
                precio = found_course_info["precio"]
                link = found_course_info["link"]
                dispatcher.utter_message(text=f"El curso de {nombre_curso.title()} tiene un precio de {precio} y puedes encontrar más detalles aquí: {link}")
            else:
                dispatcher.utter_message(response="utter_no_course_found", nombre_curso=nombre_curso)
        else:
            dispatcher.utter_message(response="utter_ask_course_name")
        return []
