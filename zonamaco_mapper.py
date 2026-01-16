#!/usr/bin/env python3
"""
ZonaMaco Week Mapper v3.1
-------------------------
Premium light theme - Goldman Sachs inspired (light blues, oranges, clean white)
"""

import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
import json

try:
    import folium
    from folium.plugins import MarkerCluster, AntPath
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run(["pip", "install", "folium"], check=True)
    import folium
    from folium.plugins import MarkerCluster, AntPath


# =============================================================================
# VENUE DATABASE
# =============================================================================
@dataclass
class Venue:
    name: str
    lat: float
    lon: float
    venue_type: str
    neighborhood: str = ""
    address: str = ""


VENUES: Dict[str, Venue] = {
    # MUSEUMS
    "MUSEO JUMEX": Venue("Museo Jumex", 19.4402, -99.2044, "museum", "Polanco", "Miguel de Cervantes Saavedra 303"),
    "MUSEO DE ARTE MODERNO": Venue("Museo de Arte Moderno", 19.4215, -99.1786, "museum", "Chapultepec", "Paseo de la Reforma s/n"),
    "MUSEO DE ARTE CARRILLO GIL": Venue("Museo de Arte Carrillo Gil", 19.3534, -99.1894, "museum", "San Ángel", "Av. Revolución 1608"),
    "MUSEO KALUZ": Venue("Museo Kaluz", 19.4354, -99.1487, "museum", "Centro", "Av. Hidalgo 85"),
    "MUSEO DEL PALACIO DE BELLAS ARTES": Venue("Palacio de Bellas Artes", 19.4352, -99.1412, "museum", "Centro", "Av. Juárez s/n"),
    "MUSEO UNIVERSITARIO DEL CHOPO": Venue("Museo del Chopo", 19.4475, -99.1529, "museum", "Santa María la Ribera", "Dr. Enrique González Martínez 10"),
    "MUSEO DE LA CIUDAD DE MÉXICO": Venue("Museo de la Ciudad de México", 19.4285, -99.1319, "museum", "Centro", "Pino Suárez 30"),
    "MUAC": Venue("MUAC", 19.3183, -99.1867, "museum", "Ciudad Universitaria", "Insurgentes Sur 3000"),
    "SALA DE ARTE PÚBLICO SIQUEIROS": Venue("Sala de Arte Público Siqueiros", 19.4165, -99.1905, "museum", "Polanco", "Tres Picos 29"),

    # GALLERIES
    "LABOR": Venue("Labor", 19.4188, -99.1673, "gallery", "Roma Norte", "Gral. Antonio León 48"),
    "KURIMANZUTTO": Venue("kurimanzutto", 19.4264, -99.1687, "gallery", "San Miguel Chapultepec", "Gob. Rafael Rebollar 94"),
    "OMR": Venue("OMR", 19.4195, -99.1682, "gallery", "Roma Norte", "Córdoba 100"),
    "BODEGA OMR": Venue("Bodega OMR", 19.4142, -99.1635, "gallery", "Roma Sur", "Colima 168"),
    "GALERÍA KAREN HUBER": Venue("Galería Karen Huber", 19.4175, -99.1698, "gallery", "Roma Norte", "Bucareli 120"),
    "GALERÍA ENRIQUE GUERRERO": Venue("Galería Enrique Guerrero", 19.4162, -99.1678, "gallery", "Roma Norte", "Horacio 1549"),
    "GALERÍA DANIELA ELBAHARA": Venue("Galería Daniela Elbahara", 19.4198, -99.1712, "gallery", "Roma Norte", "Zacatecas 93"),
    "ARRÓNIZ": Venue("Arróniz Arte Contemporáneo", 19.4186, -99.1625, "gallery", "Roma Norte", "Plaza Río de Janeiro 53"),
    "TRAVESÍA CUATRO": Venue("Travesía Cuatro", 19.4172, -99.1695, "gallery", "Roma Norte", "Tehuantepec 254"),
    "PROYECTOS MONCLOVA GALLERY": Venue("Proyectos Monclova", 19.4158, -99.1668, "gallery", "Roma Norte", "Colima 55"),
    "MARIANE IBRAHIM": Venue("Mariane Ibrahim", 19.4145, -99.1715, "gallery", "Roma Norte", "Guanajuato 124"),
    "GALERIE NORDENHAKE": Venue("Galerie Nordenhake", 19.4178, -99.1702, "gallery", "Roma Norte", "Tabasco 260"),
    "SAENGER GALERÍA": Venue("Saenger Galería", 19.4189, -99.1658, "gallery", "Roma Norte", "Jalapa 31"),
    "LATINOU": Venue("Latinou", 19.4165, -99.1745, "gallery", "Roma Norte", "Frontera 148"),
    "CAM GALERÍA": Venue("CAM Galería", 19.4195, -99.1725, "gallery", "Roma Norte", "Córdoba 109"),
    "LS / GALERÍA": Venue("LS Galería", 19.4168, -99.1688, "gallery", "Roma Norte", "Tonalá 155"),
    "GALERÍA DE ARTE MEXICANO GAM": Venue("GAM", 19.4235, -99.1752, "gallery", "Juárez", "Gobernador Rafael Rebollar 43"),
    "GALERÍA ANA TEJEDA": Venue("Galería Ana Tejeda", 19.4148, -99.1698, "gallery", "Roma Norte", "Colima 159"),
    "GALERÍA RGR": Venue("Galería RGR", 19.4182, -99.1712, "gallery", "Roma Norte", "Guanajuato 180"),
    "RICARDO REYES": Venue("Ricardo Reyes Galería", 19.4175, -99.1665, "gallery", "Roma Norte", "Mérida 54"),
    "JOVIAN FINE ART": Venue("Jovian Fine Art", 19.4112, -99.1645, "gallery", "Roma Sur", "Insurgentes Sur 398"),
    "ALEJANDRA TOPETE GALLERY": Venue("Alejandra Topete Gallery", 19.4168, -99.1705, "gallery", "Roma Norte", "Colima 180"),
    "ALMANAQUE FOTOGRÁFICA": Venue("Almanaque Fotográfica", 19.4155, -99.1678, "gallery", "Roma Norte", "Jalapa 63"),
    "AMBAR QUIJANO": Venue("Ambar Quijano", 19.4142, -99.1695, "gallery", "Roma Norte", "Colima 234"),
    "SORONDO PROJECTS": Venue("Sorondo Projects", 19.4188, -99.1658, "gallery", "Roma Norte", "Chihuahua 138"),
    "BANDA MUNICIPAL": Venue("Banda Municipal", 19.4165, -99.1742, "gallery", "Roma Norte", "Chiapas 97"),
    "BREUER STUDIO": Venue("Breuer Studio", 19.4178, -99.1715, "gallery", "Roma Norte", "Tabasco 96"),

    # FOUNDATIONS & SPECIAL
    "FUNDACIÓN CASA WABI": Venue("Casa Wabi CDMX", 19.4245, -99.1698, "foundation", "Roma Norte", "Colima 235"),
    "CASA GILARDI": Venue("Casa Gilardi", 19.4312, -99.1925, "special", "San Miguel Chapultepec", "General Antonio León 82"),
    "CASA LAMM": Venue("Casa Lamm", 19.4185, -99.1632, "special", "Roma Norte", "Álvaro Obregón 99"),
    "GEORGINA POUNDS GALLERY EN CASA LAMM": Venue("Georgina Pounds @ Casa Lamm", 19.4185, -99.1632, "gallery", "Roma Norte", "Álvaro Obregón 99"),
    "LAGOALGO": Venue("Lago/Algo", 19.4215, -99.1865, "foundation", "Chapultepec", "Lago Mayor 2da Sección"),
    "PROYECTO H": Venue("Proyecto H", 19.4152, -99.1725, "gallery", "Roma Norte", "Colima 325"),
    "DANIEL OROZCO ESTUDIO": Venue("Daniel Orozco Estudio", 19.4168, -99.1652, "studio", "Roma Norte", "Orizaba 101"),
    "CUERNAVACA3": Venue("Cuernavaca 3", 19.4188, -99.1642, "special", "Roma Norte", "Cuernavaca 3"),
    "TLC ART EDITIONS": Venue("TLC Art Editions", 19.4175, -99.1668, "gallery", "Roma Norte", "Jalapa 125"),
    "NOUVEL": Venue("Nouvel", 19.4198, -99.1702, "gallery", "Roma Norte", "Orizaba 198"),
    "GATHERING": Venue("Gathering", 19.4165, -99.1688, "studio", "Roma Norte", "Durango 262"),
    "TEREZA DIAQUE LA LAGUNA TALLER ÁNFORA \"LA MEJOR\"": Venue("Taller Ánfora", 19.4148, -99.1712, "studio", "Roma Norte", ""),
    "PUG SEAL": Venue("Pug Seal", 19.4195, -99.1685, "hotel", "Roma Norte", "Amsterdam 54"),
    "GALERÍA RODRIGO RIVERO LAKE": Venue("Rodrigo Rivero Lake", 19.4285, -99.1545, "gallery", "Centro", "Campos Elíseos 199"),
    "CENTRO DE ARTE LIMANTOUR": Venue("Centro de Arte Limantour", 19.4235, -99.1668, "gallery", "Juárez", "Río Lerma 35"),

    # HOTELS
    "HOTEL ALEXANDER": Venue("Hotel Alexander", 19.4268, -99.1715, "hotel", "Condesa", "Ámsterdam 141"),
    "HOTEL ALEXANDER X CAM GALERÍA": Venue("Hotel Alexander x CAM", 19.4268, -99.1715, "hotel", "Condesa", "Ámsterdam 141"),
    "HOTEL VOLGA": Venue("Hotel Volga", 19.4245, -99.1695, "hotel", "Roma Norte", "Praga 49"),

    # SATELLITE
    "LA BIBI + REUS": Venue("Hacienda Acamilpa", 18.8775, -99.2458, "special", "Morelos", "Acamilpa, Morelos"),
    "SAENGER GALERÍA EN CASA GILARDI": Venue("Saenger @ Casa Gilardi", 19.4312, -99.1925, "gallery", "San Miguel Chapultepec", ""),
    "SAENGER GALERÍA EN MUSEO DOLORES OLMEDO": Venue("Saenger @ Dolores Olmedo", 19.2685, -99.0975, "gallery", "Xochimilco", "Av. México 5843"),
    "SAENGER GALERÍA EN CENTRO DE ARTE LIMANTOUR": Venue("Saenger @ Limantour", 19.4235, -99.1668, "gallery", "Juárez", ""),
    "MARCHANTE ARTE CONTEMPORÁNEO & PROYECTO H": Venue("Marchante x Proyecto H", 19.4152, -99.1725, "gallery", "Roma Norte", ""),
    "LS / GALERÍA & CASA ABIERTA MONTE": Venue("LS Galería & Casa Abierta", 19.4168, -99.1688, "gallery", "Roma Norte", ""),
    "ARTSYNIGHTS X ZⓈONAMACO": Venue("ArtsyNights Venue", 19.4195, -99.1695, "special", "Roma Norte", ""),
}

