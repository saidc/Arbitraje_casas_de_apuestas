
from datetime import datetime, timedelta, timezone

# Función para generar el rango de fechas
def generar_rango_fechas():
    # Fecha y hora actual en UTC con reconocimiento de zona horaria
    ahora = datetime.now(timezone.utc)

    # Fecha y hora de inicio (ajustada al formato especificado)
    fecha_inicio = ahora.replace(hour=5, minute=0, second=0, microsecond=0)
    if ahora.hour < 5:
        # Si la hora actual es antes de las 5 AM, ajustamos al día anterior
        fecha_inicio -= timedelta(days=1)

    # Fecha y hora de fin (3 días después del inicio)
    fecha_fin = fecha_inicio + timedelta(days=3, seconds=-1)

    # Convertir a formato ISO 8601 con 'Z' indicando UTC
    fecha_inicio_str = fecha_inicio.isoformat().replace("+00:00", "Z")
    fecha_fin_str = fecha_fin.isoformat().replace("+00:00", "Z")

    # Crear el rango de fechas en el formato requerido
    rango_fechas = f"startsBefore={fecha_fin_str}&startsOnOrAfter={fecha_inicio_str}"
    return rango_fechas