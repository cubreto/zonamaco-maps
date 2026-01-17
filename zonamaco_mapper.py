#!/usr/bin/env python3
"""
ZonaMaco Week Mapper v4.1
-------------------------
Enhanced with:
- Venue contact info (phone, email, website)
- Arrow routes between venues
- Centro Banamex MACO VIP
- Material Art Fair & Salón ACME pages
- Validation report (v4.1)
- Fixed click-to-pan (v4.1)
- venue_key support (v4.1)
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter
import json

# Fail fast if folium not installed
try:
    import folium
    from folium.plugins import AntPath
    from folium.features import DivIcon
except ImportError:
    print("ERROR: folium not installed. Run: pip install folium")
    sys.exit(1)


# =============================================================================
# VENUE DATABASE WITH CONTACT INFO
# =============================================================================
@dataclass
class Venue:
    name: str
    lat: float
    lon: float
    venue_type: str
    neighborhood: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""


VENUES: Dict[str, Venue] = {
    # MAIN FAIR VENUE
    "CENTRO BANAMEX": Venue("Centro Banamex", 19.4590, -99.2030, "fair", "San Ángel",
                            "Av. del Conscripto 311", "+52 55 5268 2000", "info@zonamaco.com", "zonamaco.com"),
    "MACO VIP": Venue("Centro Banamex - MACO VIP", 19.4590, -99.2030, "fair", "San Ángel",
                      "Av. del Conscripto 311", "+52 55 5268 2000", "vip@zonamaco.com", "zonamaco.com"),

    # MUSEUMS
    "MUSEO JUMEX": Venue("Museo Jumex", 19.4402, -99.2044, "museum", "Polanco",
                         "Miguel de Cervantes Saavedra 303", "+52 55 5395 2615", "info@fundacionjumex.org", "fundacionjumex.org"),
    "MUSEO DE ARTE MODERNO": Venue("Museo de Arte Moderno", 19.4215, -99.1786, "museum", "Chapultepec",
                                    "Paseo de la Reforma s/n", "+52 55 8647 5530", "mam@cultura.gob.mx", "mam.inba.gob.mx"),
    "MUSEO DE ARTE CARRILLO GIL": Venue("Museo de Arte Carrillo Gil", 19.3534, -99.1894, "museum", "San Ángel",
                                         "Av. Revolución 1608", "+52 55 8647 5450", "macg@cultura.gob.mx", "museodeartecarrillogil.com"),
    "MUSEO KALUZ": Venue("Museo Kaluz", 19.4354, -99.1487, "museum", "Centro",
                         "Av. Hidalgo 85", "+52 55 5518 2480", "contacto@museokaluz.org", "museokaluz.org"),
    "MUSEO DEL PALACIO DE BELLAS ARTES": Venue("Palacio de Bellas Artes", 19.4352, -99.1412, "museum", "Centro",
                                                "Av. Juárez s/n", "+52 55 8647 6500", "palacio@cultura.gob.mx", "museopalaciodebellasartes.gob.mx"),
    "MUSEO UNIVERSITARIO DEL CHOPO": Venue("Museo del Chopo", 19.4475, -99.1529, "museum", "Santa María la Ribera",
                                            "Dr. Enrique González Martínez 10", "+52 55 5535 2186", "museo.chopo@unam.mx", "chopo.unam.mx"),
    "MUSEO DE LA CIUDAD DE MÉXICO": Venue("Museo de la Ciudad de México", 19.4285, -99.1319, "museum", "Centro",
                                           "Pino Suárez 30", "+52 55 5522 9936", "mcm@cultura.cdmx.gob.mx", "cultura.cdmx.gob.mx"),
    "MUAC": Venue("MUAC", 19.3183, -99.1867, "museum", "Ciudad Universitaria",
                  "Insurgentes Sur 3000", "+52 55 5622 6972", "muac@unam.mx", "muac.unam.mx"),
    "SALA DE ARTE PÚBLICO SIQUEIROS": Venue("Sala de Arte Público Siqueiros", 19.4165, -99.1905, "museum", "Polanco",
                                             "Tres Picos 29", "+52 55 5203 1289", "siqueiros@cultura.gob.mx", "sfrfrfraps.cultura.gob.mx"),

    # GALLERIES
    "LABOR": Venue("Labor", 19.4188, -99.1673, "gallery", "Roma Norte",
                   "Gral. Antonio León 48", "+52 55 5286 8761", "info@labor.org.mx", "labor.org.mx"),
    "KURIMANZUTTO": Venue("kurimanzutto", 19.4264, -99.1687, "gallery", "San Miguel Chapultepec",
                          "Gob. Rafael Rebollar 94", "+52 55 5256 2408", "info@kurimanzutto.com", "kurimanzutto.com"),
    "OMR": Venue("OMR", 19.4195, -99.1682, "gallery", "Roma Norte",
                 "Córdoba 100", "+52 55 5207 1080", "info@omr.art", "omr.art"),
    "BODEGA OMR": Venue("Bodega OMR", 19.4142, -99.1635, "gallery", "Roma Sur",
                        "Colima 168", "+52 55 5207 1080", "bodega@omr.art", "omr.art"),
    "GALERÍA KAREN HUBER": Venue("Galería Karen Huber", 19.4175, -99.1698, "gallery", "Roma Norte",
                                  "Bucareli 120", "+52 55 5511 1617", "info@galeriakarenhuber.com", "galeriakarenhuber.com"),
    "GALERÍA ENRIQUE GUERRERO": Venue("Galería Enrique Guerrero", 19.4162, -99.1678, "gallery", "Roma Norte",
                                       "Horacio 1549", "+52 55 5280 2941", "info@galeriaenriqueguerrero.com", "galeriaenriqueguerrero.com"),
    "GALERÍA DANIELA ELBAHARA": Venue("Galería Daniela Elbahara", 19.4198, -99.1712, "gallery", "Roma Norte",
                                       "Zacatecas 93", "+52 55 5511 4000", "info@danielaelbahara.com", "danielaelbahara.com"),
    "ARRÓNIZ": Venue("Arróniz Arte Contemporáneo", 19.4186, -99.1625, "gallery", "Roma Norte",
                     "Plaza Río de Janeiro 53", "+52 55 5511 1142", "info@arroniz.mx", "arroniz.mx"),
    "TRAVESÍA CUATRO": Venue("Travesía Cuatro", 19.4172, -99.1695, "gallery", "Roma Norte",
                              "Tehuantepec 254", "+52 55 5514 7339", "mexico@travesiacuatro.com", "travesiacuatro.com"),
    "PROYECTOS MONCLOVA GALLERY": Venue("Proyectos Monclova", 19.4158, -99.1668, "gallery", "Roma Norte",
                                         "Colima 55", "+52 55 5525 9715", "info@proyectosmonclova.com", "proyectosmonclova.com"),
    "MARIANE IBRAHIM": Venue("Mariane Ibrahim", 19.4145, -99.1715, "gallery", "Roma Norte",
                              "Guanajuato 124", "+52 55 5207 7630", "mexico@marianeibrahim.com", "marianeibrahim.com"),
    "GALERIE NORDENHAKE": Venue("Galerie Nordenhake", 19.4178, -99.1702, "gallery", "Roma Norte",
                                 "Tabasco 260", "+52 55 5207 5032", "mexico@nordenhake.com", "nordenhake.com"),
    "SAENGER GALERÍA": Venue("Saenger Galería", 19.4189, -99.1658, "gallery", "Roma Norte",
                              "Jalapa 31", "+52 55 5256 2032", "info@saengergaleria.com", "saengergaleria.com"),
    "LATINOU": Venue("Latinou", 19.4165, -99.1745, "gallery", "Roma Norte",
                     "Frontera 148", "+52 55 5207 6550", "info@latinou.com", "latinou.com"),
    "CAM GALERÍA": Venue("CAM Galería", 19.4195, -99.1725, "gallery", "Roma Norte",
                          "Córdoba 109", "+52 55 5286 2265", "info@camgaleria.com", "camgaleria.com"),
    "LS / GALERÍA": Venue("LS Galería", 19.4168, -99.1688, "gallery", "Roma Norte",
                           "Tonalá 155", "+52 55 5511 6397", "info@lsgaleria.com", "lsgaleria.com"),
    "GALERÍA DE ARTE MEXICANO GAM": Venue("GAM", 19.4235, -99.1752, "gallery", "Juárez",
                                           "Gobernador Rafael Rebollar 43", "+52 55 5272 5529", "gam@gam.com.mx", "gam.com.mx"),
    "GALERÍA ANA TEJEDA": Venue("Galería Ana Tejeda", 19.4148, -99.1698, "gallery", "Roma Norte",
                                 "Colima 159", "+52 55 5574 7124", "info@anatejedagaleria.com", "anatejedagaleria.com"),
    "GALERÍA RGR": Venue("Galería RGR", 19.4182, -99.1712, "gallery", "Roma Norte",
                          "Guanajuato 180", "+52 55 5207 5020", "info@galeriargr.com", "galeriargr.com"),
    "RICARDO REYES": Venue("Ricardo Reyes Galería", 19.4175, -99.1665, "gallery", "Roma Norte",
                            "Mérida 54", "+52 55 7090 1005", "info@ricardoreyes.mx", "ricardoreyes.mx"),
    "JOVIAN FINE ART": Venue("Jovian Fine Art", 19.4112, -99.1645, "gallery", "Roma Sur",
                              "Insurgentes Sur 398", "+52 55 5564 2650", "info@jovianfineart.com", "jovianfineart.com"),
    "ALEJANDRA TOPETE GALLERY": Venue("Alejandra Topete Gallery", 19.4168, -99.1705, "gallery", "Roma Norte",
                                       "Colima 180", "+52 55 4155 0970", "info@alejandratopete.com", "alejandratopete.com"),
    "ALMANAQUE FOTOGRÁFICA": Venue("Almanaque Fotográfica", 19.4155, -99.1678, "gallery", "Roma Norte",
                                    "Jalapa 63", "+52 55 5207 8877", "info@almanaquefotografica.com", "almanaquefotografica.com"),
    "AMBAR QUIJANO": Venue("Ambar Quijano", 19.4142, -99.1695, "gallery", "Roma Norte",
                           "Colima 234", "+52 55 5207 8523", "info@ambarquijano.com", "ambarquijano.com"),
    "SORONDO PROJECTS": Venue("Sorondo Projects", 19.4188, -99.1658, "gallery", "Roma Norte",
                               "Chihuahua 138", "+52 55 5511 4230", "info@sorondoprojects.com", "sorondoprojects.com"),
    "BANDA MUNICIPAL": Venue("Banda Municipal", 19.4165, -99.1742, "gallery", "Roma Norte",
                              "Chiapas 97", "+52 55 5256 5430", "info@bandamunicipal.com", "bandamunicipal.com"),
    "BREUER STUDIO": Venue("Breuer Studio", 19.4178, -99.1715, "gallery", "Roma Norte",
                            "Tabasco 96", "+52 55 5511 4567", "info@breuerstudio.com", "breuerstudio.com"),

    # FOUNDATIONS & SPECIAL
    "FUNDACIÓN CASA WABI": Venue("Casa Wabi CDMX", 19.4245, -99.1698, "foundation", "Roma Norte",
                                  "Colima 235", "+52 55 5286 7677", "info@casawabi.org", "casawabi.org"),
    "CASA GILARDI": Venue("Casa Gilardi", 19.4312, -99.1925, "special", "San Miguel Chapultepec",
                           "General Antonio León 82", "+52 55 5271 3575", "visitas@casagilardi.mx", "casagilardi.mx"),
    "CASA LAMM": Venue("Casa Lamm", 19.4185, -99.1632, "special", "Roma Norte",
                        "Álvaro Obregón 99", "+52 55 5525 3938", "info@casalamm.com.mx", "casalamm.com.mx"),
    "GEORGINA POUNDS GALLERY EN CASA LAMM": Venue("Georgina Pounds @ Casa Lamm", 19.4185, -99.1632, "gallery", "Roma Norte",
                                                   "Álvaro Obregón 99", "+52 55 5525 3938", "info@georginapounds.com", "georginapounds.com"),
    "LAGOALGO": Venue("Lago/Algo", 19.4215, -99.1865, "foundation", "Chapultepec",
                       "Lago Mayor 2da Sección", "+52 55 5286 6300", "info@lagoalgo.org", "lagoalgo.org"),
    "PROYECTO H": Venue("Proyecto H", 19.4152, -99.1725, "gallery", "Roma Norte",
                         "Colima 325", "+52 55 5574 7780", "info@proyectoh.mx", "proyectoh.mx"),
    "DANIEL OROZCO ESTUDIO": Venue("Daniel Orozco Estudio", 19.4168, -99.1652, "studio", "Roma Norte",
                                    "Orizaba 101", "+52 55 5511 9900", "info@danielorozco.com", "danielorozco.com"),
    "CUERNAVACA3": Venue("Cuernavaca 3", 19.4188, -99.1642, "special", "Roma Norte",
                          "Cuernavaca 3", "+52 55 5511 0033", "info@cuernavaca3.com", ""),
    "TLC ART EDITIONS": Venue("TLC Art Editions", 19.4175, -99.1668, "gallery", "Roma Norte",
                               "Jalapa 125", "+52 55 5207 6699", "info@tlcarteditions.com", "tlcarteditions.com"),
    "NOUVEL": Venue("Nouvel", 19.4198, -99.1702, "gallery", "Roma Norte",
                     "Orizaba 198", "+52 55 5286 8850", "info@nouvel.mx", "nouvel.mx"),
    "GATHERING": Venue("Gathering", 19.4165, -99.1688, "studio", "Roma Norte",
                        "Durango 262", "+52 55 5207 5540", "studio@gathering.mx", "gathering.mx"),
    "TEREZA DIAQUE LA LAGUNA TALLER ÁNFORA \"LA MEJOR\"": Venue("Taller Ánfora", 19.4148, -99.1712, "studio", "Roma Norte",
                                                                 "", "", "", ""),
    "PUG SEAL": Venue("Pug Seal", 19.4195, -99.1685, "hotel", "Roma Norte",
                       "Amsterdam 54", "+52 55 5584 3510", "reservations@pugseal.com", "pugseal.com"),
    "GALERÍA RODRIGO RIVERO LAKE": Venue("Rodrigo Rivero Lake", 19.4285, -99.1545, "gallery", "Centro",
                                          "Campos Elíseos 199", "+52 55 5281 5005", "info@rodrigoriverolake.com", "rodrigoriverolake.com"),
    "CENTRO DE ARTE LIMANTOUR": Venue("Centro de Arte Limantour", 19.4235, -99.1668, "gallery", "Juárez",
                                       "Río Lerma 35", "+52 55 5208 6400", "info@limantour.mx", "limantour.mx"),

    # HOTELS
    "HOTEL ALEXANDER": Venue("Hotel Alexander", 19.4268, -99.1715, "hotel", "Condesa",
                              "Ámsterdam 141", "+52 55 5584 2000", "reservas@hotelalexander.mx", "hotelalexander.mx"),
    "HOTEL ALEXANDER X CAM GALERÍA": Venue("Hotel Alexander x CAM", 19.4268, -99.1715, "hotel", "Condesa",
                                            "Ámsterdam 141", "+52 55 5584 2000", "reservas@hotelalexander.mx", ""),
    "HOTEL VOLGA": Venue("Hotel Volga", 19.4245, -99.1695, "hotel", "Roma Norte",
                          "Praga 49", "+52 55 5207 9280", "info@hotelvolga.mx", "hotelvolga.mx"),

    # OTHER FAIRS
    "EXPO REFORMA": Venue("Expo Reforma", 19.4328, -99.1545, "fair", "Juárez",
                          "Morelos 67", "+52 55 5566 1950", "info@exporeforma.com", "exporeforma.com"),
    "FRONTÓN MÉXICO": Venue("Frontón México", 19.4365, -99.1525, "fair", "Tabacalera",
                             "Plaza de la República s/n", "+52 55 5535 0060", "info@frontonmexico.com", "frontonmexico.com"),

    # SATELLITE
    "LA BIBI + REUS": Venue("Hacienda Acamilpa", 18.8775, -99.2458, "special", "Morelos",
                             "Acamilpa, Morelos", "+52 777 312 5678", "info@haciendaacamilpa.com", ""),
    "SAENGER GALERÍA EN CASA GILARDI": Venue("Saenger @ Casa Gilardi", 19.4312, -99.1925, "gallery", "San Miguel Chapultepec",
                                              "", "+52 55 5256 2032", "info@saengergaleria.com", ""),
    "SAENGER GALERÍA EN MUSEO DOLORES OLMEDO": Venue("Saenger @ Dolores Olmedo", 19.2685, -99.0975, "gallery", "Xochimilco",
                                                      "Av. México 5843", "+52 55 5555 0891", "", ""),
    "SAENGER GALERÍA EN CENTRO DE ARTE LIMANTOUR": Venue("Saenger @ Limantour", 19.4235, -99.1668, "gallery", "Juárez",
                                                          "", "+52 55 5256 2032", "", ""),
    "MARCHANTE ARTE CONTEMPORÁNEO & PROYECTO H": Venue("Marchante x Proyecto H", 19.4152, -99.1725, "gallery", "Roma Norte",
                                                        "", "+52 55 5574 7780", "", ""),
    "LS / GALERÍA & CASA ABIERTA MONTE": Venue("LS Galería & Casa Abierta", 19.4168, -99.1688, "gallery", "Roma Norte",
                                                "", "+52 55 5511 6397", "", ""),
    "ARTSYNIGHTS X ZⓈONAMACO": Venue("ArtsyNights Venue", 19.4195, -99.1695, "special", "Roma Norte",
                                      "", "", "", "artsy.net"),
}

VENUE_ICONS = {
    "museum": {"icon": "university", "prefix": "fa", "color": "#1e3a5f", "label": "Museo"},
    "gallery": {"icon": "image", "prefix": "fa", "color": "#4a90d9", "label": "Galería"},
    "hotel": {"icon": "bed", "prefix": "fa", "color": "#2ecc71", "label": "Hotel"},
    "studio": {"icon": "paint-brush", "prefix": "fa", "color": "#e67e22", "label": "Estudio"},
    "foundation": {"icon": "landmark", "prefix": "fa", "color": "#f39c12", "label": "Fundación"},
    "special": {"icon": "star", "prefix": "fa", "color": "#e74c3c", "label": "Especial"},
    "fair": {"icon": "building", "prefix": "fa", "color": "#9b59b6", "label": "Feria"},
}

CATEGORY_COLORS = {"Público": "#4a90d9", "Privado": "#e67e22"}

TIME_PERIODS = {
    "morning": {"label": "Mañana", "icon": "☀️", "color": "#f39c12", "range": (0, 12)},
    "afternoon": {"label": "Tarde", "icon": "🌤️", "color": "#e67e22", "range": (12, 18)},
    "evening": {"label": "Noche", "icon": "🌙", "color": "#1e3a5f", "range": (18, 24)},
}

SPANISH_DAYS = {0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"}
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
    fair: str = "zonamaco"
    venue_key: Optional[str] = None  # Explicit venue override (takes priority over organizer matching)

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
            "fair": self.fair,
        }


def get_venue(organizer: str, venue_key: Optional[str] = None) -> Optional[Venue]:
    """Get venue by key or organizer name. venue_key takes priority."""
    # Priority 1: Explicit venue_key
    if venue_key:
        key_upper = venue_key.upper().strip()
        if key_upper in VENUES:
            return VENUES[key_upper]

    # Priority 2: Exact organizer match
    org_upper = organizer.upper().strip()
    if org_upper in VENUES:
        return VENUES[org_upper]

    # Priority 3: Substring matching (less reliable)
    for key, venue in VENUES.items():
        if key in org_upper or org_upper in key:
            return venue
    return None


def validate_events(events: List[Event]) -> None:
    """Validate events and print a report. Call after parsing to catch issues early."""
    print("\n" + "="*60)
    print("VALIDATION REPORT")
    print("="*60)

    valid_categories = {"Público", "Privado"}
    issues = {"missing_coords": [], "unknown_category": [], "duplicates": []}

    # Check for missing coordinates
    for e in events:
        if e.lat is None or e.lon is None:
            issues["missing_coords"].append(e.organizer)

    # Check for unknown categories
    for e in events:
        if e.category not in valid_categories:
            issues["unknown_category"].append((e.organizer, e.category))

    # Check for duplicates (same organizer, date, title)
    seen = Counter()
    for e in events:
        key = (e.date.isoformat(), e.organizer, e.title)
        seen[key] += 1
    for key, count in seen.items():
        if count > 1:
            issues["duplicates"].append((key[1], key[2], count))

    # Print report
    if issues["missing_coords"]:
        print(f"\nMISSING_COORDS ({len(issues['missing_coords'])} events without location):")
        for org in sorted(set(issues["missing_coords"])):
            count = issues["missing_coords"].count(org)
            print(f"  - {org} ({count} events)")
    else:
        print("\nMISSING_COORDS: None - all events have coordinates")

    if issues["unknown_category"]:
        print(f"\nUNKNOWN_CATEGORY ({len(issues['unknown_category'])}):")
        for org, cat in issues["unknown_category"]:
            print(f"  - {org}: '{cat}' (expected: Público or Privado)")
    else:
        print("\nUNKNOWN_CATEGORY: None - all categories valid")

    if issues["duplicates"]:
        print(f"\nDUPLICATES ({len(issues['duplicates'])}):")
        for org, title, count in issues["duplicates"]:
            print(f"  - {org}: '{title}' appears {count} times")
    else:
        print("\nDUPLICATES: None - no duplicate events")

    total_issues = len(issues["missing_coords"]) + len(issues["unknown_category"]) + len(issues["duplicates"])
    print(f"\n{'='*60}")
    if total_issues == 0:
        print(f"VALIDATION PASSED - {len(events)} events OK")
    else:
        print(f"VALIDATION WARNING - {total_issues} issues found in {len(events)} events")
    print("="*60 + "\n")


def parse_events() -> List[Event]:
    events_data = [
        # MACO VIP at Centro Banamex
        (datetime(2026, 2, 4, 11, 0), "CENTRO BANAMEX", "ZonaMaco VIP Preview", "Acceso exclusivo para coleccionistas VIP antes de la apertura general.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 10, 0), "CENTRO BANAMEX", "ZonaMaco Día 1", "Apertura oficial de la feria ZonaMaco 2026.", "Público", "zonamaco"),
        (datetime(2026, 2, 6, 10, 0), "CENTRO BANAMEX", "ZonaMaco Día 2", "Segundo día de la feria con tours guiados.", "Público", "zonamaco"),
        (datetime(2026, 2, 7, 10, 0), "CENTRO BANAMEX", "ZonaMaco Día 3", "Tercer día de la feria.", "Público", "zonamaco"),
        (datetime(2026, 2, 8, 10, 0), "CENTRO BANAMEX", "ZonaMaco Día 4 - Cierre", "Último día de la feria ZonaMaco 2026.", "Público", "zonamaco"),

        # Monday Feb 2
        (datetime(2026, 2, 2, 11, 0), "LABOR", "Inauguración 'A Espessura dos Días' - Eduardo Berliner", "La primera exposición del artista carioca Eduardo Berliner en Labor.", "Público", "zonamaco"),
        (datetime(2026, 2, 2, 11, 0), "LA BIBI + REUS", "Almuerzo y experiencia artística en Hacienda Acamilpa", "Almuerzo exclusivo y experiencia artística en el marco de ZonaMaco.", "Privado", "zonamaco"),
        (datetime(2026, 2, 2, 17, 0), "LATINOU", "Exposición individual de Chavis Mármol", "Chavis Mármol regresa al color con mezcla de materiales y texturas únicas.", "Privado", "zonamaco"),
        (datetime(2026, 2, 2, 18, 0), "BODEGA OMR", "Inauguración 'Dorian Ulises: Mexicano'", "Nueva exposición de Dorian Ulises.", "Público", "zonamaco"),

        # Tuesday Feb 3
        (datetime(2026, 2, 3, 10, 0), "GALERIE NORDENHAKE", "Exposición individual de Sarah Crowner", "Exhibición individual de la artista estadounidense Sarah Crowner.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 10, 0), "FUNDACIÓN CASA WABI", "Mesa de Centro - Cristina Umaña", "Obra nueva de la artista colombiana Cristina Umaña, curada por Andrea Bustillos.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 10, 0), "FUNDACIÓN CASA WABI", "Cristalización Especular - María Naidich", "Obra nueva de María Naidich en la terraza de Casa Wabi CDMX.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 10, 0), "ARRÓNIZ", "Inauguración: Madeline Jiménez, Ria Bosman, Karlo Andrei Ibarra", "Tres exposiciones simultáneas de artistas internacionales.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 10, 0), "FUNDACIÓN CASA WABI", "Sísifo Dichoso - Bosco Sodi", "La obra de Bosco Sodi habita el esfuerzo eterno del mito de Sísifo.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 10, 0), "GATHERING", "Visita privada al estudio de Stefan Brüggemann", "Acceso exclusivo al espacio de trabajo del artista.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 10, 0), "SAENGER GALERÍA", "Visita guiada: Gregor Hildebrandt en Casa Gilardi", "La arquitectura de Barragán en diálogo con la obra de Hildebrandt.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 11, 0), "BANDA MUNICIPAL", "Inauguración 'Sol Nocturno' - Renata Cassiano Álvarez", "Últimas obras de la artista mexicana.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 11, 0), "SAENGER GALERÍA", "Visita guiada: Yoab Vera y Diego Rivera", "Paisajes marinos y las puestas de sol en Acapulco.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 11, 0), "ALEJANDRA TOPETE GALLERY", "Performance callejero de Randy Shull", "Performance para inaugurar 'I Have Never Worn a Watch'.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 11, 0), "SORONDO PROJECTS", "Sorondo x Adhesivo", "Dos galerías fundadas por mujeres venezolanas se unen.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 12, 0), "FUNDACIÓN CASA WABI", "Mesa de Centro (horario público)", "Exposición abierta al público.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 12, 0), "FUNDACIÓN CASA WABI", "Cristalización Especular (horario público)", "Exposición abierta al público.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 12, 0), "TRAVESÍA CUATRO", "Inauguración: Tania Pérez Córdova", "Exposición individual de la artista.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 12, 0), "MARIANE IBRAHIM", "Exposición individual de Carmen Neely", "Primera presentación en México de Carmen Neely.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 12, 0), "ALEJANDRA TOPETE GALLERY", "'I Have Never Worn a Watch' - Randy Shull", "Exposición del artista estadounidense.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 12, 10), "FUNDACIÓN CASA WABI", "Sísifo Dichoso (horario público)", "Exposición abierta al público.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 16, 0), "GEORGINA POUNDS GALLERY EN CASA LAMM", "'Paraíso de Monstruos' - Vanessa Raw", "Pinturas de la artista en Casa Lamm.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 16, 0), "PROYECTOS MONCLOVA GALLERY", "Inauguración: Macaparana, Juan Parada, Gabriel Garcilazo", "Exposición colectiva.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 17, 0), "ALMANAQUE FOTOGRÁFICA", "'Madre Tierra' - Exposición colectiva", "Fotografía contemporánea de artistas destacados.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 17, 0), "TEREZA DIAQUE LA LAGUNA TALLER ÁNFORA \"LA MEJOR\"", "Presentación de Krytzia Dabdoub", "Presentación de la artista.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 17, 0), "GALERÍA DE ARTE MEXICANO GAM", "'Extreme Words' - Stefan Brüggemann", "Nueva exposición del artista conceptual.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 17, 0), "CUERNAVACA3", "Inauguración de Cuernavaca3", "Nueva fundación del coleccionista Jeff Magid.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 18, 0), "PROYECTO H", "Inauguración: Pablo Armesto, Patrick Hughes, José Romussi", "Tres exposiciones y residencia artística.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 18, 0), "GALERIE NORDENHAKE", "'Loose Geometries' - Selección de Sarah Crowner", "Obras históricas curadas por la artista.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 18, 0), "KURIMANZUTTO", "Preview: Oscar Murillo 'El Pozo de Agua'", "Adelanto de la nueva exposición.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 18, 0), "GALERÍA KAREN HUBER", "'Goodbye Ebony Horse' - Ian Grose + 'Rise and Shine'", "Dos exposiciones simultáneas.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 18, 0), "GALERÍA DANIELA ELBAHARA", "Exposición individual de Hugo Robledo", "Pinturas y cerámicas entre lo físico y lo mental.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 18, 0), "GALERÍA ENRIQUE GUERRERO", "'Néctar' - Fernanda Caballero", "Segunda exposición personal de la artista.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 18, 0), "DANIEL OROZCO ESTUDIO", "Subasta benéfica para LADLE", "Piezas intervenidas por diversos artistas.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 18, 0), "PUG SEAL", "Subasta de arte curada", "Piezas selectas en torno a los hoteles Pug Seal.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 18, 0), "OMR", "Inauguración: Marcel Dzama y Leonora Carrington", "Diálogo entre dos universos artísticos.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 18, 0), "GALERÍA RGR", "Inauguración: Roberto Matta", "Primera vez de la obra de Matta en RGR.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 19, 0), "RICARDO REYES", "'Serenísimo Pop' - Salustiano", "Pintura y obras en papel del artista sevillano.", "Público", "zonamaco"),
        (datetime(2026, 2, 3, 19, 0), "HOTEL ALEXANDER X CAM GALERÍA", "Pop-up Alejandra España en Caviar Bar", "Exhibición activa toda la semana.", "Privado", "zonamaco"),
        (datetime(2026, 2, 3, 20, 30), "GALERIE NORDENHAKE", "Cena de inauguración 'Loose Geometries'", "Cena exclusiva para coleccionistas.", "Privado", "zonamaco"),

        # Wednesday Feb 4
        (datetime(2026, 2, 4, 19, 0), "LS / GALERÍA", "'Echoes of the Unseen' - Carrington, Lempicka, Costa, Carrillo", "Creadoras que transformaron el arte.", "Privado", "zonamaco"),
        (datetime(2026, 2, 4, 19, 0), "HOTEL VOLGA", "Cóctel de kickoff ZonaMaco", "Inicio oficial de la semana en Hotel Volga.", "Público", "zonamaco"),
        (datetime(2026, 2, 4, 19, 30), "TLC ART EDITIONS", "TLC Art Editions en Artemis Project", "Graciela Iturbide, Jan Hendrix y más.", "Público", "zonamaco"),
        (datetime(2026, 2, 4, 19, 30), "CAM GALERÍA", "'Túnel y Vislumbre' - Alejandra España", "Obra inédita curada por Charles Moore.", "Privado", "zonamaco"),
        (datetime(2026, 2, 4, 20, 0), "MUSEO DE ARTE MODERNO", "Pre-inauguración: Rafael Lozano-Hemmer 'Jardín Inconcluso'", "Paseo nocturno por la instalación.", "Privado", "zonamaco"),

        # Thursday Feb 5
        (datetime(2026, 2, 5, 9, 30), "LATINOU", "Visita al estudio de Chavis Mármol + desayuno", "Recorrido exclusivo para coleccionistas.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 10, 0), "MUSEO JUMEX", "Recorridos guiados + firma: Gabriel de la Mora", "Presentación del catálogo 'La Petite Mort'.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 10, 0), "DANIEL OROZCO ESTUDIO", "Showroom abierto al público", "Visita al showroom del estudio.", "Público", "zonamaco"),
        (datetime(2026, 2, 5, 10, 0), "SAENGER GALERÍA EN CASA GILARDI", "Visita guiada: Gregor Hildebrandt", "La música como silencio y materia.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 10, 0), "GALERIE NORDENHAKE", "Exposición: Sarah Crowner", "Exhibición individual de la artista.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 10, 0), "SAENGER GALERÍA", "Visita al estudio de Robert Janitz", "Nómada entre NY y CDMX.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 10, 30), "AMBAR QUIJANO", "Visita al estudio de Mariana Paniagua", "Trayectoria sólida y presencia institucional.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 11, 0), "SAENGER GALERÍA EN MUSEO DOLORES OLMEDO", "Visitas guiadas: Yoab Vera y Diego Rivera", "Paisajes y puestas de sol.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 11, 0), "SALA DE ARTE PÚBLICO SIQUEIROS", "'Fusiones' + performance Valentina Díaz", "El legado de Siqueiros explorado.", "Público", "zonamaco"),
        (datetime(2026, 2, 5, 12, 0), "GALERÍA RODRIGO RIVERO LAKE", "Visita guiada: colección privada", "Elementos arquitectónicos de la época virreinal.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 12, 0), "MUSEO DEL PALACIO DE BELLAS ARTES", "'Colosos' - Intervención de Diego Vega", "Coreografía del laboratorio Cuerpos Arquitectos.", "Público", "zonamaco"),
        (datetime(2026, 2, 5, 18, 0), "PUG SEAL", "Cóctel + performance para expositores EJES", "Arts, drinks and fun.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 19, 0), "LS / GALERÍA", "Cena 25 aniversario", "Un cuarto de siglo dedicado al arte.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 19, 0), "MUSEO DE ARTE MODERNO", "'Pánico en el Interior Externo' - Conversación", "Con Lozano-Hemmer, Medina, Szántó.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 19, 0), "MUSEO UNIVERSITARIO DEL CHOPO", "'San Pedro - Carrera de Patos' - Elyla", "Monólogo teatral con música en vivo.", "Privado", "zonamaco"),
        (datetime(2026, 2, 5, 19, 30), "GALERÍA ANA TEJEDA", "Recorrido curatorial: Karen Cordero Reiman", "Exposición colectiva de artistas.", "Público", "zonamaco"),
        (datetime(2026, 2, 5, 19, 30), "HOTEL ALEXANDER", "Pop-up: Marcos Cojab", "Esculturas y gráficas con humor y simbolismo.", "Público", "zonamaco"),
        (datetime(2026, 2, 5, 20, 0), "JOVIAN FINE ART", "'Umbrales' - Nicolás Beltrán y Kevin Artavia", "Inauguración de Roma Sur, Proyectos Curatoriales.", "Público", "zonamaco"),
        (datetime(2026, 2, 5, 20, 0), "ALMANAQUE FOTOGRÁFICA", "Cóctel 10 aniversario - Madre Tierra", "Celebración de una década de fotografía.", "Privado", "zonamaco"),

        # Friday Feb 6
        (datetime(2026, 2, 6, 9, 30), "MUSEO DE ARTE CARRILLO GIL", "Brunch MACG + recorridos", "Gerzso, Botánica de Asfalto, y más.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 9, 30), "LATINOU", "Visita al estudio de Raúl Cordero", "Visión íntima del proceso creativo.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 10, 0), "LAGOALGO", "'Alucinaciones' + 'Rafa Esparza: Juntxs'", "Trevor Paglen, Troika y Rafa Esparza.", "Público", "zonamaco"),
        (datetime(2026, 2, 6, 10, 0), "SAENGER GALERÍA", "Visita guiada: Gregor Hildebrandt", "Repetición de módulos, lleno y vacío.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 10, 0), "AMBAR QUIJANO", "Visita al estudio de Andrea Bores", "Diálogo íntimo con los materiales.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 10, 0), "SAENGER GALERÍA", "Visita al estudio de Yoab Vera", "Casa familiar convertida en estudio.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 11, 0), "MARCHANTE ARTE CONTEMPORÁNEO & PROYECTO H", "Visita al estudio de Román de Castro", "Espacio de creación del artista.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 11, 0), "LS / GALERÍA & CASA ABIERTA MONTE", "Diálogo: Coen, Tzucumo, Candiani, Rojo", "Arte y arquitectura en conversación.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 11, 0), "MUAC", "Brunch + preview: 'Los Grupos' y Néstor Jiménez", "Exposiciones próximas a inaugurar.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 11, 0), "GALERÍA KAREN HUBER", "Visita al estudio de César Rangel Ramos", "Imágenes perfeccionadas por años.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 11, 0), "SAENGER GALERÍA", "Visitas guiadas: Yoab Vera y Diego Rivera", "Paisajes marinos y jardines.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 11, 45), "AMBAR QUIJANO", "Visita al estudio de Juana Subercaseaux", "Pintora chilena radicada en CDMX.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 12, 0), "MUSEO DEL PALACIO DE BELLAS ARTES", "'Colosos' - Intervención coreográfica", "Cuerpos Arquitectos en acción.", "Público", "zonamaco"),
        (datetime(2026, 2, 6, 13, 0), "ARRÓNIZ", "Open House: Mauro Giaconi 'Temporal Ventaja'", "Tour por Obrera Centro.", "Público", "zonamaco"),
        (datetime(2026, 2, 6, 19, 0), "AMBAR QUIJANO", "Cóctel + activación: Mariana Garibay Raeke", "Diálogo con Manuela Riestra.", "Público", "zonamaco"),
        (datetime(2026, 2, 6, 19, 0), "BREUER STUDIO", "Inauguración: artistas nacionales e internacionales", "Diseño con precisión y conciencia.", "Público", "zonamaco"),
        (datetime(2026, 2, 6, 19, 0), "MUSEO DE ARTE MODERNO", "Eli Keszler activa 'Jardín Inconcluso'", "Performances, poesía y coreografía.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 19, 0), "NOUVEL", "Glass Reflections Cocktail", "Primera vez en México, con Ciento.", "Privado", "zonamaco"),
        (datetime(2026, 2, 6, 20, 0), "MUSEO KALUZ", "Cóctel + recorrido: 'El Jardín de Velasco'", "Hendrix, Lagarde, Cabrera Rubio, Guzik, Glassford.", "Privado", "zonamaco"),

        # Saturday Feb 7
        (datetime(2026, 2, 7, 10, 0), "LS / GALERÍA", "'Memoria en Construcción' - Arnaldo Coen", "Procesos y capas del universo creativo.", "Privado", "zonamaco"),
        (datetime(2026, 2, 7, 10, 0), "ARRÓNIZ", "Desayuno + estudios: Giaconi y Castro", "Tour por Obrera Centro.", "Privado", "zonamaco"),
        (datetime(2026, 2, 7, 10, 0), "SAENGER GALERÍA", "Visita guiada: Gregor Hildebrandt en Casa Gilardi", "Arquitectura, luz y sombra.", "Privado", "zonamaco"),
        (datetime(2026, 2, 7, 10, 0), "NOUVEL", "Glass Reflections Open House", "Exhibición abierta al público.", "Público", "zonamaco"),
        (datetime(2026, 2, 7, 11, 0), "ALEJANDRA TOPETE GALLERY", "Conversatorio: Lucía Lundt y Rafael Lozano-Hemmer", "Topografías de lo Invisible.", "Público", "zonamaco"),
        (datetime(2026, 2, 7, 11, 0), "SAENGER GALERÍA", "Visitas guiadas: Yoab Vera y Diego Rivera", "Paisajes erosionados y otros tiempos.", "Privado", "zonamaco"),
        (datetime(2026, 2, 7, 11, 0), "SAENGER GALERÍA EN CENTRO DE ARTE LIMANTOUR", "'Ebriedad Geométrica' - Visita guiada", "Con curadores y artistas.", "Privado", "zonamaco"),
        (datetime(2026, 2, 7, 11, 30), "PROYECTO H", "Visita al estudio de Pablo de Laborde Lascaris", "Escultor mexicano.", "Privado", "zonamaco"),
        (datetime(2026, 2, 7, 11, 30), "AMBAR QUIJANO", "Visita al estudio de Meryl Yana", "Nacida en París, radicada en San Miguel Chapultepec.", "Privado", "zonamaco"),
        (datetime(2026, 2, 7, 12, 0), "MARIANE IBRAHIM", "Charla + libro: Carmen Neely", "Conversación con la artista.", "Público", "zonamaco"),
        (datetime(2026, 2, 7, 12, 0), "MUSEO DEL PALACIO DE BELLAS ARTES", "'Colosos' - Recorrido coreográfico", "Diego Vega y Cuerpos Arquitectos.", "Privado", "zonamaco"),
        (datetime(2026, 2, 7, 12, 0), "KURIMANZUTTO", "Future Dialogues: Oscar Murillo & Magali Arriola", "Lanzamiento del libro 'El Pozo de Agua'.", "Público", "zonamaco"),
        (datetime(2026, 2, 7, 19, 0), "ARTSYNIGHTS X ZⓈONAMACO", "Abracadabra con Blond:ish", "Fiesta de cierre.", "Público", "zonamaco"),

        # Sunday Feb 8
        (datetime(2026, 2, 8, 10, 0), "SAENGER GALERÍA", "Visita guiada: Gregor Hildebrandt en Casa Gilardi", "Última oportunidad de la semana.", "Privado", "zonamaco"),
        (datetime(2026, 2, 8, 10, 0), "MUSEO DE LA CIUDAD DE MÉXICO", "'Columna Rota' - Visita guiada", "Exploración artística con organizadores.", "Privado", "zonamaco"),
        (datetime(2026, 2, 8, 11, 0), "SAENGER GALERÍA", "Visitas guiadas: Yoab Vera y Diego Rivera", "Cierre de la semana.", "Privado", "zonamaco"),
    ]

    events = []
    for item in events_data:
        venue_key = None
        if len(item) == 7:
            dt, org, title, desc, cat, fair, venue_key = item
        elif len(item) == 6:
            dt, org, title, desc, cat, fair = item
        else:
            dt, org, title, desc, cat = item
            fair = "zonamaco"
        venue = get_venue(org, venue_key)
        events.append(Event(date=dt, organizer=org, title=title, description=desc, category=cat, venue=venue, fair=fair, venue_key=venue_key))
    return events


def parse_material_events() -> List[Event]:
    """Material Art Fair events at Expo Reforma."""
    events_data = [
        # Format: (datetime, organizer, title, desc, category) or (datetime, organizer, title, desc, category, venue_key)
        (datetime(2026, 2, 4, 18, 0), "EXPO REFORMA", "Material Art Fair - VIP Preview", "Acceso exclusivo para coleccionistas antes de la apertura.", "Privado"),
        (datetime(2026, 2, 5, 11, 0), "EXPO REFORMA", "Material Art Fair - Día 1", "Feria de arte emergente y diseño.", "Público"),
        (datetime(2026, 2, 6, 11, 0), "EXPO REFORMA", "Material Art Fair - Día 2", "Galerías emergentes de México y Latinoamérica.", "Público"),
        (datetime(2026, 2, 7, 11, 0), "EXPO REFORMA", "Material Art Fair - Día 3", "Programación especial y performances.", "Público"),
        (datetime(2026, 2, 8, 11, 0), "EXPO REFORMA", "Material Art Fair - Cierre", "Último día de la feria Material.", "Público"),
    ]
    events = []
    for item in events_data:
        venue_key = item[5] if len(item) == 6 else None
        dt, org, title, desc, cat = item[:5]
        venue = get_venue(org, venue_key)
        events.append(Event(date=dt, organizer=org, title=title, description=desc, category=cat, venue=venue, fair="material", venue_key=venue_key))
    return events


def parse_acme_events() -> List[Event]:
    """Salón ACME events at Frontón México."""
    events_data = [
        # Format: (datetime, organizer, title, desc, category) or (datetime, organizer, title, desc, category, venue_key)
        (datetime(2026, 2, 4, 19, 0), "FRONTÓN MÉXICO", "Salón ACME - Preview VIP", "Acceso exclusivo antes de la apertura general.", "Privado"),
        (datetime(2026, 2, 5, 12, 0), "FRONTÓN MÉXICO", "Salón ACME - Día 1", "Arte independiente y experimental.", "Público"),
        (datetime(2026, 2, 6, 12, 0), "FRONTÓN MÉXICO", "Salón ACME - Día 2", "Proyectos de artistas emergentes.", "Público"),
        (datetime(2026, 2, 7, 12, 0), "FRONTÓN MÉXICO", "Salón ACME - Día 3", "Charlas y performances especiales.", "Público"),
        (datetime(2026, 2, 8, 12, 0), "FRONTÓN MÉXICO", "Salón ACME - Cierre", "Último día del Salón ACME.", "Público"),
    ]
    events = []
    for item in events_data:
        venue_key = item[5] if len(item) == 6 else None
        dt, org, title, desc, cat = item[:5]
        venue = get_venue(org, venue_key)
        events.append(Event(date=dt, organizer=org, title=title, description=desc, category=cat, venue=venue, fair="acme", venue_key=venue_key))
    return events


def create_popup_html(event: Event) -> str:
    """Create popup with venue contact info."""
    cat_color = CATEGORY_COLORS.get(event.category, "#666")
    venue = event.venue
    neighborhood = venue.neighborhood if venue else ""
    address = venue.address if venue else ""
    phone = venue.phone if venue else ""
    email = venue.email if venue else ""
    website = venue.website if venue else ""

    contact_html = ""
    if phone:
        contact_html += f'<div style="margin: 3px 0;"><i class="fa fa-phone" style="width: 16px; color: #4a90d9;"></i> <a href="tel:{phone}" style="color: #4a90d9; text-decoration: none;">{phone}</a></div>'
    if email:
        contact_html += f'<div style="margin: 3px 0;"><i class="fa fa-envelope" style="width: 16px; color: #4a90d9;"></i> <a href="mailto:{email}" style="color: #4a90d9; text-decoration: none;">{email}</a></div>'
    if website:
        contact_html += f'<div style="margin: 3px 0;"><i class="fa fa-globe" style="width: 16px; color: #4a90d9;"></i> <a href="https://{website}" target="_blank" style="color: #4a90d9; text-decoration: none;">{website}</a></div>'

    return f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; width: 340px; padding: 5px;">
        <div style="border-left: 4px solid {cat_color}; padding-left: 12px; margin-bottom: 12px;">
            <h3 style="margin: 0 0 8px 0; font-size: 15px; color: #1e3a5f; line-height: 1.3;">{event.title}</h3>
            <div style="font-size: 13px; color: #555; margin-bottom: 4px;"><strong>{event.organizer}</strong></div>
        </div>
        <div style="display: flex; gap: 15px; margin-bottom: 10px; font-size: 12px;">
            <div style="background: #f0f4f8; padding: 6px 10px; border-radius: 4px;"><strong>⏰</strong> {event.date.strftime('%H:%M')}</div>
            <div style="background: {cat_color}15; color: {cat_color}; padding: 6px 10px; border-radius: 4px; font-weight: 600;">{event.category}</div>
        </div>
        <div style="font-size: 12px; color: #666; margin-bottom: 10px;">
            <div><strong>📍</strong> {neighborhood}</div>
            {'<div style="margin-left: 18px; color: #888;">' + address + '</div>' if address else ''}
        </div>
        <div style="background: #f8fafc; border-radius: 8px; padding: 10px; margin-bottom: 10px; font-size: 11px;">
            <div style="font-weight: 600; color: #1e3a5f; margin-bottom: 6px;">📞 Contacto</div>
            {contact_html if contact_html else '<div style="color: #94a3b8;">Sin información de contacto</div>'}
        </div>
        <div style="font-size: 12px; color: #444; line-height: 1.5; border-top: 1px solid #e8ecf0; padding-top: 10px;">
            {event.description[:200] + '...' if len(event.description) > 200 else event.description}
        </div>
    </div>
    """