VENUE_ICONS = {
    "museum": {"icon": "university", "prefix": "fa", "color": "#1e3a5f", "label": "Museo"},
    "gallery": {"icon": "image", "prefix": "fa", "color": "#4a90d9", "label": "Galería"},
    "hotel": {"icon": "bed", "prefix": "fa", "color": "#2ecc71", "label": "Hotel"},
    "studio": {"icon": "paint-brush", "prefix": "fa", "color": "#e67e22", "label": "Estudio"},
    "foundation": {"icon": "landmark", "prefix": "fa", "color": "#f39c12", "label": "Fundación"},
    "special": {"icon": "star", "prefix": "fa", "color": "#e74c3c", "label": "Especial"},
}

CATEGORY_COLORS = {"Público": "#4a90d9", "Privado": "#e67e22"}

TIME_PERIODS = {
    "morning": {"label": "Mañana", "icon": "☀️", "color": "#f39c12", "range": (0, 12)},
    "afternoon": {"label": "Tarde", "icon": "🌤️", "color": "#e67e22", "range": (12, 18)},
    "evening": {"label": "Noche", "icon": "🌙", "color": "#1e3a5f", "range": (18, 24)},
}

SPANISH_DAYS = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
SPANISH_DAYS_SHORT = {0: "Lun", 1: "Mar", 2: "Mié", 3: "Jue", 4: "Vie", 5: "Sáb", 6: "Dom"}
SPANISH_MONTHS = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                  7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}


@dataclass
class Event:
    date: datetime
    organizer: str
    title: str
    description: str
    category: str
    venue: Optional[Venue] = None

    @property
    def time_period(self) -> str:
        hour = self.date.hour
        for period, info in TIME_PERIODS.items():
            if info["range"][0] <= hour < info["range"][1]:
                return period
        return "evening"

    @property
    def lat(self) -> Optional[float]:
        return self.venue.lat if self.venue else None

    @property
    def lon(self) -> Optional[float]:
        return self.venue.lon if self.venue else None

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "time": self.date.strftime("%H:%M"),
            "organizer": self.organizer,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "neighborhood": self.venue.neighborhood if self.venue else "",
            "venue_type": self.venue.venue_type if self.venue else "special",
            "time_period": self.time_period,
        }


def get_venue(organizer: str) -> Optional[Venue]:
    org_upper = organizer.upper().strip()
    if org_upper in VENUES:
        return VENUES[org_upper]
    for key, venue in VENUES.items():
        if key in org_upper or org_upper in key:
            return venue
    return None


