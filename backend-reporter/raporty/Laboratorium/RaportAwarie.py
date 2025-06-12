import datetime
from dialog import Dialog, VBox, TextInput, DateInput, InfoText
from tasks import TaskGroup
from helpers import prepare_for_json
from datasources.awarie import Awarie

MENU_ENTRY = 'Raport awarii urządzeń'

LAUNCH_DIALOG = Dialog(title=MENU_ENTRY, panel=VBox(
    TextInput(field="model_name", title="Filtruj po nazwie", required=False),
    TextInput(field="symbol", title="Filtruj po symbolu", required=False),
    TextInput(field="serial_number", title="Filtruj po numerze seryjnym", required=False),
    TextInput(field="workshop_name", title="Filtruj po pracowni", required=False),
    TextInput(field="device_type", title="Filtruj po rodzaju sprzętu", required=False),
    TextInput(field="report_number", title="Filtruj po numerze raportu serwisowego", required=False),
))




def start_report(params):
    loaded_params = LAUNCH_DIALOG.load_params(params)

    print(f"DEBUG: RAW params before load: {params}")
    print(f"DEBUG: Loaded params from Dialog: {loaded_params}")

    # Lista pól tekstowych do oczyszczenia
    for field in ['model_name','symbol', 'serial_number', 'workshop_name', 'device_type', 'report_number']:
        value = loaded_params.get(field)
        if value is not None:
            value = value.strip()
            if value == '':
                value = None
            loaded_params[field] = value
        else:
            loaded_params[field] = None

    print(f"DEBUG: Final params used for task: {loaded_params}")

    report = TaskGroup(__PLUGIN__, loaded_params)

    task = {
        'type': 'ick',
        'priority': 0,
        'params': loaded_params,
        'function': 'raport',
    }
    report.create_task(task)
    report.save()

    return report




def raport(task_params):
    print(f"DEBUG: TASK PARAMS W RAPORCIE: {task_params}")

    params = task_params.get('params', {}) if task_params else {}

    model_name = params.get('model_name')
    symbol = params.get('symbol')
    serial_number = params.get('serial_number')
    workshop_name = params.get('workshop_name')
    device_type = params.get('device_type')
    report_number = params.get('report_number')

    awarie = Awarie()
    columns, rows = awarie.lista_awarii(
        model_name=model_name,
        symbol=symbol,
        serial_number=serial_number,
        workshop_name=workshop_name,
        device_type=device_type,
        report_number=report_number,
    )

    header = [
        'Nazwa urządzenia', 'Symbol', 'Numer seryjny', 'Rodzaj serwisu', 'Data zgłoszenia',
        'Data przybycia', 'Data zakończenia', 'Firma serwisująca', 'Koszt',
        'Czas przestoju (godziny)', 'Nr raportu serwisowego', 'Laboratorium',
        'Pracownia', 'Rodzaj sprzętu'
    ]

    data = [list(row) for row in rows]

    return {
        "type": "table",
        "header": header,
        "data": prepare_for_json(data)
    }

