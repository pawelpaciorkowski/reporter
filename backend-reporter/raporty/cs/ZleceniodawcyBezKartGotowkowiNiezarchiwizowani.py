from datasources.kakl import KaKlDatasource
from dialog import (
    Dialog,
    VBox,
    LabSelector,
    ValidationError,
)
from tasks import TaskGroup
from helpers import (
    prepare_for_json,
)

MENU_ENTRY = "Zleceniodawcy gotówkowi bez kart, niezarchiwizowani"

REQUIRE_ROLE = ["C-CS"]
ADD_TO_ROLE = ["R-DYR", "R-PM"]

SQL = """
    select kz.id, kz.nazwa, kz.symbol from kartoteki_zleceniodawca kz
    left join kakl_kartaklienta_zleceniodawcy kkz on kz.id = kkz.zleceniodawca_id
    left join kartoteki_platnik kp on kz.platnik_id = kp.id
    left join kartoteki_laboratorium_platnicy klp on klp.platnik_id = kp.id
    left join kartoteki_laboratorium kl on kl.id = klp.laboratorium_id
    left join kakl_kartaklienta kk on kkz.id = kk.id
    where kz.archived = false and kz.archived_manually = false AND kk.id IS null and kp.gotowkowe = true and kl.symbol in %s;
"""

LAUNCH_DIALOG = Dialog(
    title="Zestawienie Zleceniodawców gotówkowych, którzy nie mają podpiętej karty klienta oraz nie są zarchiwizowani",
    panel=VBox(
        LabSelector(multiselect=True, field="laboratoria", title="Laboratorium"),
    ),
)


def start_report(params):
    report = TaskGroup(__PLUGIN__, params)
    params = LAUNCH_DIALOG.load_params(params)
    if len(params["laboratoria"]) == 0:
        raise ValidationError("")
    task = {"type": "noc", "priority": 1, "params": params, "function": "raport_djalab"}
    report.create_task(task)
    report.save()
    return report


def raport_djalab(task_params):
    params = task_params["params"]
    kakl = KaKlDatasource()
    cols, rows = kakl.select(SQL, [tuple(params["laboratoria"])])
    return {"type": "table", "header": cols, "data": prepare_for_json(rows)}