def parse_events() -> List[Event]:
    events_data = [
        # Monday Feb 2
        (datetime(2026, 2, 2, 11, 0), "LABOR", "Inauguración 'A Espessura dos Días' - Eduardo Berliner", "La primera exposición del artista carioca Eduardo Berliner en Labor.", "Público"),
        (datetime(2026, 2, 2, 11, 0), "LA BIBI + REUS", "Almuerzo y experiencia artística en Hacienda Acamilpa", "Almuerzo exclusivo y experiencia artística en el marco de ZonaMaco.", "Privado"),
        (datetime(2026, 2, 2, 17, 0), "LATINOU", "Exposición individual de Chavis Mármol", "Chavis Mármol regresa al color con mezcla de materiales y texturas únicas.", "Privado"),
        (datetime(2026, 2, 2, 18, 0), "BODEGA OMR", "Inauguración 'Dorian Ulises: Mexicano'", "Nueva exposición de Dorian Ulises.", "Público"),

        # Tuesday Feb 3
        (datetime(2026, 2, 3, 10, 0), "GALERIE NORDENHAKE", "Exposición individual de Sarah Crowner", "Exhibición individual de la artista estadounidense Sarah Crowner.", "Privado"),
        (datetime(2026, 2, 3, 10, 0), "FUNDACIÓN CASA WABI", "Mesa de Centro - Cristina Umaña", "Obra nueva de la artista colombiana Cristina Umaña, curada por Andrea Bustillos.", "Privado"),
        (datetime(2026, 2, 3, 10, 0), "FUNDACIÓN CASA WABI", "Cristalización Especular - María Naidich", "Obra nueva de María Naidich en la terraza de Casa Wabi CDMX.", "Privado"),
        (datetime(2026, 2, 3, 10, 0), "ARRÓNIZ", "Inauguración: Madeline Jiménez, Ria Bosman, Karlo Andrei Ibarra", "Tres exposiciones simultáneas de artistas internacionales.", "Público"),
        (datetime(2026, 2, 3, 10, 0), "FUNDACIÓN CASA WABI", "Sísifo Dichoso - Bosco Sodi", "La obra de Bosco Sodi habita el esfuerzo eterno del mito de Sísifo.", "Privado"),
        (datetime(2026, 2, 3, 10, 0), "GATHERING", "Visita privada al estudio de Stefan Brüggemann", "Acceso exclusivo al espacio de trabajo del artista.", "Privado"),
        (datetime(2026, 2, 3, 10, 0), "SAENGER GALERÍA", "Visita guiada: Gregor Hildebrandt en Casa Gilardi", "La arquitectura de Barragán en diálogo con la obra de Hildebrandt.", "Privado"),
        (datetime(2026, 2, 3, 11, 0), "BANDA MUNICIPAL", "Inauguración 'Sol Nocturno' - Renata Cassiano Álvarez", "Últimas obras de la artista mexicana.", "Público"),
        (datetime(2026, 2, 3, 11, 0), "SAENGER GALERÍA", "Visita guiada: Yoab Vera y Diego Rivera", "Paisajes marinos y las puestas de sol en Acapulco.", "Privado"),
        (datetime(2026, 2, 3, 11, 0), "ALEJANDRA TOPETE GALLERY", "Performance callejero de Randy Shull", "Performance para inaugurar 'I Have Never Worn a Watch'.", "Público"),
        (datetime(2026, 2, 3, 11, 0), "SORONDO PROJECTS", "Sorondo x Adhesivo", "Dos galerías fundadas por mujeres venezolanas se unen.", "Público"),
        (datetime(2026, 2, 3, 12, 0), "FUNDACIÓN CASA WABI", "Mesa de Centro (horario público)", "Exposición abierta al público.", "Público"),
        (datetime(2026, 2, 3, 12, 0), "FUNDACIÓN CASA WABI", "Cristalización Especular (horario público)", "Exposición abierta al público.", "Público"),
        (datetime(2026, 2, 3, 12, 0), "TRAVESÍA CUATRO", "Inauguración: Tania Pérez Córdova", "Exposición individual de la artista.", "Privado"),
        (datetime(2026, 2, 3, 12, 0), "MARIANE IBRAHIM", "Exposición individual de Carmen Neely", "Primera presentación en México de Carmen Neely.", "Público"),
        (datetime(2026, 2, 3, 12, 0), "ALEJANDRA TOPETE GALLERY", "'I Have Never Worn a Watch' - Randy Shull", "Exposición del artista estadounidense.", "Público"),
        (datetime(2026, 2, 3, 12, 10), "FUNDACIÓN CASA WABI", "Sísifo Dichoso (horario público)", "Exposición abierta al público.", "Público"),
        (datetime(2026, 2, 3, 16, 0), "GEORGINA POUNDS GALLERY EN CASA LAMM", "'Paraíso de Monstruos' - Vanessa Raw", "Pinturas de la artista en Casa Lamm.", "Privado"),
        (datetime(2026, 2, 3, 16, 0), "PROYECTOS MONCLOVA GALLERY", "Inauguración: Macaparana, Juan Parada, Gabriel Garcilazo", "Exposición colectiva.", "Público"),
        (datetime(2026, 2, 3, 17, 0), "ALMANAQUE FOTOGRÁFICA", "'Madre Tierra' - Exposición colectiva", "Fotografía contemporánea de artistas destacados.", "Público"),
        (datetime(2026, 2, 3, 17, 0), "TEREZA DIAQUE LA LAGUNA TALLER ÁNFORA \"LA MEJOR\"", "Presentación de Krytzia Dabdoub", "Presentación de la artista.", "Público"),
        (datetime(2026, 2, 3, 17, 0), "GALERÍA DE ARTE MEXICANO GAM", "'Extreme Words' - Stefan Brüggemann", "Nueva exposición del artista conceptual.", "Público"),
        (datetime(2026, 2, 3, 17, 0), "CUERNAVACA3", "Inauguración de Cuernavaca3", "Nueva fundación del coleccionista Jeff Magid.", "Privado"),
        (datetime(2026, 2, 3, 18, 0), "PROYECTO H", "Inauguración: Pablo Armesto, Patrick Hughes, José Romussi", "Tres exposiciones y residencia artística.", "Privado"),
        (datetime(2026, 2, 3, 18, 0), "GALERIE NORDENHAKE", "'Loose Geometries' - Selección de Sarah Crowner", "Obras históricas curadas por la artista.", "Privado"),
        (datetime(2026, 2, 3, 18, 0), "KURIMANZUTTO", "Preview: Oscar Murillo 'El Pozo de Agua'", "Adelanto de la nueva exposición.", "Público"),
        (datetime(2026, 2, 3, 18, 0), "GALERÍA KAREN HUBER", "'Goodbye Ebony Horse' - Ian Grose + 'Rise and Shine'", "Dos exposiciones simultáneas.", "Público"),
        (datetime(2026, 2, 3, 18, 0), "GALERÍA DANIELA ELBAHARA", "Exposición individual de Hugo Robledo", "Pinturas y cerámicas entre lo físico y lo mental.", "Público"),
        (datetime(2026, 2, 3, 18, 0), "GALERÍA ENRIQUE GUERRERO", "'Néctar' - Fernanda Caballero", "Segunda exposición personal de la artista.", "Público"),
        (datetime(2026, 2, 3, 18, 0), "DANIEL OROZCO ESTUDIO", "Subasta benéfica para LADLE", "Piezas intervenidas por diversos artistas.", "Privado"),
        (datetime(2026, 2, 3, 18, 0), "PUG SEAL", "Subasta de arte curada", "Piezas selectas en torno a los hoteles Pug Seal.", "Público"),
        (datetime(2026, 2, 3, 18, 0), "OMR", "Inauguración: Marcel Dzama y Leonora Carrington", "Diálogo entre dos universos artísticos.", "Público"),
        (datetime(2026, 2, 3, 18, 0), "GALERÍA RGR", "Inauguración: Roberto Matta", "Primera vez de la obra de Matta en RGR.", "Público"),
        (datetime(2026, 2, 3, 19, 0), "RICARDO REYES", "'Serenísimo Pop' - Salustiano", "Pintura y obras en papel del artista sevillano.", "Público"),
        (datetime(2026, 2, 3, 19, 0), "HOTEL ALEXANDER X CAM GALERÍA", "Pop-up Alejandra España en Caviar Bar", "Exhibición activa toda la semana.", "Privado"),
        (datetime(2026, 2, 3, 20, 30), "GALERIE NORDENHAKE", "Cena de inauguración 'Loose Geometries'", "Cena exclusiva para coleccionistas.", "Privado"),

        # Wednesday Feb 4
        (datetime(2026, 2, 4, 19, 0), "LS / GALERÍA", "'Echoes of the Unseen' - Carrington, Lempicka, Costa, Carrillo", "Creadoras que transformaron el arte.", "Privado"),
        (datetime(2026, 2, 4, 19, 0), "HOTEL VOLGA", "Cóctel de kickoff ZonaMaco", "Inicio oficial de la semana en Hotel Volga.", "Público"),
        (datetime(2026, 2, 4, 19, 30), "TLC ART EDITIONS", "TLC Art Editions en Artemis Project", "Graciela Iturbide, Jan Hendrix y más.", "Público"),
        (datetime(2026, 2, 4, 19, 30), "CAM GALERÍA", "'Túnel y Vislumbre' - Alejandra España", "Obra inédita curada por Charles Moore.", "Privado"),
        (datetime(2026, 2, 4, 20, 0), "MUSEO DE ARTE MODERNO", "Pre-inauguración: Rafael Lozano-Hemmer 'Jardín Inconcluso'", "Paseo nocturno por la instalación.", "Privado"),

        # Thursday Feb 5
        (datetime(2026, 2, 5, 9, 30), "LATINOU", "Visita al estudio de Chavis Mármol + desayuno", "Recorrido exclusivo para coleccionistas.", "Privado"),
        (datetime(2026, 2, 5, 10, 0), "MUSEO JUMEX", "Recorridos guiados + firma: Gabriel de la Mora", "Presentación del catálogo 'La Petite Mort'.", "Privado"),
        (datetime(2026, 2, 5, 10, 0), "DANIEL OROZCO ESTUDIO", "Showroom abierto al público", "Visita al showroom del estudio.", "Público"),
        (datetime(2026, 2, 5, 10, 0), "SAENGER GALERÍA EN CASA GILARDI", "Visita guiada: Gregor Hildebrandt", "La música como silencio y materia.", "Privado"),
        (datetime(2026, 2, 5, 10, 0), "GALERIE NORDENHAKE", "Exposición: Sarah Crowner", "Exhibición individual de la artista.", "Privado"),
        (datetime(2026, 2, 5, 10, 0), "SAENGER GALERÍA", "Visita al estudio de Robert Janitz", "Nómada entre NY y CDMX.", "Privado"),
        (datetime(2026, 2, 5, 10, 30), "AMBAR QUIJANO", "Visita al estudio de Mariana Paniagua", "Trayectoria sólida y presencia institucional.", "Privado"),
        (datetime(2026, 2, 5, 11, 0), "SAENGER GALERÍA EN MUSEO DOLORES OLMEDO", "Visitas guiadas: Yoab Vera y Diego Rivera", "Paisajes y puestas de sol.", "Privado"),
        (datetime(2026, 2, 5, 11, 0), "SALA DE ARTE PÚBLICO SIQUEIROS", "'Fusiones' + performance Valentina Díaz", "El legado de Siqueiros explorado.", "Público"),
        (datetime(2026, 2, 5, 12, 0), "GALERÍA RODRIGO RIVERO LAKE", "Visita guiada: colección privada", "Elementos arquitectónicos de la época virreinal.", "Privado"),
        (datetime(2026, 2, 5, 12, 0), "MUSEO DEL PALACIO DE BELLAS ARTES", "'Colosos' - Intervención de Diego Vega", "Coreografía del laboratorio Cuerpos Arquitectos.", "Público"),
        (datetime(2026, 2, 5, 18, 0), "PUG SEAL", "Cóctel + performance para expositores EJES", "Arts, drinks and fun.", "Privado"),
        (datetime(2026, 2, 5, 19, 0), "LS / GALERÍA", "Cena 25 aniversario", "Un cuarto de siglo dedicado al arte.", "Privado"),
        (datetime(2026, 2, 5, 19, 0), "MUSEO DE ARTE MODERNO", "'Pánico en el Interior Externo' - Conversación", "Con Lozano-Hemmer, Medina, Szántó.", "Privado"),
        (datetime(2026, 2, 5, 19, 0), "MUSEO UNIVERSITARIO DEL CHOPO", "'San Pedro - Carrera de Patos' - Elyla", "Monólogo teatral con música en vivo.", "Privado"),
        (datetime(2026, 2, 5, 19, 30), "GALERÍA ANA TEJEDA", "Recorrido curatorial: Karen Cordero Reiman", "Exposición colectiva de artistas.", "Público"),
        (datetime(2026, 2, 5, 19, 30), "HOTEL ALEXANDER", "Pop-up: Marcos Cojab", "Esculturas y gráficas con humor y simbolismo.", "Público"),
        (datetime(2026, 2, 5, 20, 0), "JOVIAN FINE ART", "'Umbrales' - Nicolás Beltrán y Kevin Artavia", "Inauguración de Roma Sur, Proyectos Curatoriales.", "Público"),
        (datetime(2026, 2, 5, 20, 0), "ALMANAQUE FOTOGRÁFICA", "Cóctel 10 aniversario - Madre Tierra", "Celebración de una década de fotografía.", "Privado"),

        # Friday Feb 6
        (datetime(2026, 2, 6, 9, 30), "MUSEO DE ARTE CARRILLO GIL", "Brunch MACG + recorridos", "Gerzso, Botánica de Asfalto, y más.", "Privado"),
        (datetime(2026, 2, 6, 9, 30), "LATINOU", "Visita al estudio de Raúl Cordero", "Visión íntima del proceso creativo.", "Privado"),
        (datetime(2026, 2, 6, 10, 0), "LAGOALGO", "'Alucinaciones' + 'Rafa Esparza: Juntxs'", "Trevor Paglen, Troika y Rafa Esparza.", "Público"),
        (datetime(2026, 2, 6, 10, 0), "SAENGER GALERÍA", "Visita guiada: Gregor Hildebrandt", "Repetición de módulos, lleno y vacío.", "Privado"),
        (datetime(2026, 2, 6, 10, 0), "AMBAR QUIJANO", "Visita al estudio de Andrea Bores", "Diálogo íntimo con los materiales.", "Privado"),
        (datetime(2026, 2, 6, 10, 0), "SAENGER GALERÍA", "Visita al estudio de Yoab Vera", "Casa familiar convertida en estudio.", "Privado"),
        (datetime(2026, 2, 6, 11, 0), "MARCHANTE ARTE CONTEMPORÁNEO & PROYECTO H", "Visita al estudio de Román de Castro", "Espacio de creación del artista.", "Privado"),
        (datetime(2026, 2, 6, 11, 0), "LS / GALERÍA & CASA ABIERTA MONTE", "Diálogo: Coen, Tzucumo, Candiani, Rojo", "Arte y arquitectura en conversación.", "Privado"),
        (datetime(2026, 2, 6, 11, 0), "MUAC", "Brunch + preview: 'Los Grupos' y Néstor Jiménez", "Exposiciones próximas a inaugurar.", "Privado"),
        (datetime(2026, 2, 6, 11, 0), "GALERÍA KAREN HUBER", "Visita al estudio de César Rangel Ramos", "Imágenes perfeccionadas por años.", "Privado"),
        (datetime(2026, 2, 6, 11, 0), "SAENGER GALERÍA", "Visitas guiadas: Yoab Vera y Diego Rivera", "Paisajes marinos y jardines.", "Privado"),
        (datetime(2026, 2, 6, 11, 45), "AMBAR QUIJANO", "Visita al estudio de Juana Subercaseaux", "Pintora chilena radicada en CDMX.", "Privado"),
        (datetime(2026, 2, 6, 12, 0), "MUSEO DEL PALACIO DE BELLAS ARTES", "'Colosos' - Intervención coreográfica", "Cuerpos Arquitectos en acción.", "Público"),
        (datetime(2026, 2, 6, 13, 0), "ARRÓNIZ", "Open House: Mauro Giaconi 'Temporal Ventaja'", "Tour por Obrera Centro.", "Público"),
        (datetime(2026, 2, 6, 19, 0), "AMBAR QUIJANO", "Cóctel + activación: Mariana Garibay Raeke", "Diálogo con Manuela Riestra.", "Público"),
        (datetime(2026, 2, 6, 19, 0), "BREUER STUDIO", "Inauguración: artistas nacionales e internacionales", "Diseño con precisión y conciencia.", "Público"),
        (datetime(2026, 2, 6, 19, 0), "MUSEO DE ARTE MODERNO", "Eli Keszler activa 'Jardín Inconcluso'", "Performances, poesía y coreografía.", "Privado"),
        (datetime(2026, 2, 6, 19, 0), "NOUVEL", "Glass Reflections Cocktail", "Primera vez en México, con Ciento.", "Privado"),
        (datetime(2026, 2, 6, 20, 0), "MUSEO KALUZ", "Cóctel + recorrido: 'El Jardín de Velasco'", "Hendrix, Lagarde, Cabrera Rubio, Guzik, Glassford.", "Privado"),

        # Saturday Feb 7
        (datetime(2026, 2, 7, 10, 0), "LS / GALERÍA", "'Memoria en Construcción' - Arnaldo Coen", "Procesos y capas del universo creativo.", "Privado"),
        (datetime(2026, 2, 7, 10, 0), "ARRÓNIZ", "Desayuno + estudios: Giaconi y Castro", "Tour por Obrera Centro.", "Privado"),
        (datetime(2026, 2, 7, 10, 0), "SAENGER GALERÍA", "Visita guiada: Gregor Hildebrandt en Casa Gilardi", "Arquitectura, luz y sombra.", "Privado"),
        (datetime(2026, 2, 7, 10, 0), "NOUVEL", "Glass Reflections Open House", "Exhibición abierta al público.", "Público"),
        (datetime(2026, 2, 7, 11, 0), "ALEJANDRA TOPETE GALLERY", "Conversatorio: Lucía Lundt y Rafael Lozano-Hemmer", "Topografías de lo Invisible.", "Público"),
        (datetime(2026, 2, 7, 11, 0), "SAENGER GALERÍA", "Visitas guiadas: Yoab Vera y Diego Rivera", "Paisajes erosionados y otros tiempos.", "Privado"),
        (datetime(2026, 2, 7, 11, 0), "SAENGER GALERÍA EN CENTRO DE ARTE LIMANTOUR", "'Ebriedad Geométrica' - Visita guiada", "Con curadores y artistas.", "Privado"),
        (datetime(2026, 2, 7, 11, 30), "PROYECTO H", "Visita al estudio de Pablo de Laborde Lascaris", "Escultor mexicano.", "Privado"),
        (datetime(2026, 2, 7, 11, 30), "AMBAR QUIJANO", "Visita al estudio de Meryl Yana", "Nacida en París, radicada en San Miguel Chapultepec.", "Privado"),
        (datetime(2026, 2, 7, 12, 0), "MARIANE IBRAHIM", "Charla + libro: Carmen Neely", "Conversación con la artista.", "Público"),
        (datetime(2026, 2, 7, 12, 0), "MUSEO DEL PALACIO DE BELLAS ARTES", "'Colosos' - Recorrido coreográfico", "Diego Vega y Cuerpos Arquitectos.", "Privado"),
        (datetime(2026, 2, 7, 12, 0), "KURIMANZUTTO", "Future Dialogues: Oscar Murillo & Magali Arriola", "Lanzamiento del libro 'El Pozo de Agua'.", "Público"),
        (datetime(2026, 2, 7, 19, 0), "ARTSYNIGHTS X ZⓈONAMACO", "Abracadabra con Blond:ish", "Fiesta de cierre.", "Público"),

        # Sunday Feb 8
        (datetime(2026, 2, 8, 10, 0), "SAENGER GALERÍA", "Visita guiada: Gregor Hildebrandt en Casa Gilardi", "Última oportunidad de la semana.", "Privado"),
        (datetime(2026, 2, 8, 10, 0), "MUSEO DE LA CIUDAD DE MÉXICO", "'Columna Rota' - Visita guiada", "Exploración artística con organizadores.", "Privado"),
        (datetime(2026, 2, 8, 11, 0), "SAENGER GALERÍA", "Visitas guiadas: Yoab Vera y Diego Rivera", "Cierre de la semana.", "Privado"),
    ]

    events = []
    for dt, org, title, desc, cat in events_data:
        venue = get_venue(org)
        events.append(Event(date=dt, organizer=org, title=title, description=desc, category=cat, venue=venue))
    return events