def create_tooltip_html(event: Event) -> str:
    """Create rich tooltip with venue info."""
    venue = event.venue
    phone = venue.phone if venue else ""

    return f"""
    <div style="font-family: -apple-system, sans-serif; padding: 8px; min-width: 200px;">
        <div style="font-weight: 700; color: #1e3a5f; font-size: 13px;">{event.date.strftime('%H:%M')} - {event.organizer}</div>
        <div style="color: #666; font-size: 11px; margin-top: 4px;">{event.title[:50]}{'...' if len(event.title) > 50 else ''}</div>
        {f'<div style="color: #4a90d9; font-size: 10px; margin-top: 4px;">📞 {phone}</div>' if phone else ''}
    </div>
    """


def create_timeline_html(events: List[Event], day_date: datetime) -> str:
    day_name = SPANISH_DAYS[day_date.weekday()]
    morning = sorted([e for e in events if e.time_period == "morning"], key=lambda x: x.date)
    afternoon = sorted([e for e in events if e.time_period == "afternoon"], key=lambda x: x.date)
    evening = sorted([e for e in events if e.time_period == "evening"], key=lambda x: x.date)

    # JavaScript helper to find Leaflet map (Folium uses map_<uuid> not 'map')
    find_map_js = """(function(){var m=Object.values(window).find(function(v){return v&&v._leaflet_id&&v.setView});if(m){m.setView([%s,%s],16)}})()"""

    def event_item(e: Event) -> str:
        cat_color = CATEGORY_COLORS.get(e.category, "#666")
        onclick_js = find_map_js % (e.lat, e.lon) if e.lat and e.lon else ""
        # Add data attributes for filtering
        search_text = f"{e.organizer} {e.title} {e.description}".lower().replace('"', '&quot;')
        return f"""<div class="event-item" data-search="{search_text}" data-category="{e.category}" style="padding: 8px 10px; margin: 4px 0; background: white; border-radius: 6px; border-left: 3px solid {cat_color}; font-size: 11px; cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.08); transition: opacity 0.2s;" onclick="{onclick_js}"><div style="font-weight: 600; color: #1e3a5f;">{e.date.strftime('%H:%M')}</div><div style="color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{e.organizer}</div></div>"""

    def period_section(title: str, events_list: List[Event], color: str, period_id: str) -> str:
        if not events_list:
            return ""
        items = "".join(event_item(e) for e in events_list)
        return f"""<div class="period-section" id="{period_id}" style="margin-bottom: 15px;"><div class="period-header" style="font-size: 11px; font-weight: 700; color: {color}; margin-bottom: 6px; padding: 4px 8px; background: {color}15; border-radius: 4px;">{title} (<span class="period-count">{len(events_list)}</span>)</div>{items}</div>"""

    # Search box HTML
    search_box = """<div style="margin-bottom: 12px;"><input type="text" id="sidebarSearch" placeholder="Buscar..." style="width: 100%; padding: 8px 10px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 12px; background: white;"></div>"""

    # Filter buttons
    filter_buttons = """<div style="display: flex; gap: 4px; margin-bottom: 12px;"><button class="filter-btn active" data-filter="all" style="flex: 1; padding: 6px; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 10px; cursor: pointer; background: #4a90d9; color: white;">Todos</button><button class="filter-btn" data-filter="Público" style="flex: 1; padding: 6px; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 10px; cursor: pointer; background: white;">🔵 Púb</button><button class="filter-btn" data-filter="Privado" style="flex: 1; padding: 6px; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 10px; cursor: pointer; background: white;">🟠 Priv</button></div>"""

    # JavaScript for filtering
    filter_script = """<script>
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('sidebarSearch');
        const filterBtns = document.querySelectorAll('.filter-btn');
        const eventItems = document.querySelectorAll('.event-item');
        let activeFilter = 'all';

        function applyFilters() {
            const searchTerm = searchInput.value.toLowerCase();
            let visibleCount = { morning: 0, afternoon: 0, evening: 0 };

            eventItems.forEach(item => {
                const searchText = item.dataset.search;
                const category = item.dataset.category;
                const matchesSearch = !searchTerm || searchText.includes(searchTerm);
                const matchesFilter = activeFilter === 'all' || category === activeFilter;
                const show = matchesSearch && matchesFilter;
                item.style.display = show ? 'block' : 'none';
                item.style.opacity = show ? '1' : '0.3';

                if (show) {
                    const section = item.closest('.period-section');
                    if (section) {
                        if (section.id === 'morning') visibleCount.morning++;
                        else if (section.id === 'afternoon') visibleCount.afternoon++;
                        else if (section.id === 'evening') visibleCount.evening++;
                    }
                }
            });

            // Update period counts
            document.querySelectorAll('.period-section').forEach(section => {
                const count = section.querySelectorAll('.event-item[style*="display: block"], .event-item:not([style*="display"])').length;
                const countEl = section.querySelector('.period-count');
                if (countEl) countEl.textContent = Array.from(section.querySelectorAll('.event-item')).filter(i => i.style.display !== 'none').length;
            });
        }

        searchInput.addEventListener('input', applyFilters);

        filterBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                filterBtns.forEach(b => {
                    b.style.background = 'white';
                    b.style.color = '#333';
                    b.classList.remove('active');
                });
                this.style.background = '#4a90d9';
                this.style.color = 'white';
                this.classList.add('active');
                activeFilter = this.dataset.filter;
                applyFilters();
            });
        });

        // Keyboard shortcut
        document.addEventListener('keydown', e => {
            if (e.key === '/' && e.target.tagName !== 'INPUT') {
                e.preventDefault();
                searchInput.focus();
            }
            if (e.key === 'Escape') {
                searchInput.value = '';
                applyFilters();
            }
        });
    });
    </script>"""

    return f"""<div style="position: fixed; top: 10px; right: 10px; width: 220px; max-height: 90vh; background: #f8fafc; border-radius: 12px; padding: 15px; z-index: 1000; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow-y: auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; border: 1px solid #e2e8f0;"><div style="text-align: center; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 2px solid #e2e8f0;"><div style="font-size: 18px; font-weight: 700; color: #1e3a5f;">{day_name}</div><div style="font-size: 12px; color: #64748b;">{day_date.day} de {SPANISH_MONTHS[day_date.month]}</div><div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">{len(events)} eventos</div></div>{search_box}{filter_buttons}{period_section("☀️ Mañana", morning, "#f39c12", "morning")}{period_section("🌤️ Tarde", afternoon, "#e67e22", "afternoon")}{period_section("🌙 Noche", evening, "#1e3a5f", "evening")}</div>{filter_script}"""


