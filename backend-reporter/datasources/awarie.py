from .postgres import PostgresDatasource
import logging
from config import Config

# Utwórz logger
log = logging.getLogger(__name__)

class Awarie(PostgresDatasource):
    def __init__(self, read_write=False):
        cfg = Config()
        super().__init__(cfg.DATABASE_AWARIE, read_write=read_write)



    def lista_awarii(self, model_name=None, symbol=None, serial_number=None, workshop_name=None, device_type=None, report_number=None):
        sql = """
        SELECT 
            d.model_name AS model_name,
            d.symbol AS device_symbol,
            d.serial_number,
            s.type_name AS service_type,
            s.notification_date,
            s.arrival_date,
            s.resolve_date,
            s.company_name,
            s.cost,
            s.downtime_hours,
            s.report_number,
            d.laboratory_name,
            d.workshop_name,
            d.type_name AS device_type
        FROM 
            v_service_event_details s
        JOIN 
            v_devices d ON s.device_id = d.id
        WHERE 1=1
        """
        params = []

        # Dynamiczne dodawanie filtrów
        if model_name:
            sql += " AND d.model_name ILIKE %s"
            params.append(f"%{model_name}%")
        if symbol:
            sql += " AND d.symbol ILIKE %s"
            params.append(f"%{symbol}%")
        if serial_number:
            sql += " AND d.serial_number ILIKE %s"
            params.append(f"%{serial_number}%")
        if workshop_name:
            sql += " AND d.workshop_name ILIKE %s"
            params.append(f"%{workshop_name}%")
        if device_type:
            sql += " AND d.type_name ILIKE %s"
            params.append(f"%{device_type}%")
        if report_number:
            sql += " AND s.report_number ILIKE %s"
            params.append(f"%{report_number}%")

        sql += " ORDER BY d.name, s.notification_date"

        
        return self.select(sql, params)