def create_popup_html(event: Event) -> str:
    cat_color = CATEGORY_COLORS.get(event.category, "#666")
    neighborhood = event.venue.neighborhood if event.venue else ""
    address = event.venue.address if event.venue else ""

    return f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 320px; padding: 5px;">
        <div style="border-left: 4px solid {cat_color}; padding-left: 12px; margin-bottom: 12px;">
            <h3 style="margin: 0 0 8px 0; font-size: 15px; color: #1e3a5f; line-height: 1.3;">{event.title}</h3>
            <div style="font-size: 13px; color: #555; margin-bottom: 4px;"><strong>{event.organizer}</strong></div>
        </div>
        <div style="display: flex; gap: 15px; margin-bottom: 10px; font-size: 12px;">
            <div style="background: #f0f4f8; padding: 6px 10px; border-radius: 4px;"><strong>⏰</strong> {event.date.strftime('%H:%M')}</div>
            <div style="background: {cat_color}15; color: {cat_color}; padding: 6px 10px; border-radius: 4px; font-weight: 600;">{event.category}</div>
        </div>
        <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
            <div><strong>📍</strong> {neighborhood}</div>
            {'<div style="margin-left: 18px;">' + address + '</div>' if address else ''}
        </div>
        <div style="font-size: 12px; color: #444; line-height: 1.5; border-top: 1px solid #e8ecf0; padding-top: 10px; margin-top: 8px;">
            {event.description[:200] + '...' if len(event.description) > 200 else event.description}
        </div>
    </div>
    """


def create_timeline_html(events: List[Event], day_date: datetime) -> str:
    day_name = SPANISH_DAYS[day_date.weekday()]
    morning = sorted([e for e in events if e.time_period == "morning"], key=lambda x: x.date)
    afternoon = sorted([e for e in events if e.time_period == "afternoon"], key=lambda x: x.date)
    evening = sorted([e for e in events if e.time_period == "evening"], key=lambda x: x.date)

    def event_item(e: Event) -> str:
        cat_color = CATEGORY_COLORS.get(e.category, "#666")
        return f"""<div style="padding: 8px 10px; margin: 4px 0; background: white; border-radius: 6px; border-left: 3px solid {cat_color}; font-size: 11px; cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.08);" onclick="map.setView([{e.lat}, {e.lon}], 16)"><div style="font-weight: 600; color: #1e3a5f;">{e.date.strftime('%H:%M')}</div><div style="color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{e.organizer}</div></div>"""

    def period_section(title: str, events_list: List[Event], color: str) -> str:
        if not events_list:
            return ""
        items = "".join(event_item(e) for e in events_list)
        return f"""<div style="margin-bottom: 15px;"><div style="font-size: 11px; font-weight: 700; color: {color}; margin-bottom: 6px; padding: 4px 8px; background: {color}15; border-radius: 4px;">{title} ({len(events_list)})</div>{items}</div>"""

    return f"""<div style="position: fixed; top: 10px; right: 10px; width: 220px; max-height: 90vh; background: #f8fafc; border-radius: 12px; padding: 15px; z-index: 1000; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow-y: auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; border: 1px solid #e2e8f0;"><div style="text-align: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e2e8f0;"><div style="font-size: 18px; font-weight: 700; color: #1e3a5f;">{day_name}</div><div style="font-size: 12px; color: #64748b;">{day_date.day} de {SPANISH_MONTHS[day_date.month]}</div><div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">{len(events)} eventos</div></div>{period_section("☀️ Mañana", morning, "#f39c12")}{period_section("🌤️ Tarde", afternoon, "#e67e22")}{period_section("🌙 Noche", evening, "#1e3a5f")}</div>"""