def add_arrow_markers(m: folium.Map, coords: List[List[float]], color: str = "#4a90d9"):
    """Add arrow markers along the route to show direction."""
    import math

    for i in range(len(coords) - 1):
        lat1, lon1 = coords[i]
        lat2, lon2 = coords[i + 1]

        # Calculate midpoint
        mid_lat = (lat1 + lat2) / 2
        mid_lon = (lon1 + lon2) / 2

        # Calculate angle
        angle = math.degrees(math.atan2(lon2 - lon1, lat2 - lat1))

        # Create arrow marker at midpoint
        arrow_icon = DivIcon(
            icon_size=(20, 20),
            icon_anchor=(10, 10),
            html=f'''<div style="
                font-size: 16px;
                color: {color};
                transform: rotate({90 - angle}deg);
                text-shadow: 1px 1px 2px white, -1px -1px 2px white;
                font-weight: bold;
            ">➤</div>'''
        )

        folium.Marker(
            location=[mid_lat, mid_lon],
            icon=arrow_icon,
        ).add_to(m)


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
    fg_route = folium.FeatureGroup(name='➡️ Ruta sugerida', show=True)

    sorted_events = sorted(mappable, key=lambda x: x.date)

    for event in sorted_events:
        venue_type = event.venue.venue_type if event.venue else "special"
        icon_info = VENUE_ICONS.get(venue_type, VENUE_ICONS["special"])
        popup = folium.Popup(create_popup_html(event), max_width=370)
        tooltip = folium.Tooltip(create_tooltip_html(event))

        marker = folium.Marker(
            location=[event.lat, event.lon],
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color='orange' if event.category == 'Privado' else 'blue', icon=icon_info["icon"], prefix=icon_info["prefix"])
        )

        if event.category == "Público":
            marker.add_to(fg_publico)
        else:
            marker.add_to(fg_privado)

    # Add route with arrows
    if len(sorted_events) >= 2:
        route_coords = [[e.lat, e.lon] for e in sorted_events]

        # Animated path
        AntPath(
            locations=route_coords,
            color="#4a90d9",
            weight=4,
            opacity=0.8,
            dash_array=[10, 20],
            delay=800,
            pulse_color="#fff"
        ).add_to(fg_route)

        # Add arrow markers
        add_arrow_markers(fg_route, route_coords, "#1e3a5f")

    fg_publico.add_to(m)
    fg_privado.add_to(m)
    fg_route.add_to(m)

    folium.LayerControl(collapsed=False, position='topleft').add_to(m)
    m.get_root().html.add_child(folium.Element(create_timeline_html(mappable, day_date)))

    legend_html = """<div style="position: fixed; bottom: 30px; left: 10px; z-index: 1000; background: white; padding: 12px 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); font-family: -apple-system, sans-serif; font-size: 11px; border: 1px solid #e2e8f0;"><div style="font-weight: 700; margin-bottom: 8px; color: #1e3a5f;">Leyenda</div><div style="margin: 4px 0;"><span style="color: #4a90d9;">●</span> Público</div><div style="margin: 4px 0;"><span style="color: #e67e22;">●</span> Privado</div><div style="margin: 4px 0;"><span style="color: #4a90d9;">➤</span> Ruta sugerida</div><div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e2e8f0;"><div><i class="fa fa-university"></i> Museo</div><div><i class="fa fa-image"></i> Galería</div><div><i class="fa fa-building"></i> Feria</div><div><i class="fa fa-bed"></i> Hotel</div></div></div>"""
    m.get_root().html.add_child(folium.Element(legend_html))
    m.get_root().header.add_child(folium.Element('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"/>'))

    m.save(output_path)
    return len(mappable)