def create_day_map(events: List[Event], day_date: datetime, output_path: str) -> int:
    mappable = [e for e in events if e.lat and e.lon]
    if not mappable:
        return 0

    center_lat = sum(e.lat for e in mappable) / len(mappable)
    center_lon = sum(e.lon for e in mappable) / len(mappable)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles=None, control_scale=True)
    folium.TileLayer('cartodbpositron', name='Claro').add_to(m)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)

    fg_publico = folium.FeatureGroup(name='🔵 Público', show=True)
    fg_privado = folium.FeatureGroup(name='🟠 Privado', show=True)

    sorted_events = sorted(mappable, key=lambda x: x.date)

    for event in sorted_events:
        venue_type = event.venue.venue_type if event.venue else "special"
        icon_info = VENUE_ICONS.get(venue_type, VENUE_ICONS["special"])
        popup = folium.Popup(create_popup_html(event), max_width=350)

        marker = folium.Marker(
            location=[event.lat, event.lon],
            popup=popup,
            tooltip=f"<b>{event.date.strftime('%H:%M')}</b> - {event.organizer}",
            icon=folium.Icon(color='orange' if event.category == 'Privado' else 'blue', icon=icon_info["icon"], prefix=icon_info["prefix"])
        )

        if event.category == "Público":
            marker.add_to(fg_publico)
        else:
            marker.add_to(fg_privado)

    if len(sorted_events) >= 2:
        route_coords = [[e.lat, e.lon] for e in sorted_events]
        AntPath(locations=route_coords, color="#4a90d9", weight=3, opacity=0.7, dash_array=[10, 20], delay=1000, pulse_color="#fff").add_to(folium.FeatureGroup(name='📍 Ruta sugerida', show=False).add_to(m))

    fg_publico.add_to(m)
    fg_privado.add_to(m)

    folium.LayerControl(collapsed=False, position='topleft').add_to(m)
    m.get_root().html.add_child(folium.Element(create_timeline_html(mappable, day_date)))

    legend_html = """<div style="position: fixed; bottom: 30px; left: 10px; z-index: 1000; background: white; padding: 12px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); font-family: -apple-system, sans-serif; font-size: 11px; border: 1px solid #e2e8f0;"><div style="font-weight: 700; margin-bottom: 8px; color: #1e3a5f;">Leyenda</div><div style="margin: 4px 0;"><span style="color: #4a90d9;">●</span> Público</div><div style="margin: 4px 0;"><span style="color: #e67e22;">●</span> Privado</div><div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e2e8f0;"><div><i class="fa fa-university"></i> Museo</div><div><i class="fa fa-image"></i> Galería</div><div><i class="fa fa-bed"></i> Hotel</div><div><i class="fa fa-paint-brush"></i> Estudio</div></div></div>"""
    m.get_root().html.add_child(folium.Element(legend_html))
    m.get_root().header.add_child(folium.Element('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"/>'))

    m.save(output_path)
    return len(mappable)


def create_premium_index(days_info: List[dict], all_events: List[Event], output_dir: str):
    """Create a clean, light Goldman-style index page."""

    total_publico = sum(1 for e in all_events if e.category == "Público")
    total_privado = sum(1 for e in all_events if e.category == "Privado")
    total_venues = len(set(e.organizer for e in all_events))

    venue_counts = {}
    for e in all_events:
        vt = e.venue.venue_type if e.venue else "special"
        venue_counts[vt] = venue_counts.get(vt, 0) + 1

    events_json = json.dumps([e.to_dict() for e in all_events], ensure_ascii=False)

    day_cards_html = ""
    for day in days_info:
        day_cards_html += f"""
            <div class="day-card" data-day="{day['dow']}" data-filename="{day['filename']}">
                <div class="day-card-header">
                    <div class="day-number">{day['day_num']}</div>
                    <div class="day-info">
                        <div class="day-name">{day['day_name']}</div>
                        <div class="day-month">Febrero 2026</div>
                    </div>
                </div>
                <div class="day-card-stats">
                    <div class="stat-pill total">{day['count']} eventos</div>
                    <div class="stat-pill publico">{day['publico']} públicos</div>
                    <div class="stat-pill privado">{day['privado']} privados</div>
                </div>
                <div class="day-card-preview" id="preview-{day['dow']}"></div>
                <a href="{day['filename']}" class="day-card-link">
                    Ver mapa interactivo
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                </a>
            </div>
        """

    venue_badges_html = ""
    for vt, info in VENUE_ICONS.items():
        count = venue_counts.get(vt, 0)
        if count > 0:
            venue_badges_html += f"""
                <div class="venue-badge">
                    <i class="fa fa-{info['icon']}" style="color: {info['color']};"></i>
                    <span class="venue-count">{count}</span>
                    <span class="venue-label">{info['label']}</span>
                </div>
            """

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ZonaMaco 2026 | Programa VIP</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --white: #ffffff;
            --bg-light: #f8fafc;
            --bg-card: #ffffff;
            --border: #e2e8f0;
            --border-hover: #cbd5e1;
            --text-dark: #0f172a;
            --text-primary: #1e3a5f;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
            --blue-primary: #4a90d9;
            --blue-light: #e8f4fd;
            --blue-dark: #1e3a5f;
            --orange-primary: #e67e22;
            --orange-light: #fef3e8;
            --gold: #d4a012;
            --gold-light: #fefce8;
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
            --shadow-lg: 0 10px 40px rgba(0,0,0,0.1);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-light);
            color: var(--text-dark);
            line-height: 1.6;
        }}

        /* Header */
        .header {{
            background: var(--white);
            border-bottom: 1px solid var(--border);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .logo-text {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }}

        .logo-badge {{
            background: linear-gradient(135deg, var(--blue-primary), var(--orange-primary));
            color: white;
            font-size: 10px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .header-date {{
            font-size: 14px;
            color: var(--text-secondary);
        }}

        /* Container */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 24px;
        }}

        /* Hero */
        .hero {{
            text-align: center;
            padding: 60px 0;
            background: linear-gradient(180deg, var(--white) 0%, var(--bg-light) 100%);
            margin: -40px -24px 40px;
            padding: 60px 24px;
        }}

        .hero h1 {{
            font-size: clamp(2.5rem, 6vw, 4rem);
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.03em;
            margin-bottom: 12px;
        }}

        .hero h1 span {{
            background: linear-gradient(135deg, var(--blue-primary), var(--orange-primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero-subtitle {{
            font-size: 1.125rem;
            color: var(--text-secondary);
            margin-bottom: 40px;
        }}

        /* Stats */
        .stats-row {{
            display: flex;
            justify-content: center;
            gap: 48px;
            margin-bottom: 32px;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-value {{
            font-size: 3rem;
            font-weight: 700;
            line-height: 1;
            margin-bottom: 4px;
        }}

        .stat-value.blue {{ color: var(--blue-primary); }}
        .stat-value.orange {{ color: var(--orange-primary); }}
        .stat-value.navy {{ color: var(--blue-dark); }}

        .stat-label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 500;
        }}

        /* Category Pills */
        .category-pills {{
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-bottom: 32px;
        }}

        .category-pill {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 100px;
            font-size: 14px;
            font-weight: 500;
        }}

        .category-pill.publico {{
            background: var(--blue-light);
            color: var(--blue-primary);
        }}

        .category-pill.privado {{
            background: var(--orange-light);
            color: var(--orange-primary);
        }}

        .category-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}

        .category-dot.blue {{ background: var(--blue-primary); }}
        .category-dot.orange {{ background: var(--orange-primary); }}

        /* Venue Badges */
        .venue-badges {{
            display: flex;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .venue-badge {{
            display: flex;
            align-items: center;
            gap: 6px;
            background: var(--white);
            border: 1px solid var(--border);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 12px;
            transition: all 0.2s ease;
        }}

        .venue-badge:hover {{
            border-color: var(--border-hover);
            box-shadow: var(--shadow-sm);
        }}

        .venue-badge i {{ font-size: 12px; }}
        .venue-count {{ font-weight: 600; color: var(--text-dark); }}
        .venue-label {{ color: var(--text-secondary); }}

        /* Search */
        .search-section {{
            max-width: 600px;
            margin: 0 auto 32px;
        }}

        .search-container {{
            position: relative;
        }}

        .search-input {{
            width: 100%;
            padding: 14px 16px 14px 48px;
            background: var(--white);
            border: 1px solid var(--border);
            border-radius: 12px;
            font-size: 15px;
            color: var(--text-dark);
            outline: none;
            transition: all 0.2s ease;
        }}

        .search-input::placeholder {{ color: var(--text-muted); }}

        .search-input:focus {{
            border-color: var(--blue-primary);
            box-shadow: 0 0 0 3px var(--blue-light);
        }}

        .search-icon {{
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
        }}

        /* Filter Tabs */
        .filter-tabs {{
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }}

        .filter-tab {{
            padding: 10px 18px;
            background: var(--white);
            border: 1px solid var(--border);
            border-radius: 100px;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .filter-tab:hover {{
            border-color: var(--border-hover);
            color: var(--text-dark);
        }}

        .filter-tab.active {{
            background: var(--blue-primary);
            border-color: var(--blue-primary);
            color: white;
        }}

        /* Days Grid */
        .days-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 24px;
        }}

        .day-card {{
            background: var(--white);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s ease;
        }}

        .day-card:hover {{
            border-color: var(--blue-primary);
            box-shadow: var(--shadow-lg);
            transform: translateY(-4px);
        }}

        .day-card-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
        }}

        .day-number {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--blue-primary);
            line-height: 1;
            min-width: 60px;
        }}

        .day-info {{ flex: 1; }}

        .day-name {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-dark);
        }}

        .day-month {{
            font-size: 13px;
            color: var(--text-muted);
        }}

        .day-card-stats {{
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}

        .stat-pill {{
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
        }}

        .stat-pill.total {{
            background: var(--bg-light);
            color: var(--text-secondary);
        }}

        .stat-pill.publico {{
            background: var(--blue-light);
            color: var(--blue-primary);
        }}

        .stat-pill.privado {{
            background: var(--orange-light);
            color: var(--orange-primary);
        }}

        .day-card-preview {{
            background: var(--bg-light);
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 16px;
            max-height: 160px;
            overflow-y: auto;
        }}

        .preview-event {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px;
            background: var(--white);
            border-radius: 6px;
            margin-bottom: 6px;
            border-left: 3px solid transparent;
        }}

        .preview-event:last-child {{ margin-bottom: 0; }}

        .preview-event.publico {{ border-left-color: var(--blue-primary); }}
        .preview-event.privado {{ border-left-color: var(--orange-primary); }}

        .preview-time {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-primary);
            min-width: 45px;
        }}

        .preview-title {{
            font-size: 12px;
            color: var(--text-secondary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .day-card-link {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 14px;
            background: var(--blue-primary);
            border-radius: 10px;
            color: white;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.2s ease;
        }}

        .day-card-link:hover {{
            background: var(--blue-dark);
            transform: scale(1.02);
        }}

        /* Footer */
        footer {{
            text-align: center;
            padding: 48px 24px;
            border-top: 1px solid var(--border);
            margin-top: 60px;
            background: var(--white);
        }}

        .footer-text {{
            color: var(--text-muted);
            font-size: 14px;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .stats-row {{ gap: 24px; }}
            .stat-value {{ font-size: 2rem; }}
            .days-grid {{ grid-template-columns: 1fr; }}
            .header-date {{ display: none; }}
        }}

        /* Scrollbar */
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-light); }}
        ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <span class="logo-text">ZonaMaco</span>
                <span class="logo-badge">VIP 2026</span>
            </div>
            <div class="header-date">2 - 8 de Febrero, Ciudad de México</div>
        </div>
    </header>

    <div class="container">
        <section class="hero">
            <h1>Programa <span>VIP</span></h1>
            <p class="hero-subtitle">99 eventos exclusivos en 7 días de arte contemporáneo</p>

            <div class="stats-row">
                <div class="stat-item">
                    <div class="stat-value navy">{len(all_events)}</div>
                    <div class="stat-label">Eventos</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value blue">{total_venues}</div>
                    <div class="stat-label">Venues</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value orange">7</div>
                    <div class="stat-label">Días</div>
                </div>
            </div>

            <div class="category-pills">
                <div class="category-pill publico">
                    <span class="category-dot blue"></span>
                    <strong>{total_publico}</strong> Eventos Públicos
                </div>
                <div class="category-pill privado">
                    <span class="category-dot orange"></span>
                    <strong>{total_privado}</strong> Eventos Privados
                </div>
            </div>

            <div class="venue-badges">
                {venue_badges_html}
            </div>
        </section>

        <div class="search-section">
            <div class="search-container">
                <i class="fas fa-search search-icon"></i>
                <input type="text" class="search-input" id="searchInput" placeholder="Buscar evento, galería o artista...">
            </div>
        </div>

        <div class="filter-tabs">
            <button class="filter-tab active" data-filter="all">Todos</button>
            <button class="filter-tab" data-filter="publico">Públicos</button>
            <button class="filter-tab" data-filter="privado">Privados</button>
            <button class="filter-tab" data-filter="morning">☀️ Mañana</button>
            <button class="filter-tab" data-filter="afternoon">🌤️ Tarde</button>
            <button class="filter-tab" data-filter="evening">🌙 Noche</button>
        </div>

        <div class="days-grid">
            {day_cards_html}
        </div>
    </div>

    <footer>
        <p class="footer-text">ZonaMaco 2026 • Mapas interactivos del programa VIP</p>
    </footer>

    <script>
        const events = {events_json};

        const eventsByDay = {{}};
        events.forEach(e => {{
            const day = new Date(e.date).getDay();
            const dayIndex = day === 0 ? 6 : day - 1;
            if (!eventsByDay[dayIndex]) eventsByDay[dayIndex] = [];
            eventsByDay[dayIndex].push(e);
        }});

        document.querySelectorAll('.day-card').forEach(card => {{
            const dow = parseInt(card.dataset.day);
            const preview = card.querySelector('.day-card-preview');
            const dayEvents = eventsByDay[dow] || [];

            const html = dayEvents.slice(0, 4).map(e => `
                <div class="preview-event ${{e.category.toLowerCase()}}">
                    <span class="preview-time">${{e.time}}</span>
                    <span class="preview-title">${{e.organizer}}</span>
                </div>
            `).join('');

            preview.innerHTML = html || '<p style="color: var(--text-muted); font-size: 12px; text-align: center; padding: 20px;">Sin eventos</p>';
        }});

        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('.day-card').forEach(card => {{
                const dow = parseInt(card.dataset.day);
                const dayEvents = eventsByDay[dow] || [];
                const hasMatch = dayEvents.some(ev =>
                    ev.title.toLowerCase().includes(query) ||
                    ev.organizer.toLowerCase().includes(query) ||
                    ev.description.toLowerCase().includes(query)
                );
                card.style.display = (query === '' || hasMatch) ? 'block' : 'none';
            }});
        }});

        document.querySelectorAll('.filter-tab').forEach(tab => {{
            tab.addEventListener('click', () => {{
                document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                const filter = tab.dataset.filter;

                document.querySelectorAll('.day-card').forEach(card => {{
                    const dow = parseInt(card.dataset.day);
                    const dayEvents = eventsByDay[dow] || [];

                    let hasMatch = true;
                    if (filter === 'publico') {{
                        hasMatch = dayEvents.some(e => e.category === 'Público');
                    }} else if (filter === 'privado') {{
                        hasMatch = dayEvents.some(e => e.category === 'Privado');
                    }} else if (['morning', 'afternoon', 'evening'].includes(filter)) {{
                        hasMatch = dayEvents.some(e => e.time_period === filter);
                    }}

                    card.style.display = hasMatch ? 'block' : 'none';
                }});
            }});
        }});
    </script>