def create_fair_map(events: List[Event], fair_name: str, fair_title: str, output_path: str):
    """Create a dedicated map for a specific fair."""
    mappable = [e for e in events if e.lat and e.lon]
    if not mappable:
        return

    # Center on the fair venue
    center_lat = mappable[0].lat
    center_lon = mappable[0].lon

    m = folium.Map(location=[center_lat, center_lon], zoom_start=15, tiles='cartodbpositron')

    for event in mappable:
        cat_color = CATEGORY_COLORS.get(event.category, "#666")
        popup = folium.Popup(create_popup_html(event), max_width=370)

        folium.Marker(
            location=[event.lat, event.lon],
            popup=popup,
            tooltip=f"<b>{event.date.strftime('%d/%m %H:%M')}</b><br>{event.title}",
            icon=folium.Icon(color='purple', icon='building', prefix='fa')
        ).add_to(m)

    # Title overlay
    title_html = f"""<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 1000; background: white; padding: 15px 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); font-family: -apple-system, sans-serif; text-align: center; border: 2px solid #9b59b6;"><div style="font-size: 20px; font-weight: 700; color: #9b59b6;">{fair_title}</div><div style="font-size: 12px; color: #666; margin-top: 4px;">{len(mappable)} eventos • Feb 4-8, 2026</div></div>"""
    m.get_root().html.add_child(folium.Element(title_html))
    m.get_root().header.add_child(folium.Element('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"/>'))

    m.save(output_path)