</body>
</html>
"""

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("   ZonaMaco 2026 - Generador de Mapas v3.1 (Light Theme)")
    print("=" * 60)

    events = parse_events()
    print(f"\n📊 Total eventos: {len(events)}")
    print(f"📍 Con coordenadas: {sum(1 for e in events if e.lat and e.lon)}")
    print(f"🔵 Públicos: {sum(1 for e in events if e.category == 'Público')}")
    print(f"🟠 Privados: {sum(1 for e in events if e.category == 'Privado')}")

    events_by_day: Dict[datetime, List[Event]] = {}
    for event in events:
        day = event.date.replace(hour=0, minute=0, second=0, microsecond=0)
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)

    sorted_days = sorted(events_by_day.keys())
    print(f"\n📅 Días: {len(sorted_days)}")

    days_info = []
    print("\nGenerando mapas...")

    for day in sorted_days:
        day_events = events_by_day[day]
        day_name = SPANISH_DAYS[day.weekday()]
        filename = f"{day.strftime('%Y-%m-%d')}_{day_name}.html"
        output_path = os.path.join(output_dir, filename)

        count = create_day_map(day_events, day, output_path)

        publico = sum(1 for e in day_events if e.category == "Público" and e.lat)
        privado = sum(1 for e in day_events if e.category == "Privado" and e.lat)

        days_info.append({
            'day_name': day_name,
            'day_num': day.day,
            'date_str': f"{day.day} de {SPANISH_MONTHS[day.month]}",
            'filename': filename,
            'count': count,
            'publico': publico,
            'privado': privado,
            'dow': day.weekday(),
        })

        print(f"  ✅ {day_name} {day.strftime('%d/%m')}: {count} eventos")

    create_premium_index(days_info, events, output_dir)

    print(f"\n{'=' * 60}")
    print(f"✨ Mapas generados en: {output_dir}")
    print(f"🌐 Abre maps/index.html en tu navegador")
    print("=" * 60)


if __name__ == "__main__":
    main()