def create_premium_index(days_info: List[dict], all_events: List[Event], output_dir: str, material_events: List[Event], acme_events: List[Event]):
    """Create index page with all fairs."""

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
                    <div class="stat-pill publico">{day['publico']} púb</div>
                    <div class="stat-pill privado">{day['privado']} priv</div>
                </div>
                <div class="day-card-preview" id="preview-{day['dow']}"></div>
                <a href="{day['filename']}" class="day-card-link">
                    Ver mapa <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </a>
            </div>
        """

    venue_badges_html = ""
    for vt, info in VENUE_ICONS.items():
        count = venue_counts.get(vt, 0)
        if count > 0:
            venue_badges_html += f"""<div class="venue-badge"><i class="fa fa-{info['icon']}" style="color: {info['color']};"></i><span class="venue-count">{count}</span><span class="venue-label">{info['label']}</span></div>"""

    # Get unique neighborhoods for filter
    neighborhoods = sorted(set(e.venue.neighborhood for e in all_events if e.venue and e.venue.neighborhood))
    neighborhoods_json = json.dumps(neighborhoods, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Art Week CDMX 2026 | ZonaMaco + Material + ACME</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --white: #ffffff;
            --bg-light: #f8fafc;
            --border: #e2e8f0;
            --text-dark: #0f172a;
            --text-primary: #1e3a5f;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
            --blue-primary: #4a90d9;
            --blue-light: #e8f4fd;
            --blue-dark: #1e3a5f;
            --orange-primary: #e67e22;
            --orange-light: #fef3e8;
            --purple-primary: #9b59b6;
            --purple-light: #f3e8ff;
            --green-primary: #27ae60;
            --green-light: #e8f8ef;
            --shadow-lg: 0 10px 40px rgba(0,0,0,0.1);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; background: var(--bg-light); color: var(--text-dark); }}
        .header {{ background: var(--white); border-bottom: 1px solid var(--border); padding: 20px 0; position: sticky; top: 0; z-index: 100; }}
        .header-content {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; }}
        .logo {{ display: flex; align-items: center; gap: 12px; }}
        .logo-text {{ font-size: 1.5rem; font-weight: 700; color: var(--text-primary); }}
        .logo-badge {{ background: linear-gradient(135deg, var(--blue-primary), var(--orange-primary)); color: white; font-size: 10px; font-weight: 600; padding: 4px 8px; border-radius: 4px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 40px 24px; }}

        /* Fair Cards Section */
        .fairs-section {{ margin-bottom: 60px; }}
        .section-title {{ font-size: 1.5rem; font-weight: 700; color: var(--text-primary); margin-bottom: 24px; text-align: center; }}
        .fairs-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-bottom: 40px; }}
        .fair-card {{ background: var(--white); border-radius: 16px; padding: 24px; border: 2px solid var(--border); transition: all 0.3s ease; }}
        .fair-card:hover {{ transform: translateY(-4px); box-shadow: var(--shadow-lg); }}
        .fair-card.zonamaco {{ border-color: var(--blue-primary); }}
        .fair-card.material {{ border-color: var(--purple-primary); }}
        .fair-card.acme {{ border-color: var(--green-primary); }}
        .fair-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }}
        .fair-icon {{ width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 20px; }}
        .fair-icon.zonamaco {{ background: var(--blue-light); color: var(--blue-primary); }}
        .fair-icon.material {{ background: var(--purple-light); color: var(--purple-primary); }}
        .fair-icon.acme {{ background: var(--green-light); color: var(--green-primary); }}
        .fair-name {{ font-size: 1.25rem; font-weight: 700; color: var(--text-dark); }}
        .fair-venue {{ font-size: 13px; color: var(--text-muted); }}
        .fair-dates {{ font-size: 12px; color: var(--text-secondary); margin-bottom: 16px; padding: 8px 12px; background: var(--bg-light); border-radius: 8px; display: inline-block; }}
        .fair-link {{ display: block; padding: 12px; border-radius: 10px; text-align: center; text-decoration: none; font-weight: 600; font-size: 14px; transition: all 0.2s ease; }}
        .fair-link.zonamaco {{ background: var(--blue-primary); color: white; }}
        .fair-link.material {{ background: var(--purple-primary); color: white; }}
        .fair-link.acme {{ background: var(--green-primary); color: white; }}
        .fair-link:hover {{ opacity: 0.9; transform: scale(1.02); }}

        /* Stats */
        .hero {{ text-align: center; padding: 40px 0; }}
        .hero h1 {{ font-size: clamp(2rem, 5vw, 3rem); font-weight: 700; color: var(--text-primary); margin-bottom: 8px; }}
        .hero h1 span {{ background: linear-gradient(135deg, var(--blue-primary), var(--orange-primary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .hero-subtitle {{ font-size: 1rem; color: var(--text-secondary); margin-bottom: 32px; }}
        .stats-row {{ display: flex; justify-content: center; gap: 40px; margin-bottom: 24px; flex-wrap: wrap; }}
        .stat-item {{ text-align: center; }}
        .stat-value {{ font-size: 2.5rem; font-weight: 700; line-height: 1; }}
        .stat-value.blue {{ color: var(--blue-primary); }}
        .stat-value.orange {{ color: var(--orange-primary); }}
        .stat-value.navy {{ color: var(--blue-dark); }}
        .stat-label {{ font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; }}
        .category-pills {{ display: flex; justify-content: center; gap: 12px; margin-bottom: 24px; }}
        .category-pill {{ display: flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 100px; font-size: 13px; font-weight: 500; }}
        .category-pill.publico {{ background: var(--blue-light); color: var(--blue-primary); }}
        .category-pill.privado {{ background: var(--orange-light); color: var(--orange-primary); }}
        .venue-badges {{ display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }}
        .venue-badge {{ display: flex; align-items: center; gap: 6px; background: var(--white); border: 1px solid var(--border); padding: 6px 10px; border-radius: 6px; font-size: 11px; }}
        .venue-count {{ font-weight: 600; }}
        .venue-label {{ color: var(--text-secondary); }}

        /* Search & Filter Bar */
        .search-filter-bar {{ background: var(--white); border-bottom: 1px solid var(--border); padding: 16px 0; }}
        .search-filter-content {{ max-width: 1200px; margin: 0 auto; padding: 0 24px; display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }}
        .search-box {{ flex: 1; min-width: 200px; position: relative; }}
        .search-box input {{ width: 100%; padding: 10px 40px 10px 14px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; background: var(--bg-light); transition: all 0.2s; }}
        .search-box input:focus {{ outline: none; border-color: var(--blue-primary); background: var(--white); box-shadow: 0 0 0 3px rgba(74, 144, 217, 0.1); }}
        .search-box input::placeholder {{ color: var(--text-muted); }}
        .search-box i {{ position: absolute; right: 14px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }}
        .filter-select {{ padding: 10px 32px 10px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; background: var(--bg-light) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E") no-repeat right 10px center; appearance: none; cursor: pointer; min-width: 130px; }}
        .filter-select:focus {{ outline: none; border-color: var(--blue-primary); }}
        .clear-filters {{ padding: 10px 16px; background: transparent; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; cursor: pointer; color: var(--text-secondary); transition: all 0.2s; display: flex; align-items: center; gap: 6px; }}
        .clear-filters:hover {{ background: var(--bg-light); border-color: var(--text-muted); }}
        .filter-count {{ background: var(--blue-primary); color: white; font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-left: 8px; }}
        .no-results {{ text-align: center; padding: 40px; background: var(--white); border-radius: 12px; border: 1px dashed var(--border); margin-top: 20px; }}
        .no-results i {{ font-size: 48px; color: var(--text-muted); margin-bottom: 16px; }}
        .no-results p {{ color: var(--text-secondary); font-size: 14px; }}
        @media (max-width: 768px) {{ .search-filter-content {{ flex-direction: column; }} .search-box {{ width: 100%; }} .filter-select {{ width: 100%; }} }}

        /* Days Grid */
        .days-section {{ margin-top: 40px; }}
        .days-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
        .day-card {{ background: var(--white); border: 1px solid var(--border); border-radius: 16px; padding: 20px; transition: all 0.3s ease; }}
        .day-card:hover {{ border-color: var(--blue-primary); box-shadow: var(--shadow-lg); transform: translateY(-2px); }}
        .day-card-header {{ display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }}
        .day-number {{ font-size: 2rem; font-weight: 700; color: var(--blue-primary); min-width: 50px; }}
        .day-name {{ font-size: 1.1rem; font-weight: 600; color: var(--text-dark); }}
        .day-month {{ font-size: 12px; color: var(--text-muted); }}
        .day-card-stats {{ display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap; }}
        .stat-pill {{ padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 500; }}
        .stat-pill.total {{ background: var(--bg-light); color: var(--text-secondary); }}
        .stat-pill.publico {{ background: var(--blue-light); color: var(--blue-primary); }}
        .stat-pill.privado {{ background: var(--orange-light); color: var(--orange-primary); }}
        .day-card-preview {{ background: var(--bg-light); border-radius: 8px; padding: 10px; margin-bottom: 12px; max-height: 250px; overflow-y: auto; }}
        .preview-event {{ display: flex; align-items: center; gap: 8px; padding: 6px 8px; background: var(--white); border-radius: 6px; margin-bottom: 4px; border-left: 3px solid transparent; font-size: 11px; }}
        .preview-event.publico {{ border-left-color: var(--blue-primary); }}
        .preview-event.privado {{ border-left-color: var(--orange-primary); }}
        .preview-time {{ font-weight: 600; color: var(--text-primary); min-width: 40px; }}
        .preview-title {{ color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        .day-card-link {{ display: flex; align-items: center; justify-content: center; gap: 8px; padding: 12px; background: var(--blue-primary); border-radius: 8px; color: white; text-decoration: none; font-weight: 600; font-size: 13px; transition: all 0.2s ease; }}
        .day-card-link:hover {{ background: var(--blue-dark); }}

        footer {{ text-align: center; padding: 40px 24px; border-top: 1px solid var(--border); margin-top: 40px; background: var(--white); }}
        .footer-text {{ color: var(--text-muted); font-size: 13px; }}
        @media (max-width: 768px) {{ .stats-row {{ gap: 20px; }} .stat-value {{ font-size: 1.8rem; }} .fairs-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <span class="logo-text">Art Week CDMX</span>
                <span class="logo-badge">2026</span>
            </div>
            <div style="font-size: 14px; color: var(--text-secondary);">2 - 8 de Febrero</div>
        </div>
    </header>

    <div class="search-filter-bar">
        <div class="search-filter-content">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Buscar eventos, galerías, artistas...">
                <i class="fa fa-search"></i>
            </div>
            <select class="filter-select" id="filterCategory">
                <option value="">Categoría</option>
                <option value="Público">🔵 Público</option>
                <option value="Privado">🟠 Privado</option>
            </select>
            <select class="filter-select" id="filterVenueType">
                <option value="">Tipo de venue</option>
                <option value="museum">🏛️ Museo</option>
                <option value="gallery">🖼️ Galería</option>
                <option value="hotel">🏨 Hotel</option>
                <option value="foundation">🏛️ Fundación</option>
                <option value="studio">🎨 Estudio</option>
                <option value="fair">🎪 Feria</option>
                <option value="special">⭐ Especial</option>
            </select>
            <select class="filter-select" id="filterTimePeriod">
                <option value="">Horario</option>
                <option value="morning">🌅 Mañana</option>
                <option value="afternoon">☀️ Tarde</option>
                <option value="evening">🌙 Noche</option>
            </select>
            <select class="filter-select" id="filterFair">
                <option value="">Feria</option>
                <option value="zonamaco">💎 ZonaMaco</option>
                <option value="material">🎨 Material</option>
                <option value="acme">⚡ ACME</option>
            </select>
            <button class="clear-filters" id="clearFilters" style="display: none;">
                <i class="fa fa-times"></i> Limpiar
            </button>
            <span class="filter-count" id="filterCount" style="display: none;"></span>
        </div>
    </div>

    <div class="container">
        <section class="hero">
            <h1>Semana del <span>Arte</span></h1>
            <p class="hero-subtitle">ZonaMaco + Material + Salón ACME • Ciudad de México</p>
            <div class="stats-row">
                <div class="stat-item"><div class="stat-value navy">{len(all_events) + len(material_events) + len(acme_events)}</div><div class="stat-label">Eventos</div></div>
                <div class="stat-item"><div class="stat-value blue">{total_venues}</div><div class="stat-label">Venues</div></div>
                <div class="stat-item"><div class="stat-value orange">3</div><div class="stat-label">Ferias</div></div>
            </div>
            <div class="category-pills">
                <div class="category-pill publico"><strong>{total_publico}</strong> Públicos</div>
                <div class="category-pill privado"><strong>{total_privado}</strong> Privados</div>
            </div>
            <div class="venue-badges">{venue_badges_html}</div>
        </section>

        <section class="fairs-section">
            <h2 class="section-title">Las Ferias</h2>
            <div class="fairs-grid">
                <div class="fair-card zonamaco">
                    <div class="fair-header">
                        <div class="fair-icon zonamaco"><i class="fa fa-gem"></i></div>
                        <div><div class="fair-name">ZonaMaco</div><div class="fair-venue">Centro Banamex</div></div>
                    </div>
                    <div class="fair-dates">📅 4-8 Feb • VIP Preview 4 Feb</div>
                    <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px;">La feria de arte contemporáneo más importante de América Latina. 200+ galerías internacionales.</p>
                    <a href="2026-02-05_Jueves.html" class="fair-link zonamaco">Ver programa ZonaMaco →</a>
                </div>
                <div class="fair-card material">
                    <div class="fair-header">
                        <div class="fair-icon material"><i class="fa fa-cube"></i></div>
                        <div><div class="fair-name">Material Art Fair</div><div class="fair-venue">Expo Reforma</div></div>
                    </div>
                    <div class="fair-dates">📅 5-8 Feb • VIP Preview 4 Feb</div>
                    <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px;">Arte emergente y diseño. Galerías jóvenes de México y Latinoamérica.</p>
                    <a href="material.html" class="fair-link material">Ver programa Material →</a>
                </div>
                <div class="fair-card acme">
                    <div class="fair-header">
                        <div class="fair-icon acme"><i class="fa fa-bolt"></i></div>
                        <div><div class="fair-name">Salón ACME</div><div class="fair-venue">Frontón México</div></div>
                    </div>
                    <div class="fair-dates">📅 5-8 Feb • VIP Preview 4 Feb</div>
                    <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 16px;">Arte independiente y experimental en el icónico Frontón México.</p>
                    <a href="acme.html" class="fair-link acme">Ver programa ACME →</a>
                </div>
            </div>
        </section>

        <section class="days-section">
            <h2 class="section-title">Programa ZonaMaco VIP por Día</h2>
            <div class="days-grid">{day_cards_html}</div>
        </section>
    </div>

    <footer><p class="footer-text">Art Week CDMX 2026 • ZonaMaco + Material + Salón ACME</p></footer>

    <script>
        const events = {events_json};
        const neighborhoods = {neighborhoods_json};
        let filteredEvents = [...events];

        // DOM elements
        const searchInput = document.getElementById('searchInput');
        const filterCategory = document.getElementById('filterCategory');
        const filterVenueType = document.getElementById('filterVenueType');
        const filterTimePeriod = document.getElementById('filterTimePeriod');
        const filterFair = document.getElementById('filterFair');
        const clearFiltersBtn = document.getElementById('clearFilters');
        const filterCountEl = document.getElementById('filterCount');
        const daysGrid = document.querySelector('.days-grid');

        function normalizeText(text) {{
            return (text || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        }}

        function applyFilters() {{
            const searchTerm = normalizeText(searchInput.value);
            const category = filterCategory.value;
            const venueType = filterVenueType.value;
            const timePeriod = filterTimePeriod.value;
            const fair = filterFair.value;

            filteredEvents = events.filter(e => {{
                // Search filter (title, organizer, description, neighborhood)
                if (searchTerm) {{
                    const searchable = normalizeText(e.title + ' ' + e.organizer + ' ' + e.description + ' ' + e.neighborhood);
                    if (!searchable.includes(searchTerm)) return false;
                }}
                // Category filter
                if (category && e.category !== category) return false;
                // Venue type filter
                if (venueType && e.venue_type !== venueType) return false;
                // Time period filter
                if (timePeriod && e.time_period !== timePeriod) return false;
                // Fair filter
                if (fair && e.fair !== fair) return false;
                return true;
            }});

            updateUI();
        }}

        function updateUI() {{
            const hasFilters = searchInput.value || filterCategory.value || filterVenueType.value || filterTimePeriod.value || filterFair.value;
            clearFiltersBtn.style.display = hasFilters ? 'flex' : 'none';

            if (hasFilters) {{
                filterCountEl.style.display = 'inline';
                filterCountEl.textContent = filteredEvents.length + ' de ' + events.length;
            }} else {{
                filterCountEl.style.display = 'none';
            }}

            // Group filtered events by day
            const eventsByDay = {{}};
            filteredEvents.forEach(e => {{
                const day = new Date(e.date).getDay();
                const dayIndex = day === 0 ? 6 : day - 1;
                if (!eventsByDay[dayIndex]) eventsByDay[dayIndex] = [];
                eventsByDay[dayIndex].push(e);
            }});

            // Update day cards
            document.querySelectorAll('.day-card').forEach(card => {{
                const dow = parseInt(card.dataset.day);
                const preview = card.querySelector('.day-card-preview');
                const statsEl = card.querySelector('.day-card-stats');
                const dayEvents = eventsByDay[dow] || [];

                // Update stats
                const publico = dayEvents.filter(e => e.category === 'Público').length;
                const privado = dayEvents.filter(e => e.category === 'Privado').length;
                statsEl.innerHTML = `
                    <div class="stat-pill total">${{dayEvents.length}} eventos</div>
                    <div class="stat-pill publico">${{publico}} púb</div>
                    <div class="stat-pill privado">${{privado}} priv</div>
                `;

                // Update preview
                const html = dayEvents.map(e => `<div class="preview-event ${{e.category.toLowerCase()}}"><span class="preview-time">${{e.time}}</span><span class="preview-title">${{e.organizer}}</span></div>`).join('');
                preview.innerHTML = html || '<p style="color: var(--text-muted); font-size: 11px; text-align: center; padding: 15px;">Sin eventos</p>';

                // Dim cards with no events
                card.style.opacity = dayEvents.length === 0 && hasFilters ? '0.5' : '1';
            }});

            // Show/hide no results message
            let noResults = document.getElementById('noResults');
            if (filteredEvents.length === 0 && hasFilters) {{
                if (!noResults) {{
                    noResults = document.createElement('div');
                    noResults.id = 'noResults';
                    noResults.className = 'no-results';
                    noResults.innerHTML = '<i class="fa fa-search"></i><p>No se encontraron eventos con los filtros seleccionados</p>';
                    daysGrid.after(noResults);
                }}
                noResults.style.display = 'block';
            }} else if (noResults) {{
                noResults.style.display = 'none';
            }}
        }}

        function clearFilters() {{
            searchInput.value = '';
            filterCategory.value = '';
            filterVenueType.value = '';
            filterTimePeriod.value = '';
            filterFair.value = '';
            applyFilters();
        }}

        // Event listeners
        searchInput.addEventListener('input', applyFilters);
        filterCategory.addEventListener('change', applyFilters);
        filterVenueType.addEventListener('change', applyFilters);
        filterTimePeriod.addEventListener('change', applyFilters);
        filterFair.addEventListener('change', applyFilters);
        clearFiltersBtn.addEventListener('click', clearFilters);

        // Keyboard shortcut: Escape clears filters
        document.addEventListener('keydown', e => {{
            if (e.key === 'Escape') clearFilters();
            if (e.key === '/' && e.target.tagName !== 'INPUT') {{
                e.preventDefault();
                searchInput.focus();
            }}
        }});

        // Initial render
        applyFilters();
    </script>
</body>
</html>
"""

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "maps")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("   ZonaMaco 2026 - Generador de Mapas v4.2")
    print("   + Material Art Fair + Salón ACME")
    print("   + Search & Filter (index + day maps)")
    print("=" * 60)

    # Parse all events
    events = parse_events()
    material_events = parse_material_events()
    acme_events = parse_acme_events()

    # Validate all events (prints report)
    all_events = events + material_events + acme_events
    validate_events(all_events)

    print(f"\n📊 ZonaMaco: {len(events)} eventos")
    print(f"📊 Material: {len(material_events)} eventos")
    print(f"📊 ACME: {len(acme_events)} eventos")
    print(f"📊 TOTAL: {len(all_events)} eventos")
    print(f"\n🔵 Públicos: {sum(1 for e in all_events if e.category == 'Público')}")
    print(f"🟠 Privados: {sum(1 for e in all_events if e.category == 'Privado')}")

    # Group by day
    events_by_day: Dict[datetime, List[Event]] = {}
    for event in events:
        day = event.date.replace(hour=0, minute=0, second=0, microsecond=0)
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)

    sorted_days = sorted(events_by_day.keys())
    print(f"\n📅 Días: {len(sorted_days)}")

    days_info = []
    print("\nGenerando mapas ZonaMaco...")

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

    # Create fair-specific maps
    print("\nGenerando mapas de ferias...")
    create_fair_map(material_events, "material", "Material Art Fair", os.path.join(output_dir, "material.html"))
    print("  ✅ Material Art Fair")
    create_fair_map(acme_events, "acme", "Salón ACME", os.path.join(output_dir, "acme.html"))
    print("  ✅ Salón ACME")

    # Create index
    create_premium_index(days_info, events, output_dir, material_events, acme_events)

    # Also copy to docs for GitHub Pages
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
    os.makedirs(docs_dir, exist_ok=True)
    import shutil
    for f in os.listdir(output_dir):
        if f.endswith('.html'):
            shutil.copy(os.path.join(output_dir, f), os.path.join(docs_dir, f))

    print(f"\n{'=' * 60}")
    print(f"✨ Mapas generados en: {output_dir}")
    print(f"✨ GitHub Pages en: {docs_dir}")
    print(f"🌐 Abre index.html en tu navegador")
    print("=" * 60)


if __name__ == "__main__":
    main()
