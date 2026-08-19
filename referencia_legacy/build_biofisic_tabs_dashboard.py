from __future__ import annotations

import json
import math
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
OUT_DIR = PROJECT_DIR / "outputs"
HTML_OUT = OUT_DIR / "dashboard_vendas_mar_abr_mai_2026.html"
DEFAULT_CSV_DIR = Path(r"C:\Users\biofi\Downloads\CSV")


BRANCH_NAMES = {
    "1": "ITAJUBÁ - CENTRO",
    "2": "ITAJUBÁ - VARGINHA",
    "3": "ITAJUBÁ - CAPITÃO GOMES",
    "4": "POUSO ALEGRE - FOCH",
    "5": "POÇOS DE CALDAS",
    "6": "TRÊS CORAÇÕES - CENTRO",
    "7": "ITU",
    "8": "BATATAIS",
    "9": "GUARATINGUETÁ - BEIRA RIO",
    "10": "GUARATINGUETÁ - JK",
    "11": "TRÊS CORAÇÕES - REI PELÉ",
    "12": "LORENA",
    "13": "POUSO ALEGRE - FÁTIMA",
    "14": "JACAREÍ",
}


# Ordem oficial por inauguração. Esta lista não segue a implantação/ID do CRM.
UNIT_ORDER = [
    "Capitão Gomes",
    "Itajubá Centro",
    "Itajubá Varginha",
    "Pouso Alegre Foch",
    "Poços de Caldas",
    "Três Corações RP",
    "Batatais",
    "Itu",
    "Guaratinguetá BR",
    "Guaratinguetá JK",
    "Três Corações CE",
    "Lorena",
    "Pouso Alegre Fátima",
    "Jacareí",
]

# Siglas operacionais usadas no centro das roscas do indicador de evasão.
CHURN_UNIT_CODES = {
    "Rede": "REDE",
    "Capitão Gomes": "CG",
    "Itajubá Centro": "CE",
    "Itajubá Varginha": "VG",
    "Pouso Alegre Foch": "PA",
    "Poços de Caldas": "PC",
    "Três Corações RP": "TC1",
    "Batatais": "BAT",
    "Itu": "ITU",
    "Guaratinguetá BR": "GUA1",
    "Guaratinguetá JK": "GUA2",
    "Três Corações CE": "TC2",
    "Lorena": "LOR",
    "Pouso Alegre Fátima": "PA2",
    "Jacareí": "JAC",
}

# Metas mensais do gráfico de ativos por unidade. Atualizar este mapa quando
# uma nova linha "Diamante Total" for aprovada para o mês.
# Metas aprovadas pelo usuário para agosto/2026.
ACTIVE_GOALS_BY_MONTH = {
    "2026-08": {
        "Capitão Gomes": 1639,
        "Itajubá Centro": 849,
        "Itajubá Varginha": 1229,
        "Pouso Alegre Foch": 907,
        "Poços de Caldas": 1651,
        "Três Corações RP": 1498,
        "Batatais": 1503,
        "Itu": 1533,
        "Guaratinguetá BR": 1281,
        "Guaratinguetá JK": 1241,
        "Três Corações CE": 1415,
        "Lorena": 1328,
        "Pouso Alegre Fátima": 1267,
        "Jacareí": 1653,
    },
}

EXCLUDED_UNITS = {"BioFisic - Treinamento"}
MEDAL_GOLD = "★★★"
MEDAL_SILVER = "★★"
MEDAL_BRONZE = "★"
MEDAL_SEQUENCE = [MEDAL_GOLD, MEDAL_SILVER, MEDAL_BRONZE]
MONTH_ABBR = {
    1: "jan",
    2: "fev",
    3: "mar",
    4: "abr",
    5: "mai",
    6: "jun",
    7: "jul",
    8: "ago",
    9: "set",
    10: "out",
    11: "nov",
    12: "dez",
}
WEEKDAY_ABBR = {
    0: "seg",
    1: "ter",
    2: "qua",
    3: "qui",
    4: "sex",
    5: "sáb",
    6: "dom",
}
WEEKDAY_FULL = {
    0: "Segunda",
    1: "Terça",
    2: "Quarta",
    3: "Quinta",
    4: "Sexta",
    5: "Sábado",
    6: "Domingo",
}
AGE_BINS = [0, 18, 25, 35, 45, 60, 200]
AGE_BAND_LABELS = [
    "Adolescentes - até 18 anos",
    "Jovens - 19 a 25 anos",
    "Jovens Adultos - 26 a 35 anos",
    "Adultos - 36 a 45 anos",
    "Vitalidade - 46 a 60 anos",
    "Longevidade - 61 anos ou mais",
]
GENDER_FILTER_OPTIONS = ["Sexo feminino", "Sexo masculino", "Não informado"]
SALE_VALUE_BUCKETS = [0.99, 9.90, 19.90, 29.90, 39.90, 89.90, 99.90, 107.90, 137.90]
SALE_VALUE_BUCKET_TOLERANCE = 3.0
CANCEL_VALUE_BUCKETS = sorted(set(SALE_VALUE_BUCKETS + [169.90]))
EXCLUDED_SALES_COLLABORATORS = {
    "joao vitor",
    "joao victor",
    "juan",
    "isaias",
    "natalia vicente",
    "rafaela domingues",
    "paula renata",
    "janaina",
    "evelin giglio",
}
EXCLUDED_SALES_CONTRACT_PATTERN = re.compile(
    r"\bmy\s*nutri\b|\bmynutri\b"
)

BRANCH_NAMES = {
    "1": "Itajubá Centro",
    "2": "Itajubá Varginha",
    "3": "Capitão Gomes",
    "4": "Pouso Alegre Foch",
    "5": "Poços de Caldas",
    "6": "Três Corações CE",
    "7": "Itu",
    "8": "Batatais",
    "9": "Guaratinguetá BR",
    "10": "Guaratinguetá JK",
    "11": "Três Corações RP",
    "12": "Lorena",
    "13": "Pouso Alegre Fátima",
    "14": "Jacareí",
    "999": "BioFisic - Treinamento",
}

REVENUE_BRANCH_NAMES = {
    "1": "Itajubá Centro",
    "2": "Itajubá Varginha",
    "3": "Capitão Gomes",
    "4": "Pouso Alegre Foch",
    "5": "Poços de Caldas",
    "6": "Três Corações RP",
    "7": "Itu",
    "8": "Batatais",
    "9": "Guaratinguetá BR",
    "10": "Guaratinguetá JK",
    "11": "Três Corações CE",
    "12": "Lorena",
    "13": "Pouso Alegre Fátima",
    "14": "Jacareí",
}

WELLHUB_REVENUE_RULES = {
    "1": (9.58, 115.00),
    "2": (9.58, 115.00),
    "3": (10.63, 138.15),
    "4": (9.58, 115.00),
    "5": (9.58, 115.00),
    "6": (10.32, 138.02),
    "7": (11.51, 138.15),
    "8": (11.51, 138.15),
    "9": (11.50, 138.02),
    "10": (11.50, 138.02),
    "11": (9.58, 115.00),
    "12": (10.00, 110.00),
    "13": (10.00, 110.00),
    "14": (0.00, 0.00),
}

TOTALPASS_REVENUE_RULES = {
    "1": (11.10, 121.00),
    "2": (11.10, 121.00),
    "3": (11.10, 121.00),
    "4": (11.10, 121.00),
    "5": (11.10, 121.00),
    "6": (11.10, 121.00),
    "7": (11.10, 121.00),
    "8": (11.10, 121.00),
    "9": (11.10, 121.00),
    "10": (12.27, 134.97),
    "11": (11.10, 121.00),
    "12": (11.10, 121.00),
    "13": (11.10, 121.00),
    "14": (0.00, 0.00),
}

# Regras aprovadas para a aba Financeiro. O teto e aplicado por pessoa, unidade
# e competencia mensal, depois da contagem de check-ins validados.
FINANCE_WELLHUB_RATE = 11.51
FINANCE_WELLHUB_CAP = 138.13
FINANCE_TOTALPASS_RATE = 11.10
FINANCE_TOTALPASS_CAP = 144.26


def norm_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def norm_key(value: object) -> str:
    text = unicodedata.normalize("NFKD", norm_text(value)).encode("ascii", "ignore").decode("ascii")
    return text.lower()


UNIT_ALIASES = {
    norm_key("Capitão Gomes"): "Capitão Gomes",
    norm_key("ITAJUBÁ - CAPITÃO GOMES"): "Capitão Gomes",
    norm_key("Itajubá Centro"): "Itajubá Centro",
    norm_key("ITAJUBÁ - CENTRO"): "Itajubá Centro",
    norm_key("Itajubá Varginha"): "Itajubá Varginha",
    norm_key("ITAJUBÁ - VARGINHA"): "Itajubá Varginha",
    norm_key("Pouso Alegre Foch"): "Pouso Alegre Foch",
    norm_key("POUSO ALEGRE - FOCH"): "Pouso Alegre Foch",
    norm_key("Poços de Caldas"): "Poços de Caldas",
    norm_key("ACADEMIA BIOFISIC PC"): "Poços de Caldas",
    norm_key("POÇOS DE CALDAS"): "Poços de Caldas",
    norm_key("Três Corações RP"): "Três Corações RP",
    norm_key("TRÊS CORAÇÕES - REI PELÉ"): "Três Corações RP",
    norm_key("Batatais"): "Batatais",
    norm_key("Itu"): "Itu",
    norm_key("Guaratinguetá BR"): "Guaratinguetá BR",
    norm_key("GUARATINGUETÁ - BEIRA RIO"): "Guaratinguetá BR",
    norm_key("Guaratinguetá JK"): "Guaratinguetá JK",
    norm_key("GUARATINGUETÁ - JK"): "Guaratinguetá JK",
    norm_key("Três Corações CE"): "Três Corações CE",
    norm_key("TRÊS CORAÇÕES - CENTRO"): "Três Corações CE",
    norm_key("Lorena"): "Lorena",
    norm_key("Pouso Alegre Fátima"): "Pouso Alegre Fátima",
    norm_key("POUSO ALEGRE - FÁTIMA"): "Pouso Alegre Fátima",
    norm_key("Jacareí"): "Jacareí",
    norm_key("BIOFISIC - TREINAMENTO"): "BioFisic - Treinamento",
}


def read_csv_flexible(path: Path) -> pd.DataFrame:
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "latin1", "cp1252"):
        try:
            df = pd.read_csv(path, sep=None, engine="python", dtype=str, encoding=encoding)
            df.columns = [norm_text(c) for c in df.columns]
            return df
        except UnicodeDecodeError as exc:
            last_error = exc
    raise ValueError(f"não foi possível ler {path.name}: {last_error}")


def source_upload_label(source: str | Path | None) -> str:
    if not source:
        return "Aguardando upload"
    path = Path(source)
    timestamps: list[float] = []
    try:
        if path.is_file():
            timestamps.append(path.stat().st_mtime)
        elif path.is_dir():
            for item in path.iterdir():
                if item.is_file() and item.suffix.lower() in {".csv", ".xlsx", ".zip"}:
                    timestamps.append(item.stat().st_mtime)
            if not timestamps:
                timestamps.append(path.stat().st_mtime)
    except OSError:
        return "Aguardando upload"
    if not timestamps:
        return "Aguardando upload"
    uploaded_at = datetime.fromtimestamp(max(timestamps))
    return f"Último upload: {uploaded_at:%d/%m/%Y %H:%M}"


def parse_date(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype="datetime64[ns]")
    if len(series) == 0:
        return pd.Series(dtype="datetime64[ns]", index=series.index)
    text = series.astype(str).str.strip().replace({
        "": np.nan,
        "nan": np.nan,
        "None": np.nan,
        "NaT": np.nan,
    })
    try:
        parsed = pd.to_datetime(text, errors="coerce", format="ISO8601")
    except (TypeError, ValueError):
        parsed = pd.to_datetime(text, errors="coerce")
    parsed = pd.Series(parsed, index=series.index)
    missing = parsed.isna() & text.notna()
    if missing.any():
        fallback = pd.to_datetime(text[missing], errors="coerce", dayfirst=True)
        parsed.loc[missing] = fallback
    return parsed


def parse_embedded_date(series: pd.Series | None) -> pd.Series:
    """Parse ISO or Brazilian dates even when the cell contains descriptive text."""
    if series is None:
        return pd.Series(dtype="datetime64[ns]")
    text = series.astype(str).str.strip()
    extracted = text.str.extract(r"(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})", expand=False)
    return parse_date(extracted.where(extracted.notna(), text))


def sales_date_series(frame: pd.DataFrame) -> pd.Series:
    """Column B in VENDAS is dataVenda; accept data_venda as a defensive alias."""
    for column in ("dataVenda", "data_venda"):
        if column in frame.columns:
            return frame[column]
    return pd.Series(index=frame.index, dtype=str)


def parse_number(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype=float)
    text = (
        series.astype(str)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "None": np.nan, "a receber": np.nan})
        .str.replace("R$", "", regex=False)
        .str.replace(" ", "", regex=False)
    )

    def convert(value: object) -> float:
        if pd.isna(value):
            return np.nan
        value = str(value)
        if "," in value and "." in value:
            value = value.replace(".", "").replace(",", ".")
        elif "," in value:
            value = value.replace(",", ".")
        return pd.to_numeric(value, errors="coerce")

    return text.map(convert)


def parse_filter_date(value: object) -> pd.Timestamp | None:
    text = norm_text(value)
    if not text:
        return None
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        parsed = pd.to_datetime(text, errors="coerce", dayfirst=True)
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).normalize()


def age_values(dates: pd.Series) -> pd.Series:
    birth = parse_date(dates)
    today = pd.Timestamp("2026-06-24")
    return ((today - birth).dt.days / 365.25).where(lambda s: s.between(10, 100))


def age_band_series(dates: pd.Series) -> pd.Series:
    ages = age_values(dates)
    return pd.cut(ages, bins=AGE_BINS, labels=AGE_BAND_LABELS, right=True)


def normalize_dashboard_filters(filters: dict | None) -> dict:
    raw = filters or {}
    unit_by_key = {norm_key(item): item for item in UNIT_ORDER}

    def split_filter_values(value: object) -> list:
        if isinstance(value, str):
            return re.split(r"\|\||;", value)
        if isinstance(value, (list, tuple, set)):
            return list(value)
        return [value]

    raw_units = raw.get("unitFilters", raw.get("unitFilter", ""))
    unit_parts = split_filter_values(raw_units)
    units = []
    for raw_unit in unit_parts:
        unit_text = norm_text(raw_unit)
        unit = unit_text if unit_text in UNIT_ORDER else unit_by_key.get(norm_key(unit_text), branch_name(unit_text))
        if unit in UNIT_ORDER and unit not in units:
            units.append(unit)

    ages = []
    for raw_age in split_filter_values(raw.get("ageFilters", raw.get("ageFilter", ""))):
        age = norm_text(raw_age)
        if age in AGE_BAND_LABELS and age not in ages:
            ages.append(age)

    genders = []
    for raw_gender in split_filter_values(raw.get("genderFilters", raw.get("genderFilter", ""))):
        gender_raw = norm_text(raw_gender)
        gender = clean_gender(gender_raw) if gender_raw else ""
        if gender in GENDER_FILTER_OPTIONS and gender not in genders:
            genders.append(gender)

    start = parse_filter_date(raw.get("periodStart", ""))
    end = parse_filter_date(raw.get("periodEnd", ""))
    if start is not None and end is not None and start > end:
        start, end = end, start
    return {
        "periodStart": start.strftime("%Y-%m-%d") if start is not None else "",
        "periodEnd": end.strftime("%Y-%m-%d") if end is not None else "",
        "unitFilter": "||".join(units),
        "unitFilters": units,
        "ageFilter": "||".join(ages),
        "ageFilters": ages,
        "genderFilter": "||".join(genders),
        "genderFilters": genders,
    }


def filter_frame_by_date(frame: pd.DataFrame, dates: pd.Series, start: pd.Timestamp | None, end: pd.Timestamp | None) -> pd.DataFrame:
    if frame.empty or (start is None and end is None):
        return frame
    mask = dates.notna()
    if start is not None:
        mask &= dates.ge(start)
    if end is not None:
        mask &= dates.lt(end + pd.Timedelta(days=1))
    return frame.loc[mask].copy()


def infer_analysis_date(*date_series: pd.Series, fallback: pd.Timestamp | None = None) -> pd.Timestamp:
    """Use the loaded data as the analysis clock, not the machine date.

    This keeps month-based indicators stable when the dashboard is opened on a
    later month but the uploaded CSVs still represent the previous competence.
    """
    fallback_date = (fallback or pd.Timestamp.today()).normalize()
    maxima = []
    for series in date_series:
        if series is None or len(series) == 0:
            continue
        parsed = pd.to_datetime(series, errors="coerce")
        if parsed.notna().any():
            maxima.append(pd.Timestamp(parsed.max()).normalize())
    if not maxima:
        return fallback_date
    return min(max(maxima), fallback_date)


def id_series(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(dtype=str)
    values = series.where(series.notna(), "").astype(str)
    values = values.str.replace(r"\.0$", "", regex=True).str.strip()
    return values.mask(values.isin({"nan", "None", "<NA>", "NaT"}), "")


def br_int(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "0"
    return f"{int(round(float(value))):,}".replace(",", ".")


def br_money(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        value = 0
    text = f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {text}"


def br_pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        value = 0
    return f"{float(value):.1f}%".replace(".", ",")


def branch_name(value: object) -> str:
    key = norm_text(value).replace(".0", "")
    if key in BRANCH_NAMES:
        return BRANCH_NAMES[key]
    return UNIT_ALIASES.get(norm_key(key), key or "Sem unidade")


def branch_id_key(value: object) -> str:
    return norm_text(value).replace(".0", "")


def revenue_branch_name(value: object) -> str:
    key = branch_id_key(value)
    if key in REVENUE_BRANCH_NAMES:
        return REVENUE_BRANCH_NAMES[key]
    return UNIT_ALIASES.get(norm_key(value), norm_text(value) or "Sem unidade")


def clean_plan(value: object) -> str:
    text = norm_text(value)
    text = re.sub(r"^Contrato\s*-\s*", "", text, flags=re.I)
    text = re.sub(r"\s*-\s*Início em:.*$", "", text, flags=re.I)
    key = norm_key(text)
    if not text:
        return "Sem contrato"
    if "fidelidade slim" in key:
        return "Fidelidade Slim Recorrente"
    if "fidelidade sangue verde" in key:
        return "Fidelidade Sangue Verde Recorrente"
    if "sangue verde plus" in key:
        return "Sangue Verde Plus"
    if "grupo sangue verde" in key or "sangue verde grupo" in key:
        return "Grupo Sangue Verde Recorrente"
    if "militar" in key:
        return "Sangue Verde Militar"
    if "basico" in key:
        return "Básico Recorrente"
    if "mensal recorrente" in key:
        return "Mensal Recorrente"
    if "sangue verde recorrente" in key:
        return "Sangue Verde Recorrente"
    if "sangue verde 2026" in key or key == "sangue verde":
        return "Sangue Verde"
    return text


def clean_plan(value: object) -> str:
    text = norm_text(value)
    text = re.sub(r"^Contrato\s*-\s*", "", text, flags=re.I)
    text = re.sub(r"\s*-\s*In.*$", "", text, flags=re.I)
    key = norm_key(text)
    if not text:
        return "Não Recorrente"
    if "plus" in key:
        return "SV Plus"
    if "slim" in key:
        return "Fidelidade Slim Recorrente"
    if "militar" in key:
        return "SV Militar"
    if "grupo" in key:
        return "SV Grupo"
    if "sangue verde" in key:
        return "Sangue Verde"
    if "recorr" in key or "basico" in key or "mensal" in key or "personal" in key:
        return "Planos Recorrentes"
    return "Não Recorrente"


def clean_gender(value: object) -> str:
    text = norm_text(value)
    key = norm_key(text)
    if not key or key in {"uninformed", "unidentified", "nao informado", "sem informacao", "sem sexo"}:
        return "Não informado"
    if key in {"female", "feminino", "f", "mulher", "sexo feminino"}:
        return "Sexo feminino"
    if key in {"male", "masculino", "m", "homem", "sexo masculino"}:
        return "Sexo masculino"
    return text


def gender_distribution_rows(series: pd.Series) -> list[dict]:
    rows = top_rows(series.map(clean_gender), 6, len(series))
    for row in rows:
        label = str(row.get("label", ""))
        if label.startswith("Sexo "):
            row["label"] = label.removeprefix("Sexo ").capitalize()
    return rows


def excluded_sales_collaborator(value: object) -> bool:
    key = norm_key(value)
    return any(key == blocked or key.startswith(f"{blocked} ") for blocked in EXCLUDED_SALES_COLLABORATORS)


def excluded_sales_contract(value: object) -> bool:
    """Exclude MyNutri contracts from sales indicators."""
    return bool(EXCLUDED_SALES_CONTRACT_PATTERN.search(norm_key(value)))


def normalize_realtime_contract_sales(
    sales: pd.DataFrame,
    billing: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validate real-time contracts against FATURAMENTO by member and exact cents."""
    if "dataSale" not in sales.columns:
        return sales.copy(), pd.DataFrame(columns=sales.columns)

    work = sales.copy().rename(columns={
        "idBranch": "id_unidade",
        "idSale": "id_venda",
        "dataSale": "dataVenda",
        "item": "contrato",
        "nomeColaborador": "colaborador_responsavel",
    })
    billing_ids = id_series(
        billing.get("idMember", pd.Series(index=billing.index, dtype=str))
    )
    billing_values = parse_number(
        billing.get("valor_real", pd.Series(index=billing.index, dtype=float))
    )
    billing_units = id_series(
        billing.get("id_unidade", pd.Series(index=billing.index, dtype=str))
    )
    billed_cents_by_member: dict[str, set[int]] = {}
    billed_unit_by_key: dict[tuple[str, int], str] = {}
    for member_id, value, unit_id in zip(
        billing_ids.tolist(), billing_values.tolist(), billing_units.tolist()
    ):
        if not member_id or pd.isna(value) or float(value) <= 0:
            continue
        cents = int(round(float(value) * 100))
        billed_cents_by_member.setdefault(member_id, set()).add(cents)
        if unit_id:
            billed_unit_by_key[(member_id, cents)] = unit_id

    member_ids = id_series(
        work.get("idMember", pd.Series(index=work.index, dtype=str))
    )
    item_values = parse_number(
        work.get("itemValue", pd.Series(index=work.index, dtype=float))
    )
    sale_values = parse_number(
        work.get("saleValue", pd.Series(index=work.index, dtype=float))
    )
    valid: list[bool] = []
    matched_values: list[float] = []
    matched_units: list[str] = []
    realtime_units = id_series(
        work.get("id_unidade", pd.Series(index=work.index, dtype=str))
    )
    for member_id, item_value, sale_value in zip(
        member_ids.tolist(), item_values.tolist(), sale_values.tolist()
    ):
        billed = billed_cents_by_member.get(member_id, set())
        sale_cents = (
            int(round(float(sale_value) * 100))
            if pd.notna(sale_value) and float(sale_value) > 0
            else None
        )
        item_cents = (
            int(round(float(item_value) * 100))
            if pd.notna(item_value) and float(item_value) > 0
            else None
        )
        matched_cents = (
            sale_cents if sale_cents is not None and sale_cents in billed
            else item_cents if item_cents is not None and item_cents in billed
            else None
        )
        valid.append(matched_cents is not None)
        fallback = sale_cents if sale_cents is not None else item_cents
        matched_values.append(float((matched_cents if matched_cents is not None else fallback or 0) / 100))
        original_unit = realtime_units.iloc[len(matched_units)] if len(realtime_units) else ""
        matched_units.append(
            billed_unit_by_key.get((member_id, matched_cents), original_unit)
            if matched_cents is not None and original_unit not in BRANCH_NAMES
            else original_unit
        )

    work["venda_validada"] = pd.Series(valid, index=work.index, dtype=bool)
    work["troca_contrato"] = ~work["venda_validada"]
    work["valor_venda"] = pd.Series(matched_values, index=work.index, dtype=float)
    work["valor_real"] = work["valor_venda"]
    work["id_unidade"] = pd.Series(matched_units, index=work.index, dtype=str)
    work["unidade_nome"] = work.get(
        "id_unidade", pd.Series(index=work.index)
    ).map(branch_name)
    allowed_collaborator = ~work.get(
        "colaborador_responsavel", pd.Series(index=work.index, dtype=str)
    ).map(excluded_sales_collaborator)
    allowed_unit = ~work["unidade_nome"].isin(EXCLUDED_UNITS)
    eligible = allowed_collaborator & allowed_unit
    valid_sales = work.loc[eligible & work["venda_validada"]].copy()
    swaps = work.loc[eligible & work["troca_contrato"]].copy()
    return valid_sales, swaps


def sales_open_debt_mask(sales: pd.DataFrame, charges: pd.DataFrame) -> pd.Series:
    """Flag sales whose member has an open installment with the same exact value."""
    result = pd.Series(False, index=sales.index, dtype=bool)
    if sales.empty or charges.empty:
        return result
    charge_ids = id_series(
        charges.get("idMember", pd.Series(index=charges.index, dtype=str))
    )
    charge_values = parse_number(
        charges.get("valorCompet", pd.Series(index=charges.index, dtype=float))
    )
    charge_status = charges.get(
        "status", pd.Series(index=charges.index, dtype=str)
    ).fillna("").map(norm_key)
    open_values_by_member: dict[str, set[int]] = {}
    open_mask = charge_status.eq("a receber") & charge_values.fillna(0).gt(0)
    for member_id, value in zip(
        charge_ids[open_mask].tolist(), charge_values[open_mask].tolist()
    ):
        if member_id and pd.notna(value):
            open_values_by_member.setdefault(member_id, set()).add(
                int(round(float(value) * 100))
            )

    member_ids = id_series(
        sales.get("idMember", pd.Series(index=sales.index, dtype=str))
    )
    real_values = parse_number(
        sales.get("valor_real", pd.Series(index=sales.index, dtype=float))
    )
    sale_values = parse_number(
        sales.get("valor_venda", pd.Series(index=sales.index, dtype=float))
    )
    flags: list[bool] = []
    for member_id, real_value, sale_value in zip(
        member_ids.tolist(), real_values.tolist(), sale_values.tolist()
    ):
        open_values = open_values_by_member.get(member_id, set())
        candidates = {
            int(round(float(value) * 100))
            for value in (real_value, sale_value)
            if pd.notna(value) and float(value) > 0
        }
        flags.append(bool(open_values.intersection(candidates)))
    return pd.Series(flags, index=sales.index, dtype=bool)


def clean_sales_business_rules(
    sales: pd.DataFrame,
    charges: pd.DataFrame,
) -> pd.DataFrame:
    """Apply the authoritative VENDAS exclusions for commercial indicators.

    Contract sales remain at their source grain. Duplicate members and open
    receivables are relevant to checkout/collection analysis, but they do not
    erase a contract sale from the commercial volume.
    """
    if sales.empty:
        return sales.copy()
    work = sales.copy()
    collaborator = work.get(
        "colaborador_responsavel", pd.Series(index=work.index, dtype=str)
    )
    work = work.loc[~collaborator.map(excluded_sales_collaborator)].copy()
    contract = work.get("contrato", pd.Series(index=work.index, dtype=str))
    work = work.loc[~contract.map(excluded_sales_contract)].copy()
    return work


def clean_sales_monthly_history(
    sales: pd.DataFrame,
    charges: pd.DataFrame,
) -> pd.DataFrame:
    """Apply the sale rules independently inside each competence month."""
    if sales.empty:
        return sales.copy()
    dates = parse_date(sales_date_series(sales))
    parts = [
        clean_sales_business_rules(sales.loc[index], charges)
        for _, index in sales.loc[dates.notna()].groupby(dates[dates.notna()].dt.to_period("M")).groups.items()
    ]
    return pd.concat(parts, axis=0).sort_index() if parts else sales.iloc[0:0].copy()


def latest_realtime_contracts(
    frame: pd.DataFrame,
    limit: int = 10,
) -> list[dict]:
    """Return the latest real-time contracts formatted for the sales ticker."""
    if frame.empty:
        return []
    work = frame.copy()
    work["_sale_date"] = parse_date(
        work.get("dataSale", pd.Series(index=work.index, dtype=str))
    )
    observations = work.get(
        "observation", pd.Series(index=work.index, dtype=str)
    ).fillna("").map(norm_key)
    work = work.loc[observations.str.contains(r"\bcontrato\b", regex=True, na=False)].copy()
    if work.empty:
        return []
    work["_sale_id"] = parse_number(
        work.get("idSale", pd.Series(index=work.index, dtype=float))
    ).fillna(0)
    work = work.sort_values(
        ["_sale_date", "_sale_id"],
        ascending=[False, False],
        na_position="last",
        kind="stable",
    ).drop_duplicates("_sale_id", keep="first").head(max(1, int(limit)))
    sale_values = parse_number(
        work.get("saleValue", pd.Series(index=work.index, dtype=float))
    )
    item_values = parse_number(
        work.get("itemValue", pd.Series(index=work.index, dtype=float))
    )
    observations_raw = work.get(
        "observation", pd.Series(index=work.index, dtype=str)
    ).map(norm_text)
    items = work.get("item", pd.Series(index=work.index, dtype=str)).map(norm_text)
    units = work.get("idBranch", pd.Series(index=work.index, dtype=str)).map(branch_name)
    sellers = work.get(
        "nomeColaborador", pd.Series(index=work.index, dtype=str)
    ).map(norm_text)

    rows = []
    for index in work.index:
        timestamp = work.at[index, "_sale_date"]
        value = sale_values.get(index)
        if pd.isna(value):
            value = item_values.get(index)
        observation = observations_raw.get(index, "")
        contract = re.sub(r"^\s*contrato\s*-\s*", "", observation, flags=re.I)
        if not contract:
            contract = items.get(index, "Contrato") or "Contrato"
        rows.append({
            "time": timestamp.strftime("%H:%M") if pd.notna(timestamp) else "--:--",
            "saleDate": timestamp.strftime("%Y-%m-%d") if pd.notna(timestamp) else "",
            "seller": sellers.get(index, "") or "Colaborador não informado",
            "unit": units.get(index, "Sem unidade"),
            "contract": contract,
            "value": br_money(value if pd.notna(value) else 0),
        })
    return rows


def sales_charge_equal_masks(sales: pd.DataFrame, charges: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Match sale amount to received/open charges, preferring id_venda over member ID."""
    paid = pd.Series(False, index=sales.index, dtype=bool)
    open_equal = pd.Series(False, index=sales.index, dtype=bool)
    if sales.empty or charges.empty:
        return paid, open_equal

    charge_sale_ids = id_series(charges.get("id_venda", pd.Series(index=charges.index, dtype=str)))
    charge_member_ids = id_series(charges.get("idMember", pd.Series(index=charges.index, dtype=str)))
    charge_values = parse_number(charges.get("valorCompet", pd.Series(index=charges.index, dtype=float)))
    charge_statuses = charges.get("status", pd.Series(index=charges.index, dtype=str)).fillna("").map(norm_key)
    # O checkout da aba Vendas consulta apenas IDs presentes no recorte de
    # vendas exibido. Reduzir as cobranças antes do loop evita percorrer todo o
    # histórico financeiro para algumas centenas de vendas do mês corrente.
    requested_sale_ids = set(id_series(sales.get("id_venda", pd.Series(index=sales.index, dtype=str)))) - {""}
    requested_member_ids = set(id_series(sales.get("idMember", pd.Series(index=sales.index, dtype=str)))) - {""}
    relevant = charge_sale_ids.isin(requested_sale_ids) | charge_member_ids.isin(requested_member_ids)
    charge_sale_ids = charge_sale_ids[relevant]
    charge_member_ids = charge_member_ids[relevant]
    charge_values = charge_values[relevant]
    charge_statuses = charge_statuses[relevant]
    by_sale: dict[str, dict[str, set[int]]] = {}
    by_member: dict[str, dict[str, set[int]]] = {}

    for sale_id, member_id, value, status in zip(
        charge_sale_ids.tolist(),
        charge_member_ids.tolist(),
        charge_values.tolist(),
        charge_statuses.tolist(),
    ):
        if pd.isna(value) or float(value) <= 0 or status not in {"recebido", "a receber"}:
            continue
        cents = int(round(float(value) * 100))
        bucket = "paid" if status == "recebido" else "open"
        for mapping, key in ((by_sale, sale_id), (by_member, member_id)):
            if key:
                mapping.setdefault(key, {"paid": set(), "open": set()})[bucket].add(cents)

    sale_ids = id_series(sales.get("id_venda", pd.Series(index=sales.index, dtype=str)))
    member_ids = id_series(sales.get("idMember", pd.Series(index=sales.index, dtype=str)))
    sale_values = parse_number(sales.get("valor_venda", pd.Series(index=sales.index, dtype=float)))
    paid_values: list[bool] = []
    open_values: list[bool] = []
    for sale_id, member_id, value in zip(sale_ids.tolist(), member_ids.tolist(), sale_values.tolist()):
        if pd.isna(value) or float(value) <= 0:
            paid_values.append(False)
            open_values.append(False)
            continue
        matched = by_sale.get(sale_id) if sale_id else None
        if matched is None and member_id:
            matched = by_member.get(member_id)
        if matched is None:
            paid_values.append(False)
            open_values.append(False)
            continue
        cents = int(round(float(value) * 100))
        paid_values.append(cents in matched["paid"])
        open_values.append(cents in matched["open"])
    return (
        pd.Series(paid_values, index=sales.index, dtype=bool),
        pd.Series(open_values, index=sales.index, dtype=bool),
    )


def is_ignored_cancellation_contract(value: object) -> bool:
    key = norm_key(value)
    if not key:
        return False
    ignored_terms = ("mynutri", "freepas", "freepass", "transfer", "trasfer")
    return any(term in key for term in ignored_terms)


def active_aggregator_contract(value: object) -> bool:
    """Identify active contracts that represent aggregator-only relationships."""
    key = norm_key(value)
    return "wellhub" in key or "totalpass" in key or "total pass" in key


def eligible_cancellation_mask(cancellations: pd.DataFrame, active: pd.DataFrame) -> pd.Series:
    """Exclude IDs that remain active, except active Wellhub/TotalPass contracts."""
    if cancellations.empty:
        return pd.Series(dtype=bool, index=cancellations.index)
    cancel_ids = id_series(
        cancellations.get("idMember", pd.Series(index=cancellations.index, dtype=str))
    )
    if active.empty:
        return pd.Series(True, index=cancellations.index, dtype=bool)
    active_frame = pd.DataFrame({
        "id": id_series(active.get("idMember", pd.Series(index=active.index, dtype=str))),
        "aggregator": active.get(
            "contrato", pd.Series(index=active.index, dtype=str)
        ).map(active_aggregator_contract),
    })
    active_frame = active_frame[active_frame["id"].ne("")].copy()
    if active_frame.empty:
        return pd.Series(True, index=cancellations.index, dtype=bool)
    active_by_id = active_frame.groupby("id", dropna=True)["aggregator"].any()
    is_active = cancel_ids.isin(active_by_id.index)
    active_as_aggregator = cancel_ids.map(active_by_id).fillna(False).astype(bool)
    return (~is_active | active_as_aggregator).astype(bool)


def sales_ticket_average(values: pd.Series, contracts: pd.Series) -> tuple[float, int]:
    adjusted = adjusted_sales_ticket_values(values, contracts).dropna()
    if adjusted.empty:
        return 0.0, 0
    return float(adjusted.mean()), int(adjusted.count())


def adjusted_sales_ticket_values(values: pd.Series, contracts: pd.Series) -> pd.Series:
    frame = pd.DataFrame({
        "value": values,
        "contract": contracts.fillna("").astype(str).map(norm_key),
    })
    result = pd.Series(np.nan, index=frame.index, dtype=float)
    valid = frame["value"].notna() & frame["value"].gt(0)
    for index, value, contract in frame.loc[valid].itertuples():
        value = float(value)
        if value > 450:
            if "semestr" in contract or "6 meses" in contract or "06 meses" in contract:
                value = value / 6
            elif "anual" in contract or "12 meses" in contract or "12x" in contract:
                value = value / 12
            else:
                continue
        result.loc[index] = value
    return result


def cancellation_value_rows(
    cancel_sale_ids: pd.Series,
    sales_sale_ids: pd.Series,
    sales_values: pd.Series,
    limit: int = 10,
) -> list[dict]:
    sales_frame = pd.DataFrame({
        "sale_id": sales_sale_ids,
        "value": sales_values,
    })
    sales_frame = sales_frame[sales_frame["sale_id"].ne("") & sales_frame["value"].notna() & sales_frame["value"].ge(0)].copy()
    if sales_frame.empty:
        return []
    value_by_sale_id = sales_frame.drop_duplicates("sale_id").set_index("sale_id")["value"]
    frame = pd.DataFrame({
        "sale_id": cancel_sale_ids,
    })
    frame = frame[frame["sale_id"].ne("")].copy()
    frame["value"] = frame["sale_id"].map(value_by_sale_id)
    frame = frame[frame["value"].notna() & frame["value"].ge(0)].copy()
    if frame.empty:
        return []

    def bucket_value(value: object) -> int:
        amount = float(value)
        nearest = min(CANCEL_VALUE_BUCKETS, key=lambda target: (abs(amount - target), target))
        if abs(amount - nearest) <= SALE_VALUE_BUCKET_TOLERANCE:
            amount = nearest
        return int(round(round(amount, 2) * 100))

    sales_frame["value_key"] = sales_frame["value"].map(bucket_value)
    sold_counts = sales_frame["value_key"].value_counts()
    frame["value_key"] = frame["value"].map(bucket_value)
    cancel_counts = frame["value_key"].value_counts()
    grouped = pd.DataFrame({"canceled": cancel_counts, "sold": sold_counts}).fillna(0)
    grouped = grouped[grouped["canceled"].gt(0)].copy()
    if grouped.empty:
        return []
    grouped["rate"] = grouped["canceled"] / grouped["sold"].clip(lower=1) * 100
    grouped = grouped.sort_values(["canceled", "rate", "sold"], ascending=[False, False, False]).head(limit)
    return [
        {
            "label": br_money(value_key / 100),
            "value": int(row.canceled),
            "pct": float(row.rate),
            "display": f"{br_int(row.canceled)}/{br_int(row.sold)} · {br_pct(row.rate)}",
            "tone": "red",
        }
        for value_key, row in grouped.iterrows()
    ]


def open_sales_value_rows(
    sale_ids: pd.Series,
    sale_values: pd.Series,
    charge_ids: pd.Series,
    charge_open_mask: pd.Series,
    charge_values: pd.Series,
    limit: int = 8,
) -> list[dict]:
    open_ids = set(charge_ids[charge_open_mask & charge_values.fillna(0).gt(0) & charge_ids.ne("")])
    frame = pd.DataFrame({
        "id": sale_ids,
        "value": sale_values,
    })
    frame = frame[frame["id"].ne("") & frame["value"].notna() & frame["value"].ge(0)].copy()
    if frame.empty:
        return []
    def bucket_value(value: object) -> int:
        amount = float(value)
        nearest = min(SALE_VALUE_BUCKETS, key=lambda target: (abs(amount - target), target))
        if abs(amount - nearest) <= SALE_VALUE_BUCKET_TOLERANCE:
            amount = nearest
        return int(round(round(amount, 2) * 100))

    frame["value_key"] = frame["value"].map(bucket_value)
    frame["open"] = frame["id"].isin(open_ids).astype(int)
    grouped = frame.groupby("value_key", as_index=False).agg(sold=("id", "size"), open=("open", "sum"))
    grouped = grouped[grouped["open"].gt(0)]
    if grouped.empty:
        return []
    grouped["rate"] = grouped["open"] / grouped["sold"].clip(lower=1) * 100
    grouped = grouped.sort_values(["open", "rate", "sold"], ascending=[False, False, False]).head(limit)
    return [
        {
            "label": br_money(row.value_key / 100),
            "value": int(row.open),
            "pct": float(row.rate),
            "display": f"{br_int(row.open)}/{br_int(row.sold)} · {br_pct(row.rate)}",
            "tone": "red",
        }
        for row in grouped.itertuples(index=False)
    ]


def contract_swap_rows(
    sale_ids: pd.Series,
    sale_dates: pd.Series,
    cancel_ids: pd.Series,
    cancel_dates: pd.Series,
    total_sales: int,
) -> list[dict]:
    sales_frame = pd.DataFrame({"id": sale_ids, "sale_date": sale_dates})
    sales_frame = sales_frame[sales_frame["id"].ne("") & sales_frame["sale_date"].notna()]
    cancel_frame = pd.DataFrame({"id": cancel_ids, "cancel_date": cancel_dates})
    cancel_frame = cancel_frame[cancel_frame["id"].ne("") & cancel_frame["cancel_date"].notna()]
    if sales_frame.empty or cancel_frame.empty:
        return [{"label": "Cancelamento até 3 dias antes", "value": 0, "pct": 0.0, "display": f"0/{br_int(total_sales)} · 0,0%", "tone": "orange"}]

    cancel_by_id = {
        str(member_id): sorted(group["cancel_date"].tolist())
        for member_id, group in cancel_frame.groupby("id", dropna=True)
    }
    swap_sales = 0
    swap_ids = set()
    for member_id, sale_date in sales_frame.itertuples(index=False):
        dates = cancel_by_id.get(str(member_id), [])
        if not dates:
            continue
        start = sale_date - pd.Timedelta(days=3)
        if any(start <= cancel_date <= sale_date for cancel_date in dates):
            swap_sales += 1
            swap_ids.add(str(member_id))

    pct_value = swap_sales / max(total_sales, 1) * 100
    return [{
        "label": "Cancelamento até 3 dias antes",
        "value": swap_sales,
        "pct": pct_value,
        "display": f"{br_int(swap_sales)}/{br_int(total_sales)} · {br_pct(pct_value)}",
        "tone": "orange",
        "sub": f"{br_int(len(swap_ids))} clientes únicos",
    }]


def clean_reason(value: object) -> str:
    text = norm_text(value)
    return text.replace("inadimpl?ncia", "inadimplência").replace("Inadimpl?ncia", "Inadimplência")


def grouped_cancel_reason(value: object) -> str:
    text = clean_reason(value)
    key = norm_key(text)
    compact = re.sub(r"[^a-z0-9]+", "", key)
    if not compact:
        return "Não registrado"
    if "inadimp" in compact or "inadim" in compact or re.search(r"inadi[a-z]{0,4}p", compact):
        return "Inadimplência"
    if any(term in compact for term in ("frequent", "frequenc", "frequenta", "naofrequenta", "naofrequencia")):
        return "Não Frequenta"
    if any(term in compact for term in ("gympass", "wellhub", "totalpass", "gympas")):
        return "Agregador"
    if re.match(r"^\s*outros?\b", key):
        description = re.sub(r"^\s*outros?\s*(?:\(?\s*especificar\s*\)?)?\s*[-:;/]*\s*", "", text, flags=re.I).strip()
        description = re.sub(r"^\(?\s*especificar\s*\)?\s*[-:;/]*\s*", "", description, flags=re.I).strip()
        if not description:
            return "Não registrado"
        return description[:1].upper() + description[1:]
    generic = re.sub(r"[^a-z0-9]+", " ", key).strip()
    if generic in {"outro", "outros", "outros especificar", "outro especificar", "nao informado", "sem motivo"}:
        return "Não registrado"
    if generic.startswith("outros ") and generic.replace("outros", "", 1).strip() in {"", "especificar"}:
        return "Não registrado"
    return text or "Não registrado"


def is_inadimplencia_reason(value: object) -> bool:
    key = re.sub(r"[^a-z0-9]+", "", norm_key(value))
    if not key:
        return False
    return "inadimp" in key or "inadim" in key or bool(re.search(r"inadi[a-z]{0,4}p", key))


def identify_role(path: Path, headers: list[str]) -> str | None:
    name = norm_key(path.stem)
    header_keys = {norm_key(h) for h in headers}
    if "totalpass" in name:
        return "access_totalpass"
    if "wellhub" in name:
        return "access_wellhub"
    if "controle" in name and "acesso" in name:
        return "access_unit"
    if "cobr" in name:
        return "charges"
    if "cancel" in name:
        return "cancellations"
    if "ativo" in name or "ltv" in name:
        return "active"
    if "venda" in name:
        return "sales"
    if {"idmember", "datavenda", "valor_venda"}.issubset(header_keys):
        return "sales"
    if {"idmember", "datacancelamento", "motivo"}.issubset(header_keys):
        return "cancellations"
    if {"idmember", "datavencimento", "valorcompet", "status"}.issubset(header_keys):
        return "charges"
    if {"idmember", "diasativo", "valorcompetencia"}.issubset(header_keys):
        return "active"
    if {"id_member", "date_event"}.issubset(header_keys):
        return "access_unit"
    return None


def discover_csvs(source: str | Path | None) -> tuple[dict[str, Path], list[dict]]:
    folder = Path(source) if source else DEFAULT_CSV_DIR
    if folder.is_file():
        folder = folder.parent
    paths: dict[str, Path] = {}
    rows = []
    if not folder.exists():
        return paths, [{"arquivo": str(folder), "papel": "pasta", "status": "não encontrada"}]
    for path in sorted(folder.glob("*.csv")):
        try:
            headers = []
            for encoding in ("utf-8-sig", "utf-8", "latin1", "cp1252"):
                try:
                    headers = list(pd.read_csv(path, sep=None, engine="python", dtype=str, encoding=encoding, nrows=0).columns)
                    break
                except UnicodeDecodeError:
                    continue
            headers = [norm_text(c) for c in headers]
            role = identify_role(path, headers)
        except Exception:
            role = None
            headers = []
        status = "ignorado"
        if role and role not in paths:
            paths[role] = path
            status = "ok"
        elif role:
            status = "duplicado"
        rows.append({"arquivo": path.name, "papel": role or "-", "status": status, "colunas": len(headers)})
    return paths, rows


def top_rows(series: pd.Series, limit: int = 8, total: int | None = None) -> list[dict]:
    clean = series.fillna("").astype(str).str.strip()
    clean = clean[clean.ne("")]
    clean = clean[~clean.str.lower().isin({"nan", "none", "nat"})]
    counts = clean.value_counts().head(limit)
    base = total or int(counts.sum()) or 1
    return [{"label": str(label), "value": int(value), "pct": float(value / base * 100)} for label, value in counts.items()]


def legacy_payment_status_rows_counts(ids: pd.Series, statuses: pd.Series, due_dates: pd.Series) -> list[dict]:
    frame = pd.DataFrame({
        "id": id_series(ids),
        "status": statuses.fillna("").astype(str).map(norm_key),
        "due": due_dates,
    })
    frame = frame[frame["id"].ne("") & frame["due"].notna()]
    month_start = pd.Timestamp.today().normalize().replace(day=1)

    def status_counts(mask: pd.Series) -> tuple[int, int]:
        period = frame[mask]
        open_ids = set(period.loc[period["status"].eq("a receber"), "id"])
        received_ids = set(period.loc[period["status"].eq("recebido"), "id"]) - open_ids
        return len(received_ids), len(open_ids)

    current_received, current_open = status_counts(frame["due"].ge(month_start))
    old_received, old_open = status_counts(frame["due"].lt(month_start))
    total = max(current_received + current_open + old_received + old_open, 1)
    return [
        {"label": "Dentro do mês - Recebido", "value": current_received, "pct": current_received / total * 100, "tone": "green"},
        {"label": "Dentro do mês - A receber", "value": current_open, "pct": current_open / total * 100, "tone": "red"},
        {"label": "Fora do mês - Recebido", "value": old_received, "pct": old_received / total * 100, "tone": "green"},
        {"label": "Fora do mês - A receber", "value": old_open, "pct": old_open / total * 100, "tone": "red"},
    ]


def legacy_payment_status_rows_values(
    ids: pd.Series,
    statuses: pd.Series,
    due_dates: pd.Series,
    values: pd.Series,
    reference_date: pd.Timestamp | None = None,
) -> list[dict]:
    frame = pd.DataFrame({
        "id": id_series(ids),
        "status": statuses.fillna("").astype(str).map(norm_key),
        "due": due_dates,
        "value": values.fillna(0),
    })
    frame = frame[frame["id"].ne("") & frame["due"].notna()]
    today = (reference_date or pd.Timestamp.today()).normalize()
    month_start = today.replace(day=1)

    def total_value(mask: pd.Series) -> float:
        return float(frame.loc[mask, "value"].sum())

    current_mask = frame["due"].ge(month_start)
    old_mask = frame["due"].lt(month_start)
    received_mask = frame["status"].eq("recebido")
    open_mask = frame["status"].eq("a receber")

    current_received = total_value(current_mask & received_mask)
    current_open = total_value(current_mask & open_mask)
    current_overdue = total_value(current_mask & open_mask & frame["due"].lt(today))
    old_received = total_value(old_mask & received_mask)
    old_open = total_value(old_mask & open_mask)
    current_total = max(current_received + current_open, 1)
    old_total = max(old_received + old_open, 1)

    def money_pct(value: float, total: float) -> str:
        return f"{br_money(value)} · {br_pct(value / total * 100)}"

    return [
        {"label": "Dentro do mês - Recebido", "value": current_received / current_total * 100, "display": money_pct(current_received, current_total), "tone": "green"},
        {"label": "Dentro do mês - A receber", "value": current_open / current_total * 100, "display": money_pct(current_open, current_total), "tone": "red"},
        {"label": "Dentro do mês - Parcelas em atraso", "value": current_overdue / current_total * 100, "display": money_pct(current_overdue, current_total), "tone": "orange"},
        {"label": "Fora do mês - Recebido", "value": old_received / old_total * 100, "display": money_pct(old_received, old_total), "tone": "green"},
        {"label": "Fora do mês - A receber", "value": old_open / old_total * 100, "display": money_pct(old_open, old_total), "tone": "red"},
    ]


def payment_status_rows(
    ids: pd.Series,
    statuses: pd.Series,
    due_dates: pd.Series,
    values: pd.Series,
    reference_date: pd.Timestamp | None = None,
) -> list[dict]:
    frame = pd.DataFrame({
        "id": id_series(ids),
        "status": statuses.fillna("").astype(str).map(norm_key),
        "due": due_dates,
        "value": values.fillna(0),
    })
    frame = frame[frame["id"].ne("") & frame["due"].notna()]
    today = (reference_date or pd.Timestamp.today()).normalize()
    month_start = today.replace(day=1)

    current_mask = frame["due"].ge(month_start)
    old_mask = frame["due"].lt(month_start)
    received_mask = frame["status"].eq("recebido")
    open_mask = frame["status"].eq("a receber")

    current_received = float(frame.loc[current_mask & received_mask, "value"].sum())
    current_open = float(frame.loc[current_mask & open_mask, "value"].sum())
    current_overdue = float(frame.loc[current_mask & open_mask & frame["due"].lt(today), "value"].sum())
    old_received = float(frame.loc[old_mask & received_mask, "value"].sum())
    old_open = float(frame.loc[old_mask & open_mask, "value"].sum())
    current_total = max(current_received + current_open, 1)
    old_total = max(old_received + old_open, 1)

    def money_pct(value: float, total: float) -> str:
        return f"{br_money(value)} {br_pct(value / total * 100)}"

    return [
        {"label": "Dentro do mês - Recebido", "value": current_received / current_total * 100, "display": money_pct(current_received, current_total), "tone": "green", "description": "Parcelas com vencimento dentro do mês atual pagas"},
        {"label": "Dentro do mês - A receber", "value": current_open / current_total * 100, "display": money_pct(current_open, current_total), "tone": "red", "description": "Parcelas com vencimento dentro do mês atual com vencimento programado"},
        {"label": "Dentro do mês - Parcelas em atraso", "value": current_overdue / current_total * 100, "display": money_pct(current_overdue, current_total), "tone": "orange", "description": "Parcelas ja vencidas dentro do mês atual"},
        {"label": "Fora do mês - Recebido", "value": old_received / old_total * 100, "display": money_pct(old_received, old_total), "tone": "green", "description": "Parcelas de meses anteriores pagas"},
        {"label": "Fora do mês - A receber", "value": old_open / old_total * 100, "display": money_pct(old_open, old_total), "tone": "red", "description": "Parcelas de meses anteriores com saldo devedor"},
    ]


def charge_success_unit_rows(
    units: pd.Series,
    ids: pd.Series,
    statuses: pd.Series,
    due_dates: pd.Series,
    values: pd.Series,
    period: str,
    reference_date: pd.Timestamp | None = None,
) -> list[dict]:
    frame = pd.DataFrame({
        "unit": units.fillna("").map(branch_name),
        "id": id_series(ids),
        "status": statuses.fillna("").astype(str).map(norm_key),
        "due": due_dates,
        "value": values.fillna(0),
    })
    frame = frame[
        frame["unit"].ne("")
        & frame["id"].ne("")
        & frame["due"].notna()
        & frame["value"].gt(0)
    ].copy()
    frame = frame[~frame["unit"].isin(EXCLUDED_UNITS)].copy()
    today = (reference_date or pd.Timestamp.today()).normalize()
    month_start = today.replace(day=1)
    if period == "current":
        frame = frame[frame["due"].ge(month_start) & frame["due"].lt(today)].copy()
    else:
        frame = frame[frame["due"].lt(month_start)].copy()

    totals: dict[str, dict[str, int | float]] = {}
    for unit in UNIT_ORDER:
        unit_frame = frame[frame["unit"].eq(unit)]
        base_ids = set(unit_frame["id"])
        open_ids = set(unit_frame.loc[unit_frame["status"].eq("a receber"), "id"])
        received_ids = set(unit_frame.loc[unit_frame["status"].eq("recebido"), "id"])
        success_ids = received_ids - open_ids
        base = len(base_ids)
        success = len(success_ids)
        rate = success / max(base, 1) * 100
        totals[unit] = {"base": base, "success": success, "rate": rate}

    ranked = sorted(
        [
            (unit, float(data["rate"]), int(data["success"]), int(data["base"]))
            for unit, data in totals.items()
            if int(data["base"]) > 0
        ],
        key=lambda item: (-item[1], -item[2], -item[3], UNIT_ORDER.index(item[0])),
    )
    medal_by_label = {
        unit: medal
        for (unit, rate, success, base), medal in zip(ranked, MEDAL_SEQUENCE)
    }
    rows = []
    for unit in UNIT_ORDER:
        data = totals[unit]
        base = int(data["base"])
        success = int(data["success"])
        rate = float(data["rate"])
        rows.append({
            "label": unit,
            "value": rate,
            "display": f"{br_int(success)}/{br_int(base)} · {br_pct(rate)}",
            "medal": medal_by_label.get(unit, ""),
        })
    return rows


def charge_collection_unit_rows(
    units: pd.Series,
    statuses: pd.Series,
    due_dates: pd.Series,
    values: pd.Series,
    reference_date: pd.Timestamp | None = None,
) -> list[dict]:
    """Parcelas previstas e recebidas na competência até a data de referência."""
    frame = pd.DataFrame({
        "unit": units.fillna("").map(branch_name),
        "status": statuses.fillna("").astype(str).map(norm_key),
        "due": due_dates,
        "value": values.fillna(0),
    })
    frame = frame[
        frame["unit"].ne("")
        & frame["due"].notna()
        & frame["value"].gt(0)
        & ~frame["unit"].isin(EXCLUDED_UNITS)
    ].copy()
    today = (reference_date or pd.Timestamp.today()).normalize()
    month_start = today.replace(day=1)
    frame = frame[frame["due"].between(month_start, today, inclusive="both")].copy()

    totals: dict[str, dict[str, int | float]] = {}
    for unit in UNIT_ORDER:
        unit_frame = frame[frame["unit"].eq(unit)]
        scheduled = int(len(unit_frame))
        received = int(unit_frame["status"].eq("recebido").sum())
        rate = received / max(scheduled, 1) * 100
        totals[unit] = {"scheduled": scheduled, "received": received, "rate": rate}

    ranked = sorted(
        [
            (unit, float(data["rate"]), int(data["received"]), int(data["scheduled"]))
            for unit, data in totals.items()
            if int(data["scheduled"]) > 0
        ],
        key=lambda item: (-item[1], -item[2], -item[3], UNIT_ORDER.index(item[0])),
    )
    medal_by_label = {
        unit: medal
        for (unit, rate, received, scheduled), medal in zip(ranked, MEDAL_SEQUENCE)
    }
    return [
        {
            "label": unit,
            "scheduled": int(totals[unit]["scheduled"]),
            "received": int(totals[unit]["received"]),
            "rate": float(totals[unit]["rate"]),
            "medal": medal_by_label.get(unit, ""),
        }
        for unit in UNIT_ORDER
    ]


def delinquency_day_column_rows(days: pd.Series) -> list[dict]:
    """Faixas de atraso preservando a leitura diária até o 15º dia."""
    numeric = pd.to_numeric(days, errors="coerce").dropna()
    numeric = numeric[numeric.gt(0)].astype(int)
    buckets: list[tuple[str, int, int | None]] = [
        *[(str(day), day, day) for day in range(1, 16)],
        ("16–22", 16, 22),
        ("23–31", 23, 31),
        ("32–45", 32, 45),
        ("46–65", 46, 65),
        ("66+", 66, None),
    ]
    total = max(int(len(numeric)), 1)
    rows: list[dict] = []
    for label, start, end in buckets:
        mask = numeric.ge(start) if end is None else numeric.between(start, end, inclusive="both")
        value = int(mask.sum())
        rows.append({"label": label, "value": value, "pct": value / total * 100})
    return rows


def revenue_by_unit_rows(
    sale_units: pd.Series,
    sale_values: pd.Series,
    sale_contracts: pd.Series,
    sale_dates: pd.Series,
    charge_units: pd.Series,
    charge_statuses: pd.Series,
    charge_values: pd.Series,
    access: pd.DataFrame,
    reference_date: pd.Timestamp | None = None,
) -> list[dict]:
    own_totals = {unit: 0.0 for unit in UNIT_ORDER}
    adjusted_sales = adjusted_sales_ticket_values(sale_values, sale_contracts)
    analysis_date = (reference_date or pd.Timestamp.today()).normalize()
    month_start = analysis_date.replace(day=1)
    next_month = month_start + pd.offsets.MonthBegin(1)
    sales_frame = pd.DataFrame({
        "unit": sale_units.map(revenue_branch_name),
        "value": adjusted_sales.fillna(0),
        "date": sale_dates,
    })
    sales_frame = sales_frame[
        sales_frame["unit"].isin(UNIT_ORDER)
        & sales_frame["value"].gt(0)
        & sales_frame["date"].ge(month_start)
        & sales_frame["date"].lt(next_month)
    ]
    for unit, value in sales_frame.groupby("unit")["value"].sum().items():
        own_totals[str(unit)] += float(value)

    charges_frame = pd.DataFrame({
        "unit": charge_units.map(revenue_branch_name),
        "status": charge_statuses.fillna("").astype(str).map(norm_key),
        "value": charge_values.fillna(0),
    })
    charges_frame = charges_frame[
        charges_frame["unit"].isin(UNIT_ORDER)
        & charges_frame["status"].eq("recebido")
        & charges_frame["value"].gt(0)
    ]
    for unit, value in charges_frame.groupby("unit")["value"].sum().items():
        own_totals[str(unit)] += float(value)

    def platform_totals(platform: str, rules: dict[str, tuple[float, float]]) -> dict[str, float]:
        totals = {unit: 0.0 for unit in UNIT_ORDER}
        if access.empty:
            return totals
        frame = access[access.get("canal", pd.Series(index=access.index)).eq(platform)].copy()
        if frame.empty:
            return totals
        action_key = frame.get("entry_action", pd.Series(index=frame.index)).fillna("").astype(str).map(norm_key)
        reason_key = frame.get("block_reason", pd.Series(index=frame.index)).fillna("").astype(str).map(norm_key)
        paid_checkin = action_key.eq("entry") | reason_key.str.contains("validada com sucesso|validado com sucesso", na=False)
        frame = frame[paid_checkin].copy()
        if frame.empty:
            return totals
        frame["branch_id"] = frame.get("id_branch", pd.Series(index=frame.index)).map(branch_id_key)
        frame["unit"] = frame["branch_id"].map(lambda value: REVENUE_BRANCH_NAMES.get(value, ""))
        frame["member_id"] = id_series(frame.get("id_member", pd.Series(index=frame.index)))
        event_dates = parse_date(frame.get("date_event", pd.Series(index=frame.index)))
        frame["event_date"] = event_dates
        frame["competence"] = event_dates.dt.to_period("M").astype(str).replace("NaT", "Sem data")
        frame = frame[
            frame["branch_id"].isin(rules.keys())
            & frame["unit"].isin(UNIT_ORDER)
            & frame["member_id"].ne("")
            & frame["event_date"].ge(month_start)
            & frame["event_date"].lt(next_month)
        ].copy()
        if frame.empty:
            return totals
        visits = (
            frame.groupby(["branch_id", "unit", "member_id", "competence"], dropna=False)
            .size()
            .reset_index(name="visits")
        )
        for branch_id, unit, member_id, competence, visit_count in visits.itertuples(index=False):
            rate, cap = rules.get(str(branch_id), (0.0, 0.0))
            if rate <= 0 or cap <= 0:
                continue
            totals[str(unit)] += min(float(visit_count) * rate, cap)
        return totals

    wellhub_totals = platform_totals("Wellhub", WELLHUB_REVENUE_RULES)
    totalpass_totals = platform_totals("TotalPass", TOTALPASS_REVENUE_RULES)
    total_by_unit = {
        unit: own_totals.get(unit, 0.0) + wellhub_totals.get(unit, 0.0) + totalpass_totals.get(unit, 0.0)
        for unit in UNIT_ORDER
    }
    ranked = sorted(
        [(unit, value) for unit, value in total_by_unit.items() if value > 0],
        key=lambda item: (-item[1], UNIT_ORDER.index(item[0])),
    )
    medal_by_label = {
        unit: medal
        for (unit, value), medal in zip(ranked, MEDAL_SEQUENCE)
    }
    grand_total = max(sum(total_by_unit.values()), 1)
    return [
        {
            "label": unit,
            "value": float(total_by_unit.get(unit, 0.0)),
            "display": br_money(total_by_unit.get(unit, 0.0)),
            "pct": float(total_by_unit.get(unit, 0.0) / grand_total * 100),
            "medal": medal_by_label.get(unit, ""),
        }
        for unit in UNIT_ORDER
    ]


def financial_monthly_matrix(
    billing: pd.DataFrame,
    charges: pd.DataFrame,
    sales: pd.DataFrame,
    access: pd.DataFrame,
    period_start: pd.Timestamp | None = None,
    period_end: pd.Timestamp | None = None,
    selected_units: list[str] | None = None,
) -> dict:
    """Build the auditable monthly Financeiro matrix at unit grain."""
    units = [unit for unit in UNIT_ORDER if not selected_units or unit in selected_units]
    billing = billing.copy()
    charges = charges.copy()
    sales = sales.copy()
    access = access.copy()

    billing_dates = parse_date(billing.get("dataVenda", pd.Series(index=billing.index, dtype=str)))
    charge_due = parse_date(charges.get("dataVencimento", pd.Series(index=charges.index, dtype=str)))
    charge_paid = parse_date(charges.get("dataPagamento", pd.Series(index=charges.index, dtype=str)))
    sales_dates = parse_date(sales_date_series(sales))
    access_dates = parse_date(access.get("date_event", pd.Series(index=access.index, dtype=str)))

    available_months: set[pd.Period] = set()
    for dates in (billing_dates, charge_paid, sales_dates, access_dates):
        if len(dates):
            available_months.update(dates.dropna().dt.to_period("M").tolist())
    if period_start is not None:
        start_period = period_start.to_period("M")
        available_months = {month for month in available_months if month >= start_period}
    if period_end is not None:
        end_period = period_end.to_period("M")
        available_months = {month for month in available_months if month <= end_period}
    if not available_months:
        fallback = (period_end or period_start or pd.Timestamp.today()).to_period("M")
        available_months = {fallback}
    months = sorted(available_months, reverse=True)

    billing_values = parse_number(billing.get("valor_real", pd.Series(index=billing.index, dtype=float))).fillna(0)
    billing_items = billing.get("item_vendido", pd.Series(index=billing.index, dtype=str)).fillna("").map(norm_key)
    billing_notes = billing.get("observa", pd.Series(index=billing.index, dtype=str)).fillna("").map(norm_key)
    sales_values = parse_number(sales.get("valor_real", pd.Series(index=sales.index, dtype=float))).fillna(0)
    charge_values = parse_number(charges.get("valorCompet", pd.Series(index=charges.index, dtype=float))).fillna(0)
    charge_status = charges.get("status", pd.Series(index=charges.index, dtype=str)).fillna("").map(norm_key)

    def sums_by_unit(frame: pd.DataFrame, values: pd.Series, mask: pd.Series) -> dict[str, float]:
        if frame.empty or not mask.any():
            return {unit: 0.0 for unit in units}
        work = pd.DataFrame({"unit": frame["unidade_nome"], "value": values}).loc[mask]
        work = work[work["unit"].isin(units)]
        grouped = work.groupby("unit")["value"].sum() if not work.empty else pd.Series(dtype=float)
        return {unit: round(float(grouped.get(unit, 0.0)), 2) for unit in units}

    def counts_by_unit(frame: pd.DataFrame, mask: pd.Series) -> dict[str, int]:
        if frame.empty or not mask.any():
            return {unit: 0 for unit in units}
        counts = frame.loc[mask & frame["unidade_nome"].isin(units), "unidade_nome"].value_counts()
        return {unit: int(counts.get(unit, 0)) for unit in units}

    def access_revenue(platform: str, month: pd.Period, rate: float, cap: float) -> dict[str, float]:
        totals = {unit: 0.0 for unit in units}
        if access.empty:
            return totals
        platform_mask = access.get("canal", pd.Series(index=access.index, dtype=str)).eq(platform)
        action = access.get("entry_action", pd.Series(index=access.index, dtype=str)).fillna("").map(norm_key)
        reason = access.get("block_reason", pd.Series(index=access.index, dtype=str)).fillna("").map(norm_key)
        valid_entry = action.eq("entry") | reason.str.contains("validada com sucesso|validado com sucesso", na=False)
        month_mask = access_dates.notna() & access_dates.dt.to_period("M").eq(month)
        frame = access.loc[platform_mask & valid_entry & month_mask].copy()
        if frame.empty:
            return totals
        member = id_series(frame.get("id_member", pd.Series(index=frame.index, dtype=str)))
        prospect = id_series(frame.get("id_prospect", pd.Series(index=frame.index, dtype=str)))
        employee = id_series(frame.get("id_employee", pd.Series(index=frame.index, dtype=str)))
        frame["person_id"] = np.where(
            member.ne(""),
            "m:" + member,
            np.where(prospect.ne(""), "p:" + prospect, np.where(employee.ne(""), "e:" + employee, "")),
        )
        frame = frame[frame["unidade_nome"].isin(units) & frame["person_id"].ne("")]
        if frame.empty:
            return totals
        visits = frame.groupby(["unidade_nome", "person_id"]).size()
        revenue = visits.map(lambda count: min(float(count) * rate, cap))
        grouped = revenue.groupby(level=0).sum()
        return {unit: round(float(grouped.get(unit, 0.0)), 2) for unit in units}

    row_specs = [
        ("total", "Resumo", "Faturamento total do mês", "money", "COBRANÇA + VENDAS + FATURAMENTO + AGREGADORES", "Soma das recorrências recebidas no mês, planos válidos, serviços, produtos, MyNutri e receitas de Wellhub/TotalPass, sem repetir os subtotais."),
        ("rec_current_value", "Recorrência", "Recorrência recebida — vencimento do próprio mês", "money", "COBRANÇA", "Status recebido, pagamento no mês selecionado e vencimento no mesmo mês."),
        ("rec_current_count", "Recorrência", "Parcelas pagas — vencimento do próprio mês", "count", "COBRANÇA", "Contagem das parcelas da linha anterior."),
        ("rec_previous_value", "Recorrência", "Recorrência recebida — vencimentos anteriores", "money", "COBRANÇA", "Status recebido, pagamento no mês selecionado e vencimento anterior ao mês."),
        ("rec_previous_count", "Recorrência", "Parcelas pagas — vencimentos anteriores", "count", "COBRANÇA", "Contagem das parcelas da linha anterior."),
        ("plans", "Vendas e serviços", "Planos vendidos no mês", "money", "VENDAS", "Soma de valor_real após excluir MyNutri e os consultores bloqueados da regra comercial vigente."),
        ("fees", "Vendas e serviços", "Serviços de multa e pró-rata", "money", "FATURAMENTO", "Itens contendo multa, pró-rata, prorata, prorrata ou desativado."),
        ("short_plans", "Vendas e serviços", "Aula avulsa, diária, semanal e quinzenal", "money", "FATURAMENTO", "Itens contendo aula avulsa, diária, semanal ou quinzenal."),
        ("products", "Vendas e serviços", "Produtos", "money", "FATURAMENTO", "Itens identificados como Produto."),
        ("mynutri_rec", "MyNutri", "MyNutri recorrência", "money", "FATURAMENTO", "MyNutri com observação de venda automática ou débito recorrente."),
        ("mynutri_sale", "MyNutri", "MyNutri venda", "money", "FATURAMENTO", "Demais lançamentos MyNutri não contabilizados como recorrência."),
        ("wellhub", "Agregadores", "Faturamento Wellhub", "money", "WELLHUB ACESSOS", "R$ 11,51 por check-in validado e por ID, limitado a R$ 138,13 no mês."),
        ("totalpass", "Agregadores", "Faturamento TotalPass", "money", "TOTALPASS ACESSOS", "R$ 11,10 por check-in validado e por ID, limitado a R$ 144,26 no mês."),
        ("aggregators", "Agregadores", "Faturamento agregadores total", "money", "WELLHUB + TOTALPASS", "Soma do faturamento Wellhub e TotalPass."),
    ]

    views = []
    for month in months:
        billing_month = billing_dates.notna() & billing_dates.dt.to_period("M").eq(month)
        sales_month = sales_dates.notna() & sales_dates.dt.to_period("M").eq(month)
        cleaned_sales_month = clean_sales_business_rules(sales.loc[sales_month], charges)
        valid_sales_month = pd.Series(sales.index.isin(cleaned_sales_month.index), index=sales.index)
        paid_in_month = charge_paid.notna() & charge_paid.dt.to_period("M").eq(month)
        received = charge_status.eq("recebido")
        due_period = charge_due.dt.to_period("M")
        current_due = charge_due.notna() & due_period.eq(month)
        previous_due = charge_due.notna() & due_period.lt(month)
        mynutri = billing_items.str.contains(r"my\s*nutri", regex=True, na=False)
        recurring_note = billing_notes.str.contains(r"venda automatica|debito recorrente|venda recorrente", regex=True, na=False)
        mynutri_rec = mynutri & recurring_note

        values_by_key: dict[str, dict[str, float | int]] = {
            "rec_current_value": sums_by_unit(charges, charge_values, received & paid_in_month & current_due),
            "rec_current_count": counts_by_unit(charges, received & paid_in_month & current_due),
            "rec_previous_value": sums_by_unit(charges, charge_values, received & paid_in_month & previous_due),
            "rec_previous_count": counts_by_unit(charges, received & paid_in_month & previous_due),
            "plans": sums_by_unit(sales, sales_values, valid_sales_month),
            "fees": sums_by_unit(billing, billing_values, billing_month & billing_items.str.contains(r"multa|pro\s*rata|prorata|prorrata|desativad", regex=True, na=False)),
            "short_plans": sums_by_unit(billing, billing_values, billing_month & billing_items.str.contains(r"aula\s*avulsa|diaria|semanal|quinzenal", regex=True, na=False)),
            "products": sums_by_unit(billing, billing_values, billing_month & billing_items.str.contains(r"\bproduto\b", regex=True, na=False)),
            "mynutri_rec": sums_by_unit(billing, billing_values, billing_month & mynutri_rec),
            "mynutri_sale": sums_by_unit(billing, billing_values, billing_month & mynutri & ~mynutri_rec),
            "wellhub": access_revenue("Wellhub", month, FINANCE_WELLHUB_RATE, FINANCE_WELLHUB_CAP),
            "totalpass": access_revenue("TotalPass", month, FINANCE_TOTALPASS_RATE, FINANCE_TOTALPASS_CAP),
        }
        values_by_key["aggregators"] = {
            unit: round(float(values_by_key["wellhub"][unit]) + float(values_by_key["totalpass"][unit]), 2)
            for unit in units
        }
        # O faturamento total deve representar a receita completa da competência,
        # e não apenas os lançamentos avulsos da tabela FATURAMENTO. As categorias
        # abaixo são mutuamente exclusivas na composição: planos vêm da VENDAS já
        # saneada; serviços/produtos/MyNutri vêm da FATURAMENTO; recorrência vem da
        # COBRANÇA; e agregadores são calculados pelos acessos validados.
        total_component_keys = (
            "rec_current_value",
            "rec_previous_value",
            "plans",
            "fees",
            "short_plans",
            "products",
            "mynutri_rec",
            "mynutri_sale",
            "aggregators",
        )
        values_by_key["total"] = {
            unit: round(sum(float(values_by_key[key][unit]) for key in total_component_keys), 2)
            for unit in units
        }
        rows = []
        for key, section, label, kind, source, rule in row_specs:
            unit_values = values_by_key[key]
            total = sum(unit_values.values())
            rows.append({
                "key": key,
                "section": section,
                "label": label,
                "kind": kind,
                "source": source,
                "rule": rule,
                "values": [unit_values.get(unit, 0) for unit in units],
                "total": int(total) if kind == "count" else round(float(total), 2),
            })
        views.append({
            "key": str(month),
            "label": f"{MONTH_ABBR.get(month.month, month.month)}/{month.year}",
            "rows": rows,
        })

    return {
        "type": "financialMatrix",
        "title": "Faturamento mensal por unidade",
        "subtitle": "Valores por competência mensal · passe o mouse sobre o nome do indicador para consultar a regra.",
        "className": "chart-financial-matrix",
        "units": units,
        "defaultMonth": str(months[0]),
        "views": views,
    }


def financial_tab_payload(
    matrix: dict,
    payment_rows: list[dict] | None = None,
    received_ticket_mean: float = 0.0,
    received_ticket_count: int = 0,
    extra_charts: list[dict] | None = None,
) -> dict:
    views = matrix.get("views", [])
    default_view = next(
        (view for view in views if str(view.get("key")) == str(matrix.get("defaultMonth"))),
        views[0] if views else {"label": "mês atual", "rows": []},
    )
    totals = {row.get("key"): float(row.get("total", 0) or 0) for row in default_view.get("rows", [])}
    month_label = default_view.get("label", "mês atual")
    recurring_total = totals.get("rec_current_value", 0) + totals.get("rec_previous_value", 0)
    return {
        "layout": "financial_summary",
        "cards": [
            card("Faturamento total do mês", br_money(totals.get("total", 0)), f"Receitas recebidas · {month_label}", "activeBlue"),
            card("Recorrência recebida", br_money(recurring_total), f"COBRANÇA · {month_label}", "activeCyan"),
            card("Planos vendidos", br_money(totals.get("plans", 0)), f"VENDAS · {month_label}", "activeTeal"),
            card("Agregadores", br_money(totals.get("aggregators", 0)), f"Wellhub + TotalPass · {month_label}", "activeGreen"),
            card("Ticket Médio de Recebimento", br_money(received_ticket_mean), f"{br_int(received_ticket_count)} recebimentos", "activeBlue"),
        ],
        "charts": [matrix] + ([{
            "type": "bar",
            "title": "Status de pagamento por competência",
            "className": "chart-payment-status compact",
            "palette": "active",
            "maxValue": 100,
            "rows": payment_rows,
        }] if payment_rows is not None else []) + (extra_charts or []),
    }


def growth_waterfall_chart(
    active_count: int,
    sales_count: int,
    cancellation_count: int,
    non_renewed_count: int,
    period_label: str,
) -> dict:
    """Build the sales growth bridge requested by the business.

    The explicit rule is: active base + valid sales - valid cancellations -
    non-renewed contracts.
    """
    active_value = max(int(active_count or 0), 0)
    sales_value = max(int(sales_count or 0), 0)
    cancellation_value = max(int(cancellation_count or 0), 0)
    non_renewed_value = max(int(non_renewed_count or 0), 0)
    ending_value = active_value + sales_value - cancellation_value - non_renewed_value
    return {
        "type": "waterfall",
        "title": "Crescimento",
        "subtitle": f"Ativos + vendas válidas - cancelamentos válidos - não renovados · {period_label}",
        "className": "chart-sales-growth",
        "palette": "active",
        "rows": [
            {"label": "Ativos", "value": active_value, "kind": "total"},
            {"label": "Vendas", "value": sales_value, "kind": "increase"},
            {"label": "Cancelamentos", "value": -cancellation_value, "kind": "decrease", "tone": "wellhub"},
            {"label": "Não renovados", "value": -non_renewed_value, "kind": "decrease", "tone": "growthOrange"},
            {"label": "Saldo estimado", "value": ending_value, "kind": "result"},
        ],
    }


def financial_revenue_filter_chart(matrix: dict) -> dict:
    """Expose auditable Financeiro components as chart-local filter views."""
    views = matrix.get("views", [])
    default_key = str(matrix.get("defaultMonth") or (views[0].get("key") if views else ""))
    selected = next((view for view in views if str(view.get("key")) == default_key), views[0] if views else {"rows": []})
    units = list(matrix.get("units", []))
    rows_by_key = {str(row.get("key")): row for row in selected.get("rows", [])}

    def values_for(*keys: str) -> list[float]:
        values = [0.0 for _ in units]
        for key in keys:
            source_values = list(rows_by_key.get(key, {}).get("values", []))
            for index in range(len(units)):
                values[index] += float(source_values[index] if index < len(source_values) else 0.0)
        return values

    view_specs = [
        ("total", "Total", ("total",)),
        ("sales", "Vendas", ("plans",)),
        ("recurrences", "Recorrências", ("rec_current_value",)),
        ("recovery", "Recuperação", ("rec_previous_value",)),
        ("wellhub", "Wellhub", ("wellhub",)),
        ("totalpass", "TotalPass", ("totalpass",)),
    ]
    chart_views = []
    for key, label, source_keys in view_specs:
        values = values_for(*source_keys)
        chart_views.append({
            "key": key,
            "label": label,
            "total": round(sum(values), 2),
            "rows": [
                {"label": unit, "value": round(values[index], 2), "display": br_money(values[index])}
                for index, unit in enumerate(units)
            ],
        })
    return {
        "type": "financialRevenueFilter",
        "title": "Faturamento mês atual",
        "subtitle": f"Composição por unidade · {selected.get('label', 'mês atual')}",
        "className": "chart-profile-revenue",
        "palette": "active",
        "defaultView": "total",
        "views": chart_views,
    }


def unit_rows(series: pd.Series, total: int | None = None, medals: bool = False) -> list[dict]:
    clean = series.fillna("").map(branch_name).astype(str)
    clean = clean[clean.ne("")]
    clean = clean[~clean.str.lower().isin({"nan", "none", "nat"})]
    clean = clean[~clean.isin(EXCLUDED_UNITS)]
    counts = clean.value_counts()
    base = total or int(counts.sum()) or 1
    medal_by_label = {}
    if medals:
        ranked = sorted(
            [(label, int(value)) for label, value in counts.items() if label in UNIT_ORDER],
            key=lambda item: (-item[1], UNIT_ORDER.index(item[0])),
        )
        for label, medal in zip((label for label, value in ranked if value > 0), MEDAL_SEQUENCE):
            medal_by_label[label] = medal
    rows = []
    seen = set()
    for label in UNIT_ORDER:
        value = int(counts.get(label, 0))
        rows.append({"label": label, "value": value, "pct": float(value / base * 100), "medal": medal_by_label.get(label, "")})
        seen.add(label)
    extras = [(label, int(value)) for label, value in counts.items() if label not in seen]
    for label, value in sorted(extras, key=lambda item: norm_key(item[0])):
        rows.append({"label": str(label), "value": value, "pct": float(value / base * 100), "medal": ""})
    return rows


def aggregator_unique_unit_chart(access_units: pd.Series, access_channels: pd.Series, access_ids: pd.Series) -> dict:
    frame = pd.DataFrame({
        "unit": access_units.fillna("").map(branch_name),
        "channel": access_channels.fillna("").astype(str),
        "id": id_series(access_ids),
    })
    frame = frame[
        frame["unit"].isin(UNIT_ORDER)
        & frame["channel"].isin(["Wellhub", "TotalPass"])
        & frame["id"].ne("")
    ].copy()
    counts = frame.groupby(["unit", "channel"])["id"].nunique() if not frame.empty else pd.Series(dtype=int)
    access_counts = frame.groupby(["unit", "channel"]).size() if not frame.empty else pd.Series(dtype=int)
    unit_access_counts = frame.groupby("unit").size() if not frame.empty else pd.Series(dtype=int)
    unit_user_counts = frame.groupby("unit")["id"].nunique() if not frame.empty else pd.Series(dtype=int)
    rows = []
    for opening_order, unit in enumerate(UNIT_ORDER):
        wellhub = int(counts.get((unit, "Wellhub"), 0))
        totalpass = int(counts.get((unit, "TotalPass"), 0))
        wellhub_accesses = int(access_counts.get((unit, "Wellhub"), 0))
        totalpass_accesses = int(access_counts.get((unit, "TotalPass"), 0))
        total_accesses = int(unit_access_counts.get(unit, 0))
        unique_users = int(unit_user_counts.get(unit, 0))
        rows.append({
            "label": unit,
            "wellhub": wellhub,
            "totalpass": totalpass,
            "total": wellhub + totalpass,
            "wellhubAccesses": wellhub_accesses,
            "totalpassAccesses": totalpass_accesses,
            "totalAccesses": total_accesses,
            "uniqueUsers": unique_users,
            "averageVisits": total_accesses / unique_users if unique_users else 0.0,
            "openingOrder": opening_order,
            "stars": 0,
        })
    ranked = sorted(
        (row for row in rows if row["uniqueUsers"] > 0),
        key=lambda row: (-row["averageVisits"], -row["totalAccesses"], row["openingOrder"]),
    )
    for stars, row in zip((3, 2, 1), ranked[:3]):
        row["stars"] = stars
    network = frame.drop_duplicates(["channel", "id"]).groupby("channel")["id"].nunique() if not frame.empty else pd.Series(dtype=int)
    network_accesses = frame.groupby("channel").size() if not frame.empty else pd.Series(dtype=int)
    network_wellhub = int(network.get("Wellhub", 0))
    network_totalpass = int(network.get("TotalPass", 0))
    network_unique_users = int(frame["id"].nunique()) if not frame.empty else 0
    network_total_accesses = int(len(frame))
    return {
        "type": "aggregatorUnique",
        "title": "AGREGADORES POR UNIDADE",
        "subtitle": "Acessos e Alunos Wellhub e TotalPass",
        "className": "chart-active-aggregators",
        "rows": rows,
        "network": {
            "wellhub": network_wellhub,
            "totalpass": network_totalpass,
            "total": network_wellhub + network_totalpass,
            "wellhubAccesses": int(network_accesses.get("Wellhub", 0)),
            "totalpassAccesses": int(network_accesses.get("TotalPass", 0)),
            "totalAccesses": network_total_accesses,
            "uniqueUsers": network_unique_users,
            "averageVisits": network_total_accesses / network_unique_users if network_unique_users else 0.0,
        },
    }


def weekly_access_unit_rows(units: pd.Series, channels: pd.Series, dates: pd.Series) -> list[dict]:
    frame = pd.DataFrame({
        "unit": units.fillna("").map(branch_name),
        "channel": channels.fillna("").astype(str),
        "date": dates,
    })
    frame = frame[frame["unit"].ne("") & frame["date"].notna()]
    frame = frame[~frame["unit"].isin(EXCLUDED_UNITS)].copy()
    if frame.empty:
        return []
    frame["day"] = frame["date"].dt.normalize()
    days_count = int(frame["day"].dropna().nunique()) or 1
    frame["group"] = np.where(frame["channel"].eq("Unidade"), "own", "aggregator")
    grouped = frame.groupby(["unit", "group"], dropna=True).size().unstack(fill_value=0)

    def average_for(unit: str, group: str) -> float:
        if unit not in grouped.index or group not in grouped.columns:
            return 0.0
        return float(grouped.loc[unit, group]) / days_count

    order_index = {unit: index for index, unit in enumerate(UNIT_ORDER)}
    own_ranked = sorted(
        [(unit, average_for(unit, "own")) for unit in UNIT_ORDER],
        key=lambda item: (-item[1], order_index[item[0]]),
    )
    aggregator_ranked = sorted(
        [(unit, average_for(unit, "aggregator")) for unit in UNIT_ORDER],
        key=lambda item: (-item[1], order_index[item[0]]),
    )
    own_medals = {unit: medal for (unit, value), medal in zip((item for item in own_ranked if item[1] > 0), MEDAL_SEQUENCE)}
    aggregator_medals = {unit: medal for (unit, value), medal in zip((item for item in aggregator_ranked if item[1] > 0), MEDAL_SEQUENCE)}

    def display_average(value: float) -> str:
        return f"{value:.1f}/dia".replace(".", ",")

    def row_for(unit: str) -> dict:
        own = average_for(unit, "own")
        aggregator = average_for(unit, "aggregator")
        bars = [
            {
                "label": "Alunos próprios",
                "value": own,
                "display": display_average(own),
                "tone": "blue",
                "medal": own_medals.get(unit, ""),
            },
            {
                "label": "Agregadores",
                "value": aggregator,
                "display": display_average(aggregator),
                "tone": "orange",
                "medal": aggregator_medals.get(unit, ""),
            },
        ]
        return {
            "label": unit,
            "value": max(own, aggregator),
            "bars": bars,
            "segments": bars,
        }

    rows = [row_for(unit) for unit in UNIT_ORDER]
    extras = sorted([unit for unit in grouped.index if unit not in set(UNIT_ORDER)], key=norm_key)
    rows.extend(row_for(str(unit)) for unit in extras)
    return rows


def access_daily_unit_comparison_chart(units: pd.Series, dates: pd.Series) -> dict | None:
    frame = pd.DataFrame({"unit": units.fillna("").map(branch_name), "date": dates})
    frame = frame[frame["unit"].ne("") & frame["date"].notna()]
    frame = frame[~frame["unit"].isin(EXCLUDED_UNITS)].copy()
    if frame.empty:
        return None
    frame["day"] = frame["date"].dt.normalize()
    frame["month"] = frame["date"].dt.to_period("M")
    month = frame["month"].max()
    frame = frame[frame["month"].eq(month)].copy()
    if frame.empty:
        return None

    pivot = frame.groupby(["day", "unit"]).size().unstack(fill_value=0).sort_index()
    monthly_totals = pivot.sum(axis=0)
    candidate_units = [unit for unit in UNIT_ORDER if unit in monthly_totals.index and float(monthly_totals[unit]) > 0]
    if len(candidate_units) < 2:
        return None

    order_index = {unit: index for index, unit in enumerate(UNIT_ORDER)}
    ranked = sorted(candidate_units, key=lambda unit: (-float(monthly_totals[unit]), order_index[unit]))
    highest_unit = ranked[0]
    lowest_unit = ranked[-1]
    median_series = pivot[candidate_units].median(axis=1)
    palette = ["#38a3ff", "#ff5049", "#ffbd14", "#b56cff", "#00d7ff", "#ff7b54", "#8be28b", "#d693ff", "#5f8dff", "#ff6faa", "#65d1a5", "#ffc95c", "#9aaeff", "#f58e8e"]
    unit_key_by_name = {unit: f"unit_{index}" for index, unit in enumerate(candidate_units)}
    unit_series = [
        {
            "key": unit_key_by_name[unit],
            "label": unit,
            "color": palette[index % len(palette)],
            "selectable": True,
        }
        for index, unit in enumerate(candidate_units)
    ]

    rows = []
    for day, row in pivot.iterrows():
        rows.append({
            "label": day.strftime("%d/%m"),
            "median": float(median_series.loc[day]),
            **{unit_key_by_name[unit]: int(row.get(unit, 0)) for unit in candidate_units},
        })

    month_label = f"{MONTH_ABBR.get(int(month.month), str(month.month).zfill(2))}/{month.year}"
    return {
        "type": "lineChart",
        "title": "Comparativo diário de frequência por unidade",
        "subtitle": f"{month_label}: selecione as unidades que deseja comparar; linha laranja = mediana diária da rede.",
        "className": "chart-access-daily-comparison line-chart",
        "selectableSeries": True,
        "defaultSelectedKeys": [unit_key_by_name[highest_unit], unit_key_by_name[lowest_unit]],
        "series": unit_series + [
            {"key": "median", "label": "Mediana da rede", "tone": "orange", "fixed": True},
        ],
        "rows": rows,
    }


def unit_rows_low_medals(series: pd.Series, total: int | None = None) -> list[dict]:
    clean = series.fillna("").map(branch_name)
    clean = clean[clean.ne("")]
    clean = clean[~clean.str.lower().isin({"nan", "none", "nat"})]
    clean = clean[~clean.isin(EXCLUDED_UNITS)]
    counts = clean.value_counts()
    base = total or int(counts.sum()) or 1
    ranked = sorted(
        [(label, int(counts.get(label, 0))) for label in UNIT_ORDER],
        key=lambda item: (item[1], UNIT_ORDER.index(item[0])),
    )
    medal_by_label = {
        label: medal
        for (label, value), medal in zip(ranked, MEDAL_SEQUENCE)
    }
    rows = []
    seen = set()
    for label in UNIT_ORDER:
        value = int(counts.get(label, 0))
        rows.append({"label": label, "value": value, "pct": float(value / base * 100), "medal": medal_by_label.get(label, "")})
        seen.add(label)
    extras = [(label, int(value)) for label, value in counts.items() if label not in seen]
    for label, value in sorted(extras, key=lambda item: norm_key(item[0])):
        rows.append({"label": str(label), "value": value, "pct": float(value / base * 100), "medal": ""})
    return rows


def cancellation_unit_multi_rows(units: pd.Series, cancel_dates: pd.Series, reasons: pd.Series) -> list[dict]:
    frame = pd.DataFrame({
        "unit": units.fillna("").map(branch_name),
        "date": cancel_dates,
        "reason": reasons,
    })
    frame = frame[frame["unit"].ne("")]
    frame = frame[~frame["unit"].isin(EXCLUDED_UNITS)].copy()
    frame["month"] = frame["date"].dt.to_period("M")
    frame["inadimplencia"] = frame["reason"].map(is_inadimplencia_reason)
    months_count = int(frame["month"].dropna().nunique()) or 1
    grouped = frame.groupby("unit", dropna=True).agg(
        total=("unit", "size"),
        inadimplencia=("inadimplencia", "sum"),
    )
    order_index = {unit: index for index, unit in enumerate(UNIT_ORDER)}
    ranked = sorted(
        [
            (unit, float(grouped.loc[unit, "total"]) / months_count if unit in grouped.index else 0.0, int(grouped.loc[unit, "total"]) if unit in grouped.index else 0)
            for unit in UNIT_ORDER
        ],
        key=lambda item: (item[1], item[2], order_index[item[0]]),
    )
    medal_by_label = {
        unit: medal
        for (unit, monthly_average, total), medal in zip(ranked, MEDAL_SEQUENCE)
    }

    def row_for(unit: str) -> dict:
        if unit in grouped.index:
            total = int(grouped.loc[unit, "total"])
            inadimplencia = int(grouped.loc[unit, "inadimplencia"])
        else:
            total = 0
            inadimplencia = 0
        solicitados = max(total - inadimplencia, 0)
        monthly_average = total / months_count
        return {
            "label": unit,
            "value": monthly_average,
            "bars": [
                {"label": "Cancelamentos solicitados", "value": solicitados, "display": f"{br_int(solicitados)} solicitados", "tone": "blue"},
                {"label": "Média mensal", "value": monthly_average, "display": f"{monthly_average:.1f}/mês".replace(".", ","), "tone": "orange"},
                {"label": "Inadimplência", "value": inadimplencia, "display": f"{br_int(inadimplencia)} inad.", "tone": "red"},
            ],
            "medal": medal_by_label.get(unit, ""),
        }

    rows = [row_for(unit) for unit in UNIT_ORDER]
    extras = sorted([unit for unit in grouped.index if unit not in set(UNIT_ORDER)], key=norm_key)
    rows.extend(row_for(str(unit)) for unit in extras)
    return rows


def scoped_non_renewed_rows(
    frame: pd.DataFrame,
    period_start: pd.Timestamp | None = None,
    period_end: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Filter effective non-renewals and keep one record per contract.

    DataFim is the business-effective date. Without an explicit dashboard
    period, the current competence is used only through today.
    """
    if frame.empty:
        return frame.copy()
    work = frame.copy()
    effective_dates = parse_date(work.get("DataFim", pd.Series(index=work.index, dtype=str)))
    if period_start is not None or period_end is not None:
        work = filter_frame_by_date(work, effective_dates, period_start, period_end)
    else:
        today = pd.Timestamp(date.today()).normalize()
        work = work.loc[
            effective_dates.dt.to_period("M").eq(today.to_period("M"))
            & effective_dates.le(today)
        ].copy()
    if work.empty:
        return work
    effective_dates = parse_date(work.get("DataFim", pd.Series(index=work.index, dtype=str)))
    row_ids = id_series(work.get("id", pd.Series(index=work.index, dtype=str)))
    client_ids = id_series(work.get("idCliente", pd.Series(index=work.index, dtype=str)))
    contract_names = work.get("ContratoAnterior", pd.Series(index=work.index, dtype=str)).fillna("").astype(str).str.strip()
    unit_names = work.get("unidade_nome", pd.Series(index=work.index, dtype=str)).fillna("").astype(str).str.strip()
    fallback_contract_ids = (
        client_ids
        + "|"
        + contract_names
        + "|"
        + effective_dates.dt.strftime("%Y-%m-%d").fillna("")
        + "|"
        + unit_names
    )
    work["_non_renewed_id"] = row_ids.where(row_ids.ne(""), fallback_contract_ids)
    work["_non_renewed_date"] = effective_dates
    work = work.loc[
        work["_non_renewed_id"].ne("")
        & work["_non_renewed_date"].notna()
        & work.get("unidade_nome", pd.Series(index=work.index, dtype=str)).fillna("").ne("")
    ].copy()
    return (
        work.sort_values(["_non_renewed_date", "_non_renewed_id"])
        .drop_duplicates("_non_renewed_id", keep="last")
        .copy()
    )


def cancellation_unit_column_rows(
    units: pd.Series,
    cancel_dates: pd.Series,
    reasons: pd.Series,
    non_renewed_units: pd.Series | None = None,
) -> list[dict]:
    """Convert cancellations and non-renewals into stacked columns by unit."""
    rows = cancellation_unit_multi_rows(units, cancel_dates, reasons)
    non_renewed_counts = (
        non_renewed_units.fillna("").map(branch_name).value_counts()
        if non_renewed_units is not None and len(non_renewed_units)
        else pd.Series(dtype=int)
    )
    return [
        {
            "label": row.get("label", ""),
            "value": (
                sum(float(bar.get("value", 0) or 0) for bar in row.get("bars", []) if bar.get("label") != "Média mensal")
                + int(non_renewed_counts.get(row.get("label", ""), 0))
            ),
            "medal": row.get("medal", ""),
            "segments": [
                {
                    "label": bar.get("label", ""),
                    "value": float(bar.get("value", 0) or 0),
                    "tone": bar.get("tone", ""),
                }
                for bar in row.get("bars", [])
                if bar.get("label") != "Média mensal"
            ] + [{
                "label": "Não renovados",
                "value": int(non_renewed_counts.get(row.get("label", ""), 0)),
                "tone": "activeTeal",
            }],
        }
        for row in rows
    ]


def cannibalization_period_chart(
    cancellations: pd.DataFrame,
    access: pd.DataFrame,
    period_start: pd.Timestamp | None = None,
    period_end: pd.Timestamp | None = None,
) -> dict:
    """Count former own students who later accessed through an aggregator.

    Each member is counted once: the latest valid cancellation establishes the
    period and the first Wellhub/TotalPass access on or after that cancellation
    establishes the unit.
    """
    empty_chart = {
        "type": "cannibalizationPeriod",
        "title": "CANIBALIZAÇÃO",
        "subtitle": (
            "IDs únicos com cancelamento e acesso posterior em Wellhub ou TotalPass · "
            "período = último cancelamento · unidade = primeiro acesso como agregador"
        ),
        "className": "chart-cancel-cannibalization",
        "defaultPeriod": "all",
        "overall": {"key": "all", "label": "Todos os períodos", "total": 0, "rows": []},
        "periods": [],
    }
    if cancellations.empty or access.empty:
        return empty_chart

    cancel_frame = pd.DataFrame({
        "id": id_series(cancellations.get("idMember")),
        "cancel_date": parse_date(cancellations.get("dataCancelamento")),
    })
    cancel_frame = cancel_frame[
        cancel_frame["id"].ne("")
        & ~cancel_frame["id"].isin({"nan", "None", "NaT"})
        & cancel_frame["cancel_date"].notna()
    ].copy()
    if cancel_frame.empty:
        return empty_chart
    latest_cancellation = (
        cancel_frame.sort_values(["id", "cancel_date"])
        .drop_duplicates("id", keep="last")
    )

    access_units = access.get("unidade_nome", pd.Series(index=access.index, dtype=str)).fillna("").map(branch_name)
    missing_unit = access_units.eq("")
    if missing_unit.any():
        access_units.loc[missing_unit] = access.get(
            "id_branch", pd.Series(index=access.index, dtype=str)
        ).loc[missing_unit].map(branch_name)
    access_frame = pd.DataFrame({
        "id": id_series(access.get("id_member")),
        "access_date": parse_date(access.get("date_event")),
        "unit": access_units,
        "channel": access.get("canal", pd.Series(index=access.index, dtype=str)).fillna("").astype(str),
    })
    access_frame = access_frame[
        access_frame["channel"].isin({"Wellhub", "TotalPass"})
        & access_frame["id"].ne("")
        & ~access_frame["id"].isin({"nan", "None", "NaT"})
        & access_frame["access_date"].notna()
        & access_frame["unit"].isin(UNIT_ORDER)
    ].copy()
    if access_frame.empty:
        return empty_chart

    candidates = access_frame.merge(latest_cancellation, on="id", how="inner")
    candidates = candidates[candidates["access_date"].ge(candidates["cancel_date"])].copy()
    if candidates.empty:
        return empty_chart
    unit_order = {unit: index for index, unit in enumerate(UNIT_ORDER)}
    candidates["unit_order"] = candidates["unit"].map(unit_order)
    switched = (
        candidates.sort_values(["id", "access_date", "unit_order", "channel"])
        .drop_duplicates("id", keep="first")
        .copy()
    )

    visible = switched.copy()
    if period_start is not None:
        visible = visible[visible["cancel_date"].ge(period_start)]
    if period_end is not None:
        visible = visible[visible["cancel_date"].lt(period_end + pd.Timedelta(days=1))]
    visible = visible.copy()
    visible["period"] = visible["cancel_date"].dt.to_period("M")

    def rows_for(frame: pd.DataFrame) -> list[dict]:
        counts = frame.groupby("unit")["id"].nunique() if not frame.empty else pd.Series(dtype=int)
        return [
            {
                "label": unit,
                "value": int(counts.get(unit, 0)),
                "openingOrder": unit_order[unit],
            }
            for unit in UNIT_ORDER
        ]

    overall_rows = rows_for(visible)
    periods = []
    for period in sorted(visible["period"].dropna().unique()):
        period_frame = visible[visible["period"].eq(period)]
        periods.append({
            "key": str(period),
            "label": f"{MONTH_ABBR.get(period.month, period.month)}/{period.year}",
            "total": int(period_frame["id"].nunique()),
            "rows": rows_for(period_frame),
        })

    chart = dict(empty_chart)
    chart.update({
        "defaultPeriod": periods[-1]["key"] if periods else "all",
        "overall": {
            "key": "all",
            "label": "Todos os períodos",
            "total": int(visible["id"].nunique()),
            "rows": overall_rows,
        },
        "periods": periods,
    })
    return chart


def cancellation_before_purchase_rows(
    units: pd.Series,
    ids: pd.Series,
    sale_dates: pd.Series,
    cancel_dates: pd.Series,
    active_days: pd.Series,
    threshold_days: int,
) -> list[dict]:
    frame = pd.DataFrame({
        "unit": units.fillna("").map(branch_name),
        "id": id_series(ids),
        "sale_date": sale_dates,
        "cancel_date": cancel_dates,
        "active_days": active_days,
    })
    frame = frame[frame["unit"].ne("") & frame["id"].ne("")]
    frame = frame[~frame["unit"].isin(EXCLUDED_UNITS)].copy()
    if frame.empty:
        return [
            {"label": unit, "value": 0, "pct": 0.0, "display": "0/0 · 0,0%"}
            for unit in UNIT_ORDER
        ]

    date_days = (frame["cancel_date"] - frame["sale_date"]).dt.days
    frame["days_after_purchase"] = date_days.where(date_days.notna(), frame["active_days"])
    frame = frame[frame["days_after_purchase"].notna() & frame["days_after_purchase"].ge(0)]
    qualified = frame[frame["days_after_purchase"].lt(threshold_days)]

    total_by_unit = frame.groupby("unit")["id"].nunique()
    qualified_by_unit = qualified.groupby("unit")["id"].nunique()

    rows = []
    seen = set()
    for unit in UNIT_ORDER:
        total = int(total_by_unit.get(unit, 0))
        value = int(qualified_by_unit.get(unit, 0))
        pct_value = value / max(total, 1) * 100
        rows.append({
            "label": unit,
            "value": value,
            "pct": pct_value,
            "display": f"{br_int(value)}/{br_int(total)} · {br_pct(pct_value)}",
        })
        seen.add(unit)

    extras = sorted(set(total_by_unit.index) - seen, key=norm_key)
    for unit in extras:
        total = int(total_by_unit.get(unit, 0))
        value = int(qualified_by_unit.get(unit, 0))
        pct_value = value / max(total, 1) * 100
        rows.append({
            "label": str(unit),
            "value": value,
            "pct": pct_value,
            "display": f"{br_int(value)}/{br_int(total)} · {br_pct(pct_value)}",
        })
    return rows


def churn_unit_rows(
    cancel_units: pd.Series,
    cancel_ids: pd.Series,
    cancel_dates: pd.Series,
    cancel_start_dates: pd.Series,
    cancel_sale_ids: pd.Series,
    sales_units: pd.Series,
    sales_ids: pd.Series,
    sales_dates: pd.Series,
    sales_start_dates: pd.Series,
    sales_sale_ids: pd.Series,
    active_units: pd.Series,
    active_ids: pd.Series,
    active_days: pd.Series,
    reference_date: pd.Timestamp | None = None,
    non_renewed_units: pd.Series | None = None,
    non_renewed_dates: pd.Series | None = None,
) -> list[dict]:
    cancels = pd.DataFrame({
        "unit": cancel_units.fillna("").map(branch_name),
        "id": cancel_ids,
        "cancel_date": cancel_dates,
        "start": cancel_start_dates,
        "sale_id": cancel_sale_ids,
    })
    cancels = cancels[cancels["unit"].ne("") & cancels["id"].ne("") & cancels["cancel_date"].notna()]
    cancels = cancels[~cancels["unit"].isin(EXCLUDED_UNITS)].copy()
    non_renewed = pd.DataFrame({
        "unit": (
            non_renewed_units.fillna("").map(branch_name)
            if non_renewed_units is not None
            else pd.Series(dtype=str)
        ),
        "non_renewed_date": (
            non_renewed_dates
            if non_renewed_dates is not None
            else pd.Series(dtype="datetime64[ns]")
        ),
    })
    non_renewed = non_renewed[
        non_renewed["unit"].ne("") & non_renewed["non_renewed_date"].notna()
    ].copy()
    non_renewed = non_renewed[~non_renewed["unit"].isin(EXCLUDED_UNITS)].copy()
    if cancels.empty and non_renewed.empty:
        return [{"label": unit, "value": 0, "pct": 0.0, "display": "0/0 · 0,0%"} for unit in UNIT_ORDER]

    cancel_by_sale = (
        cancels[cancels["sale_id"].ne("")]
        .sort_values("cancel_date")
        .drop_duplicates("sale_id")
        .set_index("sale_id")["cancel_date"]
        .to_dict()
    )
    sales_periods = pd.DataFrame({
        "unit": sales_units.fillna("").map(branch_name),
        "id": sales_ids,
        "start": sales_start_dates.where(sales_start_dates.notna(), sales_dates),
        "sale_id": sales_sale_ids,
    })
    sales_periods = sales_periods[sales_periods["unit"].ne("") & sales_periods["id"].ne("") & sales_periods["start"].notna()]
    sales_periods = sales_periods[~sales_periods["unit"].isin(EXCLUDED_UNITS)].copy()
    sales_periods["end"] = sales_periods["sale_id"].map(cancel_by_sale)

    cancel_periods = pd.DataFrame({
        "unit": cancels["unit"],
        "id": cancels["id"],
        "start": cancels["start"].where(cancels["start"].notna(), cancels["cancel_date"]),
        "end": cancels["cancel_date"],
    })

    today = (reference_date or pd.Timestamp.today()).normalize()
    active_periods = pd.DataFrame({
        "unit": active_units.fillna("").map(branch_name),
        "id": active_ids,
        "days": active_days,
    })
    active_periods = active_periods[active_periods["unit"].ne("") & active_periods["id"].ne("")]
    active_periods = active_periods[~active_periods["unit"].isin(EXCLUDED_UNITS)].copy()
    active_periods["start"] = today - pd.to_timedelta(active_periods["days"].fillna(0).clip(lower=0), unit="D")
    active_periods["end"] = pd.NaT

    periods = pd.concat(
        [
            sales_periods[["unit", "id", "start", "end"]],
            cancel_periods[["unit", "id", "start", "end"]],
            active_periods[["unit", "id", "start", "end"]],
        ],
        ignore_index=True,
    )
    periods["start"] = pd.to_datetime(periods["start"], errors="coerce")
    periods["end"] = pd.to_datetime(periods["end"], errors="coerce")
    periods = periods[periods["start"].notna()]

    months = sorted(
        set(cancels["cancel_date"].dt.to_period("M").dropna().unique())
        | set(non_renewed["non_renewed_date"].dt.to_period("M").dropna().unique())
    )
    totals = {
        unit: {"cancels": 0, "non_renewed": 0, "exits": 0, "base_sum": 0}
        for unit in UNIT_ORDER
    }
    for month in months:
        month_start = month.to_timestamp()
        snapshot = month_start - pd.Timedelta(days=1)
        month_cancels = cancels[cancels["cancel_date"].dt.to_period("M").eq(month)]
        month_non_renewed = non_renewed[
            non_renewed["non_renewed_date"].dt.to_period("M").eq(month)
        ]
        for unit in UNIT_ORDER:
            cancel_count = int(month_cancels["unit"].eq(unit).sum())
            non_renewed_count = int(month_non_renewed["unit"].eq(unit).sum())
            exit_count = cancel_count + non_renewed_count
            active_mask = (
                periods["unit"].eq(unit)
                & periods["start"].le(snapshot)
                & (periods["end"].isna() | periods["end"].gt(snapshot))
            )
            active_base = int(periods.loc[active_mask, "id"].nunique())
            totals[unit]["cancels"] += cancel_count
            totals[unit]["non_renewed"] += non_renewed_count
            totals[unit]["exits"] += exit_count
            totals[unit]["base_sum"] += active_base

    ranked = sorted(
        [
            (
                unit,
                totals[unit]["exits"] / max(totals[unit]["base_sum"], 1) * 100,
                totals[unit]["exits"],
            )
            for unit in UNIT_ORDER
            if totals[unit]["base_sum"] > 0
        ],
        key=lambda item: (item[1], item[2], UNIT_ORDER.index(item[0])),
    )
    medal_by_label = {
        unit: medal
        for (unit, rate, cancel_count), medal in zip(ranked, MEDAL_SEQUENCE)
    }
    rows = []
    for unit in UNIT_ORDER:
        cancel_count = totals[unit]["cancels"]
        non_renewed_count = totals[unit]["non_renewed"]
        exit_count = totals[unit]["exits"]
        base_sum = totals[unit]["base_sum"]
        rate = exit_count / max(base_sum, 1) * 100
        rows.append({
            "label": unit,
            "value": rate,
            "pct": rate,
            "display": f"{br_int(exit_count)}/{br_int(base_sum)} · {br_pct(rate)}",
            "cancellations": cancel_count,
            "nonRenewed": non_renewed_count,
            "medal": medal_by_label.get(unit, ""),
            "valueClass": "alert" if rate > 8 else "",
        })
    return rows


def sales_success_unit_rows(units: pd.Series, sale_ids: pd.Series, active_ids: pd.Series) -> list[dict]:
    active_id_set = set(active_ids[active_ids.ne("")])
    frame = pd.DataFrame({
        "unit": units.fillna("").map(branch_name),
        "id": sale_ids,
    })
    frame = frame[frame["unit"].ne("") & frame["id"].ne("")]
    frame = frame[~frame["unit"].isin(EXCLUDED_UNITS)].copy()
    frame["active"] = frame["id"].isin(active_id_set).astype(int)
    grouped = frame.groupby("unit", dropna=True).agg(sold=("id", "size"), active=("active", "sum"))
    grouped["rate"] = grouped["active"] / grouped["sold"].clip(lower=1) * 100
    order_index = {unit: index for index, unit in enumerate(UNIT_ORDER)}
    ranked = sorted(
        [
            (unit, float(row["rate"]), int(row["active"]), int(row["sold"]))
            for unit, row in grouped.iterrows()
            if unit in UNIT_ORDER and int(row["sold"]) > 0
        ],
        key=lambda item: (-item[1], -item[2], -item[3], order_index.get(item[0], 10_000)),
    )
    medal_by_label = {
        unit: medal
        for (unit, rate, active, sold), medal in zip((item for item in ranked if item[1] > 0), MEDAL_SEQUENCE)
    }

    def row_for(unit: str) -> dict:
        if unit in grouped.index:
            sold = int(grouped.loc[unit, "sold"])
            active = int(grouped.loc[unit, "active"])
            rate = float(grouped.loc[unit, "rate"])
        else:
            sold = 0
            active = 0
            rate = 0.0
        return {
            "label": unit,
            "value": rate,
            "pct": rate,
            "display": f"{br_int(active)}/{br_int(sold)} · {br_pct(rate)}",
            "medal": medal_by_label.get(unit, ""),
            "valueClass": "alert" if sold > 0 and rate < 70 else "",
        }

    rows = [row_for(unit) for unit in UNIT_ORDER]
    extras = [unit for unit in grouped.index if unit not in set(UNIT_ORDER)]
    rows.extend(row_for(str(unit)) for unit in sorted(extras, key=norm_key))
    return rows


def sales_ticket_received_unit_rows(
    sale_units: pd.Series,
    sale_values: pd.Series,
    sale_contracts: pd.Series,
    charge_units: pd.Series,
    charge_values: pd.Series,
    charge_status: pd.Series,
) -> list[dict]:
    adjusted_sales = adjusted_sales_ticket_values(sale_values, sale_contracts)
    sales_frame = pd.DataFrame({
        "unit": sale_units.fillna("").map(branch_name),
        "value": adjusted_sales,
    })
    sales_frame = sales_frame[
        sales_frame["unit"].ne("")
        & ~sales_frame["unit"].isin(EXCLUDED_UNITS)
        & sales_frame["value"].notna()
        & sales_frame["value"].gt(0)
    ]

    received_frame = pd.DataFrame({
        "unit": charge_units.fillna("").map(branch_name),
        "value": charge_values,
        "status": charge_status.fillna("").astype(str).map(norm_key),
    })
    received_frame = received_frame[
        received_frame["unit"].ne("")
        & ~received_frame["unit"].isin(EXCLUDED_UNITS)
        & received_frame["value"].notna()
        & received_frame["value"].gt(0)
        & received_frame["status"].eq("recebido")
    ]

    sales_avg = sales_frame.groupby("unit")["value"].mean() if not sales_frame.empty else pd.Series(dtype=float)
    received_avg = received_frame.groupby("unit")["value"].mean() if not received_frame.empty else pd.Series(dtype=float)
    order_index = {unit: index for index, unit in enumerate(UNIT_ORDER)}
    ranked = sorted(
        [(unit, float(received_avg.get(unit, 0))) for unit in UNIT_ORDER],
        key=lambda item: (-item[1], order_index[item[0]]),
    )
    medal_by_label = {
        unit: medal
        for (unit, value), medal in zip((item for item in ranked if item[1] > 0), MEDAL_SEQUENCE)
    }

    def row_for(unit: str) -> dict:
        sale_ticket = float(sales_avg.get(unit, 0))
        received_ticket = float(received_avg.get(unit, 0))
        return {
            "label": unit,
            "value": received_ticket,
            "medianValue": received_ticket,
            "meanValue": sale_ticket,
            "medianDisplay": br_money(received_ticket),
            "meanDisplay": br_money(sale_ticket),
            "medal": medal_by_label.get(unit, ""),
        }

    rows = [row_for(unit) for unit in UNIT_ORDER]
    extras = sorted((set(sales_avg.index) | set(received_avg.index)) - set(UNIT_ORDER), key=norm_key)
    rows.extend(row_for(str(unit)) for unit in extras)
    return rows


def br_months(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        value = 0
    return f"{float(value):.1f}".replace(".", ",") + " meses"


def ltv_month_rows(labels: pd.Series, days: pd.Series, order: list[str] | None = None, limit: int | None = None, medals: bool = False) -> list[dict]:
    frame = pd.DataFrame({
        "label": labels.fillna("").astype(str).str.strip(),
        "days": days,
    })
    frame = frame[frame["label"].ne("")]
    frame = frame[~frame["label"].isin(EXCLUDED_UNITS)]
    frame = frame[frame["days"].notna() & frame["days"].ge(0)]
    grouped = frame.groupby("label", dropna=True)["days"].agg(["median", "mean"]) / 30
    medal_by_label = {}
    if medals:
        ordered_labels = set(order or grouped.index)
        order_index = {label: index for index, label in enumerate(order or [])}
        ranked = sorted(
            [(str(label), float(row["median"])) for label, row in grouped.iterrows() if str(label) in ordered_labels],
            key=lambda item: (-item[1], order_index.get(item[0], 10_000), norm_key(item[0])),
        )
        for label, medal in zip((label for label, value in ranked if value > 0), MEDAL_SEQUENCE):
            medal_by_label[label] = medal

    def row_for(label: str) -> dict:
        median_value = float(grouped.loc[label, "median"]) if label in grouped.index else 0
        mean_value = float(grouped.loc[label, "mean"]) if label in grouped.index else 0
        return {
            "label": str(label),
            "value": median_value,
            "medianValue": median_value,
            "meanValue": mean_value,
            "medianDisplay": br_months(median_value),
            "meanDisplay": br_months(mean_value),
            "medal": medal_by_label.get(str(label), ""),
        }

    rows = []
    if order:
        for label in order:
            rows.append(row_for(label))
        extras = [label for label in grouped.index if label not in set(order)]
        for label in sorted(extras, key=norm_key):
            rows.append(row_for(str(label)))
        return rows

    grouped = grouped.sort_values("median", ascending=False)
    if limit:
        grouped = grouped.head(limit)
    return [row_for(str(label)) for label in grouped.index]


def medal_board_rows(tabs: dict) -> list[dict]:
    medal_keys = {
        MEDAL_GOLD: "gold",
        MEDAL_SILVER: "silver",
        MEDAL_BRONZE: "bronze",
    }
    scores = {unit: {"unit": unit, "gold": 0, "silver": 0, "bronze": 0} for unit in UNIT_ORDER}
    for tab in tabs.values():
        for chart in tab.get("charts", []):
            if not isinstance(chart, dict):
                continue
            for row in chart.get("rows", []):
                unit = branch_name(row.get("label", ""))
                if unit not in scores or unit in EXCLUDED_UNITS:
                    continue
                awards = [row]
                awards.extend(row.get("bars", []))
                for award in awards:
                    medal = str(award.get("medal") or "")
                    stars = int(award.get("stars") or 0)
                    key = medal_keys.get(medal) or {3: "gold", 2: "silver", 1: "bronze"}.get(stars)
                    if key:
                        scores[unit][key] += 1

    for row in scores.values():
        row["total"] = row["gold"] * 3 + row["silver"] * 2 + row["bronze"]

    return sorted(
        scores.values(),
        key=lambda row: (
            -row["total"],
            -row["gold"],
            -row["silver"],
            -row["bronze"],
            UNIT_ORDER.index(row["unit"]),
        ),
    )


ANALYSIS_SNAPSHOT_FILE = OUT_DIR / "analysis_daily_snapshots.json"


def build_analysis_unit_matrix(
    tabs: dict,
    active: pd.DataFrame,
    charges: pd.DataFrame,
    access: pd.DataFrame,
    churn_risk_chart: dict | None,
    reference_date: pd.Timestamp,
    selected_units: list[str] | None = None,
) -> dict:
    """Consolidate unit-grain metrics already validated across the five operating tabs."""
    units = [unit for unit in UNIT_ORDER if not selected_units or unit in selected_units]
    columns = units + ["Rede"]
    rows: list[dict] = []

    def safe_float(value: object) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.0
        return number if math.isfinite(number) else 0.0

    def chart_by_class(fragment: str) -> dict:
        for tab_key in ("ativos", "vendas", "cancelamentos", "financeiro", "frequencia"):
            for chart in tabs.get(tab_key, {}).get("charts", []) or []:
                if isinstance(chart, dict) and fragment in str(chart.get("className") or ""):
                    return chart
        return {}

    def row_map(chart: dict, field: str = "value") -> dict[str, float]:
        return {
            branch_name(row.get("label", "")): float(row.get(field) or 0)
            for row in chart.get("rows", []) or []
            if branch_name(row.get("label", "")) in units
        }

    def add_row(
        section: str,
        key: str,
        label: str,
        values: dict[str, float | int],
        value_format: str = "int",
        network_value: float | int | None = None,
        aggregation: str = "sum",
        source: str = "",
        reset_mode: str = "month_to_date",
    ) -> None:
        normalized = {unit: values.get(unit, 0) for unit in units}
        if network_value is None:
            numeric = [float(normalized.get(unit, 0) or 0) for unit in units]
            if aggregation == "mean":
                nonzero = [value for value in numeric if value != 0]
                network_value = sum(nonzero) / len(nonzero) if nonzero else 0
            else:
                network_value = sum(numeric)
        normalized["Rede"] = network_value
        rows.append({
            "section": section,
            "key": key,
            "label": label,
            "format": value_format,
            "values": normalized,
            "source": source,
            "resetMode": reset_mode,
        })

    active_goal = chart_by_class("chart-active-goals")
    active_values = row_map(active_goal)
    active_goals = row_map(active_goal, "goal")
    active_goal_pct = row_map(active_goal, "goalPct")
    active_growth = row_map(active_goal, "growthDelta")
    active_growth_pct = row_map(active_goal, "growthPct")
    active_network = active_goal.get("network", {}) or {}
    add_row("Ativos e perfil", "active_total", "Alunos ativos", active_values, network_value=active_network.get("value", sum(active_values.values())), source="HISTORICO ATIVOS", reset_mode="snapshot")
    add_row("Ativos e perfil", "active_goal", "Meta de ativos", active_goals, network_value=active_network.get("goal", sum(active_goals.values())), source="Metas Diamante Total", reset_mode="snapshot")
    add_row("Ativos e perfil", "active_goal_pct", "Atingimento da meta de ativos", active_goal_pct, "pct", active_network.get("goalPct", 0), aggregation="mean", source="HISTORICO ATIVOS + metas", reset_mode="snapshot")
    add_row("Ativos e perfil", "active_growth", "Evolução de ativos no mês", active_growth, "signed_int", active_network.get("growthDelta", 0), source="HISTORICO ATIVOS")
    add_row("Ativos e perfil", "active_growth_pct", "Evolução percentual de ativos", active_growth_pct, "signed_pct", active_network.get("growthPct", 0), aggregation="mean", source="HISTORICO ATIVOS")

    active_frame = pd.DataFrame(index=active.index)
    active_frame["id"] = id_series(active.get("idMember", pd.Series(index=active.index, dtype=str)))
    active_frame["unit"] = active.get("unidade_nome", active.get("Filial", pd.Series(index=active.index, dtype=str))).map(branch_name)
    active_frame["days"] = parse_number(active.get("diasAtivo", pd.Series(index=active.index, dtype=float))).fillna(0)
    active_frame["gender"] = active.get("sexo", pd.Series(index=active.index, dtype=str)).map(clean_gender)
    birth_dates = parse_date(active.get("dataNascimento", pd.Series(index=active.index, dtype=str)))
    active_frame["age"] = ((reference_date.normalize() - birth_dates).dt.days / 365.2425).where(birth_dates.notna())
    active_frame["plan"] = active.get("contrato_norm", active.get("contrato", pd.Series(index=active.index, dtype=str)).map(clean_plan)).fillna("")
    active_frame = active_frame[active_frame["id"].ne("") & active_frame["unit"].isin(units)].drop_duplicates("id", keep="last")

    charge_frame = pd.DataFrame(index=charges.index)
    charge_frame["id"] = id_series(charges.get("idMember", pd.Series(index=charges.index, dtype=str)))
    charge_frame["status"] = charges.get("status", pd.Series(index=charges.index, dtype=str)).fillna("").map(norm_key)
    charge_frame["value"] = parse_number(charges.get("valorCompet", pd.Series(index=charges.index, dtype=float))).fillna(0)
    charge_frame["days"] = parse_number(charges.get("diasInad", pd.Series(index=charges.index, dtype=float))).fillna(0)
    overdue_ids = set(charge_frame.loc[charge_frame["status"].eq("a receber") & charge_frame["value"].gt(0) & charge_frame["days"].gt(0), "id"])
    active_frame["overdue"] = active_frame["id"].isin(overdue_ids)

    def unit_group_value(column: str, operation: str = "sum", predicate=None) -> dict[str, float]:
        work = active_frame if predicate is None else active_frame[predicate(active_frame)]
        grouped = work.groupby("unit")[column]
        result = grouped.mean() if operation == "mean" else grouped.nunique() if operation == "nunique" else grouped.sum()
        return {unit: float(result.get(unit, 0)) for unit in units}

    active_counts = {unit: int(active_frame.loc[active_frame["unit"].eq(unit), "id"].nunique()) for unit in units}
    overdue_counts = {unit: int(active_frame.loc[active_frame["unit"].eq(unit) & active_frame["overdue"], "id"].nunique()) for unit in units}
    compliant_counts = {unit: max(active_counts.get(unit, 0) - overdue_counts.get(unit, 0), 0) for unit in units}
    compliant_pct = {unit: compliant_counts[unit] / max(active_counts[unit], 1) * 100 for unit in units}
    overdue_pct = {unit: overdue_counts[unit] / max(active_counts[unit], 1) * 100 for unit in units}
    add_row("Ativos e perfil", "compliant_total", "Alunos adimplentes", compliant_counts, network_value=sum(compliant_counts.values()), source="Ativos_LTV + COBRANÇA", reset_mode="snapshot")
    add_row("Ativos e perfil", "compliant_pct", "Adimplência da base ativa", compliant_pct, "pct", sum(compliant_counts.values()) / max(sum(active_counts.values()), 1) * 100, aggregation="mean", source="Ativos_LTV + COBRANÇA", reset_mode="snapshot")
    add_row("Ativos e perfil", "overdue_total", "Alunos inadimplentes", overdue_counts, network_value=sum(overdue_counts.values()), source="Ativos_LTV + COBRANÇA", reset_mode="snapshot")
    add_row("Ativos e perfil", "overdue_pct", "Inadimplência da base ativa", overdue_pct, "pct", sum(overdue_counts.values()) / max(sum(active_counts.values()), 1) * 100, aggregation="mean", source="Ativos_LTV + COBRANÇA", reset_mode="snapshot")
    average_days = {unit: safe_float(active_frame.loc[active_frame["unit"].eq(unit), "days"].mean()) for unit in units}
    add_row("Ativos e perfil", "active_days_mean", "Média de dias ativos", average_days, "decimal", safe_float(active_frame["days"].mean()), aggregation="mean", source="Ativos_LTV", reset_mode="snapshot")
    average_age = {unit: safe_float(active_frame.loc[active_frame["unit"].eq(unit), "age"].mean()) for unit in units}
    add_row("Ativos e perfil", "age_mean", "Idade média", average_age, "decimal", safe_float(active_frame["age"].mean()), aggregation="mean", source="Ativos_LTV", reset_mode="snapshot")

    for gender_label, gender_key in (("Sexo feminino", "female"), ("Sexo masculino", "male"), ("Não informado", "gender_unknown")):
        counts = {unit: int((active_frame.loc[active_frame["unit"].eq(unit), "gender"] == gender_label).sum()) for unit in units}
        pcts = {unit: counts[unit] / max(active_counts[unit], 1) * 100 for unit in units}
        add_row("Ativos e perfil", f"{gender_key}_total", gender_label.replace("Sexo ", "").capitalize(), counts, network_value=sum(counts.values()), source="Ativos_LTV", reset_mode="snapshot")
        add_row("Ativos e perfil", f"{gender_key}_pct", f"{gender_label.replace('Sexo ', '').capitalize()} da base", pcts, "pct", sum(counts.values()) / max(sum(active_counts.values()), 1) * 100, aggregation="mean", source="Ativos_LTV", reset_mode="snapshot")

    age_bands = age_band_series(active.get("dataNascimento", pd.Series(index=active.index, dtype=str))).astype(str)
    active_frame["age_band"] = age_bands.reindex(active_frame.index).fillna("")
    for index, band in enumerate(AGE_BAND_LABELS):
        counts = {unit: int((active_frame.loc[active_frame["unit"].eq(unit), "age_band"] == band).sum()) for unit in units}
        add_row("Faixa etária", f"age_band_{index}", band, counts, network_value=sum(counts.values()), source="Ativos_LTV", reset_mode="snapshot")

    top_plans = [plan for plan in active_frame["plan"].value_counts().head(10).index if norm_text(plan)]
    for index, plan in enumerate(top_plans):
        counts = {unit: int((active_frame.loc[active_frame["unit"].eq(unit), "plan"] == plan).sum()) for unit in units}
        add_row("Planos ativos", f"active_plan_{index}", f"Plano ativo · {plan}", counts, network_value=sum(counts.values()), source="Ativos_LTV", reset_mode="snapshot")

    aggregator_chart = chart_by_class("chart-active-aggregators")
    aggregator_rows = {branch_name(row.get("label", "")): row for row in aggregator_chart.get("rows", []) or []}
    aggregator_network = aggregator_chart.get("network", {}) or {}
    for key, label, fmt, network_key in (
        ("wellhub", "Alunos Wellhub", "int", "wellhub"),
        ("totalpass", "Alunos TotalPass", "int", "totalpass"),
        ("wellhubAccesses", "Acessos Wellhub", "int", "wellhubAccesses"),
        ("totalpassAccesses", "Acessos TotalPass", "int", "totalpassAccesses"),
        ("averageVisits", "Média de visitas por agregador", "decimal", "averageVisits"),
    ):
        values = {unit: float(aggregator_rows.get(unit, {}).get(key) or 0) for unit in units}
        add_row("Agregadores", f"aggregator_{key}", label, values, fmt, aggregator_network.get(network_key, 0), aggregation="mean" if fmt == "decimal" else "sum", source="controle_acesso_wellhub + controle_acesso_totalpass")

    sales_units_chart = chart_by_class("chart-sales-units")
    sales_success_chart = chart_by_class("chart-sales-success")
    sales_ticket_chart = chart_by_class("chart-sales-ticket")
    add_row("Vendas", "sales_total", "Contratos vendidos", row_map(sales_units_chart), source="VENDAS")
    add_row("Vendas", "sales_success_pct", "Taxa de sucesso das vendas", row_map(sales_success_chart), "pct", aggregation="mean", source="VENDAS + Ativos_LTV")
    add_row("Vendas", "sales_ticket", "Ticket médio vendido", row_map(sales_ticket_chart, "meanValue"), "money", aggregation="mean", source="VENDAS")
    add_row("Vendas", "received_ticket", "Ticket médio recebido", row_map(sales_ticket_chart, "medianValue"), "money", aggregation="mean", source="COBRANÇA")

    cancel_chart = chart_by_class("chart-cancel-units")
    cancel_rows = {branch_name(row.get("label", "")): row for row in cancel_chart.get("rows", []) or []}
    for bar_index, key, label in ((0, "cancel_requested", "Cancelamentos solicitados"), (2, "cancel_overdue", "Cancelamentos por inadimplência")):
        values = {unit: float((cancel_rows.get(unit, {}).get("bars") or [{}, {}, {}])[bar_index].get("value") or 0) for unit in units}
        add_row("Cancelamentos", key, label, values, source="CANCELAMENTO")
    total_cancels = {unit: sum(float(bar.get("value") or 0) for bar in cancel_rows.get(unit, {}).get("bars", []) if bar.get("label") != "Média mensal") for unit in units}
    add_row("Cancelamentos", "cancel_total", "Cancelamentos totais", total_cancels, source="CANCELAMENTO")
    add_row("Cancelamentos", "churn_pct", "Churn", row_map(chart_by_class("chart-cancel-churn")), "pct", aggregation="mean", source="CANCELAMENTO + bases ativas")
    cannibalization = chart_by_class("chart-cancel-cannibalization")
    cannibalization_rows = cannibalization.get("overall", {}).get("rows", []) or []
    add_row("Cancelamentos", "cannibalization", "Canibalização", {branch_name(row.get("label", "")): float(row.get("value") or 0) for row in cannibalization_rows}, source="CANCELAMENTO + acessos agregadores")

    financial_chart = chart_by_class("chart-financial-matrix")
    financial_view = next((view for view in financial_chart.get("views", []) if str(view.get("key")) == str(financial_chart.get("defaultMonth"))), (financial_chart.get("views") or [{}])[0] if financial_chart.get("views") else {})
    financial_units = financial_chart.get("units", []) or []
    for index, finance_row in enumerate(financial_view.get("rows", []) or []):
        values_list = finance_row.get("values", []) or []
        values = {unit: float(values_list[financial_units.index(unit)] or 0) if unit in financial_units and financial_units.index(unit) < len(values_list) else 0 for unit in units}
        add_row("Financeiro", f"finance_{finance_row.get('key', index)}", finance_row.get("label", "Indicador financeiro"), values, "int" if finance_row.get("kind") == "count" else "money", finance_row.get("total", 0), source=finance_row.get("source", "FATURAMENTO / COBRANÇA / VENDAS / acessos"))

    weekly_chart = chart_by_class("chart-weekly-access-units")
    weekly_rows = {branch_name(row.get("label", "")): row for row in weekly_chart.get("rows", []) or []}
    for bar_index, key, label in ((0, "own_daily_access", "Média diária de acessos próprios"), (1, "aggregator_daily_access", "Média diária de acessos agregadores")):
        values = {unit: float((weekly_rows.get(unit, {}).get("bars") or [{}, {}])[bar_index].get("value") or 0) for unit in units}
        add_row("Frequência e risco", key, label, values, "decimal", aggregation="mean", source="controle_acesso")
    ltv_chart = chart_by_class("chart-ltv-unit")
    add_row("Frequência e risco", "ltv_median", "LTV mediana em meses", row_map(ltv_chart, "medianValue"), "decimal", aggregation="mean", source="Ativos_LTV", reset_mode="snapshot")
    add_row("Frequência e risco", "ltv_mean", "LTV média em meses", row_map(ltv_chart, "meanValue"), "decimal", aggregation="mean", source="Ativos_LTV", reset_mode="snapshot")

    risk_views = {view.get("label"): view for view in (churn_risk_chart or {}).get("views", []) or []}
    network_risk = risk_views.get("Rede", {})
    for band_key, band_label in (("Médio", "Risco médio"), ("Alto", "Risco alto"), ("Crítico", "Risco crítico")):
        values = {}
        for unit in units:
            distribution = {item.get("label"): item for item in risk_views.get(unit, {}).get("distribution", []) or []}
            values[unit] = float(distribution.get(band_key, {}).get("value") or 0)
        network_distribution = {item.get("label"): item for item in network_risk.get("distribution", []) or []}
        add_row("Frequência e risco", f"risk_{norm_key(band_key)}", band_label, values, network_value=network_distribution.get(band_key, {}).get("value", 0), source="Ativos_LTV + COBRANÇA + controle_acesso", reset_mode="snapshot")
    add_row("Frequência e risco", "risk_high_critical_pct", "Alunos em risco alto ou crítico", {unit: float(risk_views.get(unit, {}).get("highCriticalPct") or 0) for unit in units}, "pct", network_risk.get("highCriticalPct", 0), aggregation="mean", source="Ativos_LTV + COBRANÇA + controle_acesso", reset_mode="snapshot")
    add_row("Frequência e risco", "risk_average_score", "Score médio de evasão", {unit: float(risk_views.get(unit, {}).get("averageScore") or 0) for unit in units}, "score", network_risk.get("averageScore", 0), aggregation="mean", source="Ativos_LTV + COBRANÇA + controle_acesso", reset_mode="snapshot")

    for cluster_chart_key, prefix, source_label in (("Clusters por unidade - Alunos próprios", "own", "Ativos_LTV + controle_acesso"), ("Clusters por unidade - Agregadores", "aggregator", "acessos agregadores")):
        cluster_chart = next((chart for chart in tabs.get("frequencia", {}).get("charts", []) or [] if isinstance(chart, dict) and chart.get("title") == cluster_chart_key), {})
        cluster_rows = {row.get("unit"): row for row in cluster_chart.get("rows", []) or []}
        for cluster_label, _range_label, _tone_name in frequency_cluster_order():
            values = {}
            for unit in units:
                clusters = {item.get("label"): item for item in cluster_rows.get(unit, {}).get("clusters", []) or []}
                values[unit] = float(clusters.get(cluster_label, {}).get("value") or 0)
            add_row("Frequência e risco", f"{prefix}_cluster_{norm_key(cluster_label).replace(' ', '_')}", f"{cluster_label} · {'próprios' if prefix == 'own' else 'agregadores'}", values, source=source_label, reset_mode="snapshot")

    period_label = f"{MONTH_ABBR.get(reference_date.month, reference_date.month)}/{reference_date.year}"
    return {
        "title": "Matriz executiva por unidade",
        "subtitle": f"Indicadores das cinco abas · {period_label} · valores mensais respeitam o período global; estoques representam a fotografia atual.",
        "units": columns,
        "rows": rows,
        "referenceDate": reference_date.strftime("%d/%m/%Y"),
        "periodKey": reference_date.strftime("%Y-%m"),
    }


def analysis_matrix_history(matrix: dict, period_start: pd.Timestamp | None, period_end: pd.Timestamp | None) -> dict:
    if not ANALYSIS_SNAPSHOT_FILE.exists():
        return {"captures": 0, "firstDate": "", "lastDate": "", "deltas": {}}
    try:
        snapshots = json.loads(ANALYSIS_SNAPSHOT_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return {"captures": 0, "firstDate": "", "lastDate": "", "deltas": {}}
    start = (period_start or pd.Timestamp(matrix.get("periodKey", "") + "-01")).normalize()
    end = (period_end or pd.Timestamp.today()).normalize()
    eligible = []
    for snapshot in snapshots if isinstance(snapshots, list) else []:
        captured = pd.to_datetime(snapshot.get("date"), errors="coerce")
        if pd.notna(captured) and start <= captured.normalize() <= end:
            eligible.append(snapshot)
    eligible.sort(key=lambda item: item.get("date", ""))
    if not eligible:
        return {"captures": 0, "firstDate": "", "lastDate": "", "deltas": {}}
    first_rows = {row.get("key"): row for row in eligible[0].get("matrix", {}).get("rows", []) or []}
    deltas = {}
    for row in matrix.get("rows", []) or []:
        baseline = first_rows.get(row.get("key"), {}).get("values", {}) or {}
        deltas[row.get("key")] = {
            unit: float(row.get("values", {}).get(unit, 0) or 0) - float(baseline.get(unit, row.get("values", {}).get(unit, 0)) or 0)
            for unit in matrix.get("units", [])
        }
    return {
        "captures": len(eligible),
        "firstDate": eligible[0].get("date", ""),
        "lastDate": eligible[-1].get("date", ""),
        "deltas": deltas,
    }


def build_analysis_unit_alerts(matrix: dict) -> list[dict]:
    rows = {row.get("key"): row for row in matrix.get("rows", []) or []}
    units = [unit for unit in matrix.get("units", []) if unit != "Rede"]
    specs = [
        ("active_growth_pct", "Crescimento de ativos", "low", 1.0, "pct"),
        ("compliant_pct", "Adimplência", "low", 4.0, "pct"),
        ("overdue_pct", "Inadimplência", "high", 4.0, "pct"),
        ("sales_success_pct", "Sucesso de vendas", "low", 8.0, "pct"),
        ("churn_pct", "Churn", "high", 2.0, "pct"),
        ("own_daily_access", "Frequência própria", "low", 0.8, "decimal"),
        ("risk_high_critical_pct", "Risco alto ou crítico", "high", 3.0, "pct"),
    ]
    alerts = []
    for key, label, direction, threshold, value_format in specs:
        row = rows.get(key, {})
        values = row.get("values", {}) or {}
        network = float(values.get("Rede", 0) or 0)
        for unit in units:
            value = float(values.get(unit, 0) or 0)
            difference = value - network
            adverse = difference <= -threshold if direction == "low" else difference >= threshold
            positive = difference >= threshold if direction == "low" else difference <= -threshold
            if not adverse and not positive:
                continue
            alerts.append({
                "unit": unit,
                "indicator": label,
                "value": value,
                "network": network,
                "difference": difference,
                "format": value_format,
                "status": "attention" if adverse else "positive",
                "severity": abs(difference) / max(threshold, 0.01),
                "observation": (
                    f"{label} abaixo do comportamento da rede; requer diagnóstico local."
                    if adverse and direction == "low"
                    else f"{label} acima do comportamento da rede; requer ação local."
                    if adverse
                    else f"{label} apresenta desempenho melhor que a referência da rede."
                ),
            })
    attention = sorted((item for item in alerts if item["status"] == "attention"), key=lambda item: -item["severity"])[:6]
    positive = sorted((item for item in alerts if item["status"] == "positive"), key=lambda item: -item["severity"])[:4]
    return attention + positive


def month_rows(dates: pd.Series) -> list[dict]:
    valid = dates.dropna()
    if valid.empty:
        return []
    counts = valid.dt.to_period("M").value_counts().sort_index()
    return [
        {"label": f"{MONTH_ABBR.get(period.month, str(period.month).zfill(2))}/{period.year}", "value": int(value)}
        for period, value in counts.items()
    ]


def cancel_month_reason_rows(dates: pd.Series, reasons: pd.Series) -> list[dict]:
    frame = pd.DataFrame({
        "date": dates,
        "reason": reasons,
    })
    frame = frame[frame["date"].notna()].copy()
    if frame.empty:
        return []
    frame["month"] = frame["date"].dt.to_period("M")
    frame["inadimplencia"] = frame["reason"].map(is_inadimplencia_reason)
    grouped = frame.groupby(["month", "inadimplencia"], dropna=False).size().unstack(fill_value=0).sort_index()
    rows = []
    for period, row in grouped.iterrows():
        inadimplencia = int(row.get(True, 0))
        demais = int(row.get(False, 0))
        rows.append({
            "label": f"{MONTH_ABBR.get(period.month, str(period.month).zfill(2))}/{period.year}",
            "value": inadimplencia + demais,
            "segments": [
                {"label": "Inadimplência", "value": inadimplencia, "tone": "red"},
                {"label": "Cancelamentos solicitados", "value": demais, "tone": "orange"},
            ],
        })
    return rows


def date_rows(dates: pd.Series, limit: int = 24) -> list[dict]:
    valid = dates.dropna()
    if valid.empty:
        return []
    counts = valid.dt.date.value_counts().sort_index().tail(limit)
    return [{"label": str(day)[5:], "value": int(value)} for day, value in counts.items()]


def hourly_access_rows(dates: pd.Series) -> list[dict]:
    valid = dates.dropna()
    if valid.empty:
        return []
    counts = valid.dt.hour.value_counts().sort_index()
    counts = counts[~counts.index.isin([0, 4])]
    return [
        {"label": f"{int(hour):02d}:00", "value": int(count)}
        for hour, count in counts.items()
    ]


def weekday_access_rows(dates: pd.Series) -> list[dict]:
    valid = dates.dropna()
    if valid.empty:
        return []
    counts = valid.dt.weekday.value_counts().sort_index()
    total = int(counts.sum()) or 1
    tones = {
        0: "blue",
        1: "green",
        2: "orange",
        3: "violet",
        4: "red",
        5: "blue",
        6: "green",
    }
    return [
        {
            "label": WEEKDAY_FULL.get(index, str(index)),
            "value": int(counts.get(index, 0)),
            "pct": float(counts.get(index, 0) / total * 100),
            "tone": tones.get(index, "blue"),
        }
        for index in range(7)
    ]


def hourly_access_channel_rows(dates: pd.Series, channels: pd.Series) -> tuple[list[dict], str]:
    frame = pd.DataFrame({
        "date": dates,
        "channel": channels.fillna("").astype(str),
    })
    frame = frame[frame["date"].notna()].copy()
    if frame.empty:
        return [], ""
    frame["hour"] = frame["date"].dt.hour
    frame = frame[~frame["hour"].isin([0, 4])].copy()
    frame = frame[frame["hour"].between(5, 23)].copy()
    if frame.empty:
        return [], ""
    frame["day"] = frame["date"].dt.normalize()
    days_count = int(frame["day"].dropna().nunique()) or 1

    def channel_label(value: object) -> str:
        text = norm_text(value)
        if text == "TotalPass":
            return "TotalPass"
        if text == "Wellhub":
            return "Wellhub"
        return "Alunos próprios"

    frame["group"] = frame["channel"].map(channel_label)
    grouped = frame.groupby(["hour", "group"], dropna=False).size().unstack(fill_value=0)

    def daily_average(value: int) -> float:
        return float(value) / days_count

    def display_average(value: float) -> str:
        return f"{value:.1f}/dia".replace(".", ",")

    rows = []
    for hour in range(5, 24):
        own_total = int(grouped.loc[hour, "Alunos próprios"]) if hour in grouped.index and "Alunos próprios" in grouped.columns else 0
        totalpass_total = int(grouped.loc[hour, "TotalPass"]) if hour in grouped.index and "TotalPass" in grouped.columns else 0
        wellhub_total = int(grouped.loc[hour, "Wellhub"]) if hour in grouped.index and "Wellhub" in grouped.columns else 0
        own = daily_average(own_total)
        totalpass = daily_average(totalpass_total)
        wellhub = daily_average(wellhub_total)
        rows.append({
            "label": f"{hour:02d}h",
            "value": own + wellhub + totalpass,
            "bars": [
                {"label": "Alunos próprios", "value": own, "display": display_average(own), "tone": "green"},
                {"label": "Wellhub", "value": wellhub, "display": display_average(wellhub), "tone": "red"},
                {"label": "TotalPass", "value": totalpass, "display": display_average(totalpass), "tone": "blue"},
            ],
        })
    peak = max(rows, key=lambda row: row["value"]) if rows else None
    insight = ""
    if peak and peak["value"] > 0:
        insight = f"Pico médio às {peak['label']}. Reforce equipe e experiência nos horários de maior fluxo e use horários mais leves para ações de distribuição."
    return rows, insight


def frequency_cluster_label(count: int) -> str:
    if count <= 0:
        return "Alunos sem frequência"
    if count <= 4:
        return "Passantes"
    if count <= 8:
        return "Engajados"
    if count <= 11:
        return "Recorrentes"
    return "Fidelizados"


def frequency_cluster_order() -> list[tuple[str, str, str]]:
    return [
        ("Alunos sem frequência", "0 visitas", "graphite"),
        ("Passantes", "1 a 4 visitas", "red"),
        ("Engajados", "5 a 8 visitas", "orange"),
        ("Recorrentes", "9 a 11 visitas", "blue"),
        ("Fidelizados", "12+ visitas", "green"),
    ]


def frequency_cluster_panel(title: str, base_ids: pd.Series, visit_counts: pd.Series, subtitle: str) -> dict:
    clean_base = id_series(base_ids)
    clean_base = clean_base[clean_base.ne("")]
    count_by_id = visit_counts.copy()
    if not count_by_id.empty:
        count_by_id.index = id_series(pd.Series(count_by_id.index, index=count_by_id.index)).values
        count_by_id = count_by_id[count_by_id.index != ""]
    base_index = pd.Index(clean_base.drop_duplicates())
    if base_index.empty and not count_by_id.empty:
        base_index = pd.Index(count_by_id.index).drop_duplicates()
    counts = count_by_id.groupby(level=0).sum().reindex(base_index, fill_value=0).astype(int)
    total = int(len(counts)) or 1
    cluster_order = frequency_cluster_order()
    classified = counts.map(frequency_cluster_label)
    rows = []
    for label, range_label, tone_name in cluster_order:
        value = int(classified.eq(label).sum())
        rows.append({
            "label": label,
            "range": range_label,
            "value": value,
            "pct": float(value / total * 100),
            "tone": tone_name,
        })
    return {
        "type": "clusterPanel",
        "title": title,
        "subtitle": subtitle,
        "totalLabel": "Total da base",
        "total": total,
        "rows": rows,
        "className": "frequency-cluster-panel",
    }


def frequency_cluster_donut_panel(title: str, panel: dict, subtitle: str) -> dict:
    rows = []
    for row in panel.get("rows", []):
        range_label = norm_text(row.get("range"))
        label = f"{row.get('label', '')} ({range_label})" if range_label else row.get("label", "")
        rows.append({
            "label": label,
            "value": row.get("value", 0),
            "pct": row.get("pct", 0),
            "tone": row.get("tone", "blue"),
        })
    return {
        "type": "donut",
        "title": title,
        "subtitle": subtitle,
        "className": "chart-cluster-distribution",
        "rows": rows,
    }


def frequency_cluster_unit_panel(title: str, base_frame: pd.DataFrame, visit_counts: pd.Series, subtitle: str) -> dict:
    cluster_order = frequency_cluster_order()
    if base_frame.empty or not {"id", "unit"}.issubset(base_frame.columns):
        frame = pd.DataFrame(columns=["id", "unit"])
    else:
        frame = base_frame[["id", "unit"]].copy()
        frame["id"] = id_series(frame["id"])
        frame["unit"] = frame["unit"].map(lambda value: UNIT_ALIASES.get(norm_key(value), norm_text(value)))
        frame = frame[frame["id"].ne("") & frame["unit"].ne("") & ~frame["unit"].isin(EXCLUDED_UNITS)]
        frame = frame.drop_duplicates("id", keep="last")

    count_by_id = visit_counts.copy()
    if not count_by_id.empty:
        count_by_id.index = id_series(pd.Series(count_by_id.index, index=count_by_id.index)).values
        count_by_id = count_by_id[count_by_id.index != ""].groupby(level=0).sum()

    if frame.empty:
        frame["visits"] = pd.Series(dtype=int)
        frame["cluster"] = pd.Series(dtype=str)
    else:
        frame["visits"] = frame["id"].map(count_by_id).fillna(0).astype(int)
        frame["cluster"] = frame["visits"].map(frequency_cluster_label)

    rows = []
    for unit in UNIT_ORDER:
        unit_frame = frame[frame["unit"].eq(unit)] if not frame.empty else frame
        total = int(len(unit_frame))
        clusters = []
        for label, range_label, tone_name in cluster_order:
            value = int(unit_frame["cluster"].eq(label).sum()) if total else 0
            clusters.append({
                "label": label,
                "range": range_label,
                "value": value,
                "pct": float(value / total * 100) if total else 0.0,
                "tone": tone_name,
            })
        rows.append({
            "unit": unit,
            "total": total,
            "clusters": clusters,
        })

    return {
        "type": "clusterUnitTable",
        "title": title,
        "subtitle": subtitle,
        "className": "frequency-cluster-unit-table",
        "clusters": [
            {"label": label, "range": range_label, "tone": tone_name}
            for label, range_label, tone_name in cluster_order
        ],
        "rows": rows,
    }


def churn_risk_panel(active: pd.DataFrame, charges: pd.DataFrame, access: pd.DataFrame) -> dict:
    """Score active members using overdue debt and prorated monthly attendance."""
    base = pd.DataFrame(index=active.index)
    base["id"] = id_series(active.get("idMember", pd.Series(index=active.index, dtype=str)))
    base["name"] = active.get("nome", pd.Series(index=active.index, dtype=str)).fillna("").map(norm_text)
    base["unit"] = active.get("unidade_nome", active.get("Filial", pd.Series(index=active.index, dtype=str))).map(branch_name)
    base = base[
        base["id"].ne("")
        & base["unit"].isin(UNIT_ORDER)
        & ~base["unit"].isin(EXCLUDED_UNITS)
    ].drop_duplicates("id", keep="last")

    debt = pd.DataFrame(index=charges.index)
    debt["id"] = id_series(charges.get("idMember", pd.Series(index=charges.index, dtype=str)))
    debt["value"] = parse_number(charges.get("valorCompet", pd.Series(index=charges.index, dtype=float))).fillna(0)
    debt["days"] = parse_number(charges.get("diasInad", pd.Series(index=charges.index, dtype=float))).fillna(0)
    debt["status"] = charges.get("status", pd.Series(index=charges.index, dtype=str)).fillna("").map(norm_key)
    overdue = debt[
        debt["id"].isin(set(base["id"]))
        & debt["status"].eq("a receber")
        & debt["value"].gt(0)
        & debt["days"].gt(0)
    ]
    if overdue.empty:
        debt_by_id = pd.DataFrame(columns=["debt", "overdueParcels", "maxOverdueDays"])
    else:
        debt_by_id = overdue.groupby("id").agg(
            debt=("value", "sum"),
            overdueParcels=("id", "size"),
            maxOverdueDays=("days", "max"),
        )

    own_access = pd.DataFrame(index=access.index)
    own_access["id"] = id_series(access.get("id_member", pd.Series(index=access.index, dtype=str)))
    own_access["date"] = parse_date(access.get("date_event", pd.Series(index=access.index, dtype=str)))
    own_access["channel"] = access.get("canal", pd.Series(index=access.index, dtype=str)).fillna("")
    own_access["action"] = access.get("entry_action", pd.Series(index=access.index, dtype=str)).fillna("").map(norm_key)
    own_access["reason"] = access.get("block_reason", pd.Series(index=access.index, dtype=str)).fillna("").map(norm_key)
    valid_entry = own_access["action"].eq("entry") | own_access["reason"].str.contains(
        r"validada com sucesso|validado com sucesso", regex=True, na=False
    )
    own_access = own_access[
        own_access["channel"].eq("Unidade")
        & valid_entry
        & own_access["id"].isin(set(base["id"]))
        & own_access["date"].notna()
    ]

    today = pd.Timestamp.now(tz="America/Sao_Paulo").tz_localize(None).normalize()
    latest_access_date = own_access["date"].max().normalize() if not own_access.empty else today
    analysis_date = min(today, latest_access_date)
    analysis_month = analysis_date.to_period("M")
    expected_visits = max(1.0, 12.0 * analysis_date.day / analysis_date.days_in_month)
    if own_access.empty:
        visits_by_id = pd.Series(dtype=int)
    else:
        month_access = own_access[own_access["date"].dt.to_period("M").eq(analysis_month)]
        visits_by_id = month_access["id"].value_counts()

    scored = base.set_index("id").join(debt_by_id, how="left")
    scored["debt"] = scored["debt"].fillna(0).round(2)
    scored["overdueParcels"] = scored["overdueParcels"].fillna(0).astype(int)
    scored["maxOverdueDays"] = scored["maxOverdueDays"].fillna(0).astype(int)
    scored["visits"] = scored.index.to_series().map(visits_by_id).fillna(0).astype(int)
    scored["frequencyPct"] = (scored["visits"] / expected_visits * 100).clip(upper=100).round(1)
    scored["financialPoints"] = np.where(
        scored["debt"].gt(160) | scored["overdueParcels"].gt(2), 40, 0
    )
    scored["delayPoints"] = np.select(
        [scored["maxOverdueDays"].gt(15), scored["maxOverdueDays"].gt(7)],
        [20, 10],
        default=0,
    ).astype(int)
    rounded_frequency = scored["frequencyPct"].round().astype(int)
    scored["frequencyPoints"] = np.select(
        [rounded_frequency.le(29), rounded_frequency.between(30, 70, inclusive="both")],
        [20, 10],
        default=0,
    ).astype(int)
    scored["score"] = (
        scored["financialPoints"] + scored["delayPoints"] + scored["frequencyPoints"]
    ).clip(upper=100).astype(int)
    scored["risk"] = pd.cut(
        scored["score"],
        bins=[-1, 20, 40, 60, 100],
        labels=["Baixo", "Médio", "Alto", "Crítico"],
        include_lowest=True,
    ).astype(str)
    scored = scored.reset_index()

    band_specs = [
        ("Baixo", "0–20", "green"),
        ("Médio", "21–40", "yellow"),
        ("Alto", "41–60", "orange"),
        ("Crítico", "61–100", "red"),
    ]

    def build_view(key: str, label: str, frame: pd.DataFrame, opening_order: int) -> dict:
        total = int(len(frame))
        distribution = []
        for band, interval, tone_name in band_specs:
            count = int(frame["risk"].eq(band).sum()) if total else 0
            distribution.append({
                "label": band,
                "range": interval,
                "tone": tone_name,
                "value": count,
                "pct": float(count / total * 100) if total else 0.0,
            })
        critical = int(frame["risk"].eq("Crítico").sum()) if total else 0
        high_critical = int(frame["risk"].isin(["Alto", "Crítico"]).sum()) if total else 0
        def serialize_students(student_frame: pd.DataFrame) -> list[dict]:
            ordered = student_frame.sort_values(
                ["score", "debt", "maxOverdueDays", "name"],
                ascending=[False, False, False, True],
                kind="stable",
            ).head(100)
            return [
                {
                    "id": str(row.id),
                    "name": row.name or "Nome não informado",
                    "score": int(row.score),
                    "risk": row.risk,
                    "debt": round(float(row.debt), 2),
                    "overdueParcels": int(row.overdueParcels),
                    "maxOverdueDays": int(row.maxOverdueDays),
                    "visits": int(row.visits),
                    "frequencyPct": float(row.frequencyPct),
                    "financialPoints": int(row.financialPoints),
                    "delayPoints": int(row.delayPoints),
                    "frequencyPoints": int(row.frequencyPoints),
                }
                for row in ordered.itertuples()
            ]

        students_by_risk = {
            band: serialize_students(frame[frame["risk"].eq(band)])
            for band, _interval, _tone_name in band_specs
        }
        return {
            "key": key,
            "label": label,
            "code": CHURN_UNIT_CODES.get(label, label[:4].upper()),
            "openingOrder": opening_order,
            "total": total,
            "critical": critical,
            "highCritical": high_critical,
            "highCriticalPct": float(high_critical / total * 100) if total else 0.0,
            "averageScore": float(frame["score"].mean()) if total else 0.0,
            "maxScore": int(frame["score"].max()) if total else 0,
            "distribution": distribution,
            "studentsByRisk": students_by_risk,
        }

    views = [build_view("network", "Rede", scored, 0)]
    for opening_order, unit in enumerate(UNIT_ORDER, start=1):
        unit_frame = scored[scored["unit"].eq(unit)]
        if not unit_frame.empty:
            views.append(build_view(f"unit-{opening_order}", unit, unit_frame, opening_order))

    month_label = f"{MONTH_ABBR.get(analysis_month.month, analysis_month.month)}/{analysis_month.year}"
    return {
        "type": "churnRisk",
        "title": "Risco de evasão / churn",
        "subtitle": "Score dos alunos ativos por unidade, combinando cobrança vencida e frequência mensal.",
        "className": "chart-frequency-churn-risk",
        "defaultUnit": "network",
        "referenceDate": analysis_date.strftime("%d/%m/%Y"),
        "monthLabel": month_label,
        "monthlyVisitGoal": 12,
        "expectedVisits": round(float(expected_visits), 2),
        "views": views,
        "rules": [
            "+40: saldo vencido acima de R$ 160,00 ou mais de 2 parcelas vencidas.",
            "+20: maior atraso acima de 15 dias; +10: atraso entre 8 e 15 dias.",
            "+10: frequência entre 30% e 70%; +20: frequência entre 0% e 29%.",
            "Frequência = visitas próprias no mês ÷ meta de 12 visitas, proporcional aos dias carregados.",
        ],
    }


def access_day_segment_rows(dates: pd.Series, channels: pd.Series, limit: int = 24) -> list[dict]:
    frame = pd.DataFrame({
        "date": dates,
        "channel": channels.fillna("").astype(str),
    })
    frame = frame[frame["date"].notna()].copy()
    if frame.empty:
        return []
    frame["day"] = frame["date"].dt.normalize()
    frame["group"] = np.where(frame["channel"].eq("Unidade"), "own", "aggregator")
    grouped = frame.groupby(["day", "group"], dropna=False).size().unstack(fill_value=0).sort_index().tail(limit)
    rows = []
    for day, row in grouped.iterrows():
        own = int(row.get("own", 0))
        aggregator = int(row.get("aggregator", 0))
        weekday = WEEKDAY_ABBR.get(int(day.weekday()), "")
        rows.append({
            "label": f"{weekday} {day.strftime('%d/%m')}",
            "weekday": weekday,
            "dateLabel": day.strftime("%d/%m"),
            "value": own + aggregator,
            "segments": [
                {"label": "Alunos próprios", "value": own, "tone": "blue"},
                {"label": "Agregadores", "value": aggregator, "tone": "orange"},
            ],
        })
    return rows


def age_band_rows(dates: pd.Series) -> tuple[list[dict], float | None]:
    ages = age_values(dates)
    mean_age = float(ages.mean()) if ages.notna().any() else None
    groups = pd.cut(ages, bins=AGE_BINS, labels=AGE_BAND_LABELS, right=True)
    counts = groups.value_counts(sort=False)
    total = int(counts.sum()) or 1
    tones = ["blue", "green", "orange", "violet", "red", "graphite"]
    rows = [
        {
            "label": str(label),
            "value": int(value),
            "pct": float(int(value) / total * 100),
            "tone": tones[index % len(tones)],
        }
        for index, (label, value) in enumerate(counts.items())
    ]
    return rows, mean_age


def age_gender_pyramid_data(dates: pd.Series, genders: pd.Series) -> dict:
    """Build the age-band population pyramid using the same active-base rules."""
    ages = age_values(dates)
    groups = pd.cut(ages, bins=AGE_BINS, labels=AGE_BAND_LABELS, right=True)
    normalized_genders = genders.reindex(dates.index).map(clean_gender)
    frame = pd.DataFrame({"band": groups, "gender": normalized_genders}, index=dates.index)
    frame = frame[frame["band"].notna()].copy()

    male_total = int(frame["gender"].eq("Sexo masculino").sum())
    female_total = int(frame["gender"].eq("Sexo feminino").sum())
    unreported_total = int(len(frame) - male_total - female_total)
    known_total = max(male_total + female_total, 1)
    short_labels = ["Até 18", "19–25", "26–35", "36–45", "46–60", "61+"]
    tones = ["blue", "green", "orange", "violet", "red", "graphite"]
    colors = ["#6557d9", "#16b8c8", "#27c99a", "#ff9f43", "#ef476f", "#465257"]
    rows = []
    for index, band in enumerate(AGE_BAND_LABELS):
        band_mask = frame["band"].eq(band)
        male = int((band_mask & frame["gender"].eq("Sexo masculino")).sum())
        female = int((band_mask & frame["gender"].eq("Sexo feminino")).sum())
        rows.append({
            "label": str(band),
            "shortLabel": short_labels[index],
            "male": male,
            "female": female,
            "malePct": male / known_total * 100,
            "femalePct": female / known_total * 100,
            "tone": tones[index % len(tones)],
            "color": colors[index % len(colors)],
        })

    return {
        "rows": list(reversed(rows)),
        "maleTotal": male_total,
        "femaleTotal": female_total,
        "unreportedTotal": unreported_total,
        "validAgeTotal": int(len(frame)),
    }


def card(label: str, value: str, sub: str = "", tone: str = "green", **extra) -> dict:
    payload = {"label": label, "value": value, "sub": sub, "tone": tone}
    payload.update(extra)
    return payload


def peak_sales_card(dates: pd.Series) -> dict:
    valid = dates.dropna().dt.normalize()
    if valid.empty:
        return {
            "kind": "peakSales",
            "label": "Dia com mais vendas",
            "sub": "Pico e participação no mês",
            "day": "—",
            "quantity": 0,
            "share": 0.0,
            "tone": "green",
        }
    counts = valid.value_counts().sort_index()
    peak_quantity = int(counts.max())
    peak_day = counts[counts.eq(peak_quantity)].index.min()
    return {
        "kind": "peakSales",
        "label": "Dia com mais vendas",
        "sub": "Pico e participação no mês",
        "day": pd.Timestamp(peak_day).strftime("%d/%m"),
        "quantity": peak_quantity,
        "share": peak_quantity / max(len(valid), 1) * 100,
        "tone": "green",
    }


SV_PLAN_REFERENCE_PRICE = 29.90


def previous_day_sales_indicator(dates: pd.Series, anchor_date=None) -> tuple[int, str, str]:
    valid = parse_date(dates).dropna().dt.normalize()
    anchor = pd.Timestamp(anchor_date if anchor_date is not None else date.today()).normalize()
    yesterday = anchor - pd.Timedelta(days=1)
    day_before = yesterday - pd.Timedelta(days=1)
    yesterday_count = int(valid.eq(yesterday).sum())
    day_before_count = int(valid.eq(day_before).sum())
    delta = yesterday_count - day_before_count
    if delta > 0:
        return yesterday_count, f"↑ +{br_int(delta)}", "good"
    if delta < 0:
        return yesterday_count, f"↓ -{br_int(abs(delta))}", "bad"
    return yesterday_count, "● 0", "neutral"


def active_plan_share(active: pd.DataFrame, plan_label: str = "SV Plus") -> tuple[int, float]:
    if active.empty:
        return 0, 0.0
    active_ids = id_series(active.get("idMember", pd.Series(index=active.index, dtype=str)))
    plan_source = active.get("contrato_norm", active.get("contrato", pd.Series(index=active.index, dtype=str)))
    active_plans = plan_source.fillna("").astype(str).map(clean_plan)
    frame = pd.DataFrame({"id": active_ids, "plan": active_plans}, index=active.index)
    if frame["id"].ne("").any():
        frame = frame[frame["id"].ne("")].drop_duplicates("id", keep="last")
    total = len(frame)
    plan_count = int(frame["plan"].eq(plan_label).sum())
    return plan_count, plan_count / max(total, 1) * 100


def first_row(rows: list[dict], reverse: bool = True) -> dict:
    valid_rows = [row for row in rows or [] if row.get("value") not in (None, "")]
    if not valid_rows:
        return {}
    return sorted(valid_rows, key=lambda row: float(row.get("value") or 0), reverse=reverse)[0]


def build_isaias_tab(
    ids_active: int,
    adimplentes: int,
    inadimplentes: int,
    adimplentes_pct: float,
    inadimplentes_pct: float,
    sales_total: int,
    ids_sales: int,
    cancel_total: int,
    ids_cancel: int,
    access_total: int,
    access_unique: int,
    unit_access_mean: float,
    aggregator_access_mean: float,
    sales_ticket_mean: float,
    received_ticket_mean: float,
    sv_plus_sales_pct: float,
    revenue_rows: list[dict],
    sales_success_rows: list[dict],
    churn_rows: list[dict],
    payment_rows: list[dict],
) -> dict:
    revenue_top = first_row(revenue_rows)
    success_top = first_row(sales_success_rows)
    churn_best = first_row(churn_rows, reverse=False)
    payment_alert = first_row([row for row in payment_rows if row.get("tone") == "red"]) or first_row(payment_rows)
    churn_display = churn_best.get("display", "sem leitura")
    revenue_display = revenue_top.get("display", "sem leitura")
    success_display = success_top.get("display", "sem leitura")
    payment_display = payment_alert.get("display", "sem leitura")
    cancellation_rate = cancel_total / max(sales_total, 1) * 100
    active_base_quality = adimplentes / max(ids_active, 1) * 100
    own_access_label = "recorrente" if unit_access_mean >= 9 else "engajada" if unit_access_mean >= 5 else "passante"
    aggregator_access_label = "recorrente" if aggregator_access_mean >= 9 else "engajada" if aggregator_access_mean >= 5 else "passante"
    sv_plus_direction = "mix premium ainda com espaco de crescimento" if sv_plus_sales_pct < 12 else "mix premium ja relevante"
    diagnostics = [
        {
            "title": "Ativos | Base financeira",
            "body": f"{br_pct(active_base_quality)} da base ativa esta adimplente ({br_int(adimplentes)} de {br_int(ids_active)}). Em operacao fitness recorrente, esse indicador precisa sustentar a expansao antes de acelerar nova venda.",
            "tone": "green" if active_base_quality >= 90 else "red",
        },
        {
            "title": "Ativos | Inadimplencia",
            "body": f"{br_pct(inadimplentes_pct)} da base ativa esta inadimplente ({br_int(inadimplentes)} alunos). A meta operacional e ficar perto de 10%; acima disso, o caminho e cobranca preventiva antes do aluno virar churn.",
            "tone": "green" if inadimplentes_pct <= 10 else "red",
        },
        {
            "title": "Ativos | Qualidade da base",
            "body": f"A rede fecha com {br_int(ids_active)} ativos. A leitura de mercado e separar base saudavel de base apenas matriculada: ativo com saldo e baixa visita deve entrar em rotina de resgate.",
            "tone": "blue",
        },
        {
            "title": "Vendas | Volume com qualidade",
            "body": f"Foram {br_int(sales_total)} contratos vendidos para {br_int(ids_sales)} clientes. O melhor sucesso esta em {success_top.get('label', 'sem unidade')} ({success_display}); essa unidade deve virar referencia de playbook comercial.",
            "tone": "blue",
        },
        {
            "title": "Vendas | Mix premium",
            "body": f"SV Plus representa {br_pct(sv_plus_sales_pct)} das vendas. Para mercado fitness de recorrencia, o caminho e elevar plano de maior valor sem derrubar ativacao e frequencia nos primeiros 30 dias.",
            "tone": "green" if sv_plus_sales_pct >= 12 else "orange",
        },
        {
            "title": "Vendas | Ticket de entrada",
            "body": f"Ticket vendido medio em {br_money(sales_ticket_mean)} contra ticket recebido de {br_money(received_ticket_mean)}. Se a venda entra promocional, a recorrencia precisa compensar com retencao e baixa inadimplencia.",
            "tone": "orange",
        },
        {
            "title": "Cancelamentos | Pressao sobre venda",
            "body": f"O recorte tem {br_int(cancel_total)} contratos cancelados, equivalente a {br_pct(cancellation_rate)} do volume vendido. Em rede fitness, esse nivel exige olhar LTV, motivo e frequencia antes do cancelamento.",
            "tone": "red" if cancellation_rate >= 25 else "orange",
        },
        {
            "title": "Cancelamentos | Benchmark interno",
            "body": f"Menor churn em {churn_best.get('label', 'sem unidade')} ({churn_display}). A unidade com menor perda deve orientar padrao de acompanhamento, cobranca e experiencia das demais.",
            "tone": "violet",
        },
        {
            "title": "Cancelamentos | Cliente cancelado",
            "body": f"{br_int(ids_cancel)} clientes aparecem cancelados. O caminho e separar cancelamento por inadimplencia, troca de contrato e abandono real para nao tratar causas diferentes com a mesma acao.",
            "tone": "red",
        },
        {
            "title": "Frequencia | Uso real",
            "body": f"A base registrou {br_int(access_total)} acessos de {br_int(access_unique)} clientes. No fitness, visita e prova de valor: sem frequencia, a venda vira risco financeiro e operacional.",
            "tone": "green",
        },
        {
            "title": "Frequencia | Alunos proprios",
            "body": f"Media de {unit_access_mean:.1f}".replace(".", ",") + f" visitas por aluno proprio, uma base {own_access_label}. O caminho e empurrar engajados para recorrentes e fidelizados.",
            "tone": "blue" if unit_access_mean >= 8 else "orange",
        },
        {
            "title": "Frequencia | Agregadores",
            "body": f"Agregadores fazem media de {aggregator_access_mean:.1f}".replace(".", ",") + f" visitas, leitura {aggregator_access_label}. Wellhub e TotalPass devem ser tratados como funil de relacionamento, nao so receita acessoria.",
            "tone": "violet",
        },
        {
            "title": "Perfil | Receita por unidade",
            "body": f"Maior faturamento em {revenue_top.get('label', 'sem unidade')} ({revenue_display}). Mercado fitness escala melhor quando receita alta vem junto de retencao, adimplencia e frequencia.",
            "tone": "green",
        },
        {
            "title": "Perfil | Cobranca critica",
            "body": f"Ponto critico: {payment_alert.get('label', 'sem leitura')} com {payment_display}. O caminho e separar divida recente de recuperacao antiga e medir taxa de conversao por unidade.",
            "tone": "red",
        },
        {
            "title": "Perfil | Caminho da rede",
            "body": f"O painel aponta {sv_plus_direction}, ticket recebido de {br_money(received_ticket_mean)} e base com {br_pct(active_base_quality)} adimplente. A rota e crescer com qualidade de receita, nao apenas volume.",
            "tone": "orange",
        },
    ]
    return {
        "layout": "isaias",
        "cards": [
            card("Base saudável", br_pct(active_base_quality), f"{br_int(adimplentes)} adimplentes de {br_int(ids_active)} ativos", "green"),
            card("Pressão de cancelamento", br_pct(cancellation_rate), f"{br_int(cancel_total)} contratos cancelados / {br_int(sales_total)} vendidos", "red"),
            card("Ticket recebido", br_money(received_ticket_mean), "referência de caixa confirmado", "blue"),
            card("Frequência própria", f"{unit_access_mean:.1f}".replace(".", ","), "média de visitas por aluno próprio", "orange"),
            card("Frequência agregadores", f"{aggregator_access_mean:.1f}".replace(".", ","), "média de visitas Wellhub + TotalPass", "violet"),
            card("SV Plus nas vendas", br_pct(sv_plus_sales_pct), "sinal de mix premium", "green"),
        ],
        "briefing": [
            {
                "title": "Leitura crítica",
                "body": "O isaIAs cruza crescimento, retenção, frequência, inadimplência e mix de contrato. A leitura é intencionalmente executiva: identifica o que escala, o que drena caixa e onde a operação precisa padronizar execução.",
                "tone": "green",
            },
            {
                "title": "Tese de crescimento",
                "body": f"A rede tem {br_int(ids_active)} alunos ativos, {br_int(sales_total)} contratos vendidos e {br_int(access_total)} acessos no recorte atual. O crescimento saudável depende de manter vendas com frequência real, baixa inadimplência e sucesso de venda por unidade.",
                "tone": "blue",
            },
            {
                "title": "Alerta de retenção",
                "body": f"O recorte mostra {br_int(cancel_total)} cancelamentos e {br_int(inadimplentes)} ativos inadimplentes. Em mercado fitness de escala, retenção nasce de rotina de uso: aluno que compra e não visita vira risco antes de virar churn.",
                "tone": "red",
            },
            {
                "title": "Benchmark operacional",
                "body": "A lógica combina visão de expansão, padronização, eficiência de unidade, mix de planos e experiência recorrente. A referência externa reforça que fitness cresce como ecossistema: academia, benefício corporativo, tecnologia e comunidade.",
                "tone": "orange",
            },
        ],
        "briefing": diagnostics,
        "signals": [
            {"label": "Maior faturamento", "value": revenue_top.get("label", "Sem unidade"), "detail": revenue_display, "tone": "green"},
            {"label": "Melhor sucesso de venda", "value": success_top.get("label", "Sem unidade"), "detail": success_display, "tone": "blue"},
            {"label": "Menor churn", "value": churn_best.get("label", "Sem unidade"), "detail": churn_display, "tone": "violet"},
            {"label": "Status de cobrança crítico", "value": payment_alert.get("label", "Sem leitura"), "detail": payment_display, "tone": "red"},
        ],
        "benchmarks": [
            {
                "title": "Brasil ainda é mercado fragmentado",
                "body": "A HFA cita o mercado brasileiro com mais de 31 mil clubes e 7,9 milhões de membros. Isso sugere espaço para redes regionais ganharem eficiência por padronização, dados e execução local.",
                "url": "https://www.healthandfitness.org/",
            },
            {
                "title": "Fitness virou ecossistema de bem-estar",
                "body": "A Wellhub posiciona o benefício corporativo como rede de fitness, mindfulness, nutrição e sono, com mais de 100 mil academias e estúdios em sua rede global.",
                "url": "https://wellhub.com/en-us/",
            },
            {
                "title": "Adoção incremental via agregadores",
                "body": "A Wellhub informa que 61% dos colaboradores não tinham matrícula em academia antes do benefício. Para a BioFisic, agregadores podem ser funil, não apenas receita acessória.",
                "url": "https://wellhub.com/en-us/",
            },
            {
                "title": "Tecnologia e IA entram na jornada do aluno",
                "body": "A HFA destaca tecnologia e IA como temas de transformação da jornada do membro. O próximo salto é usar dados de venda, acesso e cobrança para antecipar risco.",
                "url": "https://www.healthandfitness.org/",
            },
        ],
        "questions": [],
        "chatContext": {
            "active": ids_active,
            "adimplentes": adimplentes,
            "inadimplentes": inadimplentes,
            "adimplentesPct": adimplentes_pct,
            "inadimplentesPct": inadimplentes_pct,
            "sales": sales_total,
            "salesClients": ids_sales,
            "cancellations": cancel_total,
            "cancelClients": ids_cancel,
            "access": access_total,
            "accessClients": access_unique,
            "ownAccessMean": unit_access_mean,
            "aggregatorAccessMean": aggregator_access_mean,
            "salesTicket": br_money(sales_ticket_mean),
            "receivedTicket": br_money(received_ticket_mean),
            "svPlusPct": br_pct(sv_plus_sales_pct),
            "topRevenueUnit": revenue_top.get("label", ""),
            "topRevenueDisplay": revenue_display,
            "topSalesSuccessUnit": success_top.get("label", ""),
            "topSalesSuccessDisplay": success_display,
            "bestChurnUnit": churn_best.get("label", ""),
            "bestChurnDisplay": churn_display,
            "paymentAlert": payment_alert.get("label", ""),
            "paymentAlertDisplay": payment_display,
        },
    }


def build_blank_payload(source_label: str | None = None, validation: list[dict] | None = None, filters: dict | None = None) -> dict:
    empty_tab = {"cards": [], "charts": []}
    filter_state = normalize_dashboard_filters(filters)
    return {
        "sourceFile": source_label or "Aguardando CSVs",
        "sourcePath": str(DEFAULT_CSV_DIR),
        "filters": filter_state,
        "filterOptions": {
            "units": UNIT_ORDER,
            "ageBands": AGE_BAND_LABELS,
            "genders": GENDER_FILTER_OPTIONS,
        },
        "tabs": {
            "ativos": empty_tab,
            "vendas": empty_tab,
            "cancelamentos": empty_tab,
            "financeiro": {"layout": "financial_summary", "cards": [], "charts": []},
            "frequencia": empty_tab,
            "isaias": {"layout": "isaias", "cards": [], "briefing": [], "signals": [], "benchmarks": [], "questions": [], "chatContext": {}},
        },
        "overview": {
            "cards": [
                card("Alunos ativos", "0", "ATIVOS_LTV.csv"),
                card("Vendas", "0", "VENDAS.csv", "blue"),
                card("Cancelamentos", "0", "CANCELAMENTO.csv", "red"),
                card("Acessos", "0", "Controle de acesso", "orange"),
            ]
        },
        "validation": validation or [],
    }


def prepare_table_frames(
    table_frames: dict[str, pd.DataFrame],
    source_path: str = "supabase://basededadosEVO/public",
    validation: list[dict] | None = None,
    paths: dict | None = None,
) -> dict:
    """Normalize in-memory tables so CSV and Supabase sources share one engine."""
    required = {"sales", "active", "cancellations", "charges"}
    missing = sorted(required.difference(table_frames))
    if missing:
        return {
            "valid": False,
            "paths": paths or {},
            "validation": validation or [],
            "sourcePath": source_path,
            "missingRoles": missing,
        }

    frames = {
        role: frame.copy()
        for role, frame in table_frames.items()
        if isinstance(frame, pd.DataFrame)
    }
    for frame in frames.values():
        frame.columns = [norm_text(column) for column in frame.columns]

    sales = frames["sales"]
    sales_realtime = frames.get("sales_realtime", pd.DataFrame()).copy()
    billing = frames.get("billing", pd.DataFrame())
    sales, sales_swaps = normalize_realtime_contract_sales(sales, billing)
    active = frames["active"]
    canc = frames["cancellations"]
    non_renewed = frames.get("non_renewed", pd.DataFrame()).copy()
    charges = frames["charges"]
    access_parts = []
    for role, label in [("access_unit", "Unidade"), ("access_wellhub", "Wellhub"), ("access_totalpass", "TotalPass")]:
        if role in frames:
            part = frames[role].copy()
            part["canal"] = label
            access_parts.append(part)
    access = pd.concat(access_parts, ignore_index=True) if access_parts else pd.DataFrame()

    sales["unidade_nome"] = sales.get("id_unidade", pd.Series(index=sales.index)).map(branch_name)
    if not sales_realtime.empty:
        sales_realtime["unidade_nome"] = sales_realtime.get(
            "idBranch", pd.Series(index=sales_realtime.index)
        ).map(branch_name)
    if not billing.empty:
        billing["unidade_nome"] = billing.get("id_unidade", pd.Series(index=billing.index)).map(branch_name)
    active["unidade_nome"] = active.get("Filial", pd.Series(index=active.index)).map(branch_name)
    canc["unidade_nome"] = canc.get("idBranch", pd.Series(index=canc.index)).map(branch_name)
    if not non_renewed.empty:
        non_renewed["unidade_nome"] = non_renewed.get(
            "idFilial", pd.Series(index=non_renewed.index)
        ).map(branch_name)
        missing_non_renewed_unit = non_renewed["unidade_nome"].fillna("").isin({"", "Sem unidade"})
        if missing_non_renewed_unit.any():
            non_renewed.loc[missing_non_renewed_unit, "unidade_nome"] = non_renewed.loc[
                missing_non_renewed_unit
            ].get("NomeFilial", pd.Series(index=non_renewed.index)).map(branch_name)
    charges["unidade_nome"] = charges.get("filial", pd.Series(index=charges.index)).map(branch_name)
    if not access.empty:
        access["unidade_nome"] = access.get("id_branch", pd.Series(index=access.index)).map(branch_name)

    sales = sales[~sales["unidade_nome"].isin(EXCLUDED_UNITS)].copy()
    if not sales_realtime.empty:
        sales_realtime = sales_realtime[
            ~sales_realtime["unidade_nome"].isin(EXCLUDED_UNITS)
        ].copy()
    if not billing.empty:
        billing = billing[~billing["unidade_nome"].isin(EXCLUDED_UNITS)].copy()
    active = active[~active["unidade_nome"].isin(EXCLUDED_UNITS)].copy()
    canc = canc[~canc["unidade_nome"].isin(EXCLUDED_UNITS)].copy()
    if not non_renewed.empty:
        non_renewed = non_renewed[~non_renewed["unidade_nome"].isin(EXCLUDED_UNITS)].copy()
    charges = charges[~charges["unidade_nome"].isin(EXCLUDED_UNITS)].copy()
    if not access.empty:
        access = access[~access["unidade_nome"].isin(EXCLUDED_UNITS)].copy()
    if "contrato" in canc:
        canc = canc[~canc["contrato"].map(is_ignored_cancellation_contract)].copy()

    if validation is None:
        validation = [
            {
                "arquivo": role,
                "papel": role,
                "status": "ok",
                "colunas": int(len(frame.columns)),
                "linhas": int(len(frame.index)),
            }
            for role, frame in frames.items()
        ]

    return {
        "valid": True,
        "paths": paths or {},
        "validation": validation,
        "sourcePath": source_path,
        "sales": sales,
        "sales_realtime": sales_realtime,
        "sales_swaps": sales_swaps,
        "billing": billing,
        "active": active,
        "active_history": frames.get("active_history", pd.DataFrame()),
        "cancellations": canc,
        "non_renewed": non_renewed,
        "charges": charges,
        "access": access,
    }


def load_processed_tables(workbook_path: str | Path | None = None) -> dict:
    paths, validation = discover_csvs(workbook_path)
    required = {"sales", "active", "cancellations", "charges"}
    source_path = str(Path(workbook_path) if workbook_path else DEFAULT_CSV_DIR)
    if not required.issubset(paths):
        return {
            "valid": False,
            "paths": paths,
            "validation": validation,
            "sourcePath": source_path,
        }

    table_frames = {
        "sales": read_csv_flexible(paths["sales"]),
        "active": read_csv_flexible(paths["active"]),
        "cancellations": read_csv_flexible(paths["cancellations"]),
        "charges": read_csv_flexible(paths["charges"]),
    }
    if "billing" in paths:
        table_frames["billing"] = read_csv_flexible(paths["billing"])
    for role in ("access_unit", "access_wellhub", "access_totalpass"):
        if role in paths:
            table_frames[role] = read_csv_flexible(paths[role])
    return prepare_table_frames(
        table_frames,
        source_path=source_path,
        validation=validation,
        paths=paths,
    )


def latest_active_history_snapshot(
    frame: pd.DataFrame,
    fallback: int = 0,
) -> tuple[int, pd.Timestamp | None]:
    """Sum today's latest HISTORICO ATIVOS snapshot, excluding training."""
    if frame.empty or "dia" not in frame or "quantidade" not in frame:
        return fallback, None

    timestamps = pd.to_datetime(frame["dia"], errors="coerce")
    today = pd.Timestamp.now(tz="America/Sao_Paulo").tz_localize(None).normalize()
    today_mask = timestamps.notna() & timestamps.dt.normalize().eq(today)
    if not today_mask.any():
        return fallback, None

    latest = timestamps[today_mask].max()
    snapshot = frame.loc[today_mask & timestamps.eq(latest)].copy()
    if "Filial" in snapshot:
        training_mask = snapshot["Filial"].map(norm_key).str.contains("treinamento", na=False)
        snapshot = snapshot.loc[~training_mask]
    quantities = pd.to_numeric(snapshot["quantidade"], errors="coerce").fillna(0)
    return int(round(float(quantities.sum()))), latest


def active_history_snapshot_by_unit(
    frame: pd.DataFrame,
    timestamps: pd.Series,
    target_day: pd.Timestamp,
) -> tuple[dict[str, int], pd.Timestamp | None]:
    day_mask = timestamps.notna() & timestamps.dt.normalize().eq(target_day.normalize())
    if not day_mask.any():
        return {}, None
    latest = timestamps[day_mask].max()
    snapshot = frame.loc[day_mask & timestamps.eq(latest)].copy()
    snapshot["unidade_nome"] = snapshot.get("Filial", pd.Series(index=snapshot.index)).map(branch_name)
    snapshot = snapshot[
        snapshot["unidade_nome"].isin(UNIT_ORDER)
        & ~snapshot["unidade_nome"].isin(EXCLUDED_UNITS)
    ].copy()
    snapshot["quantidade_num"] = pd.to_numeric(snapshot.get("quantidade"), errors="coerce").fillna(0)
    values = snapshot.groupby("unidade_nome")["quantidade_num"].sum()
    return {unit: int(round(float(values.get(unit, 0)))) for unit in UNIT_ORDER}, latest


def active_unit_goal_chart(frame: pd.DataFrame) -> dict:
    """Build target progress, month growth and daily movement by unit."""
    empty_chart = {
        "type": "activeGoals",
        "title": "ATIVOS POR UNIDADE",
        "subtitle": "HISTORICO ATIVOS sem snapshots suficientes para a comparação.",
        "className": "chart-active-units chart-active-goals",
        "rows": [],
        "network": {},
        "goalLabel": "Diamante Total",
    }
    if frame.empty or "dia" not in frame or "quantidade" not in frame:
        return empty_chart

    timestamps = pd.to_datetime(frame["dia"], errors="coerce")
    if not timestamps.notna().any():
        return empty_chart

    current_timestamp = timestamps.max()
    current_day = current_timestamp.normalize()
    previous_day = current_day - pd.Timedelta(days=1)
    prior_month_end = current_day.replace(day=1) - pd.Timedelta(days=1)
    current_values, current_snapshot = active_history_snapshot_by_unit(frame, timestamps, current_day)
    previous_values, previous_snapshot = active_history_snapshot_by_unit(frame, timestamps, previous_day)
    baseline_values, baseline_snapshot = active_history_snapshot_by_unit(frame, timestamps, prior_month_end)
    if not current_values:
        return empty_chart

    month_key = current_day.strftime("%Y-%m")
    goals = ACTIVE_GOALS_BY_MONTH.get(month_key, {})
    rows = []
    for opening_order, unit in enumerate(UNIT_ORDER):
        current = int(current_values.get(unit, 0))
        baseline = int(baseline_values.get(unit, 0))
        previous = int(previous_values.get(unit, 0)) if previous_snapshot is not None else None
        goal = int(goals.get(unit, 0))
        growth_delta = current - baseline
        growth_pct = growth_delta / baseline * 100 if baseline else 0.0
        daily_delta = current - previous if previous is not None else None
        goal_pct = current / goal * 100 if goal else 0.0
        rows.append(
            {
                "label": unit,
                "value": current,
                "goal": goal,
                "goalPct": goal_pct,
                "baseline": baseline,
                "growthDelta": growth_delta,
                "growthPct": growth_pct,
                "dailyDelta": daily_delta,
                "openingOrder": opening_order,
                "stars": 0,
            }
        )

    ranked = sorted(
        rows,
        key=lambda row: (row["growthPct"], row["growthDelta"], -row["openingOrder"]),
        reverse=True,
    )
    for stars, row in zip((3, 2, 1), ranked[:3]):
        row["stars"] = stars

    current_total = sum(row["value"] for row in rows)
    baseline_total = sum(row["baseline"] for row in rows)
    previous_total = sum(previous_values.get(unit, 0) for unit in UNIT_ORDER) if previous_snapshot is not None else None
    goal_total = sum(row["goal"] for row in rows)
    network_delta = current_total - baseline_total
    network_growth_pct = network_delta / baseline_total * 100 if baseline_total else 0.0
    network_daily_delta = current_total - previous_total if previous_total is not None else None
    month_name = MONTH_ABBR.get(current_day.month, str(current_day.month))
    baseline_label = baseline_snapshot.strftime("%d/%m/%Y") if baseline_snapshot is not None else "sem base"
    current_label = current_snapshot.strftime("%d/%m/%Y %H:%M") if current_snapshot is not None else ""

    return {
        "type": "activeGoals",
        "title": "ATIVOS POR UNIDADE",
        "subtitle": (
            f"Crescimento em {month_name}/{current_day.year} · base em {baseline_label} · "
            "barras = progresso da meta Diamante Total"
        ),
        "className": "chart-active-units chart-active-goals",
        "rows": rows,
        "goalLabel": "Diamante Total",
        "monthKey": month_key,
        "currentSnapshot": current_label,
        "network": {
            "value": current_total,
            "goal": goal_total,
            "goalPct": current_total / goal_total * 100 if goal_total else 0.0,
            "growthDelta": network_delta,
            "growthPct": network_growth_pct,
            "dailyDelta": network_daily_delta,
        },
    }


def build_payload(
    workbook_path: str | Path | None = None,
    source_label: str | None = None,
    filters: dict | None = None,
    prepared_data: dict | None = None,
    only_tab: str | None = None,
) -> dict:
    prepared = prepared_data or load_processed_tables(workbook_path)
    validation = prepared.get("validation", [])
    if not prepared.get("valid"):
        return build_blank_payload(source_label=source_label, validation=validation, filters=filters)

    paths = prepared.get("paths", {})
    source_path = prepared.get("sourcePath", str(Path(workbook_path) if workbook_path else DEFAULT_CSV_DIR))
    source = source_label or source_upload_label(source_path)
    sales = prepared["sales"].copy()
    sales_realtime = prepared.get("sales_realtime", pd.DataFrame()).copy()
    sales_swaps = prepared.get("sales_swaps", pd.DataFrame()).copy()
    billing = prepared.get("billing", pd.DataFrame()).copy()
    active = prepared["active"].copy()
    active_cancellation_reference = active.copy()
    sales_ticker = latest_realtime_contracts(sales_realtime, limit=10)
    active_history = prepared.get("active_history", pd.DataFrame()).copy()
    canc = prepared["cancellations"].copy()
    non_renewed = prepared.get("non_renewed", pd.DataFrame()).copy()
    charges = prepared["charges"].copy()
    access = prepared["access"].copy()
    cannibalization_canc = prepared["cancellations"].copy()
    cannibalization_access = prepared["access"].copy()

    filter_state = normalize_dashboard_filters(filters)
    selected_units = filter_state.get("unitFilters", [])
    selected_ages = filter_state.get("ageFilters", [])
    selected_genders = filter_state.get("genderFilters", [])
    period_start = parse_filter_date(filter_state["periodStart"])
    period_end = parse_filter_date(filter_state["periodEnd"])
    only_tab = only_tab if only_tab in {"ativos", "vendas", "cancelamentos", "financeiro", "frequencia", "isaias"} else None

    def partial_payload(tab_key: str, tab: dict) -> dict:
        return {
            "sourceFile": source,
            "sourcePath": source_path,
            "filters": filter_state,
            "filterOptions": {
                "units": UNIT_ORDER,
                "ageBands": AGE_BAND_LABELS,
                "genders": GENDER_FILTER_OPTIONS,
            },
            "tabs": {tab_key: tab},
            "overview": {"cards": []},
            "validation": validation,
            "medalBoard": [],
        }

    if selected_units:
        sales = sales[sales["unidade_nome"].isin(selected_units)].copy()
        if not sales_swaps.empty:
            sales_swaps = sales_swaps[sales_swaps["unidade_nome"].isin(selected_units)].copy()
        if not billing.empty:
            billing = billing[billing["unidade_nome"].isin(selected_units)].copy()
        active = active[active["unidade_nome"].isin(selected_units)].copy()
        canc = canc[canc["unidade_nome"].isin(selected_units)].copy()
        if not non_renewed.empty:
            non_renewed = non_renewed[non_renewed["unidade_nome"].isin(selected_units)].copy()
        charges = charges[charges["unidade_nome"].isin(selected_units)].copy()
        if not access.empty:
            access = access[access["unidade_nome"].isin(selected_units)].copy()
        if not cannibalization_access.empty:
            cannibalization_access = cannibalization_access[
                cannibalization_access["unidade_nome"].isin(selected_units)
            ].copy()

    active["faixa_etaria_filtro"] = age_band_series(active.get("dataNascimento", pd.Series(index=active.index, dtype=str))).astype(str)
    active["sexo_filtro"] = active.get("sexo", pd.Series(index=active.index, dtype=str)).map(clean_gender)
    if selected_ages or selected_genders:
        demographic_mask = pd.Series(True, index=active.index)
        if selected_ages:
            demographic_mask &= active["faixa_etaria_filtro"].isin(selected_ages)
        if selected_genders:
            demographic_mask &= active["sexo_filtro"].isin(selected_genders)
        demographic_ids = set(id_series(active.loc[demographic_mask, "idMember"]))
        active = active[id_series(active.get("idMember")).isin(demographic_ids)].copy()
        sales = sales[id_series(sales.get("idMember")).isin(demographic_ids)].copy()
        if not sales_swaps.empty:
            sales_swaps = sales_swaps[
                id_series(sales_swaps.get("idMember")).isin(demographic_ids)
            ].copy()
        if not billing.empty:
            billing = billing[id_series(billing.get("idMember")).isin(demographic_ids)].copy()
        canc = canc[id_series(canc.get("idMember")).isin(demographic_ids)].copy()
        charges = charges[id_series(charges.get("idMember")).isin(demographic_ids)].copy()
        if not access.empty:
            access = access[id_series(access.get("id_member")).isin(demographic_ids)].copy()
        cannibalization_canc = cannibalization_canc[
            id_series(cannibalization_canc.get("idMember")).isin(demographic_ids)
        ].copy()
        if not cannibalization_access.empty:
            cannibalization_access = cannibalization_access[
                id_series(cannibalization_access.get("id_member")).isin(demographic_ids)
            ].copy()

    # A série histórica de vendas permanece fora do filtro de período para que
    # o gráfico mensal continue exibindo todos os meses. As cobranças completas
    # são preservadas para o cruzamento financeiro de cada venda.
    non_renewed = scoped_non_renewed_rows(non_renewed, period_start, period_end)
    if only_tab == "vendas":
        # Fast path: Vendas does not process access, billing or churn history.
        sales_history_fast = sales.copy()
        sales_dates_fast = parse_date(sales_date_series(sales))
        if period_start is not None or period_end is not None:
            sales_scope_fast = filter_frame_by_date(sales, sales_dates_fast, period_start, period_end)
            sales_history_fast = sales_scope_fast.copy()
            sales_scope_label_fast = "período selecionado"
        else:
            reference_month_fast = pd.Timestamp(date.today()).to_period("M")
            sales_scope_fast = sales.loc[sales_dates_fast.dt.to_period("M").eq(reference_month_fast)].copy()
            sales_scope_label_fast = f"{MONTH_ABBR.get(reference_month_fast.month, reference_month_fast.month)}/{reference_month_fast.year}"

        sales_history_fast = (
            clean_sales_business_rules(sales_history_fast, charges)
            if period_start is not None or period_end is not None
            else clean_sales_monthly_history(sales_history_fast, charges)
        )
        sales_scope_fast = clean_sales_business_rules(sales_scope_fast, charges)
        sales_history_dates_fast = parse_date(sales_date_series(sales_history_fast))
        sales_scope_dates_fast = parse_date(sales_date_series(sales_scope_fast))
        sales_scope_values_fast = parse_number(
            sales_scope_fast.get("valor_venda", pd.Series(index=sales_scope_fast.index, dtype=float))
        )
        sales_scope_ids_fast = id_series(
            sales_scope_fast.get("idMember", pd.Series(index=sales_scope_fast.index, dtype=str))
        )
        sales_scope_fast["unidade_nome"] = sales_scope_fast.get(
            "id_unidade", pd.Series(index=sales_scope_fast.index)
        ).map(branch_name)
        sales_scope_fast["contrato_norm"] = sales_scope_fast.get(
            "contrato", pd.Series(index=sales_scope_fast.index)
        ).map(clean_plan)

        checkout_paid_fast, _ = sales_charge_equal_masks(sales_scope_fast, charges)
        qualified_unit_sales_fast = sales_scope_fast.copy()

        active_ids_fast = id_series(active.get("idMember", pd.Series(index=active.index, dtype=str)))
        charge_ids_fast = id_series(charges.get("idMember", pd.Series(index=charges.index, dtype=str)))
        charge_values_fast = parse_number(
            charges.get("valorCompet", pd.Series(index=charges.index, dtype=float))
        )
        charge_status_fast = charges.get(
            "status", pd.Series(index=charges.index, dtype=str)
        ).fillna("").astype(str).map(norm_key)
        open_charge_fast = charge_status_fast.eq("a receber")
        charge_units_fast = charges.get(
            "unidade_nome", charges.get("idFilial", pd.Series(index=charges.index))
        ).map(branch_name)

        sales_ticket_mean_fast, sales_ticket_count_fast = sales_ticket_average(
            sales_scope_values_fast,
            sales_scope_fast.get("contrato", pd.Series(index=sales_scope_fast.index)),
        )
        sv_plus_sales_fast = int(sales_scope_fast["contrato_norm"].eq("SV Plus").sum())
        sv_plus_pct_fast = sv_plus_sales_fast / max(len(sales_scope_fast), 1) * 100
        yesterday_sales_fast, yesterday_metric_fast, yesterday_status_fast = previous_day_sales_indicator(
            sales_scope_dates_fast,
            period_end or pd.Timestamp(date.today()),
        )
        _, active_sv_plus_pct_fast = active_plan_share(active)
        ticket_status_fast = "good" if sales_ticket_mean_fast >= SV_PLAN_REFERENCE_PRICE else "bad"
        ticket_metric_fast = "↑ acima da referência" if ticket_status_fast == "good" else "↓ abaixo da referência"
        active_detail_ids_fast = int(active_ids_fast[active_ids_fast.ne("")].nunique())
        active_total_fast, _ = latest_active_history_snapshot(active_history, fallback=active_detail_ids_fast)
        growth_cancellations_fast = prepared["cancellations"].copy()
        if selected_units:
            growth_cancel_units_fast = growth_cancellations_fast.get(
                "idBranch", pd.Series(index=growth_cancellations_fast.index)
            ).map(branch_name)
            growth_cancellations_fast = growth_cancellations_fast[growth_cancel_units_fast.isin(selected_units)].copy()
        growth_cancellations_fast = growth_cancellations_fast.loc[
            eligible_cancellation_mask(growth_cancellations_fast, active_cancellation_reference)
        ].copy()
        growth_cancel_dates_fast = parse_date(growth_cancellations_fast.get("dataCancelamento"))
        if period_start is not None or period_end is not None:
            growth_cancellations_fast = filter_frame_by_date(
                growth_cancellations_fast, growth_cancel_dates_fast, period_start, period_end
            )
        else:
            growth_cancellations_fast = growth_cancellations_fast.loc[
                growth_cancel_dates_fast.dt.to_period("M").eq(reference_month_fast)
            ].copy()
        growth_chart_fast = growth_waterfall_chart(
            active_total_fast,
            len(sales_scope_fast),
            len(growth_cancellations_fast),
            len(non_renewed),
            sales_scope_label_fast,
        )
        tab = {
            "layout": "sales_summary",
            "ticker": sales_ticker,
            "cards": [
                card("Total de Contratos vendidos", br_int(len(sales_scope_fast)), "", "blue", meta=f"Ontem: {br_int(yesterday_sales_fast)} vendas", metric=yesterday_metric_fast, status=yesterday_status_fast),
                card("Ticket Médio Vendido", br_money(sales_ticket_mean_fast), "", "orange", meta=f"Referência SV: {br_money(SV_PLAN_REFERENCE_PRICE)}", metric=ticket_metric_fast, status=ticket_status_fast, valueStatus=ticket_status_fast),
                card("Check Out", br_int(int(checkout_paid_fast.sum())), "valor da venda igual à cobrança recebida", "green"),
                card("% de Vendas SV Plus", br_pct(sv_plus_pct_fast), "", "violet", meta=f"{br_int(sv_plus_sales_fast)} contratos", metric=f"{br_pct(active_sv_plus_pct_fast)} da base ativa", status="violet"),
                peak_sales_card(sales_scope_dates_fast),
            ],
            "charts": [
                {"type": "columnBar", "title": "Vendas por mês", "subtitle": "Tabela VENDAS após exclusão de MyNutri e dos consultores bloqueados.", "className": "chart-sales-month", "palette": "active", "rows": month_rows(sales_history_dates_fast)},
                {"type": "columnBar", "title": "Vendas totais por unidade", "subtitle": "Tabela VENDAS após exclusão de MyNutri e dos consultores bloqueados.", "className": "chart-sales-units unit-sales-columns", "palette": "active", "rows": unit_rows(qualified_unit_sales_fast["unidade_nome"], len(qualified_unit_sales_fast), medals=True)},
                {"type": "dualBar", "title": "Ticket médio venda x recebimento por unidade", "subtitle": "Recebimentos confirmados x vendas mensalizadas.", "className": "chart-sales-ticket dual-chart", "palette": "active", "primaryLabel": "Ticket recebido", "secondaryLabel": "Ticket venda", "rows": sales_ticket_received_unit_rows(sales_scope_fast["unidade_nome"], sales_scope_values_fast, sales_scope_fast.get("contrato", pd.Series(index=sales_scope_fast.index)), charge_units_fast, charge_values_fast, charge_status_fast)},
                {"type": "donut", "title": "Contratos vendidos no mês", "subtitle": f"Participação dos contratos vendidos em {sales_scope_label_fast}", "className": "chart-sales-contracts", "palette": "active", "rows": top_rows(sales_scope_fast["contrato_norm"], 10, len(sales_scope_fast))},
                growth_chart_fast,
            ],
        }
        return partial_payload("vendas", tab)

    sales_history = sales.copy()
    checkout_charges = charges.copy()
    financial_billing = billing.copy()
    financial_sales = sales.copy()
    financial_charges = charges.copy()
    financial_access = access.copy()
    churn_risk_active = active.copy()
    churn_risk_charges = charges.copy()
    churn_risk_access = access.copy()

    # Cancelamentos exibidos nos indicadores excluem qualquer ID que ainda
    # esteja ativo. A exceção são contratos ativos de agregadores, pois nesse
    # caso o aluno deixou de ser próprio e o cancelamento deve ser preservado.
    canc = canc.loc[eligible_cancellation_mask(canc, active_cancellation_reference)].copy()
    cancel_history = canc.copy()
    if period_start is None and period_end is None:
        cancel_reference_month = pd.Timestamp(date.today()).to_period("M")
        cancel_dates_for_scope = parse_date(canc.get("dataCancelamento"))
        canc = canc.loc[
            cancel_dates_for_scope.dt.to_period("M").eq(cancel_reference_month)
        ].copy()
        cancel_scope_label = (
            f"{MONTH_ABBR.get(cancel_reference_month.month, cancel_reference_month.month)}/"
            f"{cancel_reference_month.year}"
        )
    else:
        cancel_scope_label = "período selecionado"

    if period_start is not None or period_end is not None:
        sales = filter_frame_by_date(sales, parse_date(sales.get("dataVenda")), period_start, period_end)
        sales_history = sales.copy()
        canc = filter_frame_by_date(canc, parse_date(canc.get("dataCancelamento")), period_start, period_end)
        charges = filter_frame_by_date(charges, parse_date(charges.get("dataVencimento")), period_start, period_end)
        if not access.empty:
            access = filter_frame_by_date(access, parse_date(access.get("date_event")), period_start, period_end)

    sales_ids = id_series(sales.get("idMember"))
    active_ids = id_series(active.get("idMember"))
    active_detail_ids = int(active_ids[active_ids.ne("")].nunique())
    active_total, _ = latest_active_history_snapshot(
        active_history,
        fallback=active_detail_ids,
    )
    active_goal_chart = (
        active_unit_goal_chart(active_history)
        if only_tab in {None, "ativos", "isaias"}
        else {"type": "activeGoalBars", "title": "Ativos por unidade", "rows": [], "network": {}}
    )
    cancel_ids = id_series(canc.get("idMember"))
    charge_ids = id_series(charges.get("idMember"))
    access_ids = id_series(access.get("id_member")) if not access.empty else pd.Series(dtype=str)
    sales_sale_ids = id_series(sales.get("id_venda", pd.Series(index=sales.index, dtype=str)))
    cancel_sale_ids = id_series(canc.get("idSale", pd.Series(index=canc.index, dtype=str)))

    sales_dates = parse_date(sales_date_series(sales))
    cancel_dates = parse_date(canc.get("dataCancelamento"))
    cancel_history_dates = parse_date(cancel_history.get("dataCancelamento"))
    cancel_sale_dates = parse_date(canc.get("dataVenda", pd.Series(index=canc.index, dtype=str)))
    sales_start_dates = parse_embedded_date(sales.get("inicio_contrato", pd.Series(index=sales.index, dtype=str)))
    cancel_start_dates = parse_embedded_date(canc.get("inicioContrato", pd.Series(index=canc.index, dtype=str)))
    charge_due = parse_date(charges.get("dataVencimento"))
    charge_payment_dates = parse_date(charges.get("dataPagamento", pd.Series(index=charges.index, dtype=str)))
    access_dates = parse_date(access.get("date_event")) if not access.empty else pd.Series(dtype="datetime64[ns]")
    reference_date = period_end or infer_analysis_date(sales_dates, cancel_dates, charge_payment_dates, access_dates)

    sales_history = (
        clean_sales_business_rules(sales_history, checkout_charges)
        if period_start is not None or period_end is not None
        else clean_sales_monthly_history(sales_history, checkout_charges)
    )
    sales_history_dates = parse_date(sales_date_series(sales_history))
    sales_history["unidade_nome"] = sales_history.get("id_unidade", pd.Series(index=sales_history.index)).map(branch_name)
    sales_history["contrato_norm"] = sales_history.get("contrato", pd.Series(index=sales_history.index)).map(clean_plan)

    # Sem filtro explícito, a página Vendas abre sempre na competência atual.
    # Quando o usuário escolhe um período, respeitamos integralmente a seleção.
    if period_start is None and period_end is None:
        reference_month = pd.Timestamp(date.today()).to_period("M")
        sales_scope = sales.loc[sales_dates.dt.to_period("M").eq(reference_month)].copy()
        sales_scope_label = f"{MONTH_ABBR.get(reference_month.month, reference_month.month)}/{reference_month.year}"
    else:
        sales_scope = sales.copy()
        sales_scope_label = "período selecionado"
    sales_scope = clean_sales_business_rules(sales_scope, checkout_charges)
    sales_scope_dates = parse_date(sales_date_series(sales_scope))
    sales_scope_values = parse_number(sales_scope.get("valor_venda", pd.Series(index=sales_scope.index, dtype=float)))
    sales_scope_ids = id_series(sales_scope.get("idMember", pd.Series(index=sales_scope.index, dtype=str)))
    sales_scope["unidade_nome"] = sales_scope.get("id_unidade", pd.Series(index=sales_scope.index)).map(branch_name)
    sales_scope["contrato_norm"] = sales_scope.get("contrato", pd.Series(index=sales_scope.index)).map(clean_plan)
    checkout_paid_mask, _ = sales_charge_equal_masks(sales_scope, checkout_charges)
    qualified_unit_sales = sales_scope.copy()
    sales_growth_chart = growth_waterfall_chart(
        active_total,
        len(sales_scope),
        len(canc),
        len(non_renewed),
        sales_scope_label,
    )

    financial_matrix = (
        financial_monthly_matrix(
            financial_billing,
            financial_charges,
            financial_sales,
            financial_access,
            period_start,
            period_end,
            selected_units,
        )
        if only_tab in {None, "financeiro", "isaias"}
        else {"type": "financialMatrix", "views": [], "units": [], "defaultMonth": ""}
    )
    sales_value = parse_number(sales.get("valor_venda"))
    active_value = parse_number(active.get("valorCompetencia"))
    active_days = parse_number(active.get("diasAtivo"))
    active_access_month = parse_number(active.get("acessos_mes"))
    cancel_days = parse_number(canc.get("diasAtivos"))
    cancel_debt = parse_number(canc.get("quantidadeDevido"))
    charge_value = parse_number(charges.get("valorCompet"))
    charge_days = parse_number(charges.get("diasInad"))

    sales["unidade_nome"] = sales.get("id_unidade", pd.Series(index=sales.index)).map(branch_name)
    active["unidade_nome"] = active.get("Filial", pd.Series(index=active.index)).map(branch_name)
    sales["contrato_norm"] = sales.get("contrato", pd.Series(index=sales.index)).map(clean_plan)
    active["contrato_norm"] = active.get("contrato", pd.Series(index=active.index)).map(clean_plan)
    canc["contrato_norm"] = canc.get("contrato", pd.Series(index=canc.index)).map(clean_plan)
    canc["motivo_limpo"] = canc.get("Motivo", pd.Series(index=canc.index)).map(grouped_cancel_reason)
    cancel_history["contrato_norm"] = cancel_history.get(
        "contrato", pd.Series(index=cancel_history.index)
    ).map(clean_plan)
    cancel_history["motivo_limpo"] = cancel_history.get(
        "Motivo", pd.Series(index=cancel_history.index)
    ).map(grouped_cancel_reason)
    charges["contrato_norm"] = charges.get("contrato", pd.Series(index=charges.index)).map(clean_plan)

    cannibalization_chart = (
        cannibalization_period_chart(
            cannibalization_canc,
            cannibalization_access,
            period_start,
            period_end,
        )
        if only_tab in {None, "cancelamentos", "isaias"}
        else None
    )

    charge_status = charges.get("status", pd.Series(index=charges.index)).fillna("").astype(str).map(norm_key)
    open_charge = charge_status.eq("a receber")
    charge_payment_rows = (
        payment_status_rows(charge_ids, charge_status, charge_due, charge_value, reference_date)
        if only_tab in {None, "financeiro", "isaias"}
        else []
    )
    received_charge_mask = charge_status.eq("recebido") & charge_value.fillna(0).gt(0)
    received_ticket_mean = float(charge_value[received_charge_mask].mean()) if received_charge_mask.any() else 0.0
    received_ticket_count = int(received_charge_mask.sum())
    churn_risk_chart = (
        churn_risk_panel(churn_risk_active, churn_risk_charges, churn_risk_access)
        if only_tab in {None, "cancelamentos", "isaias"}
        else None
    )
    if only_tab == "ativos":
        active_id_set = set(active_ids[active_ids.ne("")])
        overdue_charge = open_charge & charge_value.fillna(0).gt(0) & charge_days.fillna(0).gt(0)
        inadimplente_ids = active_id_set & set(charge_ids[overdue_charge & charge_ids.ne("")])
        adimplente_ids = active_id_set - inadimplente_ids
        adimplentes = len(adimplente_ids)
        inadimplentes = len(inadimplente_ids)
        ids_active = int(active_ids[active_ids.ne("")].nunique())
        adimplentes_pct = adimplentes / max(ids_active, 1) * 100
        inadimplentes_pct = inadimplentes / max(ids_active, 1) * 100
        active_days_mean = active_days[active_days >= 0].mean()
        unit_access_mask = access["canal"].eq("Unidade") if not access.empty else pd.Series(dtype=bool)
        wellhub_ids = id_series(access.loc[access["canal"].eq("Wellhub"), "id_member"]) if not access.empty else pd.Series(dtype=str)
        totalpass_ids = id_series(access.loc[access["canal"].eq("TotalPass"), "id_member"]) if not access.empty else pd.Series(dtype=str)
        ids_wellhub = int(wellhub_ids[wellhub_ids.ne("")].nunique()) if len(wellhub_ids) else 0
        ids_totalpass = int(totalpass_ids[totalpass_ids.ne("")].nunique()) if len(totalpass_ids) else 0
        active_public_total = max(adimplentes + inadimplentes + ids_wellhub + ids_totalpass, 1)
        access_unique = int(access_ids[access_ids.ne("")].nunique()) if len(access_ids) else 0
        age_rows, mean_age = age_band_rows(active.get("dataNascimento", pd.Series(dtype=str)))
        age_gender_data = age_gender_pyramid_data(
            active.get("dataNascimento", pd.Series(index=active.index, dtype=str)),
            active.get("sexo", pd.Series(index=active.index, dtype=str)),
        )
        access["unidade_nome"] = access.get("id_branch", pd.Series(index=access.index)).map(branch_name) if not access.empty else ""
        aggregator_unit_chart = aggregator_unique_unit_chart(
            access["unidade_nome"] if not access.empty else pd.Series(dtype=str),
            access.get("canal", pd.Series(index=access.index)) if not access.empty else pd.Series(dtype=str),
            access_ids,
        )
        adimplentes_target_status = "good" if adimplentes_pct >= 90 else "bad"
        inadimplentes_target_status = "good" if inadimplentes_pct <= 10 else "bad"
        tab = {
            "layout": "active_summary",
            "cards": [
                card("Alunos ativos", br_int(active_total), "", "green"),
                card("Adimplentes", br_int(adimplentes), "", "blue", metric=br_pct(adimplentes_pct), meta="Meta: 90%\u00a0da\u00a0base\u00a0ativa", status=adimplentes_target_status),
                card("Inadimplentes", br_int(inadimplentes), "", "red", metric=br_pct(inadimplentes_pct), meta="Meta: 10%\u00a0da\u00a0base\u00a0ativa", status=inadimplentes_target_status),
                card("Agregadores Wellhub", br_int(ids_wellhub), "NÃºmero de Agregadores com acesso", "violet"),
                card("Agregadores TotalPass", br_int(ids_totalpass), "NÃºmero de Agregadores com acesso", "orange"),
            ],
            "aggregatorCards": [],
            "composition": {
                "title": "Base ativa + agregadores",
                "subtitle": "",
                "rows": [
                    {"label": "Adimplentes", "value": adimplentes, "pct": adimplentes / active_public_total * 100, "tone": "blue"},
                    {"label": "Inadimplentes", "value": inadimplentes, "pct": inadimplentes / active_public_total * 100, "tone": "red"},
                    {"label": "Wellhub", "value": ids_wellhub, "pct": ids_wellhub / active_public_total * 100, "tone": "violet"},
                    {"label": "TotalPass", "value": ids_totalpass, "pct": ids_totalpass / active_public_total * 100, "tone": "orange"},
                ],
            },
            "charts": [
                active_goal_chart,
                aggregator_unit_chart,
                {"type": "bar", "title": "Ativos por contrato", "className": "chart-active-contract compact", "barTone": "blue", "rows": top_rows(active["contrato_norm"], 10, len(active))},
                {"type": "columnBar", "title": "Distribuição por sexo", "className": "chart-profile-gender compact", "rowTones": ["green", "blue", "orange"], "showPct": True, "rows": gender_distribution_rows(active.get("sexo", pd.Series(dtype=str)))},
                {"type": "ageGenderPyramid", "title": "Faixa etária por sexo", "subtitle": "Homens à esquerda · mulheres à direita · percentuais sobre a base com idade e sexo identificados.", "subtitlePosition": "footer", "className": "chart-profile-age active-demographic-age", **age_gender_data},
            ],
            "footerCards": [
                card("Alunos com entradas registradas", br_int(access_unique), "alunos próprios + Wellhub + TotalPass", "green"),
                card("Idade média", f"{mean_age:.1f}".replace(".", ",") if mean_age else "0,0", "nascimentos válidos", "blue"),
                card("Média de dias Ativos", f"{active_days_mean:.1f}".replace(".", ",") if pd.notna(active_days_mean) else "0,0", "diasAtivo", "orange"),
                card("% de alunos próprios", br_pct(ids_active / active_public_total * 100), f"{br_int(ids_active)} IDs", "green"),
                card("% de Wellhub", br_pct(ids_wellhub / active_public_total * 100), f"{br_int(ids_wellhub)} IDs", "violet"),
                card("% de TotalPass", br_pct(ids_totalpass / active_public_total * 100), f"{br_int(ids_totalpass)} IDs", "orange"),
            ],
        }
        return partial_payload("ativos", tab)

    if only_tab == "vendas":
        sales_ticket_mean, sales_ticket_count = sales_ticket_average(
            sales_scope_values,
            sales_scope.get("contrato", pd.Series(index=sales_scope.index)),
        )
        sv_plus_sales = int(sales_scope["contrato_norm"].eq("SV Plus").sum())
        sv_plus_sales_pct = sv_plus_sales / max(len(sales_scope), 1) * 100
        checkout_count = int(checkout_paid_mask.sum())
        yesterday_sales, yesterday_metric, yesterday_status = previous_day_sales_indicator(
            sales_scope_dates,
            period_end or reference_date,
        )
        _, active_sv_plus_pct = active_plan_share(active)
        ticket_status = "good" if sales_ticket_mean >= SV_PLAN_REFERENCE_PRICE else "bad"
        ticket_metric = "↑ acima da referência" if ticket_status == "good" else "↓ abaixo da referência"
        tab = {
            "layout": "sales_summary",
            "ticker": sales_ticker,
            "cards": [
                card("Total de Contratos vendidos", br_int(len(sales_scope)), "", "blue", meta=f"Ontem: {br_int(yesterday_sales)} vendas", metric=yesterday_metric, status=yesterday_status),
                card("Ticket MÃ©dio Vendido", br_money(sales_ticket_mean), "", "orange", meta=f"Referência SV: {br_money(SV_PLAN_REFERENCE_PRICE)}", metric=ticket_metric, status=ticket_status, valueStatus=ticket_status),
                card("Check Out", br_int(checkout_count), "valor da venda igual à cobrança recebida", "green"),
                card("% de Vendas SV Plus", br_pct(sv_plus_sales_pct), "", "violet", meta=f"{br_int(sv_plus_sales)} contratos", metric=f"{br_pct(active_sv_plus_pct)} da base ativa", status="violet"),
                peak_sales_card(sales_scope_dates),
            ],
            "charts": [
                {"type": "columnBar", "title": "Vendas por mês", "subtitle": "Tabela VENDAS após exclusão de MyNutri e dos consultores bloqueados.", "className": "chart-sales-month", "palette": "active", "rows": month_rows(sales_history_dates)},
                {"type": "columnBar", "title": "Vendas totais por unidade", "subtitle": "Tabela VENDAS após exclusão de MyNutri e dos consultores bloqueados.", "className": "chart-sales-units unit-sales-columns", "palette": "active", "rows": unit_rows(qualified_unit_sales["unidade_nome"], len(qualified_unit_sales), medals=True)},
                {"type": "dualBar", "title": "Ticket médio venda x recebimento por unidade", "subtitle": "Recebimentos confirmados x vendas mensalizadas.", "className": "chart-sales-ticket dual-chart", "palette": "active", "primaryLabel": "Ticket recebido", "secondaryLabel": "Ticket venda", "rows": sales_ticket_received_unit_rows(sales_scope["unidade_nome"], sales_scope_values, sales_scope.get("contrato", pd.Series(index=sales_scope.index)), charges["unidade_nome"], charge_value, charge_status)},
                {"type": "donut", "title": "Contratos vendidos no mês", "subtitle": f"Participação dos contratos vendidos em {sales_scope_label}", "className": "chart-sales-contracts", "palette": "active", "rows": top_rows(sales_scope["contrato_norm"], 10, len(sales_scope))},
                sales_growth_chart,
            ],
        }
        return partial_payload("vendas", tab)

    if only_tab == "cancelamentos":
        ids_cancel = int(cancel_ids[cancel_ids.ne("")].nunique())
        active_id_set = set(active_ids[active_ids.ne("")])
        cancel_id_set = set(cancel_ids[cancel_ids.ne("")])
        canceled_still_active = len(cancel_id_set & active_id_set)
        cancel_with_debt = int((cancel_debt.fillna(0) > 0).sum())
        tab = {
            "layout": "cancel_summary",
            "cards": [
                card("Contratos Cancelados", br_int(len(canc)), f"{cancel_scope_label} · exclui IDs ainda ativos", "wellhub"),
                card("Clientes Cancelados", br_int(ids_cancel), "clientes únicos", "activeBlue"),
                card("Média de meses Ativos", f"{(cancel_days[cancel_days >= 0].mean() / 30):.1f}".replace(".", ",") if pd.notna(cancel_days[cancel_days >= 0].mean()) else "0,0", "diasAtivos / 30", "activeCyan"),
                card("Inativados com saldo Devedor", br_int(cancel_with_debt), f"{br_pct(cancel_with_debt / max(len(canc), 1) * 100)} da base", "activeTeal"),
                card("NÃO RENOVADOS", br_int(len(non_renewed)), "contratos no período", "activeGreen"),
            ],
            "charts": [
                {"type": "columnBar", "title": "Cancelamentos por mês", "subtitle": "Histórico comparativo entre inadimplência e cancelamentos solicitados.", "className": "chart-cancel-month chart-sales-month grouped-month-chart", "palette": "cancellation", "rows": cancel_month_reason_rows(cancel_history_dates, cancel_history["motivo_limpo"])},
                {"type": "donut", "title": "Cancelamentos por contrato", "subtitle": f"Participação dos contratos cancelados em {cancel_scope_label}.", "className": "chart-cancel-contracts", "palette": "cancellation", "rows": top_rows(canc["contrato_norm"], 10, len(canc))},
                {"type": "stackedColumn", "title": "Cancelamentos por unidade", "subtitle": "Cancelamentos solicitados, inadimplência e não renovados no período.", "className": "chart-cancel-units", "palette": "cancellation", "rows": cancellation_unit_column_rows(canc.get("idBranch", pd.Series(dtype=str)).map(branch_name), cancel_dates, canc["motivo_limpo"], non_renewed.get("unidade_nome", pd.Series(dtype=str)))},
                {"type": "bar", "title": "Churn por unidade", "subtitle": "Cancelamentos + não renovados / base ativa estimada no dia anterior ao início do mês.", "className": "chart-cancel-churn compact", "palette": "cancellation", "rows": churn_unit_rows(canc["unidade_nome"], cancel_ids, cancel_dates, cancel_start_dates, cancel_sale_ids, sales["unidade_nome"], sales_ids, sales_dates, sales_start_dates, sales_sale_ids, active["unidade_nome"], active_ids, active_days, reference_date, non_renewed.get("unidade_nome", pd.Series(dtype=str)), parse_date(non_renewed.get("DataFim", pd.Series(index=non_renewed.index, dtype=str))))},
                {"type": "bar", "title": "Motivos de cancelamento", "className": "chart-cancel-reasons", "palette": "cancellation", "rows": top_rows(canc["motivo_limpo"], 12, len(canc))},
            ],
        }
        tab["charts"].insert(0, cannibalization_chart)
        tab["charts"].append(churn_risk_chart)
        return partial_payload("cancelamentos", tab)

    if only_tab == "frequencia":
        access_total = len(access)
        access_unique = int(access_ids[access_ids.ne("")].nunique()) if len(access_ids) else 0
        unit_access_mask = access["canal"].eq("Unidade") if not access.empty else pd.Series(dtype=bool)
        aggregator_access_mask = ~unit_access_mask if not access.empty else pd.Series(dtype=bool)
        unit_access_count = int(unit_access_mask.sum()) if not access.empty else 0
        aggregator_access_count = int(aggregator_access_mask.sum()) if not access.empty else 0
        unit_access_ids = id_series(access.loc[unit_access_mask, "id_member"]) if not access.empty else pd.Series(dtype=str)
        aggregator_access_ids = id_series(access.loc[aggregator_access_mask, "id_member"]) if not access.empty else pd.Series(dtype=str)
        unit_access_unique = int(unit_access_ids[unit_access_ids.ne("")].nunique()) if len(unit_access_ids) else 0
        aggregator_access_unique = int(aggregator_access_ids[aggregator_access_ids.ne("")].nunique()) if len(aggregator_access_ids) else 0
        unit_access_mean = unit_access_count / max(unit_access_unique, 1)
        aggregator_access_mean = aggregator_access_count / max(aggregator_access_unique, 1)
        access["unidade_nome"] = access.get("id_branch", pd.Series(index=access.index)).map(branch_name) if not access.empty else ""
        access_day_rows = access_day_segment_rows(access_dates, access.get("canal", pd.Series(index=access.index)), 24) if not access.empty else []
        weekday_access_chart_rows = weekday_access_rows(access_dates) if not access.empty else []
        hourly_channel_rows, _hourly_channel_insight = hourly_access_channel_rows(access_dates, access.get("canal", pd.Series(index=access.index))) if not access.empty else ([], "")
        access_daily_comparison_chart = access_daily_unit_comparison_chart(access["unidade_nome"], access_dates) if not access.empty else None
        latest_access_month = access_dates.dropna().dt.to_period("M").max() if not access_dates.dropna().empty else None
        if latest_access_month is not None and not access.empty:
            access_month_mask = access_dates.dt.to_period("M").eq(latest_access_month)
            month_label = f"{MONTH_ABBR.get(int(latest_access_month.month), str(latest_access_month.month).zfill(2))}/{latest_access_month.year}"
            own_month_counts = id_series(access.loc[access_month_mask & unit_access_mask, "id_member"]).value_counts()
            aggregator_month_counts = id_series(access.loc[access_month_mask & aggregator_access_mask, "id_member"]).value_counts()
        else:
            month_label = "mÃªs atual"
            own_month_counts = pd.Series(dtype=int)
            aggregator_month_counts = pd.Series(dtype=int)
        own_cluster_panel = frequency_cluster_panel("Clusters de entradas - Alunos prÃ³prios", active_ids, own_month_counts, f"ClassificaÃ§Ã£o por visitas em {month_label}; base ATIVOS_LTV.")
        aggregator_cluster_panel = frequency_cluster_panel("Clusters de entradas - Agregadores", aggregator_access_ids, aggregator_month_counts, f"ClassificaÃ§Ã£o por visitas em {month_label}; base Wellhub + TotalPass identificada.")
        own_cluster_base = pd.DataFrame({"id": active_ids, "unit": active["unidade_nome"] if "unidade_nome" in active else pd.Series(index=active.index, dtype=str)})
        if not access.empty:
            aggregator_base = pd.DataFrame({"id": aggregator_access_ids, "unit": access.loc[aggregator_access_mask, "unidade_nome"], "date": access_dates.loc[aggregator_access_mask]})
            aggregator_base = aggregator_base[aggregator_base["id"].ne("") & aggregator_base["unit"].notna()].sort_values("date").drop_duplicates("id", keep="last")
        else:
            aggregator_base = pd.DataFrame(columns=["id", "unit"])
        tab = {
            "layout": "frequency_summary",
            "cards": [
                card("Quantidade de Acessos", br_int(access_total), "Unidade + Wellhub + TotalPass", "activeBlue"),
                card("Quantidade de clientes com acesso", br_int(access_unique), "IDs Ãºnicos identificados", "blue"),
                card("Acesso Alunos PrÃ³prios", br_int(unit_access_count), f"{br_int(unit_access_unique)} clientes Ãºnicos", "orange"),
                card("Acesso Agregadores", br_int(aggregator_access_count), f"{br_int(aggregator_access_unique)} clientes Ãºnicos", "violet"),
                card("MÃ©dia de Acessos Alunos PrÃ³prios", f"{unit_access_mean:.1f}".replace(".", ","), "acessos / clientes Ãºnicos", "blue"),
                card("MÃ©dia de Acessos Agregadores", f"{aggregator_access_mean:.1f}".replace(".", ","), "acessos / clientes Ãºnicos", "green"),
            ],
            "charts": [
                {"type": "dualBar", "title": "LTV média x mediana por plano", "className": "chart-ltv-plan dual-chart", "palette": "active", "rows": ltv_month_rows(active["contrato_norm"], active_days, limit=10)},
                {"type": "dualBar", "title": "LTV média x mediana por unidade", "className": "chart-ltv-unit dual-chart", "palette": "active", "rows": ltv_month_rows(active["unidade_nome"], active_days, order=UNIT_ORDER, medals=True)},
                {"type": "columnBar", "title": "Acessos por dia", "subtitle": "Barras por alunos prÃ³prios e agregadores, com dia da semana no rÃ³tulo.", "className": "chart-access-day chart-sales-month grouped-day-chart", "palette": "active", "rows": access_day_rows},
                {"type": "donut", "title": "DistribuiÃ§Ã£o por dia da semana", "subtitle": "ParticipaÃ§Ã£o dos acessos de segunda a domingo.", "className": "chart-weekday-access", "palette": "active", "rows": weekday_access_chart_rows},
                {"type": "multiBar", "title": "Entradas por horário", "subtitle": "Média diária por horário, separada por alunos próprios, Wellhub e TotalPass.", "className": "chart-access-hour multi-chart", "palette": "active", "rows": hourly_channel_rows},
            ] + ([{**access_daily_comparison_chart, "palette": "active"}] if access_daily_comparison_chart else []) + [
                {**own_cluster_panel, "palette": "active"},
                {**aggregator_cluster_panel, "palette": "active"},
                {**frequency_cluster_unit_panel("Clusters por unidade - Alunos prÃ³prios", own_cluster_base, own_month_counts, f"IDs da base ATIVOS_LTV classificados por visitas em {month_label}."), "palette": "active"},
                {**frequency_cluster_unit_panel("Clusters por unidade - Agregadores", aggregator_base, aggregator_month_counts, f"IDs Wellhub + TotalPass classificados por visitas em {month_label}."), "palette": "active"},
            ],
        }
        return partial_payload("frequencia", tab)

    if only_tab == "perfil":
        ids_active = int(active_ids[active_ids.ne("")].nunique())
        access_unique = int(access_ids[access_ids.ne("")].nunique()) if len(access_ids) else 0
        wellhub_ids = id_series(access.loc[access["canal"].eq("Wellhub"), "id_member"]) if not access.empty else pd.Series(dtype=str)
        totalpass_ids = id_series(access.loc[access["canal"].eq("TotalPass"), "id_member"]) if not access.empty else pd.Series(dtype=str)
        ids_wellhub = int(wellhub_ids[wellhub_ids.ne("")].nunique()) if len(wellhub_ids) else 0
        ids_totalpass = int(totalpass_ids[totalpass_ids.ne("")].nunique()) if len(totalpass_ids) else 0
        active_public_total = max(ids_active + ids_wellhub + ids_totalpass, 1)
        age_rows, mean_age = age_band_rows(active.get("dataNascimento", pd.Series(dtype=str)))
        profile_today = reference_date.normalize()
        profile_month_start = profile_today.replace(day=1)
        profile_charge_valid_mask = charge_ids.ne("") & charge_due.notna() & charge_value.fillna(0).gt(0)
        profile_current_due_mask = profile_charge_valid_mask & charge_due.ge(profile_month_start) & charge_due.lt(profile_today)
        profile_previous_due_mask = profile_charge_valid_mask & charge_due.lt(profile_month_start)
        profile_current_due_total = max(charge_ids[profile_current_due_mask].nunique(), 1)
        profile_previous_due_total = max(charge_ids[profile_previous_due_mask].nunique(), 1)
        profile_current_debt_ids = set(charge_ids[profile_current_due_mask & open_charge])
        profile_previous_debt_ids = set(charge_ids[profile_previous_due_mask & open_charge])
        profile_current_debt_pct = len(profile_current_debt_ids) / profile_current_due_total * 100
        profile_previous_debt_pct = len(profile_previous_debt_ids) / profile_previous_due_total * 100
        tab = {
            "cards": [
                card("Alunos com entradas registradas", br_int(access_unique), "alunos prÃ³prios + Wellhub + TotalPass", "green"),
                card("Idade mÃ©dia", f"{mean_age:.1f}".replace(".", ",") if mean_age else "0,0", "nascimentos vÃ¡lidos", "blue"),
                card("% de alunos prÃ³prios", br_pct(ids_active / active_public_total * 100), f"{br_int(ids_active)} IDs", "green"),
                card("% de Wellhub", br_pct(ids_wellhub / active_public_total * 100), f"{br_int(ids_wellhub)} IDs", "violet"),
                card("% de TotalPass", br_pct(ids_totalpass / active_public_total * 100), f"{br_int(ids_totalpass)} IDs", "orange"),
                card("% saldo devedor no mÃªs", br_pct(profile_current_debt_pct), f"{br_int(len(profile_current_debt_ids))} de {br_int(profile_current_due_total)} IDs vencidos atÃ© ontem", "red"),
                card("% saldo devedor anterior", br_pct(profile_previous_debt_pct), f"{br_int(len(profile_previous_debt_ids))} de {br_int(profile_previous_due_total)} IDs de meses anteriores", "orange"),
            ],
            "charts": [
                {"type": "bar", "title": "Faturamento mÃªs atual", "subtitle": "Parcelas recebidas + vendas do mÃªs mensalizadas + Wellhub/TotalPass com teto por ID.", "className": "chart-profile-revenue", "barTone": "green", "rows": revenue_by_unit_rows(sales.get("id_unidade", pd.Series(index=sales.index)), sales_value, sales.get("contrato", pd.Series(index=sales.index)), sales_dates, charges.get("filial", pd.Series(index=charges.index)), charge_status, charge_value, access, reference_date)},
                {"type": "collectionCombo", "title": "Sucesso na cobranÃ§a por unidade", "subtitle": "Competência até a data: barras = parcelas previstas; curva = parcelas recebidas.", "className": "chart-profile-charge-success", "palette": "active", "rows": charge_collection_unit_rows(charges["unidade_nome"], charge_status, charge_due, charge_value, reference_date)},
                {"type": "bar", "title": "RecuperaÃ§Ã£o de inadimplentes por unidade", "subtitle": "% de sucesso na cobranÃ§a de clientes de meses anteriores; valorCompet > 0.", "className": "chart-profile-recovery-success", "barTone": "blue", "maxValue": 100, "rows": charge_success_unit_rows(charges["unidade_nome"], charge_ids, charge_status, charge_due, charge_value, "previous", reference_date)},
                {"type": "columnBar", "title": "Dias de inadimplência", "subtitle": "Atrasos dia a dia até o 15º; depois agrupados em faixas.", "className": "chart-profile-delinquency-days", "palette": "active", "rows": delinquency_day_column_rows(charge_days)},
            ],
        }
        return partial_payload("perfil", tab)

    current_charge_collection_rows = charge_collection_unit_rows(
        charges["unidade_nome"],
        charge_status,
        charge_due,
        charge_value,
        reference_date,
    )
    current_charge_success_rows = charge_success_unit_rows(
        charges["unidade_nome"],
        charge_ids,
        charge_status,
        charge_due,
        charge_value,
        "current",
        reference_date,
    )
    previous_charge_recovery_rows = charge_success_unit_rows(
        charges["unidade_nome"],
        charge_ids,
        charge_status,
        charge_due,
        charge_value,
        "previous",
        reference_date,
    )
    revenue_unit_chart_rows = revenue_by_unit_rows(
        sales.get("id_unidade", pd.Series(index=sales.index)),
        sales_value,
        sales.get("contrato", pd.Series(index=sales.index)),
        sales_dates,
        charges.get("filial", pd.Series(index=charges.index)),
        charge_status,
        charge_value,
        access,
        reference_date,
    )
    financial_extra_charts = [
        financial_revenue_filter_chart(financial_matrix),
        {"type": "collectionCombo", "title": "Sucesso na cobrança por unidade", "subtitle": "Competência até a data: barras = parcelas previstas; curva = parcelas recebidas.", "className": "chart-profile-charge-success", "palette": "active", "rows": current_charge_collection_rows},
        {"type": "bar", "title": "Recuperação de inadimplentes por unidade", "subtitle": "% de sucesso na cobrança de clientes de meses anteriores; valorCompet > 0.", "className": "chart-profile-recovery-success", "palette": "active", "maxValue": 100, "rows": previous_charge_recovery_rows},
        {"type": "columnBar", "title": "Dias de inadimplência", "subtitle": "Atrasos dia a dia até o 15º; depois agrupados em 16–22, 23–31, 32–45, 46–65 e 66+.", "className": "chart-profile-delinquency-days", "palette": "active", "rows": delinquency_day_column_rows(charge_days)},
    ]
    if only_tab == "financeiro":
        return partial_payload(
            "financeiro",
            financial_tab_payload(
                financial_matrix,
                charge_payment_rows,
                received_ticket_mean,
                received_ticket_count,
                financial_extra_charts,
            ),
        )
    sales_open_value_rows = open_sales_value_rows(sales_ids, sales_value, charge_ids, open_charge, charge_value)
    sales_success_rows = sales_success_unit_rows(sales["unidade_nome"], sales_ids, active_ids)
    contract_swap_chart_rows = contract_swap_rows(sales_ids, sales_dates, cancel_ids, cancel_dates, len(sales))
    churn_unit_chart_rows = churn_unit_rows(
        canc["unidade_nome"],
        cancel_ids,
        cancel_dates,
        cancel_start_dates,
        cancel_sale_ids,
        sales["unidade_nome"],
        sales_ids,
        sales_dates,
        sales_start_dates,
        sales_sale_ids,
        active["unidade_nome"],
        active_ids,
        active_days,
        reference_date,
        non_renewed.get("unidade_nome", pd.Series(dtype=str)),
        parse_date(non_renewed.get("DataFim", pd.Series(index=non_renewed.index, dtype=str))),
    )
    cancel_unit_chart_rows = cancellation_unit_multi_rows(canc.get("idBranch", pd.Series(dtype=str)).map(branch_name), cancel_dates, canc["motivo_limpo"])
    cancel_value_chart_rows = cancellation_value_rows(cancel_sale_ids, sales_sale_ids, sales_value)
    sales_ticket_received_rows = sales_ticket_received_unit_rows(
        sales["unidade_nome"],
        sales_value,
        sales.get("contrato", pd.Series(index=sales.index)),
        charges["unidade_nome"],
        charge_value,
        charge_status,
    )
    valid_birth = parse_date(active.get("dataNascimento"))
    age_rows, mean_age = age_band_rows(active.get("dataNascimento", pd.Series(dtype=str)))
    age_gender_data = age_gender_pyramid_data(
        active.get("dataNascimento", pd.Series(index=active.index, dtype=str)),
        active.get("sexo", pd.Series(index=active.index, dtype=str)),
    )

    access_total = len(access)
    access_unique = int(access_ids[access_ids.ne("")].nunique()) if len(access_ids) else 0
    unit_access_mask = access["canal"].eq("Unidade") if not access.empty else pd.Series(dtype=bool)
    aggregator_access_mask = ~unit_access_mask if not access.empty else pd.Series(dtype=bool)
    unit_access_count = int(unit_access_mask.sum()) if not access.empty else 0
    aggregator_access_count = int(aggregator_access_mask.sum()) if not access.empty else 0
    unit_access_ids = id_series(access.loc[unit_access_mask, "id_member"]) if not access.empty else pd.Series(dtype=str)
    aggregator_access_ids = id_series(access.loc[aggregator_access_mask, "id_member"]) if not access.empty else pd.Series(dtype=str)
    unit_access_unique = int(unit_access_ids[unit_access_ids.ne("")].nunique()) if len(unit_access_ids) else 0
    aggregator_access_unique = int(aggregator_access_ids[aggregator_access_ids.ne("")].nunique()) if len(aggregator_access_ids) else 0
    unit_access_mean = unit_access_count / max(unit_access_unique, 1)
    aggregator_access_mean = aggregator_access_count / max(aggregator_access_unique, 1)
    wellhub_ids = id_series(access.loc[access["canal"].eq("Wellhub"), "id_member"]) if not access.empty else pd.Series(dtype=str)
    totalpass_ids = id_series(access.loc[access["canal"].eq("TotalPass"), "id_member"]) if not access.empty else pd.Series(dtype=str)
    ids_wellhub = int(wellhub_ids[wellhub_ids.ne("")].nunique()) if len(wellhub_ids) else 0
    ids_totalpass = int(totalpass_ids[totalpass_ids.ne("")].nunique()) if len(totalpass_ids) else 0
    access_by_channel = top_rows(access.get("canal", pd.Series(dtype=str)), limit=5, total=max(access_total, 1)) if not access.empty else []
    access["unidade_nome"] = access.get("id_branch", pd.Series(index=access.index)).map(branch_name) if not access.empty else ""
    aggregator_unit_chart = aggregator_unique_unit_chart(
        access["unidade_nome"] if not access.empty else pd.Series(dtype=str),
        access.get("canal", pd.Series(index=access.index)) if not access.empty else pd.Series(dtype=str),
        access_ids,
    )
    access_day_rows = access_day_segment_rows(access_dates, access.get("canal", pd.Series(index=access.index)), 24) if not access.empty else []
    weekday_access_chart_rows = weekday_access_rows(access_dates) if not access.empty else []
    hourly_channel_rows, hourly_channel_insight = hourly_access_channel_rows(access_dates, access.get("canal", pd.Series(index=access.index))) if not access.empty else ([], "")
    access_daily_comparison_chart = access_daily_unit_comparison_chart(access["unidade_nome"], access_dates) if not access.empty else None
    latest_access_month = access_dates.dropna().dt.to_period("M").max() if not access_dates.dropna().empty else None
    if latest_access_month is not None and not access.empty:
        access_month_mask = access_dates.dt.to_period("M").eq(latest_access_month)
        month_label = f"{MONTH_ABBR.get(int(latest_access_month.month), str(latest_access_month.month).zfill(2))}/{latest_access_month.year}"
        own_month_counts = id_series(access.loc[access_month_mask & unit_access_mask, "id_member"]).value_counts()
        aggregator_month_counts = id_series(access.loc[access_month_mask & aggregator_access_mask, "id_member"]).value_counts()
    else:
        month_label = "mês atual"
        own_month_counts = pd.Series(dtype=int)
        aggregator_month_counts = pd.Series(dtype=int)
    own_cluster_panel = frequency_cluster_panel(
        "Clusters de entradas - Alunos próprios",
        active_ids,
        own_month_counts,
        f"Classificação por visitas em {month_label}; base ATIVOS_LTV.",
    )
    aggregator_cluster_panel = frequency_cluster_panel(
        "Clusters de entradas - Agregadores",
        aggregator_access_ids,
        aggregator_month_counts,
        f"Classificação por visitas em {month_label}; base Wellhub + TotalPass identificada.",
    )
    own_cluster_base = pd.DataFrame({
        "id": active_ids,
        "unit": active["unidade_nome"] if "unidade_nome" in active else pd.Series(index=active.index, dtype=str),
    })
    if not access.empty:
        aggregator_base = pd.DataFrame({
            "id": aggregator_access_ids,
            "unit": access.loc[aggregator_access_mask, "unidade_nome"],
            "date": access_dates.loc[aggregator_access_mask],
        })
        aggregator_base = (
            aggregator_base[aggregator_base["id"].ne("") & aggregator_base["unit"].notna()]
            .sort_values("date")
            .drop_duplicates("id", keep="last")
        )
    else:
        aggregator_base = pd.DataFrame(columns=["id", "unit"])
    own_cluster_unit_panel = frequency_cluster_unit_panel(
        "Clusters por unidade - Alunos próprios",
        own_cluster_base,
        own_month_counts,
        f"IDs da base ATIVOS_LTV classificados por visitas em {month_label}.",
    )
    aggregator_cluster_unit_panel = frequency_cluster_unit_panel(
        "Clusters por unidade - Agregadores",
        aggregator_base,
        aggregator_month_counts,
        f"IDs Wellhub + TotalPass classificados por visitas em {month_label}.",
    )

    active_with_access = int((active_access_month.fillna(0) > 0).sum())
    debt_clients = int(open_charge.sum())
    debt_value = float(charge_value[open_charge].sum()) if len(charge_value) else 0
    cancel_with_debt = int((cancel_debt.fillna(0) > 0).sum())
    ids_sales = int(sales_ids[sales_ids.ne("")].nunique())
    ids_active = int(active_ids[active_ids.ne("")].nunique())
    ids_cancel = int(cancel_ids[cancel_ids.ne("")].nunique())
    ids_charge = int(charge_ids[charge_ids.ne("")].nunique())
    active_id_set = set(active_ids[active_ids.ne("")])
    cancel_id_set = set(cancel_ids[cancel_ids.ne("")])
    canceled_still_active = len(cancel_id_set & active_id_set)
    overdue_charge = open_charge & charge_value.fillna(0).gt(0) & charge_days.fillna(0).gt(0)
    inadimplente_ids = active_id_set & set(charge_ids[overdue_charge & charge_ids.ne("")])
    adimplente_ids = active_id_set - inadimplente_ids
    adimplentes = len(adimplente_ids)
    inadimplentes = len(inadimplente_ids)
    adimplentes_pct = adimplentes / max(ids_active, 1) * 100
    inadimplentes_pct = inadimplentes / max(ids_active, 1) * 100
    active_days_mean = active_days[active_days >= 0].mean()
    active_public_total = max(adimplentes + inadimplentes + ids_wellhub + ids_totalpass, 1)
    profile_today = reference_date.normalize()
    profile_month_start = profile_today.replace(day=1)
    profile_charge_valid_mask = (
        charge_ids.ne("")
        & charge_due.notna()
        & charge_value.fillna(0).gt(0)
    )
    profile_current_due_mask = (
        profile_charge_valid_mask
        & charge_due.ge(profile_month_start)
        & charge_due.lt(profile_today)
    )
    profile_previous_due_mask = profile_charge_valid_mask & charge_due.lt(profile_month_start)
    profile_current_due_total = max(charge_ids[profile_current_due_mask].nunique(), 1)
    profile_previous_due_total = max(charge_ids[profile_previous_due_mask].nunique(), 1)
    profile_current_debt_ids = set(charge_ids[
        profile_current_due_mask
        & open_charge
    ])
    profile_previous_debt_ids = set(charge_ids[
        profile_previous_due_mask
        & open_charge
    ])
    profile_current_debt_pct = len(profile_current_debt_ids) / profile_current_due_total * 100
    profile_previous_debt_pct = len(profile_previous_debt_ids) / profile_previous_due_total * 100
    sales_ticket_mean, sales_ticket_count = sales_ticket_average(
        sales_value,
        sales.get("contrato", pd.Series(index=sales.index)),
    )
    received_charge_mask = charge_status.map(norm_key).eq("recebido") & charge_value.fillna(0).gt(0)
    received_ticket_mean = float(charge_value[received_charge_mask].mean()) if received_charge_mask.any() else 0.0
    received_ticket_count = int(received_charge_mask.sum())
    sv_plus_sales = int(sales["contrato_norm"].eq("SV Plus").sum())
    sv_plus_sales_pct = sv_plus_sales / max(len(sales), 1) * 100
    sales_scope_ticket_mean, sales_scope_ticket_count = sales_ticket_average(
        sales_scope_values,
        sales_scope.get("contrato", pd.Series(index=sales_scope.index)),
    )
    sales_scope_sv_plus = int(sales_scope["contrato_norm"].eq("SV Plus").sum())
    sales_scope_sv_plus_pct = sales_scope_sv_plus / max(len(sales_scope), 1) * 100
    sales_scope_checkout_count = int(checkout_paid_mask.sum())
    sales_scope_yesterday, sales_scope_yesterday_metric, sales_scope_yesterday_status = previous_day_sales_indicator(
        sales_scope_dates,
        period_end or reference_date,
    )
    _, active_sv_plus_pct = active_plan_share(active)
    sales_scope_ticket_status = "good" if sales_scope_ticket_mean >= SV_PLAN_REFERENCE_PRICE else "bad"
    sales_scope_ticket_metric = "↑ acima da referência" if sales_scope_ticket_status == "good" else "↓ abaixo da referência"

    overview_cards = [
        card("Alunos ativos", br_int(active_total), "", "green"),
        card("Vendas", br_int(len(sales)), f"{br_int(ids_sales)} IDs únicos", "blue"),
        card("Cancelamentos", br_int(len(canc)), f"{br_int(ids_cancel)} IDs únicos", "red"),
        card("Acessos", br_int(access_total), f"{br_int(access_unique)} IDs únicos", "orange"),
    ]

    tabs = {
        "ativos": {
            "cards": [
                card("Alunos ativos", br_int(active_total), "", "green"),
                card("Ticket médio mensal", br_money(active_value[active_value > 0].mean()), "valorCompetencia > 0", "blue"),
                card("Média dias ativos", f"{active_days[active_days >= 0].mean():.1f}".replace(".", ","), "diasAtivo", "orange"),
                card("Com acesso no mês", br_int(active_with_access), f"{br_pct(active_with_access / max(len(active), 1) * 100)} dos ativos", "violet"),
            ],
            "charts": [
                active_goal_chart,
                {"type": "bar", "title": "Ativos por contrato", "className": "chart-active-contract compact", "barTone": "blue", "rows": top_rows(active["contrato_norm"], 10, len(active))},
                {"type": "columnBar", "title": "Distribuição por sexo", "className": "chart-profile-gender compact", "rowTones": ["green", "blue", "orange"], "showPct": True, "rows": gender_distribution_rows(active.get("sexo", pd.Series(dtype=str)))},
                {"type": "ageGenderPyramid", "title": "Faixa etária por sexo", "subtitle": "Homens à esquerda · mulheres à direita · percentuais sobre a base com idade e sexo identificados.", "subtitlePosition": "footer", "className": "chart-profile-age active-demographic-age", **age_gender_data},
            ],
        },
        "vendas": {
            "layout": "sales_summary",
            "ticker": sales_ticker,
            "cards": [
                card("Total de Contratos vendidos", br_int(len(sales_scope)), "", "blue", meta=f"Ontem: {br_int(sales_scope_yesterday)} vendas", metric=sales_scope_yesterday_metric, status=sales_scope_yesterday_status),
                card("Ticket Médio Vendido", br_money(sales_scope_ticket_mean), "", "orange", meta=f"Referência SV: {br_money(SV_PLAN_REFERENCE_PRICE)}", metric=sales_scope_ticket_metric, status=sales_scope_ticket_status, valueStatus=sales_scope_ticket_status),
                card("Check Out", br_int(sales_scope_checkout_count), "valor da venda igual à cobrança recebida", "green"),
                card("% de Vendas SV Plus", br_pct(sales_scope_sv_plus_pct), "", "violet", meta=f"{br_int(sales_scope_sv_plus)} contratos", metric=f"{br_pct(active_sv_plus_pct)} da base ativa", status="violet"),
                peak_sales_card(sales_scope_dates),
            ],
            "charts": [
                {"type": "columnBar", "title": "Vendas por mês", "subtitle": "Tabela VENDAS após exclusão de MyNutri e dos consultores bloqueados.", "className": "chart-sales-month", "palette": "active", "rows": month_rows(sales_history_dates)},
                {"type": "columnBar", "title": "Vendas totais por unidade", "subtitle": "Tabela VENDAS após exclusão de MyNutri e dos consultores bloqueados.", "className": "chart-sales-units unit-sales-columns", "palette": "active", "rows": unit_rows(qualified_unit_sales["unidade_nome"], len(qualified_unit_sales), medals=True)},
                {"type": "dualBar", "title": "Ticket médio venda x recebimento por unidade", "subtitle": "Recebimentos confirmados x vendas mensalizadas.", "className": "chart-sales-ticket dual-chart", "palette": "active", "primaryLabel": "Ticket recebido", "secondaryLabel": "Ticket venda", "rows": sales_ticket_received_unit_rows(sales_scope["unidade_nome"], sales_scope_values, sales_scope.get("contrato", pd.Series(index=sales_scope.index)), charges["unidade_nome"], charge_value, charge_status)},
                {"type": "donut", "title": "Contratos vendidos no mês", "subtitle": f"Participação dos contratos vendidos em {sales_scope_label}", "className": "chart-sales-contracts", "palette": "active", "rows": top_rows(sales_scope["contrato_norm"], 10, len(sales_scope))},
                sales_growth_chart,
            ],
        },
        "cancelamentos": {
            "layout": "cancel_summary",
            "cards": [
                card("Contratos Cancelados", br_int(len(canc)), f"{cancel_scope_label} · exclui IDs ainda ativos", "wellhub"),
                card("Clientes Cancelados", br_int(ids_cancel), "clientes únicos", "activeBlue"),
                card("Média de meses Ativos", f"{(cancel_days[cancel_days >= 0].mean() / 30):.1f}".replace(".", ",") if pd.notna(cancel_days[cancel_days >= 0].mean()) else "0,0", "diasAtivos / 30", "activeCyan"),
                card("Inativados com saldo Devedor", br_int(cancel_with_debt), f"{br_pct(cancel_with_debt / max(len(canc), 1) * 100)} da base", "activeTeal"),
                card("NÃO RENOVADOS", br_int(len(non_renewed)), "contratos no período", "activeGreen"),
            ],
            "charts": [
                {"type": "columnBar", "title": "Cancelamentos por mês", "subtitle": "Histórico comparativo entre inadimplência e cancelamentos solicitados.", "className": "chart-cancel-month chart-sales-month grouped-month-chart", "palette": "cancellation", "rows": cancel_month_reason_rows(cancel_history_dates, cancel_history["motivo_limpo"])},
                {"type": "donut", "title": "Cancelamentos por contrato", "subtitle": f"Participação dos contratos cancelados em {cancel_scope_label}.", "className": "chart-cancel-contracts", "palette": "cancellation", "rows": top_rows(canc["contrato_norm"], 10, len(canc))},
                {"type": "stackedColumn", "title": "Cancelamentos por unidade", "subtitle": "Cancelamentos solicitados, inadimplência e não renovados no período.", "className": "chart-cancel-units", "palette": "cancellation", "rows": cancellation_unit_column_rows(canc.get("idBranch", pd.Series(dtype=str)).map(branch_name), cancel_dates, canc["motivo_limpo"], non_renewed.get("unidade_nome", pd.Series(dtype=str)))},
                {"type": "bar", "title": "Churn por unidade", "subtitle": "Cancelamentos + não renovados / base ativa estimada no dia anterior ao início do mês.", "className": "chart-cancel-churn compact", "palette": "cancellation", "rows": churn_unit_chart_rows},
                {"type": "bar", "title": "Motivos de cancelamento", "className": "chart-cancel-reasons", "palette": "cancellation", "rows": top_rows(canc["motivo_limpo"], 12, len(canc))},
            ],
        },
        "financeiro": financial_tab_payload(
            financial_matrix,
            charge_payment_rows,
            received_ticket_mean,
            received_ticket_count,
            financial_extra_charts,
        ),
        "frequencia": {
            "layout": "frequency_summary",
            "cards": [
                card("Quantidade de Acessos", br_int(access_total), "Unidade + Wellhub + TotalPass", "activeBlue"),
                card("Quantidade de clientes com acesso", br_int(access_unique), "IDs únicos identificados", "activeCyan"),
                card("Acesso Alunos Próprios", br_int(unit_access_count), f"{br_int(unit_access_unique)} clientes únicos", "activeTeal"),
                card("Acesso Agregadores", br_int(aggregator_access_count), f"{br_int(aggregator_access_unique)} clientes únicos", "activeGreen"),
                card("Média de Acessos Alunos Próprios", f"{unit_access_mean:.1f}".replace(".", ","), "acessos / clientes únicos", "activeCyan"),
                card("Média de Acessos Agregadores", f"{aggregator_access_mean:.1f}".replace(".", ","), "acessos / clientes únicos", "activeGreen"),
            ],
            "charts": [
                {"type": "dualBar", "title": "LTV média x mediana por plano", "className": "chart-ltv-plan dual-chart", "palette": "active", "rows": ltv_month_rows(active["contrato_norm"], active_days, limit=10)},
                {"type": "dualBar", "title": "LTV média x mediana por unidade", "className": "chart-ltv-unit dual-chart", "palette": "active", "rows": ltv_month_rows(active["unidade_nome"], active_days, order=UNIT_ORDER, medals=True)},
                {"type": "columnBar", "title": "Acessos por dia", "subtitle": "Barras por alunos próprios e agregadores, com dia da semana no rótulo.", "className": "chart-access-day chart-sales-month grouped-day-chart", "palette": "active", "rows": access_day_rows},
                {"type": "donut", "title": "Distribuição por dia da semana", "subtitle": "Participação dos acessos de segunda a domingo.", "className": "chart-weekday-access", "palette": "active", "rows": weekday_access_chart_rows},
                {"type": "multiBar", "title": "Entradas por horário", "subtitle": "Média diária por horário, separada por alunos próprios, Wellhub e TotalPass.", "className": "chart-access-hour multi-chart", "palette": "active", "rows": hourly_channel_rows},
            ] + ([{**access_daily_comparison_chart, "palette": "active"}] if access_daily_comparison_chart else []) + [
                {**own_cluster_panel, "palette": "active"},
                {**aggregator_cluster_panel, "palette": "active"},
                {**own_cluster_unit_panel, "palette": "active"},
                {**aggregator_cluster_unit_panel, "palette": "active"},
            ],
        },
        "perfil": {
            "cards": [
                card("Alunos com entradas registradas", br_int(access_unique), "alunos próprios + Wellhub + TotalPass", "green"),
                card("Idade média", f"{mean_age:.1f}".replace(".", ",") if mean_age else "0,0", "nascimentos válidos", "blue"),
                card("% de alunos próprios", br_pct(ids_active / active_public_total * 100), f"{br_int(ids_active)} IDs", "green"),
                card("% de Wellhub", br_pct(ids_wellhub / active_public_total * 100), f"{br_int(ids_wellhub)} IDs", "violet"),
                card("% de TotalPass", br_pct(ids_totalpass / active_public_total * 100), f"{br_int(ids_totalpass)} IDs", "orange"),
                card("% saldo devedor no mês", br_pct(profile_current_debt_pct), f"{br_int(len(profile_current_debt_ids))} de {br_int(profile_current_due_total)} IDs vencidos até ontem", "red"),
                card("% saldo devedor anterior", br_pct(profile_previous_debt_pct), f"{br_int(len(profile_previous_debt_ids))} de {br_int(profile_previous_due_total)} IDs de meses anteriores", "orange"),
            ],
            "charts": [
                {"type": "bar", "title": "Faturamento mês atual", "subtitle": "Parcelas recebidas + vendas do mês mensalizadas + Wellhub/TotalPass com teto por ID.", "className": "chart-profile-revenue", "barTone": "green", "rows": revenue_unit_chart_rows},
                {"type": "collectionCombo", "title": "Sucesso na cobrança por unidade", "subtitle": "Competência até a data: barras = parcelas previstas; curva = parcelas recebidas.", "className": "chart-profile-charge-success", "palette": "active", "rows": current_charge_collection_rows},
                {"type": "bar", "title": "Recuperação de inadimplentes por unidade", "subtitle": "% de sucesso na cobrança de clientes de meses anteriores; valorCompet > 0.", "className": "chart-profile-recovery-success", "barTone": "blue", "maxValue": 100, "rows": previous_charge_recovery_rows},
                {"type": "columnBar", "title": "Dias de inadimplência", "subtitle": "Atrasos dia a dia até o 15º; depois agrupados em faixas.", "className": "chart-profile-delinquency-days", "palette": "active", "rows": delinquency_day_column_rows(charge_days)},
            ],
        },
    }

    tabs.pop("perfil", None)
    source = source_label or (", ".join(path.name for path in paths.values()) if workbook_path else "CSVs padrão em Downloads/CSV")
    tabs["cancelamentos"]["charts"].insert(0, cannibalization_chart)
    tabs["cancelamentos"]["charts"].append(churn_risk_chart)
    tabs["ativos"] = {
        "layout": "active_summary",
        "cards": [
            card("Alunos ativos", br_int(active_total), "", "green"),
            card("Adimplentes", br_int(adimplentes), f"{br_pct(adimplentes_pct)} da base ativa", "blue"),
            card("Inadimplentes", br_int(inadimplentes), f"{br_pct(inadimplentes_pct)} da base ativa", "red"),
            card("Média de dias ativo", f"{active_days_mean:.1f}".replace(".", ",") if pd.notna(active_days_mean) else "0,0", "diasAtivo", "orange"),
        ],
        "aggregatorCards": [
            card("Agregadores Wellhub", br_int(ids_wellhub), "IDs únicos em acessos Wellhub", "violet"),
            card("Agregadores TotalPass", br_int(ids_totalpass), "IDs únicos em acessos TotalPass", "orange"),
        ],
        "composition": {
            "title": "Base de ativos",
            "subtitle": "Distribuição entre adimplentes e inadimplentes",
            "rows": [
                {"label": "Adimplentes", "value": adimplentes, "pct": adimplentes_pct, "tone": "blue"},
                {"label": "Inadimplentes", "value": inadimplentes, "pct": inadimplentes_pct, "tone": "red"},
            ],
        },
        "charts": [
            active_goal_chart,
            {"type": "bar", "title": "Ativos por contrato", "className": "chart-active-contract compact", "barTone": "blue", "rows": top_rows(active["contrato_norm"], 10, len(active))},
            {"type": "columnBar", "title": "Distribuição por sexo", "className": "chart-profile-gender compact", "rowTones": ["green", "blue", "orange"], "showPct": True, "rows": gender_distribution_rows(active.get("sexo", pd.Series(dtype=str)))},
            {"type": "ageGenderPyramid", "title": "Faixa etária por sexo", "subtitle": "Homens à esquerda · mulheres à direita · percentuais sobre a base com idade e sexo identificados.", "subtitlePosition": "footer", "className": "chart-profile-age active-demographic-age", **age_gender_data},
        ],
    }
    tabs["ativos"]["composition"] = {
        "title": "Base ativa + agregadores",
        "subtitle": "",
        "rows": [
            {"label": "Adimplentes", "value": adimplentes, "pct": adimplentes / active_public_total * 100, "tone": "blue"},
            {"label": "Inadimplentes", "value": inadimplentes, "pct": inadimplentes / active_public_total * 100, "tone": "red"},
            {"label": "Wellhub", "value": ids_wellhub, "pct": ids_wellhub / active_public_total * 100, "tone": "violet"},
            {"label": "TotalPass", "value": ids_totalpass, "pct": ids_totalpass / active_public_total * 100, "tone": "orange"},
        ],
    }
    adimplentes_target_status = "good" if adimplentes_pct >= 90 else "bad"
    inadimplentes_target_status = "good" if inadimplentes_pct <= 10 else "bad"
    tabs["ativos"]["cards"] = [
        card("Alunos ativos", br_int(active_total), "", "green"),
        card("Adimplentes", br_int(adimplentes), "", "blue", metric=br_pct(adimplentes_pct), meta="Meta: 90%\u00a0da\u00a0base\u00a0ativa", status=adimplentes_target_status),
        card("Inadimplentes", br_int(inadimplentes), "", "red", metric=br_pct(inadimplentes_pct), meta="Meta: 10%\u00a0da\u00a0base\u00a0ativa", status=inadimplentes_target_status),
        card("Agregadores Wellhub", br_int(ids_wellhub), "Número de Agregadores com acesso", "violet"),
        card("Agregadores TotalPass", br_int(ids_totalpass), "Número de Agregadores com acesso", "orange"),
    ]
    tabs["ativos"]["aggregatorCards"] = []
    tabs["ativos"]["charts"] = [
        active_goal_chart,
        aggregator_unit_chart,
        {"type": "bar", "title": "Ativos por contrato", "className": "chart-active-contract compact", "barTone": "blue", "rows": top_rows(active["contrato_norm"], 10, len(active))},
        {"type": "columnBar", "title": "Distribuição por sexo", "className": "chart-profile-gender compact", "rowTones": ["green", "blue", "orange"], "showPct": True, "rows": gender_distribution_rows(active.get("sexo", pd.Series(dtype=str)))},
        {"type": "ageGenderPyramid", "title": "Faixa etária por sexo", "subtitle": "Homens à esquerda · mulheres à direita · percentuais sobre a base com idade e sexo identificados.", "subtitlePosition": "footer", "className": "chart-profile-age active-demographic-age", **age_gender_data},
    ]
    tabs["ativos"]["footerCards"] = [
        card("Alunos com entradas registradas", br_int(access_unique), "alunos próprios + Wellhub + TotalPass", "green"),
        card("Idade média", f"{mean_age:.1f}".replace(".", ",") if mean_age else "0,0", "nascimentos válidos", "blue"),
        card("Média de dias Ativos", f"{active_days_mean:.1f}".replace(".", ",") if pd.notna(active_days_mean) else "0,0", "diasAtivo", "orange"),
        card("% de alunos próprios", br_pct(ids_active / active_public_total * 100), f"{br_int(ids_active)} IDs", "green"),
        card("% de Wellhub", br_pct(ids_wellhub / active_public_total * 100), f"{br_int(ids_wellhub)} IDs", "violet"),
        card("% de TotalPass", br_pct(ids_totalpass / active_public_total * 100), f"{br_int(ids_totalpass)} IDs", "orange"),
    ]
    star_board = medal_board_rows(tabs)
    analysis_matrix = build_analysis_unit_matrix(
        tabs,
        active,
        charges,
        access,
        churn_risk_chart,
        reference_date,
        selected_units,
    )
    analysis_matrix["history"] = analysis_matrix_history(analysis_matrix, period_start, period_end)
    analysis_alerts = build_analysis_unit_alerts(analysis_matrix)
    tabs["isaias"] = build_isaias_tab(
        active_total,
        adimplentes,
        inadimplentes,
        adimplentes_pct,
        inadimplentes_pct,
        len(sales_scope),
        int(sales_scope_ids[sales_scope_ids.ne("")].nunique()),
        len(canc),
        ids_cancel,
        access_total,
        access_unique,
        unit_access_mean,
        aggregator_access_mean,
        sales_ticket_mean,
        received_ticket_mean,
        sv_plus_sales_pct,
        revenue_unit_chart_rows,
        sales_success_rows,
        churn_unit_chart_rows,
        charge_payment_rows,
    )
    history_info = analysis_matrix.get("history", {})
    tabs["isaias"]["cards"] = []
    tabs["isaias"]["indicatorMatrix"] = analysis_matrix
    tabs["isaias"]["unitAlerts"] = analysis_alerts
    tabs["isaias"]["executiveSummary"] = {
        "title": "Leitura executiva da rede",
        "body": (
            f"A rede reúne {br_int(active_total)} alunos ativos, {br_pct(adimplentes_pct)} adimplentes, "
            f"{br_int(len(sales_scope))} contratos vendidos, {br_int(len(canc))} cancelamentos e "
            f"{br_int(access_total)} acessos no recorte selecionado. A matriz abaixo consolida os indicadores "
            "das cinco áreas e destaca unidades que se afastam do comportamento da rede."
        ),
        "period": analysis_matrix.get("subtitle", ""),
        "history": (
            f"{br_int(history_info.get('captures', 0))} capturas no período"
            + (f" · primeira em {history_info.get('firstDate')} · última em {history_info.get('lastDate')}" if history_info.get("captures") else " · aguardando a primeira captura diária")
        ),
    }
    tabs["isaias"]["starBoard"] = star_board
    return {
        "sourceFile": source,
        "sourcePath": prepared.get("sourcePath", str(Path(workbook_path) if workbook_path else DEFAULT_CSV_DIR)),
        "filters": filter_state,
        "filterOptions": {
            "units": UNIT_ORDER,
            "ageBands": AGE_BAND_LABELS,
            "genders": GENDER_FILTER_OPTIONS,
        },
        "tabs": tabs,
        "overview": {"cards": []},
        "validation": validation,
        "medalBoard": star_board,
    }


def build_html(payload: dict) -> str:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    template = """<!doctype html>
<html lang="pt-BR" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>BioFisic Analytics</title>
  <style>
    :root {
      --bg: #061012;
      --panel: rgba(18, 30, 32, .94);
      --panel-2: rgba(9, 19, 21, .92);
      --green: #00f529;
      --wellhub: #d8385e;
      --blue: #38a3ff;
      --red: #ff5049;
      --orange: #ffbd14;
      --violet: #b56cff;
      --muted: #b9c8d4;
      --ink: #f7fbff;
      --line: rgba(0, 255, 48, .24);
      --radius: 10px;
      --shadow: 0 18px 42px rgba(0,0,0,.24);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background:
        linear-gradient(rgba(0, 245, 41, .045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 245, 41, .045) 1px, transparent 1px),
        radial-gradient(circle at 72% 8%, rgba(0, 245, 41, .16), transparent 28%),
        var(--bg);
      background-size: 80px 80px, 80px 80px, auto, auto;
    }
    .topbar {
      position: sticky;
      top: 0;
      z-index: 5;
      min-height: 72px;
      padding: 10px 18px;
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) auto minmax(0, 1fr);
      gap: 12px;
      align-items: center;
      border-bottom: 1px solid var(--line);
      background: rgba(33, 36, 35, .96);
      backdrop-filter: blur(12px);
    }
    .brand {
      grid-column: 2;
      justify-self: center;
      display: flex;
      align-items: center;
      min-width: 120px;
      pointer-events: none;
    }
    .brand img {
      width: 108px;
      max-height: 44px;
      object-fit: contain;
      filter: drop-shadow(0 0 14px rgba(0, 245, 41, .3));
    }
    .tabs {
      grid-column: 1;
      justify-self: start;
      display: flex;
      gap: 6px;
      min-width: 0;
      overflow-x: auto;
      scrollbar-width: none;
    }
    .tabs::-webkit-scrollbar { display: none; }
    .tabs button, .print-btn, .analyze-btn, .file-button {
      border: 1px solid rgba(0, 255, 48, .34);
      border-radius: 8px;
      min-height: 34px;
      padding: 8px 10px;
      font-weight: 900;
      cursor: pointer;
      white-space: nowrap;
    }
    .tabs button {
      color: var(--muted);
      background: rgba(9, 18, 20, .86);
    }
    .tabs button.active, .tabs button:hover {
      color: #031007;
      background: var(--green);
      border-color: var(--green);
      box-shadow: 0 0 18px rgba(0, 245, 41, .3);
    }
    .top-actions {
      grid-column: 3;
      justify-self: end;
      display: flex;
      align-items: center;
      justify-content: end;
      gap: 6px;
      min-width: 0;
    }
    .top-actions input[type="file"] {
      position: absolute;
      inline-size: 0;
      block-size: 0;
      opacity: 0;
      pointer-events: none;
      overflow: hidden;
    }
    .header-upload {
      display: flex;
      align-items: center;
      gap: 6px;
      min-width: 0;
      max-width: min(48vw, 660px);
      padding: 6px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: rgba(7, 16, 18, .76);
    }
    .file-button, .analyze-btn, .print-btn {
      color: #031007;
      background: var(--green);
      border-color: var(--green);
    }
    .header-upload-status {
      min-width: 88px;
      max-width: 180px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .header-upload-status.ok { color: var(--green); }
    .header-upload-status.error { color: #ff9c95; }
    .shell {
      width: min(1500px, calc(100vw - 34px));
      margin: 0 auto;
      padding: 22px 0 48px;
    }
    .hero {
      display: grid;
      grid-template-columns: minmax(420px, 440px) minmax(0, 1fr);
      gap: 18px;
      align-items: center;
      margin-bottom: 18px;
      padding: 16px 18px;
      border: 3px solid var(--green);
      border-radius: 18px;
      background: linear-gradient(135deg, rgba(30, 36, 36, .96), rgba(16, 24, 27, .94));
      box-shadow: 0 0 0 1px rgba(0, 255, 48, .24), 0 0 36px rgba(0, 245, 41, .13);
    }
    .hero-title {
      min-width: 0;
    }
    h1 {
      margin: 0;
      text-transform: uppercase;
      white-space: normal;
    }
    .brand-word {
      display: block;
      color: var(--green);
      font-size: clamp(27px, 2vw, 38px);
      font-style: normal;
      font-weight: 950;
      line-height: .95;
      letter-spacing: -.035em;
      text-shadow: 0 0 18px rgba(0,245,41,.32);
    }
    .brand-sub {
      display: block;
      margin-top: 5px;
      color: #d6e2e7;
      font-size: 13px;
      font-style: normal;
      font-weight: 650;
      line-height: 1;
      letter-spacing: .16em;
    }
    .source {
      margin-top: 8px;
      color: var(--muted);
      font-weight: 700;
      font-size: 12px;
      line-height: 1.25;
    }
    .dashboard-filters {
      display: grid;
      grid-template-columns: minmax(180px, .9fr) minmax(135px, 1fr) minmax(128px, .9fr) 104px 118px;
      gap: 8px;
      align-items: end;
      justify-self: end;
      width: 100%;
      min-width: 0;
    }
    .filter-field {
      display: grid;
      gap: 4px;
      min-width: 0;
    }
    .filter-field span {
      color: var(--green);
      font-size: 9px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .filter-field input:not([type="checkbox"]),
    .filter-field select {
      width: 100%;
      min-height: 32px;
      border: 1px solid rgba(0, 255, 48, .32);
      border-radius: 8px;
      padding: 6px 7px;
      color: #061012;
      background: #f5f7f4;
      font-weight: 900;
      font-size: 11px;
      outline: none;
    }
    .filter-field input:not([type="checkbox"]):focus,
    .filter-field select:focus {
      border-color: var(--green);
      box-shadow: 0 0 0 3px rgba(0, 245, 41, .18);
    }
    .multi-select {
      position: relative;
      min-width: 0;
    }
    .multi-select-toggle {
      width: 100%;
      min-height: 32px;
      border: 1px solid rgba(0, 255, 48, .32);
      border-radius: 8px;
      padding: 6px 28px 6px 8px;
      color: #061012;
      background: #f5f7f4;
      font-size: 11px;
      font-weight: 950;
      text-align: left;
      cursor: pointer;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      position: relative;
    }
    .multi-select-toggle::after {
      content: "▾";
      position: absolute;
      right: 9px;
      top: 50%;
      transform: translateY(-50%);
      color: #061012;
      font-size: 10px;
    }
    .multi-select-toggle:focus {
      border-color: var(--green);
      box-shadow: 0 0 0 3px rgba(0, 245, 41, .18);
      outline: none;
    }
    .multi-select-menu {
      position: absolute;
      z-index: 50;
      top: calc(100% + 6px);
      left: 0;
      right: 0;
      max-height: 250px;
      overflow: auto;
      padding: 6px;
      border: 1px solid rgba(0, 255, 48, .38);
      border-radius: 10px;
      background: rgba(7, 16, 18, .98);
      box-shadow: 0 18px 44px rgba(0, 0, 0, .38);
    }
    .multi-option {
      display: flex;
      align-items: center;
      gap: 7px;
      padding: 7px 6px;
      border-radius: 7px;
      color: var(--text);
      font-size: 11px;
      font-weight: 850;
      cursor: pointer;
      white-space: nowrap;
    }
    .multi-option:hover {
      background: rgba(0, 245, 41, .12);
    }
    .multi-option input {
      width: 13px;
      height: 13px;
      accent-color: var(--green);
      flex: 0 0 auto;
    }
    .filter-popup-backdrop {
      position: fixed;
      inset: 0;
      z-index: 120;
      display: grid;
      place-items: center;
      padding: 24px;
      background: rgba(0, 0, 0, .62);
      backdrop-filter: blur(8px);
    }
    .filter-popup-backdrop[hidden] {
      display: none;
    }
    .filter-popup {
      width: min(520px, calc(100vw - 32px));
      max-height: min(680px, calc(100vh - 48px));
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      border: 1px solid rgba(0, 245, 41, .42);
      border-radius: 18px;
      background: rgba(8, 18, 20, .98);
      box-shadow: 0 28px 90px rgba(0, 0, 0, .56), 0 0 30px rgba(0, 245, 41, .16);
      overflow: hidden;
    }
    .filter-popup-head,
    .filter-popup-actions {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 16px 18px;
      border-bottom: 1px solid rgba(0, 245, 41, .18);
    }
    .filter-popup-actions {
      border-top: 1px solid rgba(0, 245, 41, .18);
      border-bottom: 0;
      justify-content: flex-end;
    }
    .filter-popup h2 {
      margin: 0;
      color: var(--green);
      font-size: 18px;
      text-transform: uppercase;
    }
    .filter-popup-close,
    .filter-popup-clear,
    .filter-popup-apply {
      min-height: 36px;
      border-radius: 10px;
      border: 1px solid rgba(0, 245, 41, .36);
      padding: 8px 12px;
      color: var(--ink);
      background: rgba(9, 18, 20, .92);
      font-weight: 950;
      cursor: pointer;
    }
    .filter-popup-close {
      width: 38px;
      padding: 0;
      font-size: 22px;
      line-height: 1;
    }
    .filter-popup-apply {
      color: #031007;
      border-color: var(--green);
      background: var(--green);
    }
    .filter-popup-list {
      display: grid;
      gap: 8px;
      padding: 14px;
      overflow: auto;
    }
    .filter-popup-option {
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 40px;
      padding: 10px 12px;
      border: 1px solid rgba(0, 245, 41, .16);
      border-radius: 10px;
      color: var(--ink);
      background: rgba(13, 29, 32, .8);
      font-size: 13px;
      font-weight: 850;
      cursor: pointer;
    }
    .filter-popup-option:hover {
      border-color: rgba(0, 245, 41, .42);
      background: rgba(0, 245, 41, .11);
    }
    .filter-popup-option input {
      width: 16px;
      height: 16px;
      accent-color: var(--green);
    }
    .filter-popup-date {
      display: grid;
      gap: 8px;
      padding: 4px;
    }
    .filter-popup-date span {
      color: var(--muted);
      font-size: 12px;
      font-weight: 850;
      text-transform: uppercase;
    }
    .filter-popup-date input {
      min-height: 46px;
      border: 1px solid rgba(0, 245, 41, .34);
      border-radius: 12px;
      padding: 10px 12px;
      color: #071012;
      background: #f5f7f4;
      font-size: 16px;
      font-weight: 950;
      outline: none;
    }
    .filter-popup-date input:focus {
      border-color: var(--green);
      box-shadow: 0 0 0 3px rgba(0, 245, 41, .18);
    }
    .period-range-fields {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .date-calendar {
      display: grid;
      gap: 14px;
      padding: 4px;
      color: var(--ink);
    }
    .date-calendar-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 12px;
      border: 1px solid rgba(0, 245, 41, .2);
      border-radius: 14px;
      background: rgba(13, 29, 32, .82);
    }
    .date-calendar-title {
      display: grid;
      gap: 2px;
      text-align: center;
      font-weight: 950;
      text-transform: uppercase;
    }
    .date-calendar-title strong {
      color: var(--green);
      font-size: 15px;
    }
    .date-calendar-title span {
      color: var(--muted);
      font-size: 11px;
    }
    .date-calendar-nav {
      width: 38px;
      height: 38px;
      border: 1px solid rgba(0, 245, 41, .34);
      border-radius: 12px;
      color: var(--green);
      background: rgba(5, 14, 16, .94);
      font-size: 20px;
      font-weight: 950;
      cursor: pointer;
    }
    .date-calendar-week,
    .date-calendar-grid {
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 7px;
    }
    .date-calendar-week span {
      color: var(--muted);
      font-size: 10px;
      font-weight: 950;
      text-align: center;
      text-transform: uppercase;
    }
    .date-calendar-day,
    .date-calendar-empty {
      min-height: 42px;
      border-radius: 12px;
    }
    .date-calendar-day {
      border: 1px solid rgba(0, 245, 41, .16);
      color: var(--ink);
      background: rgba(13, 29, 32, .78);
      font-size: 13px;
      font-weight: 950;
      cursor: pointer;
      transition: transform .16s ease, border-color .16s ease, background .16s ease;
    }
    .date-calendar-day:hover {
      transform: translateY(-1px);
      border-color: rgba(0, 245, 41, .58);
      background: rgba(0, 245, 41, .14);
    }
    .date-calendar-day.is-today {
      border-color: rgba(56, 163, 255, .74);
      box-shadow: inset 0 0 0 1px rgba(56, 163, 255, .4);
    }
    .date-calendar-day.is-selected {
      color: #031007;
      border-color: var(--green);
      background: var(--green);
      box-shadow: 0 0 18px rgba(0, 245, 41, .28);
    }
    .date-calendar-note {
      color: var(--muted);
      font-size: 11px;
      font-weight: 750;
      text-align: center;
    }
    .apply-filters-btn {
      min-height: 32px;
      border: 1px solid var(--green);
      border-radius: 8px;
      padding: 6px 8px;
      color: #031007;
      background: var(--green);
      font-weight: 950;
      font-size: 11px;
      cursor: pointer;
      white-space: nowrap;
      box-shadow: 0 0 18px rgba(0, 245, 41, .22);
    }
    .overview {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin: 14px 0 20px;
    }
    .tab-panel { display: none; }
    .tab-panel.active { display: grid; gap: 14px; }
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(205px, 1fr));
      gap: 10px;
    }
    .sales-live-ticker {
      min-width: 0;
      min-height: 46px;
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      align-items: stretch;
      overflow: hidden;
      border: 1px solid rgba(0, 245, 41, .38);
      border-radius: 12px;
      background: linear-gradient(90deg, rgba(0, 245, 41, .11), rgba(7, 21, 24, .96) 24%, rgba(7, 21, 24, .96));
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.025), 0 0 22px rgba(0,245,41,.06);
    }
    .sales-live-ticker-label {
      position: relative;
      z-index: 2;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 0 16px;
      color: #031007;
      background: var(--green);
      font-size: 11px;
      font-weight: 1000;
      letter-spacing: .05em;
      text-transform: uppercase;
      white-space: nowrap;
      box-shadow: 8px 0 18px rgba(0, 245, 41, .12);
    }
    .sales-live-ticker-pulse {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #031007;
      box-shadow: 0 0 0 0 rgba(3, 16, 7, .5);
      animation: sales-ticker-pulse 1.8s ease-out infinite;
    }
    .sales-live-ticker-viewport {
      min-width: 0;
      min-height: 54px;
      display: flex;
      align-items: center;
      overflow: hidden;
      mask-image: linear-gradient(90deg, transparent, #000 3%, #000 97%, transparent);
    }
    .sales-live-ticker-track {
      width: max-content;
      display: flex;
      align-items: center;
      will-change: transform;
      animation: sales-ticker-scroll 96s linear infinite;
    }
    .sales-live-ticker:hover .sales-live-ticker-track { animation-play-state: paused; }
    .sales-live-ticker-group {
      display: flex;
      align-items: center;
      gap: 42px;
      padding-right: 42px;
      white-space: nowrap;
    }
    .sales-live-ticker-item {
      position: relative;
      min-width: min(1030px, calc(100vw - 250px));
      display: grid;
      grid-template-columns: minmax(300px, 2.2fr) minmax(190px, 1.25fr) minmax(145px, .95fr) minmax(90px, .55fr) minmax(110px, .7fr);
      align-items: center;
      justify-items: center;
      gap: 22px;
      padding: 0 22px;
      color: var(--ink);
      font-size: 12px;
      font-weight: 800;
      text-align: center;
    }
    .sales-live-ticker-item::after {
      content: "◆";
      position: absolute;
      right: -24px;
      color: rgba(0, 245, 41, .55);
      font-size: 8px;
    }
    .sales-live-ticker-item > * {
      min-width: 0;
      width: 100%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      text-align: center;
    }
    .sales-live-ticker-contract { color: #d8e4e7; }
    .sales-live-ticker-seller { color: #b88cff; font-weight: 950; }
    .sales-live-ticker-unit { color: var(--green); font-weight: 950; }
    .sales-live-ticker-value { color: #ffc21c; font-weight: 1000; }
    .sales-live-ticker-date { color: #77d7ff; font-weight: 900; font-variant-numeric: tabular-nums; }
    @keyframes sales-ticker-scroll {
      from { transform: translateX(0); }
      to { transform: translateX(-50%); }
    }
    @keyframes sales-ticker-pulse {
      70% { box-shadow: 0 0 0 7px rgba(3, 16, 7, 0); }
      100% { box-shadow: 0 0 0 0 rgba(3, 16, 7, 0); }
    }
    @media (prefers-reduced-motion: reduce) {
      .sales-live-ticker-track,
      .sales-live-ticker-pulse { animation: none; }
      .sales-live-ticker-viewport { overflow-x: auto; mask-image: none; }
    }
    .active-summary {
      display: grid;
      grid-template-columns: minmax(0, 1.28fr) minmax(430px, .9fr);
      gap: 14px;
      align-items: stretch;
    }
    .active-card-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
      grid-auto-rows: 1fr;
    }
    .cards-2x2 {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .aggregator-cards {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
    }
    .aggregator-cards .card {
      min-height: 0;
    }
    .composition-panel {
      padding: 18px;
      display: grid;
      grid-template-columns: 190px minmax(0, 1fr);
      gap: 18px;
      align-items: center;
      min-height: 218px;
    }
    .composition-title {
      grid-column: 1 / -1;
      margin: 0 !important;
      text-align: center;
    }
    .donut {
      width: min(190px, 100%);
      aspect-ratio: 1;
      border-radius: 50%;
      background: conic-gradient(var(--donut));
      position: relative;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.06), 0 0 26px rgba(0,245,41,.12);
    }
    .chart-sales-contracts {
      grid-template-columns: 210px minmax(0, 1fr);
      gap: 30px;
    }
    .chart-sales-contracts .donut {
      width: min(210px, 100%);
    }
    .chart-sales-contracts:not(.expanded-chart-clone) .composition-copy {
      width: min(100%, 520px);
      justify-self: end;
    }
    .chart-sales-contracts:not(.expanded-chart-clone) .legend-row {
      column-gap: 10px;
    }
    .chart-sales-contracts:not(.expanded-chart-clone) .legend-row strong {
      min-width: 108px;
      text-align: right;
      font-variant-numeric: tabular-nums;
    }
    .chart-weekday-access:not(.expanded-chart-clone) .composition-copy {
      width: min(100%, 500px);
      justify-self: end;
    }
    .chart-weekday-access:not(.expanded-chart-clone) .legend-row {
      column-gap: 10px;
    }
    .chart-weekday-access:not(.expanded-chart-clone) .legend-row strong {
      min-width: 130px;
      text-align: right;
      font-variant-numeric: tabular-nums;
    }
    .donut::after {
      content: "";
      position: absolute;
      inset: 28%;
      border-radius: inherit;
      background: #071014;
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.04);
    }
    .composition-copy h2 {
      margin: 0 0 5px;
      font-size: 22px;
      line-height: 1.05;
    }
    .composition-copy p {
      margin: 0 0 14px;
      color: var(--muted);
      font-weight: 700;
      line-height: 1.35;
    }
    .composition-footer {
      grid-column: 1 / -1;
      margin: 0;
      padding-top: 10px;
      border-top: 1px solid rgba(151, 178, 190, .16);
      color: var(--muted);
      text-align: center;
      font-size: 11px;
      font-weight: 750;
    }
    .legend {
      display: grid;
      gap: 9px;
    }
    .legend-row {
      display: grid;
      grid-template-columns: 12px minmax(0, 1fr) auto;
      gap: 9px;
      align-items: center;
      font-size: 13px;
    }
    .dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--dot);
    }
    .legend-row strong {
      white-space: nowrap;
    }
    .isaias-shell {
      display: grid;
      gap: 14px;
      min-width: 0;
    }
    .analysis-executive {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      gap: 14px;
      padding: 20px;
      min-height: 0;
    }
    .analysis-executive-copy h2 {
      margin: 0 0 10px;
      color: var(--green);
      font-size: clamp(24px, 2.2vw, 34px);
    }
    .analysis-executive-copy p {
      margin: 0;
      max-width: 100ch;
      color: var(--ink);
      font-size: 15px;
      font-weight: 750;
      line-height: 1.55;
    }
    .analysis-period-note,
    .analysis-history-note {
      display: block;
      margin-top: 10px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 850;
    }
    .analysis-history-note { color: #79d8ff; }
    .analysis-alerts-panel,
    .analysis-matrix-panel,
    .analysis-observations-panel {
      min-height: 0;
      min-width: 0;
    }
    .analysis-alert-table-wrap {
      width: 100%;
      overflow: hidden;
      border-top: 1px solid rgba(206, 222, 232, .13);
    }
    .analysis-alert-table {
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
      font-size: 11px;
    }
    .analysis-alert-table th,
    .analysis-alert-table td {
      padding: 9px 8px;
      border-bottom: 1px solid rgba(206, 222, 232, .1);
      text-align: left;
      vertical-align: middle;
    }
    .analysis-alert-table th {
      color: #79d8ff;
      font-size: 9px;
      font-weight: 950;
      letter-spacing: .04em;
      text-transform: uppercase;
    }
    .analysis-alert-table th:nth-child(1) { width: 16%; }
    .analysis-alert-table th:nth-child(2) { width: 17%; }
    .analysis-alert-table th:nth-child(3),
    .analysis-alert-table th:nth-child(4) { width: 9%; text-align: right; }
    .analysis-alert-table th:nth-child(5) { width: 49%; }
    .analysis-alert-table td { color: var(--muted); font-weight: 800; }
    .analysis-alert-table td:nth-child(3),
    .analysis-alert-table td:nth-child(4) { text-align: right; color: var(--ink); }
    .analysis-alert-unit strong { color: var(--ink); }
    .analysis-alert-unit::before {
      content: "";
      display: inline-block;
      width: 7px;
      height: 7px;
      margin-right: 7px;
      border-radius: 50%;
      background: var(--alert-color);
    }
    .analysis-alert-table tr.attention { --alert-color: var(--red); }
    .analysis-alert-table tr.positive { --alert-color: var(--green); }
    .analysis-matrix-wrap {
      width: 100%;
      max-width: 100%;
      overflow-x: hidden;
      border: 1px solid rgba(206, 222, 232, .12);
      border-radius: 9px;
      background: rgba(3, 13, 16, .66);
    }
    .analysis-matrix {
      width: 100%;
      min-width: 0;
      table-layout: fixed;
      border-collapse: separate;
      border-spacing: 0;
      font-size: clamp(10px, .68vw, 12px);
    }
    .analysis-matrix th,
    .analysis-matrix td {
      min-width: 0;
      padding: 9px 3px;
      border-right: 1px solid rgba(206, 222, 232, .09);
      border-bottom: 1px solid rgba(206, 222, 232, .09);
      text-align: right;
      white-space: nowrap;
      overflow: hidden;
    }
    .analysis-matrix thead th {
      position: sticky;
      top: 0;
      z-index: 3;
      color: #dfffea;
      background: #12303a;
      font-size: clamp(10px, .64vw, 11px);
      text-transform: uppercase;
    }
    .analysis-matrix .analysis-indicator-cell,
    .analysis-matrix thead th:first-child {
      position: sticky;
      left: 0;
      z-index: 2;
      width: 18%;
      min-width: 0;
      max-width: none;
      color: var(--ink);
      background: #0d2024;
      text-align: left;
      white-space: normal;
    }
    .analysis-matrix thead th:first-child { z-index: 4; background: #12303a; }
    .analysis-matrix .network-column {
      color: var(--green);
      background: rgba(0,245,41,.07);
      font-weight: 950;
    }
    .analysis-matrix-section td {
      position: sticky;
      left: 0;
      z-index: 2;
      padding: 8px 10px;
      color: #6bc8ff;
      background: #153544;
      text-align: left;
      font-size: 12px;
      font-weight: 950;
      text-transform: uppercase;
      letter-spacing: .04em;
    }
    .analysis-matrix-value { display: block; color: var(--ink); font-weight: 900; line-height: 1.2; letter-spacing: -.025em; }
    .analysis-matrix-delta { display: block; margin-top: 4px; font-size: clamp(9px, .54vw, 10px); line-height: 1.15; font-weight: 900; }
    .analysis-matrix-delta.positive { color: var(--green); }
    .analysis-matrix-delta.negative { color: var(--red); }
    .analysis-matrix-delta.stable { color: #ffd11a; }
    .analysis-observation-list { display: grid; gap: 8px; }
    .analysis-observation-row {
      padding: 10px 12px;
      border-left: 0;
      border-bottom: 1px solid rgba(206, 222, 232, .11);
      border-radius: 0;
      background: transparent;
    }
    .analysis-observation-row strong { display: block; margin-bottom: 4px; color: var(--ink); }
    .analysis-observation-row p { margin: 0; color: var(--muted); font-size: 12px; font-weight: 750; line-height: 1.4; }
    .isaias-card-grid {
      grid-template-columns: repeat(5, minmax(0, 1fr));
    }
    .isaias-card-grid .card {
      min-height: 118px;
    }
    .isaias-card-grid .card strong {
      font-size: clamp(20px, 1.45vw, 28px);
      line-height: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .isaias-card-grid .card small {
      display: block;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .isaias-hero {
      display: none;
      grid-template-columns: minmax(0, 1.25fr) minmax(320px, .75fr);
      gap: 14px;
      align-items: stretch;
    }
    .isaias-copy {
      padding: 20px;
      border: 1px solid rgba(0, 245, 41, .48);
      border-radius: 12px;
      background: linear-gradient(135deg, rgba(18, 32, 32, .96), rgba(7, 18, 22, .94));
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.035), 0 0 28px rgba(0,245,41,.08);
    }
    .isaias-kicker {
      display: inline-flex;
      margin-bottom: 10px;
      color: var(--green);
      font-size: 11px;
      font-weight: 950;
      text-transform: uppercase;
      letter-spacing: 0;
    }
    .isaias-copy h2 {
      margin: 0 0 10px;
      color: var(--green);
      font-size: clamp(28px, 3vw, 48px);
      line-height: .96;
      font-style: italic;
      text-transform: uppercase;
    }
    .isaias-copy p {
      margin: 0;
      color: var(--muted);
      font-weight: 700;
      line-height: 1.45;
      max-width: 78ch;
    }
    .isaias-signals {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    .signal-card,
    .brief-card,
    .benchmark-card {
      border: 1px solid rgba(0, 245, 41, .28);
      border-left: 4px solid var(--tone, var(--green));
      border-radius: 10px;
      background: rgba(18, 27, 29, .92);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.025);
    }
    .signal-card {
      padding: 12px;
      min-height: 92px;
    }
    .signal-card span,
    .brief-card span {
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .signal-card strong {
      display: block;
      margin: 7px 0 5px;
      font-size: 17px;
      line-height: 1.12;
    }
    .signal-card small {
      color: #d8ecff;
      font-weight: 800;
      line-height: 1.25;
    }
    .isaias-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
      align-items: start;
    }
    .isaias-sources {
      display: none;
    }
    .brief-grid,
    .benchmark-grid {
      display: grid;
      gap: 10px;
    }
    .brief-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }
    .brief-card,
    .benchmark-card {
      padding: 14px;
    }
    .brief-card h3,
    .benchmark-card h3 {
      margin: 5px 0 8px;
      font-size: 18px;
      line-height: 1.15;
    }
    .brief-card p,
    .benchmark-card p {
      margin: 0;
      color: var(--muted);
      font-weight: 700;
      line-height: 1.45;
    }
    .benchmark-card a {
      display: inline-flex;
      margin-top: 9px;
      color: var(--green);
      font-weight: 900;
      text-decoration: none;
    }
    .isaias-chat {
      padding: 16px;
      width: 100%;
      order: -1;
    }
    .isaias-chat h2,
    .isaias-sources h2 {
      margin: 0 0 8px;
      font-size: 22px;
    }
    .isaias-chat p {
      margin: 0 0 12px;
      color: var(--muted);
      font-weight: 700;
      line-height: 1.4;
    }
    .isaias-chat > p:not(.source) {
      display: none;
    }
    .isaias-chat textarea {
      width: 100%;
      min-height: 150px;
      resize: vertical;
      border: 1px solid rgba(0, 245, 41, .32);
      border-radius: 10px;
      padding: 12px;
      background: #071014;
      color: var(--text);
      font: inherit;
      font-weight: 700;
      outline: none;
    }
    .isaias-chat textarea:focus {
      border-color: var(--green);
      box-shadow: 0 0 0 3px rgba(0,245,41,.13);
    }
    .isaias-chat button {
      margin-top: 10px;
      min-height: 38px;
      border: 1px solid var(--green);
      border-radius: 9px;
      padding: 8px 14px;
      background: var(--green);
      color: #031007;
      font-weight: 950;
      cursor: pointer;
    }
    .isaias-answer {
      margin-top: 12px;
      padding: 13px;
      border: 1px solid rgba(56, 163, 255, .28);
      border-radius: 10px;
      background: rgba(7, 16, 20, .9);
      color: #dfefff;
      font-weight: 700;
      line-height: 1.45;
      white-space: pre-wrap;
      min-height: 76px;
    }
    .isaias-answer.is-hidden {
      display: none;
    }
    .card, .panel {
      background: linear-gradient(145deg, rgba(28, 38, 40, .96), rgba(15, 24, 27, .96));
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    .progressive-loading-panel {
      min-height: 280px;
      display: grid;
      place-items: center;
      gap: 14px;
      padding: 42px;
      text-align: center;
    }
    .progressive-loading-spinner {
      width: 44px;
      height: 44px;
      border: 4px solid rgba(0, 245, 41, .16);
      border-top-color: var(--green);
      border-radius: 50%;
      animation: progressive-spin .85s linear infinite;
      box-shadow: 0 0 22px rgba(0, 245, 41, .24);
    }
    .progressive-loading-panel strong {
      color: var(--green);
      font-size: 17px;
      text-transform: uppercase;
    }
    .progressive-loading-panel small { color: var(--muted); }
    .progressive-loading-panel.is-error .progressive-loading-spinner {
      display: none;
    }
    .progressive-loading-panel.is-error strong {
      color: var(--red);
    }
    .progressive-loading-panel.is-error {
      min-height: 220px;
      align-content: center;
    }
    .progressive-load-retry {
      min-height: 40px;
      border: 1px solid rgba(0, 245, 41, .48);
      border-radius: 10px;
      padding: 9px 18px;
      background: rgba(0, 245, 41, .12);
      color: var(--green);
      font: inherit;
      font-weight: 900;
      cursor: pointer;
    }
    .progressive-load-retry:hover {
      background: var(--green);
      color: #031007;
    }
    @keyframes progressive-spin { to { transform: rotate(360deg); } }
    .card {
      min-height: 104px;
      padding: 14px 16px;
      display: grid;
      align-content: space-between;
      border-left: 4px solid var(--tone, var(--green));
    }
    .card span {
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .card strong {
      display: block;
      margin: 8px 0;
      font-size: clamp(26px, 2.2vw, 36px);
      line-height: .95;
      text-shadow: 0 2px 0 rgba(255, 71, 71, .3);
    }
    .card small {
      color: var(--muted);
      font-weight: 700;
    }
    .card-foot {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      min-height: 18px;
      font-weight: 900;
    }
    .card-foot .card-meta {
      color: var(--muted);
      font-size: 10px;
      text-transform: none;
      white-space: nowrap;
    }
    .card-foot .card-metric {
      font-size: 13px;
      text-transform: none;
    }
    .card-foot .card-metric.good { color: var(--green); }
    .card-foot .card-metric.bad { color: var(--red); }
    .card-foot .card-metric.violet { color: var(--violet); }
    .active-card-grid .card {
      min-height: 126px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      align-items: start;
    }
    .active-chart-grid {
      align-items: start;
    }
    .active-unit-chart-pair {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      align-items: stretch;
      margin-bottom: 14px;
    }
    .active-unit-chart-pair > .panel {
      height: 100%;
      margin-top: 0;
      margin-bottom: 0;
    }
    .active-chart-columns {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      align-items: start;
    }
    .active-demographic-trio {
      display: grid;
      grid-template-columns: minmax(250px, .72fr) minmax(430px, 1.35fr) minmax(330px, .93fr);
      gap: 14px;
      align-items: stretch;
    }
    .active-demographic-trio > .panel {
      min-width: 0;
      height: 100%;
      margin-top: 0;
      margin-bottom: 0;
    }
    .active-demographic-trio .composition-panel {
      grid-template-columns: minmax(140px, .72fr) minmax(0, 1.28fr);
    }
    .active-demographic-trio .chart-profile-age .donut {
      width: 185px;
    }
    .active-footer-cards {
      grid-template-columns: repeat(5, minmax(0, 1fr));
      margin-top: 14px;
    }
    .sales-chart-columns,
    .frequency-main-grid,
    .frequency-pair-grid,
    .frequency-cluster-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      align-items: start;
    }
    .frequency-analysis-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
      gap: 14px;
      align-items: start;
    }
    .frequency-analysis-column,
    .frequency-analysis-right,
    .frequency-cluster-unit-final {
      min-width: 0;
      display: grid;
      gap: 14px;
      align-content: start;
    }
    .frequency-analysis-column > .panel,
    .frequency-analysis-right > .panel,
    .frequency-cluster-unit-final > .panel {
      min-width: 0;
      margin: 0;
    }
    .frequency-analysis-left .chart-access-hour {
      min-height: 365px;
    }
    .frequency-analysis-right .chart-weekday-access {
      min-height: 330px;
    }
    .frequency-analysis-left .chart-ltv-plan,
    .frequency-analysis-right .chart-ltv-unit {
      width: 100%;
      align-self: start;
    }
    .frequency-cluster-unit-final {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .cancel-layout {
      display: grid;
      gap: 14px;
    }
    .cancel-top-pair,
    .cancel-unit-retention-grid,
    .cancel-threshold-pair {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      align-items: stretch;
    }
    .cancel-top-pair {
      grid-template-columns: minmax(0, 1.9fr) minmax(380px, 1fr);
    }
    .cancel-top-pair > .panel,
    .cancel-unit-retention-grid > .panel,
    .cancel-threshold-pair > .panel {
      min-width: 0;
      height: 100%;
      margin: 0;
    }
    .cancel-unit-retention-grid {
      grid-template-columns: minmax(0, 1.55fr) minmax(360px, .85fr);
      align-items: stretch;
    }
    .cancel-retention-stack {
      min-width: 0;
      display: grid;
      grid-template-rows: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    .cancel-retention-stack > .panel {
      min-width: 0;
      height: 100%;
      margin: 0;
    }
    .cancel-lower-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      align-items: stretch;
    }
    .cancel-lower-grid > .panel { min-width: 0; height: 100%; margin: 0; }
    .financial-chart-pair {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      align-items: stretch;
    }
    .financial-chart-pair > .panel {
      min-width: 0;
      height: 100%;
      margin: 0;
    }
    .financial-collection-layout {
      min-width: 0;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      align-items: stretch;
    }
    .financial-collection-layout > .panel,
    .financial-collection-stack > .panel,
    .financial-delinquency-full > .panel {
      min-width: 0;
      height: auto;
      margin: 0;
    }
    .financial-collection-stack {
      min-width: 0;
      display: grid;
      gap: 14px;
      align-content: start;
    }
    .financial-collection-layout > .financial-revenue-panel {
      height: 100%;
      align-self: stretch;
      display: flex;
      flex-direction: column;
    }
    .financial-revenue-panel .financial-revenue-view:not([hidden]) {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    .financial-revenue-panel .financial-revenue-view:not([hidden]) .bar-list {
      flex: 1;
      align-content: space-between;
    }
    .financial-delinquency-full {
      min-width: 0;
      display: grid;
    }
    .sales-month-contract-pair {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      align-items: stretch;
      margin-bottom: 14px;
    }
    .sales-month-contract-pair > .panel {
      height: 100%;
      margin: 0;
    }
    .sales-primary-layout {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      align-items: start;
    }
    .sales-primary-layout > .chart-stack {
      min-width: 0;
    }
    .sales-primary-layout .chart-sales-contracts {
      width: min(100%, 460px);
      min-height: 0;
      aspect-ratio: 1 / 1;
      margin: 0 auto;
    }
    .sales-primary-layout .chart-sales-contracts .contract-population-layout {
      grid-template-columns: minmax(150px, .9fr) minmax(0, 1.1fr);
      gap: 10px;
      padding: 2px 0;
    }
    .sales-primary-layout .chart-sales-contracts .contract-population-grid {
      grid-template-columns: repeat(10, minmax(6px, 1fr));
      gap: 4px;
    }
    .sales-primary-layout .chart-sales-contracts .contract-population-legend > div {
      grid-template-columns: 10px minmax(0, 1fr) auto;
      min-height: 28px;
      gap: 6px;
      padding: 2px 0;
    }
    .sales-primary-layout .chart-sales-contracts .contract-population-legend span { font-size: 11px; }
    .sales-primary-layout .chart-sales-contracts .contract-population-legend strong { font-size: 12px; }
    .sales-primary-layout .chart-sales-contracts .contract-population-note { margin-top: 4px; font-size: 10px; }
    .waterfall-panel { margin-top: 14px; min-height: 390px; }
    .waterfall-chart {
      display: grid;
      grid-template-columns: repeat(var(--wf-columns, 4), minmax(120px, 1fr));
      align-items: end;
      gap: 24px;
      min-height: 285px;
      padding: 20px 5% 0;
    }
    .waterfall-step { display: grid; grid-template-rows: 30px 220px auto; gap: 6px; text-align: center; min-width: 0; }
    .waterfall-step > strong { color: var(--ink); font-size: 18px; font-weight: 950; }
    .waterfall-step > span { color: var(--ink); font-size: 14px; font-weight: 850; }
    .waterfall-track { position: relative; }
    .waterfall-track::after {
      content: "";
      position: absolute;
      z-index: 2;
      left: 0;
      right: 0;
      bottom: var(--wf-zero);
      height: 1px;
      background: color-mix(in srgb, var(--ink), transparent 68%);
      pointer-events: none;
    }
    .waterfall-track > i {
      position: absolute;
      left: 12%;
      right: 12%;
      bottom: var(--wf-bottom);
      height: var(--wf-height);
      min-height: 4px;
      border-radius: 5px;
      background: var(--wf-color);
      box-shadow: 0 8px 22px color-mix(in srgb, var(--wf-color), transparent 72%);
    }
    .waterfall-note { margin: 12px 0 0; text-align: center; color: var(--muted); font-size: 12px; font-weight: 750; }
    .financial-revenue-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
    .financial-revenue-header h2 { text-align: left; margin-bottom: 4px; }
    .financial-revenue-tabs { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 6px; }
    .financial-revenue-tabs button {
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--panel-2);
      color: var(--muted);
      padding: 7px 11px;
      font: inherit;
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
      cursor: pointer;
    }
    .financial-revenue-tabs button.active { background: var(--green); border-color: var(--green); color: #031007; }
    .financial-revenue-total { margin: 8px 0 2px; color: var(--muted); font-size: 13px; font-weight: 800; }
    .financial-revenue-total strong { color: var(--ink); }
    @media (max-width: 900px) {
      .waterfall-chart { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .financial-revenue-header { flex-direction: column; }
      .financial-revenue-tabs { justify-content: flex-start; }
    }
    .peak-sales-card {
      min-height: 126px;
      gap: 8px;
    }
    .peak-sales-card > span {
      color: var(--green);
      font-size: 14px;
    }
    .peak-sales-card > small {
      color: #dbe8ed;
      text-transform: none;
    }
    .peak-sales-body {
      display: grid;
      grid-template-columns: 1fr auto;
      align-items: end;
      gap: 14px;
    }
    .peak-sales-day,
    .peak-sales-count {
      display: grid;
      gap: 3px;
    }
    .peak-sales-count { text-align: right; }
    .peak-sales-body em {
      color: var(--muted);
      font-size: 10px;
      font-style: normal;
      text-transform: uppercase;
    }
    .peak-sales-body strong {
      margin: 0;
      color: var(--orange);
      font-size: 29px;
    }
    .peak-sales-count strong { color: var(--blue); }
    .peak-sales-share {
      color: var(--green);
      font-size: 12px;
      font-weight: 950;
    }
    .frequency-layout {
      display: grid;
      gap: 14px;
    }
    .churn-risk-panel {
      grid-column: 1 / -1;
      display: grid;
      gap: 12px;
    }
    .churn-risk-header {
      display: flex;
      justify-content: center;
      gap: 18px;
      align-items: center;
    }
    .churn-risk-header-copy {
      width: 100%;
      min-width: 0;
      text-align: center;
    }
    .churn-risk-source {
      display: grid;
      gap: 3px;
      flex: 0 0 auto;
      padding: 9px 12px;
      border: 1px solid rgba(56, 163, 255, .22);
      border-radius: 10px;
      background: rgba(56, 163, 255, .06);
      color: var(--muted);
      font-size: 10px;
      text-align: right;
    }
    .churn-risk-source strong { color: var(--text); font-size: 11px; }
    .churn-risk-unit-grid {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 8px;
    }
    .churn-risk-unit {
      display: grid;
      gap: 3px;
      min-width: 0;
      padding: 10px 11px;
      border: 1px solid rgba(255, 255, 255, .10);
      border-left: 4px solid #ff9f1c;
      border-radius: 11px;
      background: #122126;
      color: var(--text);
      text-align: left;
      cursor: pointer;
      transition: border-color .16s ease, background .16s ease, transform .16s ease;
    }
    .churn-risk-unit:hover { transform: translateY(-1px); border-color: rgba(56, 163, 255, .55); }
    .churn-risk-unit.is-active {
      border-color: #38a3ff;
      background: rgba(56, 163, 255, .13);
      box-shadow: inset 0 0 0 1px rgba(56, 163, 255, .18);
    }
    .churn-risk-unit span {
      min-height: 28px;
      color: #dcecef;
      font-size: 10px;
      font-weight: 850;
      line-height: 1.2;
    }
    .churn-risk-unit strong { color: #ff5a67; font-size: 20px; line-height: 1; }
    .churn-risk-unit small,
    .churn-risk-unit em { color: var(--muted); font-size: 9px; font-style: normal; }
    .churn-risk-view { display: grid; gap: 12px; }
    .churn-risk-view[hidden] { display: none; }
    .churn-risk-view-title {
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
    }
    .churn-risk-view-title h3 { margin: 0; font-size: 15px; }
    .churn-risk-view-title span { color: var(--muted); font-size: 10px; }
    .churn-risk-bands {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 9px;
    }
    .churn-risk-band {
      --risk-color: #00f529;
      display: grid;
      gap: 5px;
      padding: 10px 12px;
      border: 1px solid color-mix(in srgb, var(--risk-color) 32%, transparent);
      border-radius: 11px;
      background: color-mix(in srgb, var(--risk-color) 7%, #102024);
    }
    .churn-risk-band[data-tone="yellow"] { --risk-color: #f4d68a; }
    .churn-risk-band[data-tone="orange"] { --risk-color: #ff9f1c; }
    .churn-risk-band[data-tone="red"] { --risk-color: #ff4658; }
    .churn-risk-band-head { display: flex; justify-content: space-between; gap: 8px; }
    .churn-risk-band-head span { color: var(--risk-color); font-size: 10px; font-weight: 900; text-transform: uppercase; }
    .churn-risk-band-head small { color: var(--muted); font-size: 9px; }
    .churn-risk-band strong { font-size: 20px; }
    .churn-risk-band-track { height: 5px; overflow: hidden; border-radius: 999px; background: rgba(255,255,255,.08); }
    .churn-risk-band-fill { width: var(--w); height: 100%; background: var(--risk-color); border-radius: inherit; }
    .churn-risk-table-wrap {
      max-width: 100%;
      overflow: auto;
      border: 1px solid rgba(255, 255, 255, .08);
      border-radius: 11px;
    }
    .churn-risk-table {
      width: 100%;
      min-width: 1240px;
      border-collapse: separate;
      border-spacing: 0;
      font-variant-numeric: tabular-nums;
    }
    .churn-risk-table th,
    .churn-risk-table td {
      padding: 8px 9px;
      border-right: 1px solid rgba(255,255,255,.05);
      border-bottom: 1px solid rgba(255,255,255,.05);
      white-space: nowrap;
      text-align: right;
      font-size: 10px;
    }
    .churn-risk-table thead th {
      position: sticky;
      top: 0;
      z-index: 2;
      background: #17282c;
      color: #9db4ba;
      font-size: 9px;
      letter-spacing: .025em;
      text-transform: uppercase;
    }
    .churn-risk-table th:first-child,
    .churn-risk-table td:first-child { text-align: left; }
    .churn-risk-table tbody tr:hover td { background: rgba(56,163,255,.075); }
    .churn-risk-name { display: grid; gap: 2px; min-width: 190px; }
    .churn-risk-name strong { color: #eff9fa; font-size: 11px; }
    .churn-risk-name small { color: var(--muted); font-size: 9px; }
    .churn-risk-score {
      --score-color: #00f529;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 34px;
      padding: 4px 7px;
      border-radius: 999px;
      background: color-mix(in srgb, var(--score-color) 14%, transparent);
      color: var(--score-color);
      font-weight: 950;
    }
    .churn-risk-score.risk-medium { --score-color: #f4d68a; }
    .churn-risk-score.risk-high { --score-color: #ff9f1c; }
    .churn-risk-score.risk-critical { --score-color: #ff4658; }
    .churn-risk-rules {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 5px 16px;
      padding-top: 2px;
      color: var(--muted);
      font-size: 9px;
    }
    .churn-risk-rules span::before { content: "•"; margin-right: 6px; color: #38a3ff; }
    .churn-risk-donut-legend {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      gap: 8px 20px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }
    .churn-risk-donut-legend span {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      white-space: nowrap;
    }
    .churn-risk-donut-legend i {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--legend-color);
      box-shadow: 0 0 7px color-mix(in srgb, var(--legend-color) 40%, transparent);
    }
    .churn-risk-donut-layout {
      display: grid;
      grid-template-columns: 174px minmax(0, 1fr);
      align-items: stretch;
      gap: 8px;
      width: 100%;
      max-width: 100%;
      padding: 3px 2px 8px;
    }
    .churn-risk-network-slot {
      display: grid;
      min-width: 0;
    }
    .churn-risk-unit-donut-grid {
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      grid-template-rows: repeat(2, minmax(0, 1fr));
      gap: 16px 4px;
      min-width: 0;
    }
    .churn-risk-donut-card {
      display: grid;
      align-content: center;
      justify-items: center;
      gap: 5px;
      width: 100%;
      min-width: 0;
      padding: 2px 0;
      background: transparent;
    }
    .churn-risk-donut-card.is-network {
      min-height: 288px;
      background: transparent;
    }
    .churn-risk-donut-card.is-network .churn-risk-donut {
      width: 158px;
      height: 158px;
    }
    .churn-risk-donut-card.is-network .churn-risk-donut-center { inset: 39px; }
    .churn-risk-donut-card.is-network .churn-risk-donut-center strong { font-size: 17px; }
    .churn-risk-donut-card.is-network .churn-risk-donut-center small { font-size: 9px; }
    .churn-risk-donut-card.is-network .churn-risk-donut-label { font-size: 10px; }
    .churn-risk-donut {
      position: relative;
      width: 132px;
      height: 132px;
    }
    .churn-risk-donut svg {
      display: block;
      width: 100%;
      height: 100%;
      overflow: visible;
      filter: drop-shadow(0 4px 10px rgba(0, 0, 0, .22));
    }
    .churn-risk-donut-track {
      fill: none;
      stroke: rgba(255, 255, 255, .075);
      stroke-width: 17;
    }
    .churn-risk-donut-segment {
      fill: none;
      stroke: var(--segment-color);
      stroke-width: 17;
      stroke-linecap: butt;
      cursor: pointer;
      pointer-events: stroke;
      transition: stroke-width .14s ease, filter .14s ease, opacity .14s ease;
    }
    .churn-risk-donut-segment:hover,
    .churn-risk-donut-segment:focus-visible {
      stroke-width: 21;
      filter: drop-shadow(0 0 5px var(--segment-color));
      outline: none;
    }
    .churn-risk-donut:has(.churn-risk-donut-segment:hover) .churn-risk-donut-segment:not(:hover) { opacity: .48; }
    .churn-risk-donut-center {
      position: absolute;
      inset: 31px;
      display: grid;
      place-content: center;
      gap: 1px;
      border-radius: 50%;
      background: #0b1b1e;
      color: #f2fbfc;
      text-align: center;
      pointer-events: none;
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .035);
    }
    .churn-risk-donut-center strong { font-size: 14px; line-height: 1; letter-spacing: .02em; }
    .churn-risk-donut-label {
      min-height: 24px;
      color: #dcecef;
      font-size: 12px;
      font-weight: 800;
      line-height: 1.15;
      text-align: center;
    }
    .churn-risk-donut-hint {
      margin: 0;
      color: #789097;
      font-size: 10px;
      text-align: center;
    }
    .churn-risk-modal {
      position: fixed;
      inset: 0;
      z-index: 1200;
      display: grid;
      place-items: center;
      padding: 18px;
      background: rgba(0, 10, 11, .82);
      backdrop-filter: blur(7px);
    }
    body.churn-risk-modal-open { overflow: hidden; }
    .churn-risk-modal[hidden] { display: none; }
    .churn-risk-modal-dialog {
      --modal-risk-color: #00f529;
      display: grid;
      grid-template-rows: auto auto minmax(0, 1fr) auto;
      gap: 16px;
      width: min(1760px, 98vw);
      max-height: 94vh;
      padding: 20px;
      overflow: hidden;
      border: 1px solid color-mix(in srgb, var(--modal-risk-color) 42%, rgba(255,255,255,.08));
      border-radius: 16px;
      background: #0b1b1e;
      box-shadow: 0 24px 80px rgba(0, 0, 0, .58), inset 0 3px 0 var(--modal-risk-color);
    }
    .churn-risk-modal[data-tone="yellow"] .churn-risk-modal-dialog { --modal-risk-color: #f4d68a; }
    .churn-risk-modal[data-tone="orange"] .churn-risk-modal-dialog { --modal-risk-color: #ff9f1c; }
    .churn-risk-modal[data-tone="red"] .churn-risk-modal-dialog { --modal-risk-color: #ff4658; }
    .churn-risk-modal-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
    }
    .churn-risk-modal-head h3 { margin: 0; color: var(--modal-risk-color); font-size: 26px; line-height: 1.15; }
    .churn-risk-modal-head p { margin: 6px 0 0; color: var(--muted); font-size: 14px; line-height: 1.4; }
    .churn-risk-modal-close {
      display: grid;
      place-items: center;
      width: 44px;
      height: 44px;
      flex: 0 0 auto;
      border: 1px solid rgba(255,255,255,.12);
      border-radius: 50%;
      background: rgba(255,255,255,.045);
      color: #eff9fa;
      font-size: 26px;
      cursor: pointer;
    }
    .churn-risk-modal-summary {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }
    .churn-risk-modal-summary .churn-risk-band {
      gap: 8px;
      padding: 14px 16px;
      transition: border-color .15s ease, box-shadow .15s ease, transform .15s ease;
    }
    html[data-theme] .churn-risk-modal-summary .churn-risk-band-head span { font-size: 15px; line-height: 1.25; }
    html[data-theme] .churn-risk-modal-summary .churn-risk-band-head small { font-size: 13px; line-height: 1.25; }
    .churn-risk-modal-summary .churn-risk-band > strong { font-size: 28px; line-height: 1; }
    .churn-risk-modal-summary .churn-risk-band > small { font-size: 14px; line-height: 1.3; }
    .churn-risk-modal-summary .churn-risk-band-track { height: 7px; }
    .churn-risk-modal-summary .churn-risk-band.is-selected {
      border-color: var(--risk-color);
      box-shadow: 0 0 0 1px var(--risk-color), 0 8px 24px color-mix(in srgb, var(--risk-color) 12%, transparent);
      transform: translateY(-1px);
    }
    .churn-risk-modal .churn-risk-table-wrap { max-height: 58vh; }
    .churn-risk-modal .churn-risk-table { min-width: 1450px; }
    .churn-risk-modal .churn-risk-table th,
    .churn-risk-modal .churn-risk-table td { padding: 12px 13px; font-size: 13px; line-height: 1.3; }
    .churn-risk-modal .churn-risk-table thead th { font-size: 12px; }
    .churn-risk-modal .churn-risk-name { min-width: 280px; gap: 4px; }
    .churn-risk-modal .churn-risk-name strong { font-size: 14px; }
    .churn-risk-modal .churn-risk-name small { font-size: 11px; }
    .churn-risk-modal .churn-risk-score { min-width: 44px; padding: 6px 10px; font-size: 13px; }
    .churn-risk-modal-foot { color: #789097; font-size: 12px; line-height: 1.4; }
    .frequency-cluster-side {
      display: grid;
      gap: 14px;
      align-content: start;
    }
    .chart-stack {
      display: grid;
      gap: 14px;
      align-content: start;
    }
    .chart-stack .compact {
      min-height: 0;
    }
    .active-chart-grid .chart-active-units {
      grid-row: span 2;
    }
    .active-chart-grid .compact {
      min-height: 0;
    }
    .active-chart-grid .chart-active-contract {
      align-self: start;
    }
    .active-chart-grid .chart-payment-status {
      grid-column: 1;
      grid-row: 4;
      align-self: start;
    }
    .active-chart-grid .chart-ltv-plan {
      grid-column: 1;
      grid-row: 3;
    }
    .active-chart-grid .chart-ltv-unit {
      grid-column: 2;
      grid-row: 3 / span 2;
    }
    .panel {
      padding: 14px;
      min-height: 285px;
    }
    .panel h2 {
      margin: 0 0 12px;
      font-size: 18px;
      line-height: 1.1;
      text-transform: uppercase;
    }
    .panel-subtitle {
      margin: -6px 0 12px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      line-height: 1.35;
    }
    .medal-board-panel {
      margin-top: 14px;
      min-height: 0;
      padding: 16px;
      border-color: rgba(181, 108, 255, .32);
      background:
        linear-gradient(135deg, rgba(22, 12, 32, .98), rgba(26, 30, 65, .96)),
        linear-gradient(90deg, rgba(255,255,255,.05), transparent);
      box-shadow: 0 0 34px rgba(181, 108, 255, .16);
    }
    .medal-board-panel h2 {
      color: var(--ink);
      margin-bottom: 14px;
      text-align: center;
    }
    .medal-board-table {
      display: block;
      border-radius: 14px;
      overflow-x: auto;
      overflow-y: hidden;
      background: rgba(10, 8, 22, .86);
      border: 1px solid rgba(255, 255, 255, .08);
    }
    .medal-row {
      display: grid;
      grid-template-columns: 58px minmax(220px, 1fr) repeat(3, minmax(82px, 105px)) minmax(82px, 105px);
      align-items: center;
      min-height: 42px;
      border-bottom: 1px solid rgba(255, 255, 255, .07);
      font-size: 14px;
      font-weight: 900;
    }
    .medal-row:last-child {
      border-bottom: 0;
    }
    .medal-row:nth-child(even):not(.head) {
      background: rgba(79, 75, 139, .34);
    }
    .medal-row:nth-child(odd):not(.head) {
      background: rgba(13, 9, 28, .68);
    }
    .medal-row.head {
      min-height: 48px;
      color: #f7f8ff;
      background: linear-gradient(90deg, rgba(10, 7, 24, .96), rgba(35, 31, 75, .92));
      font-size: 10px;
      text-transform: uppercase;
    }
    .medal-row > span,
    .medal-row > div {
      min-width: 0;
      height: 100%;
      padding: 8px 10px;
      display: flex;
      align-items: center;
      border-right: 1px dashed rgba(255, 255, 255, .22);
    }
    .medal-row > span:last-child,
    .medal-row > div:last-child {
      border-right: 0;
    }
    .medal-position {
      justify-content: center;
      color: #f7f8ff;
      font-size: 15px;
    }
    .medal-unit {
      color: var(--ink);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      text-transform: uppercase;
    }
    .medal-head-cell {
      justify-content: center;
      gap: 3px;
      flex-direction: column;
      line-height: 1;
    }
    .medal-head-icon {
      font-size: 21px;
      line-height: 1;
    }
    .medal-gold { color: #ffca20; }
    .medal-silver { color: #d6d9e2; }
    .medal-bronze { color: #e98a45; }
    .medal-total-head {
      justify-content: center;
    }
    .medal-count {
      justify-content: center;
      font-variant-numeric: tabular-nums;
      color: #f7f8ff;
      font-size: 16px;
    }
    .medal-total {
      color: #ffffff;
      font-size: 17px;
    }
    .medal-board-matrix {
      width: 100%;
      table-layout: fixed;
      border-collapse: separate;
      border-spacing: 0;
      color: var(--ink);
    }
    .medal-board-matrix th,
    .medal-board-matrix td {
      height: 52px;
      padding: 8px 5px;
      border-right: 1px solid rgba(255, 255, 255, .10);
      border-bottom: 1px solid rgba(255, 255, 255, .08);
      text-align: center;
      font-variant-numeric: tabular-nums;
    }
    .medal-board-matrix th:last-child,
    .medal-board-matrix td:last-child {
      border-right: 0;
    }
    .medal-board-matrix tbody tr:last-child th,
    .medal-board-matrix tbody tr:last-child td {
      border-bottom: 0;
    }
    .medal-board-matrix thead th {
      height: 62px;
      background: linear-gradient(135deg, rgba(43, 111, 242, .34), rgba(50, 170, 255, .16));
      font-size: 13px;
      text-transform: uppercase;
    }
    .medal-board-matrix thead th:first-child,
    .medal-board-matrix tbody th {
      width: 148px;
      padding-left: 14px;
      text-align: left;
    }
    .medal-unit-head {
      display: grid;
      justify-items: center;
      gap: 3px;
      line-height: 1;
    }
    .medal-unit-head strong {
      color: var(--ink);
      font-size: 14px;
      letter-spacing: .02em;
    }
    .medal-rank {
      color: var(--muted);
      font-size: 10px;
      font-weight: 800;
    }
    .medal-board-matrix tbody tr:nth-child(odd) {
      background: rgba(50, 170, 255, .045);
    }
    .medal-board-matrix tbody tr:nth-child(even) {
      background: rgba(98, 199, 118, .045);
    }
    .medal-board-matrix tbody th {
      font-size: 13px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .medal-board-matrix tbody td {
      color: var(--ink);
      font-size: 17px;
      font-weight: 900;
    }
    .medal-board-matrix .medal-gold { color: #ffca20; }
    .medal-board-matrix .medal-silver { color: #d6d9e2; }
    .medal-board-matrix .medal-bronze { color: #e98a45; }
    .medal-board-matrix .medal-points-row th,
    .medal-board-matrix .medal-points-row td {
      color: var(--green);
      background: rgba(0, 245, 41, .055);
      font-size: 18px;
    }
    @media (max-width: 900px) {
      .medal-board-matrix { min-width: 980px; }
    }
    .column-panel {
      min-height: 285px;
    }
    .column-list {
      min-height: 210px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(48px, 1fr));
      align-items: end;
      gap: 8px;
      padding-top: 12px;
    }
    .column-item {
      min-width: 0;
      display: grid;
      grid-template-rows: 1fr auto auto;
      gap: 7px;
      align-items: end;
      text-align: center;
    }
    .column-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 7px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
    }
    .column-legend span {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .column-legend span::before {
      content: "";
      width: 18px;
      height: 7px;
      border-radius: 99px;
      background: var(--legend-color);
    }
    .column-pair {
      width: 100%;
      height: 160px;
      display: grid;
      grid-template-columns: repeat(var(--cols, 2), minmax(0, 1fr));
      gap: 6px;
      align-items: end;
    }
    .column-pair .column-track {
      height: 100%;
    }
    .column-split-values {
      display: grid;
      grid-template-columns: repeat(var(--cols, 2), minmax(0, 1fr));
      gap: 4px;
      font-size: 14px;
    }
    .column-split-values span {
      min-width: 0;
      color: var(--value-color);
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .column-track {
      width: 100%;
      height: 160px;
      display: flex;
      align-items: end;
      border-radius: 10px;
      padding: 5px;
      background: rgba(206, 222, 232, .13);
      overflow: hidden;
    }
    .column-fill {
      width: 100%;
      height: var(--h);
      min-height: 3px;
      border-radius: 8px;
      background: var(--bar, var(--orange));
      box-shadow: 0 0 18px color-mix(in srgb, var(--bar, var(--orange)), transparent 54%);
    }
    .column-value {
      font-weight: 900;
      font-size: 18px;
      line-height: 1;
      white-space: nowrap;
    }
    .column-label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      white-space: nowrap;
    }
    .chart-profile-delinquency-days .column-list {
      grid-template-columns: repeat(20, minmax(0, 1fr));
      gap: 8px;
      min-height: 300px;
      width: min(100%, 1440px);
      margin-inline: auto;
      padding-inline: 10px;
    }
    .chart-profile-delinquency-days .column-item {
      grid-template-rows: auto 1fr auto;
      align-items: stretch;
    }
    .chart-profile-delinquency-days .column-track {
      grid-row: 2;
      height: 230px;
      padding: 3px;
    }
    .chart-profile-delinquency-days .column-value {
      grid-row: 1;
      align-self: end;
      min-height: 20px;
      font-size: 15px;
    }
    .chart-profile-delinquency-days .column-label {
      grid-row: 3;
      min-height: 30px;
      font-size: 13px;
      line-height: 1.05;
      white-space: normal;
    }
    .chart-sales-month {
      min-height: 238px;
    }
    .chart-sales-month .column-list {
      min-height: 160px;
    }
    .chart-sales-month .column-track {
      height: 118px;
    }
    .chart-sales-month .column-pair {
      height: 118px;
    }
    .chart-sales-month .column-value {
      font-size: 16px;
    }
    #tab-vendas .chart-sales-month {
      min-height: 330px;
    }
    #tab-vendas .chart-sales-month .column-list {
      min-height: 195px;
      padding-top: 14px;
    }
    #tab-vendas .chart-sales-month .column-track,
    #tab-vendas .chart-sales-month .column-pair {
      height: 150px;
    }
    #tab-vendas .chart-sales-month .column-value {
      font-size: 15px;
    }
    .chart-sales-units.column-panel {
      min-height: 390px;
    }
    .chart-sales-units .column-list {
      min-height: 292px;
      grid-template-columns: repeat(14, minmax(34px, 1fr));
      gap: 7px;
      padding-top: 18px;
    }
    .chart-sales-units .column-item {
      grid-template-rows: auto minmax(220px, 1fr) auto;
      gap: 8px;
    }
    .chart-sales-units .column-value {
      grid-row: 1;
      color: var(--ink);
      font-size: 14px;
      font-weight: 950;
    }
    .chart-sales-units .column-track {
      grid-row: 2;
      height: 230px;
      border-radius: 8px 8px 4px 4px;
      padding: 4px;
    }
    .chart-sales-units .column-fill {
      border-radius: 6px 6px 2px 2px;
    }
    .chart-sales-units .column-label {
      grid-row: 3;
      color: var(--ink);
      font-size: 12px;
      font-weight: 950;
      text-align: center;
    }
    .chart-access-day .column-label {
      white-space: normal;
      line-height: 1.02;
      min-height: 30px;
    }
    .chart-access-day .day-label {
      display: grid;
      gap: 2px;
      justify-items: center;
      align-content: start;
    }
    .chart-access-day .day-label strong {
      color: #d8ecff;
      font-size: 10px;
      line-height: 1;
      text-transform: lowercase;
    }
    .chart-access-day .day-label span {
      color: var(--muted);
      font-size: 10px;
      line-height: 1;
    }
    .chart-access-day .column-split-values {
      font-size: 11px;
      gap: 2px;
    }
    .chart-access-day {
      grid-column: 1 / -1;
    }
    .chart-access-hour {
      grid-column: 1 / -1;
      min-height: 320px;
    }
    .frequency-main-grid .chart-access-hour,
    .frequency-pair-grid .chart-access-hour {
      grid-column: auto;
    }
    .chart-access-hour .column-split-values {
      font-size: 10px;
      gap: 1px;
    }
    .chart-access-hour .column-label {
      font-size: 10px;
    }
    .chart-access-hour .bar-row {
      grid-template-columns: 40px minmax(0, 1fr) 78px;
      gap: 6px;
    }
    .chart-access-hour .multi-value {
      width: 78px;
    }
    .stacked-column-frame {
      margin-top: 12px;
      padding: 14px;
      border: 1px solid rgba(206, 222, 232, .1);
      border-radius: 10px;
      background: rgba(2, 12, 14, .42);
    }
    .stacked-legend {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 16px;
      margin-bottom: 12px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
    }
    .stacked-legend span {
      display: inline-flex;
      align-items: center;
      gap: 7px;
    }
    .stacked-legend span::before {
      content: "";
      width: 38px;
      height: 10px;
      border-radius: 2px;
      background: var(--legend-color);
    }
    .stacked-column-list {
      min-height: 250px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(34px, 1fr));
      gap: 6px;
      align-items: end;
    }
    .stacked-column-item {
      min-width: 0;
      display: grid;
      grid-template-rows: auto 1fr auto;
      gap: 6px;
      align-items: end;
      text-align: center;
    }
    .stacked-total {
      min-height: 22px;
      color: var(--ink);
      font-size: 14px;
      font-weight: 950;
      line-height: 1;
    }
    .stacked-track {
      height: 220px;
      display: flex;
      flex-direction: column-reverse;
      border-radius: 6px 6px 2px 2px;
      background: rgba(206, 222, 232, .1);
      overflow: hidden;
    }
    .stacked-segment {
      min-height: var(--min-h, 0);
      height: var(--h);
      background: var(--bar);
      box-shadow: inset 0 0 10px color-mix(in srgb, var(--bar), transparent 62%);
      display: grid;
      place-items: center;
      color: #fff;
      font-size: 11px;
      font-weight: 950;
      line-height: 1;
      text-shadow: 0 1px 2px rgba(0, 0, 0, .7);
    }
    .stacked-label {
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      white-space: nowrap;
    }
    .chart-callout {
      margin-top: 14px;
      padding: 13px 15px;
      border: 1px solid rgba(181, 108, 255, .48);
      border-radius: 8px;
      color: var(--muted);
      background: rgba(181, 108, 255, .08);
      font-weight: 800;
      line-height: 1.45;
    }
    .chart-callout strong {
      color: var(--green);
    }
    .frequency-cluster-panel {
      min-height: 350px;
    }
    .cluster-total {
      margin: 12px 0;
      padding: 14px;
      border: 1px solid rgba(56, 163, 255, .42);
      border-radius: 8px;
      background: rgba(56, 163, 255, .08);
    }
    .cluster-total span {
      display: block;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .cluster-total strong {
      display: block;
      margin-top: 4px;
      color: #fff;
      font-size: 34px;
      line-height: .95;
      text-shadow: 0 2px 0 rgba(255, 71, 71, .28);
    }
    .cluster-list {
      display: grid;
      gap: 9px;
    }
    .cluster-row {
      display: grid;
      grid-template-columns: minmax(130px, 190px) minmax(0, 1fr) 116px;
      gap: 10px;
      align-items: center;
      font-size: 12px;
    }
    .cluster-name {
      display: grid;
      gap: 2px;
      min-width: 0;
      color: var(--ink);
      font-weight: 900;
    }
    .cluster-name small {
      color: var(--muted);
      font-weight: 800;
    }
    .cluster-track {
      height: 13px;
      border-radius: 99px;
      background: rgba(206, 222, 232, .13);
      overflow: hidden;
    }
    .cluster-fill {
      width: var(--w);
      height: 100%;
      border-radius: inherit;
      background: var(--bar);
      box-shadow: 0 0 16px color-mix(in srgb, var(--bar), transparent 55%);
    }
    .cluster-value {
      text-align: right;
      font-weight: 900;
      white-space: nowrap;
      color: #fff;
    }
    .chart-cluster-distribution .legend-row {
      font-size: 12px;
      gap: 8px;
    }
    .frequency-cluster-unit-table {
      grid-column: 1 / -1;
    }
    .cluster-unit-table-wrap {
      margin-top: 14px;
      overflow: auto;
      border: 1px solid rgba(206, 222, 232, .1);
      border-radius: 10px;
      background: rgba(2, 12, 14, .38);
    }
    .cluster-unit-table {
      width: 100%;
      min-width: 1040px;
      border-collapse: collapse;
    }
    .cluster-unit-table th,
    .cluster-unit-table td {
      padding: 10px 12px;
      border-bottom: 1px solid rgba(206, 222, 232, .1);
      text-align: left;
      vertical-align: middle;
    }
    .cluster-unit-table th {
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
      background: rgba(206, 222, 232, .05);
      white-space: nowrap;
    }
    .cluster-unit-table tbody tr:last-child td {
      border-bottom: 0;
    }
    .cluster-unit-name {
      color: #fff;
      font-weight: 900;
      white-space: nowrap;
    }
    .cluster-unit-cell {
      min-width: 128px;
      display: grid;
      gap: 4px;
    }
    .cluster-unit-cell strong {
      color: #fff;
      font-size: 13px;
      line-height: 1;
      white-space: nowrap;
    }
    .cluster-unit-cell small {
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      white-space: nowrap;
    }
    .cluster-unit-mini-track {
      height: 6px;
      border-radius: 99px;
      background: rgba(206, 222, 232, .12);
      overflow: hidden;
    }
    .cluster-unit-mini-fill {
      width: var(--w);
      height: 100%;
      border-radius: inherit;
      background: var(--bar);
      box-shadow: 0 0 11px color-mix(in srgb, var(--bar), transparent 60%);
    }
    .cluster-unit-total {
      color: #fff;
      font-weight: 900;
      text-align: right;
      white-space: nowrap;
    }
    .line-chart {
      grid-column: 1 / -1;
      min-height: 430px;
    }
    .line-chart-frame {
      margin-top: 12px;
      padding: 14px;
      border: 1px solid rgba(206, 222, 232, .1);
      border-radius: 10px;
      background: rgba(2, 12, 14, .42);
    }
    .line-series-selector {
      margin-top: 12px;
      border: 1px solid rgba(56, 163, 255, .28);
      border-radius: 10px;
      background: rgba(4, 18, 22, .72);
      color: var(--ink);
    }
    .line-series-selector-title {
      padding: 10px 12px;
      color: var(--blue);
      font-size: 12px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .line-series-options {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 0 12px 12px;
    }
    .line-series-options label {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 12px;
      border: 1px solid rgba(206, 222, 232, .14);
      border-radius: 999px;
      background: rgba(255, 255, 255, .04);
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
      transition: border-color .18s ease, background .18s ease, color .18s ease;
    }
    .line-series-options label:has(input:checked) {
      color: #031007;
      border-color: var(--green);
      background: var(--green);
      box-shadow: 0 0 14px color-mix(in srgb, var(--green), transparent 70%);
    }
    .line-series-options input {
      position: absolute;
      width: 1px;
      height: 1px;
      opacity: 0;
      pointer-events: none;
    }
    .line-series-options label::before {
      content: "";
      width: 8px;
      height: 8px;
      border: 1px solid currentColor;
      border-radius: 50%;
      background: transparent;
    }
    .line-series-options label:has(input:checked)::before { background: currentColor; }
    .line-svg {
      width: 100%;
      min-height: 295px;
      display: block;
    }
    .line-grid {
      stroke: rgba(206, 222, 232, .12);
      stroke-width: 1;
    }
    .line-axis-label {
      fill: var(--muted);
      font-size: 10px;
      font-weight: 800;
    }
    .line-path {
      fill: none;
      stroke: var(--line);
      stroke-width: 4;
      stroke-linecap: round;
      stroke-linejoin: round;
      filter: drop-shadow(0 0 7px color-mix(in srgb, var(--line), transparent 55%));
    }
    .line-point {
      fill: var(--panel);
      stroke: var(--line);
      stroke-width: 3;
    }
    .line-legend {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 18px;
      margin-top: 12px;
      color: var(--ink);
      font-size: 12px;
      font-weight: 800;
    }
    .line-legend span {
      display: inline-flex;
      align-items: center;
      gap: 7px;
    }
    .line-legend span::before {
      content: "";
      width: 11px;
      height: 11px;
      border-radius: 50%;
      background: var(--legend-color);
      box-shadow: 0 0 12px color-mix(in srgb, var(--legend-color), transparent 45%);
    }
    .bar-list {
      display: grid;
      gap: 10px;
    }
    .bar-row {
      display: grid;
      grid-template-columns: minmax(150px, 230px) minmax(110px, 1fr) minmax(92px, auto);
      gap: 10px;
      align-items: center;
      font-size: 13px;
    }
    .chart-payment-status .bar-row {
      grid-template-columns: minmax(190px, 240px) minmax(0, 1fr) 190px;
    }
    .chart-payment-status .bar-value {
      width: 190px;
    }
    .chart-sales-open-values .bar-row {
      grid-template-columns: minmax(150px, 230px) minmax(0, 1fr) 150px;
    }
    .chart-sales-open-values .bar-value {
      width: 150px;
    }
    .chart-sales-success .bar-row {
      grid-template-columns: minmax(150px, 230px) minmax(0, 1fr) 150px;
    }
    .chart-sales-success .bar-value {
      width: 150px;
    }
    .chart-sales-success {
      min-height: 470px;
    }
    .chart-sales-success .bar-list {
      grid-template-columns: 1fr;
      gap: 8px;
    }
    .chart-sales-success .bar-row {
      grid-template-columns: minmax(160px, 220px) minmax(180px, 1fr) 150px;
      font-size: 12px;
      gap: 9px;
    }
    .chart-sales-success .bar-track {
      height: 11px;
    }
    .chart-sales-success .bar-value {
      width: 150px;
    }
    .chart-contract-swaps {
      min-height: 150px;
    }
    .chart-contract-swaps .bar-row {
      grid-template-columns: minmax(190px, 260px) minmax(0, 1fr) 150px;
    }
    .chart-contract-swaps .bar-value {
      width: 150px;
    }
    .chart-cancel-churn .bar-row {
      grid-template-columns: minmax(44px, 60px) minmax(0, 1fr) minmax(105px, 120px);
      gap: 8px;
    }
    .chart-cancel-churn .bar-value {
      width: auto;
    }
    .chart-cancel-reasons .bar-row {
      grid-template-columns: 150px minmax(170px, 1fr) 80px;
      gap: 8px;
    }
    .chart-cancel-reasons .bar-label {
      overflow: visible;
      text-overflow: clip;
      white-space: normal;
      line-height: 1.15;
    }
    .chart-cancel-reasons .bar-value {
      width: auto;
    }
    .chart-cancel-values .bar-row {
      grid-template-columns: minmax(130px, 190px) minmax(0, 1fr) 150px;
    }
    .chart-cancel-values .bar-value {
      width: 150px;
    }
    .chart-profile-gender {
      min-height: 285px;
      text-align: center;
    }
    .chart-profile-gender .column-list {
      min-height: 215px;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      padding: 8px 8px 0;
    }
    .chart-profile-gender .column-track {
      height: 150px;
    }
    .chart-profile-gender .column-value {
      display: grid;
      gap: 3px;
      justify-items: center;
      font-size: 16px;
    }
    .chart-profile-gender .column-value small {
      color: var(--muted);
      font-size: 11px;
    }
    .chart-profile-gender .column-label {
      min-height: 28px;
      white-space: normal;
      line-height: 1.15;
    }
    .chart-profile-charge-success .bar-row,
    .chart-profile-recovery-success .bar-row {
      grid-template-columns: minmax(150px, 230px) minmax(0, 1fr) 150px;
    }
    .chart-profile-charge-success .bar-value,
    .chart-profile-recovery-success .bar-value {
      width: 150px;
    }
    .chart-profile-revenue .bar-row {
      grid-template-columns: minmax(150px, 230px) minmax(0, 1fr) 180px;
    }
    .chart-profile-revenue .bar-value {
      width: 180px;
    }
    .collection-combo-legend {
      display: flex;
      justify-content: center;
      gap: 24px;
      margin: 6px 0 10px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 800;
    }
    .collection-combo-legend span {
      display: inline-flex;
      align-items: center;
      gap: 8px;
    }
    .collection-combo-legend i {
      width: 22px;
      height: 7px;
      border-radius: 999px;
      background: var(--series-color);
      box-shadow: 0 0 12px color-mix(in srgb, var(--series-color) 35%, transparent);
    }
    .collection-combo-frame {
      width: 100%;
      min-height: 330px;
    }
    .collection-combo-svg {
      display: block;
      width: 100%;
      height: auto;
      min-height: 330px;
      overflow: visible;
    }
    .collection-combo-grid { stroke: color-mix(in srgb, var(--muted) 18%, transparent); stroke-width: 1; }
    .collection-combo-axis { fill: var(--muted); font-size: 15px; font-weight: 900; }
    .collection-combo-unit { fill: var(--ink); font-size: 18px; font-weight: 400; }
    .collection-combo-bar { fill: var(--bar-color); opacity: .9; }
    .collection-combo-line { fill: none; stroke: var(--line-color); stroke-width: 5; stroke-linecap: round; stroke-linejoin: round; filter: drop-shadow(0 0 5px color-mix(in srgb, var(--line-color) 45%, transparent)); }
    .collection-combo-point { fill: var(--panel); stroke: var(--line-color); stroke-width: 4; }
    .collection-combo-value { fill: var(--ink); font-size: 20px; font-weight: 950; text-anchor: middle; paint-order: stroke; stroke: var(--panel); stroke-width: 5px; stroke-linejoin: round; }
    .collection-combo-rate { fill: var(--line-color); font-size: 17px; font-weight: 950; text-anchor: middle; paint-order: stroke; stroke: var(--panel); stroke-width: 5px; }
    .expanded-chart-clone .collection-combo-frame,
    .expanded-chart-clone .collection-combo-svg { min-height: 520px; }
    .bar-label {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      color: var(--ink);
    }
    .bar-track {
      height: 13px;
      border-radius: 99px;
      background: rgba(206, 222, 232, .13);
      overflow: hidden;
    }
    .bar-fill {
      height: 100%;
      width: var(--w);
      border-radius: inherit;
      background: var(--bar, var(--green));
      box-shadow: 0 0 18px color-mix(in srgb, var(--bar, var(--green)), transparent 55%);
    }
    .cannibalization-panel {
      min-height: 0;
      margin-bottom: 14px;
      border-color: rgba(216, 56, 94, .36);
    }
    .cannibalization-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      margin-bottom: 14px;
    }
    .cannibalization-header h2 {
      color: var(--wellhub);
      letter-spacing: .04em;
      margin-bottom: 8px;
    }
    .cannibalization-header .panel-subtitle {
      max-width: 900px;
      margin: 0;
    }
    .cannibalization-period-control {
      flex: 0 0 auto;
      display: grid;
      gap: 5px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 900;
      letter-spacing: .03em;
      text-transform: uppercase;
    }
    .cannibalization-period-control select {
      min-width: 180px;
      height: 36px;
      padding: 0 34px 0 12px;
      border: 1px solid rgba(216, 56, 94, .42);
      border-radius: 999px;
      color: var(--ink);
      background: var(--surface, rgba(8, 18, 21, .94));
      font: inherit;
      font-size: 11px;
      text-transform: none;
      cursor: pointer;
    }
    .chart-cancel-cannibalization .bar-list {
      gap: 7px;
    }
    .chart-cancel-cannibalization .bar-row {
      grid-template-columns: minmax(50px, 64px) minmax(0, 1fr) 52px;
      gap: 8px;
      font-size: 12px;
    }
    .chart-cancel-cannibalization .bar-track {
      height: 14px;
      border: 1px solid rgba(216, 56, 94, .16);
      background: rgba(216, 56, 94, .08);
    }
    .chart-cancel-cannibalization .bar-value {
      color: var(--wellhub);
      font-size: 13px;
    }
    .cannibalization-total {
      display: flex;
      align-items: baseline;
      justify-content: flex-end;
      gap: 8px;
      margin-top: 14px;
      padding: 10px 12px;
      border-top: 1px solid rgba(216, 56, 94, .24);
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }
    .cannibalization-total strong {
      color: #d8385e;
      font-size: 20px;
    }
    .cannibalization-total small {
      color: var(--muted);
    }
    .active-goals-panel {
      min-height: 0;
      margin-bottom: 14px;
      border-color: rgba(0, 245, 41, .34);
    }
    .active-goals-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 12px;
    }
    .active-goals-header h2 {
      color: var(--green);
      text-transform: uppercase;
      letter-spacing: .04em;
      margin-bottom: 8px;
    }
    .active-goals-header .panel-subtitle {
      margin: 0;
    }
    .active-goal-sort {
      flex: 0 0 auto;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      min-height: 34px;
      padding: 7px 12px;
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 999px;
      color: #b9c8d4;
      background: rgba(166, 184, 196, .10);
      font-size: 10px;
      font-weight: 950;
      letter-spacing: .04em;
      cursor: pointer;
    }
    .active-goal-sort:hover {
      border-color: rgba(0, 245, 41, .46);
      color: var(--green);
    }
    .active-goal-list {
      display: grid;
      gap: 6px;
    }
    .active-goal-row {
      display: grid;
      grid-template-columns: minmax(130px, 180px) minmax(130px, 1fr) 65px 100px 22px;
      gap: 8px;
      align-items: center;
      min-height: 25px;
      font-size: 12px;
    }
    .active-goal-label {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      color: var(--ink);
    }
    .active-goal-stars {
      color: #ffd11a;
      margin-right: 5px;
      letter-spacing: 1px;
      text-shadow: 0 0 12px rgba(255, 209, 26, .42);
    }
    .active-goal-track {
      position: relative;
      box-sizing: border-box;
      height: 24px;
      padding: 3px;
      border-radius: 7px;
      background: rgba(129, 151, 164, .18);
      overflow: hidden;
      border: 1px solid rgba(166, 184, 196, .16);
      box-shadow: inset 0 1px 2px rgba(0,0,0,.28);
    }
    .active-goal-fill {
      height: 100%;
      width: var(--w);
      min-width: 2px;
      border-radius: 4px;
      background: var(--blue);
      box-shadow: 0 0 18px rgba(56, 163, 255, .34);
    }
    .active-goal-network .active-goal-fill {
      background: var(--green);
      box-shadow: 0 0 18px rgba(0, 245, 41, .30);
    }
    .active-goal-network .active-goal-track {
      height: 32px;
      padding: 4px;
    }
    .active-goal-bar-value {
      position: absolute;
      z-index: 2;
      top: 50%;
      transform: translateY(-50%);
      color: #f5fbff;
      font-size: 10px;
      font-weight: 950;
      line-height: 1;
      text-shadow: 0 1px 3px rgba(0,0,0,.95);
      pointer-events: none;
    }
    .active-goal-bar-value.real { left: 8px; }
    .active-goal-bar-value.goal {
      right: 8px;
      display: none;
    }
    .active-goal-target {
      display: grid;
      align-items: center;
      justify-items: end;
      min-width: 0;
    }
    .active-goal-main-goal {
      color: #28b6ff;
      text-align: right;
      white-space: nowrap;
      font-size: 13px;
      font-weight: 950;
    }
    .active-goal-attainment {
      display: none;
      color: #28b6ff;
      text-align: right;
      white-space: nowrap;
      font-size: 13px;
      font-weight: 950;
    }
    .expanded-chart-clone .active-goal-bar-value.goal { display: block; }
    .expanded-chart-clone .active-goal-main-goal { display: none; }
    .expanded-chart-clone .active-goal-attainment { display: block; }
    .active-goal-growth {
      text-align: right;
      white-space: nowrap;
      font-weight: 900;
    }
    .active-goal-growth.positive { color: var(--green); }
    .active-goal-growth.negative { color: var(--red); }
    .active-goal-growth.stable { color: #ffd11a; }
    .active-goal-daily {
      text-align: center;
      font-size: 16px;
      font-weight: 950;
      line-height: 1;
    }
    .active-goal-daily.up { color: var(--green); }
    .active-goal-daily.down { color: var(--red); }
    .active-goal-daily.stable { color: #ffd11a; }
    .active-goal-daily.missing { color: var(--muted); }
    .active-goal-network {
      display: grid;
      grid-template-columns: minmax(130px, 180px) minmax(130px, 1fr) 65px 100px 22px;
      gap: 8px;
      align-items: center;
      margin-top: 10px;
      padding: 9px 0;
      border-top: 1px solid rgba(0, 245, 41, .38);
      border-radius: 10px;
      background: rgba(0, 245, 41, .10);
      font-size: 12px;
      font-weight: 900;
    }
    .active-goals-panel.active-only .active-goal-row,
    .active-goals-panel.active-only .active-goal-network {
      grid-template-columns: minmax(130px, 180px) minmax(130px, 1fr) 100px 22px;
    }
    .active-goal-network > strong {
      color: var(--green);
      text-transform: uppercase;
      text-align: center;
    }
    .aggregator-unique-panel {
      min-height: 0;
      margin-top: 0;
    }
    .aggregator-unique-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      margin-bottom: 10px;
    }
    .aggregator-unique-header h2 {
      margin-bottom: 4px;
      text-transform: uppercase;
      letter-spacing: .04em;
    }
    .aggregator-unique-legend {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      justify-content: flex-end;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      white-space: nowrap;
    }
    .aggregator-unique-legend span {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .aggregator-unique-legend i {
      width: 10px;
      height: 10px;
      border-radius: 3px;
      background: currentColor;
      box-shadow: 0 0 10px currentColor;
    }
    .aggregator-unique-legend .wellhub { color: #d8385e; }
    .aggregator-unique-legend .totalpass { color: #26d07c; }
    .aggregator-unique-list {
      display: grid;
      gap: 6px;
    }
    .aggregator-unique-row,
    .aggregator-unique-network {
      display: grid;
      grid-template-columns: minmax(120px, 170px) 54px minmax(150px, 1fr) 54px;
      gap: 6px;
      align-items: center;
      min-height: 25px;
      font-size: 12px;
    }
    .aggregator-unique-label {
      min-width: 0;
      color: var(--ink);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .aggregator-unique-track {
      position: relative;
      box-sizing: border-box;
      height: 24px;
      padding: 3px;
      border: 1px solid rgba(166, 184, 196, .16);
      border-radius: 7px;
      background: rgba(129, 151, 164, .18);
      box-shadow: inset 0 1px 2px rgba(0,0,0,.28);
      overflow: hidden;
    }
    .aggregator-unique-stack {
      display: flex;
      width: var(--w);
      height: 100%;
      min-width: 2px;
      border-radius: 4px;
      overflow: hidden;
    }
    .aggregator-unique-segment {
      display: flex;
      align-items: center;
      min-width: 0;
      height: 100%;
      overflow: hidden;
    }
    .aggregator-unique-segment.wellhub {
      background: #d8385e;
      box-shadow: 0 0 16px rgba(216, 56, 94, .34);
    }
    .aggregator-unique-segment.totalpass {
      background: #26d07c;
      box-shadow: 0 0 16px rgba(38, 208, 124, .34);
    }
    .aggregator-unique-user-value {
      position: absolute;
      z-index: 2;
      top: 50%;
      transform: translateY(-50%);
      padding: 2px 4px;
      border-radius: 4px;
      background: rgba(4, 17, 19, .58);
      color: #ffffff;
      font-size: 11px;
      font-weight: 950;
      line-height: 1;
      text-shadow: 0 1px 4px #000;
      pointer-events: none;
    }
    .aggregator-unique-user-value.wellhub { left: 7px; color: #fff4f7; }
    .aggregator-unique-user-value.totalpass { right: 7px; color: #effff7; }
    .aggregator-unique-access {
      white-space: nowrap;
      text-align: center;
      font-size: 11px;
      font-weight: 950;
    }
    .aggregator-unique-access.wellhub { color: #f04a72; }
    .aggregator-unique-access.totalpass { color: #26d07c; }
    .aggregator-unique-stars {
      color: #ffd11a;
      margin-right: 5px;
      letter-spacing: 1px;
      text-shadow: 0 0 12px rgba(255, 209, 26, .42);
    }
    .aggregator-unique-network {
      margin-top: 10px;
      padding: 9px 0;
      border-top: 1px solid rgba(0, 245, 41, .38);
      border-radius: 10px;
      background: rgba(0, 245, 41, .10);
    }
    .aggregator-unique-network > strong {
      color: var(--green);
      text-transform: uppercase;
      text-align: center;
    }
    .aggregator-unique-network .aggregator-unique-track {
      height: 32px;
      padding: 4px;
    }
    .active-unit-chart-pair .active-goal-row,
    .active-unit-chart-pair .active-goal-network {
      grid-template-columns: minmax(112px, 145px) minmax(130px, 1fr) 54px 84px 20px;
      gap: 5px;
      font-size: 12px;
    }
    .active-unit-chart-pair .active-goal-bar-value { font-size: 11px; }
    .active-unit-chart-pair .active-goal-attainment { font-size: 11px; }
    .active-unit-chart-pair .active-goal-growth { font-size: 11px; }
    .dual-legend,
    .multi-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      margin: -2px 0 10px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
    }
    .dual-legend span,
    .multi-legend span {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }
    .dual-legend span::before,
    .multi-legend span::before {
      content: "";
      width: 18px;
      height: 7px;
      border-radius: 99px;
      background: var(--legend-color);
    }
    .dual-row {
      align-items: center;
    }
    .dual-bars {
      display: grid;
      gap: 5px;
    }
    .dual-bars .bar-track {
      height: 10px;
    }
    .dual-bars .bar-track:first-child {
      height: 13px;
    }
    .dual-value {
      display: grid;
      gap: 2px;
      text-align: right;
      white-space: nowrap;
      font-weight: 900;
    }
    .dual-value small {
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
    }
    .chart-sales-ticket .bar-row {
      grid-template-columns: minmax(72px, 80px) minmax(0, 1fr) minmax(100px, 115px);
      gap: 8px;
    }
    .chart-sales-ticket .dual-value {
      width: auto;
    }
    .chart-cancel-units .bar-row {
      grid-template-columns: minmax(150px, 230px) minmax(0, 1fr) 150px;
      gap: 10px;
    }
    .multi-bars {
      display: grid;
      gap: 5px;
    }
    .multi-bars .bar-track {
      height: 11px;
    }
    .multi-value {
      display: grid;
      gap: 2px;
      text-align: right;
      white-space: nowrap;
      font-weight: 900;
      width: 150px;
    }
    .multi-value span {
      color: var(--value-color);
      font-size: 11px;
      line-height: 1.15;
    }
    .bar-value {
      text-align: right;
      font-weight: 900;
      white-space: nowrap;
    }
    .bar-value .bar-count {
      color: var(--text);
      font-weight: 500;
    }
    .bar-value strong {
      color: inherit;
      font-weight: 950;
      margin-left: 6px;
    }
    .bar-value.alert {
      color: var(--red);
    }
    /* Light glass dashboard theme inspired by the provided references. */
    :root {
      --bg: #eef3fb;
      --panel: rgba(255, 255, 255, .74);
      --panel-2: rgba(248, 250, 255, .86);
      --green: #21c98b;
      --blue: #2f9cf4;
      --red: #ff5d66;
      --orange: #ffbf38;
      --violet: #8368f4;
      --muted: #768196;
      --ink: #202638;
      --line: rgba(96, 116, 148, .16);
      --radius: 18px;
      --shadow: 0 24px 62px rgba(74, 94, 132, .14);
    }
    body {
      min-height: 100vh;
      color: var(--ink);
      background:
        linear-gradient(120deg, rgba(255, 210, 185, .72), rgba(238, 215, 255, .68) 42%, rgba(230, 242, 255, .88) 100%),
        linear-gradient(180deg, #f7fbff, #edf3fb);
      background-size: auto;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 28px;
      z-index: -1;
      border-radius: 34px;
      background: rgba(255, 255, 255, .36);
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .5), 0 28px 90px rgba(93, 110, 148, .18);
      pointer-events: none;
    }
    .topbar {
      position: sticky;
      top: 14px;
      width: min(1540px, calc(100vw - 48px));
      min-height: 68px;
      margin: 18px auto 0;
      padding: 10px 14px;
      border: 1px solid rgba(255, 255, 255, .72);
      border-bottom: 1px solid rgba(255, 255, 255, .72);
      border-radius: 28px;
      background: rgba(255, 255, 255, .68);
      box-shadow: 0 22px 58px rgba(75, 93, 130, .12);
      backdrop-filter: blur(24px);
    }
    .brand img {
      filter: none;
    }
    .tabs {
      gap: 8px;
    }
    .tabs button,
    .print-btn,
    .analyze-btn,
    .file-button,
    .apply-filters-btn,
    .isaias-chat button {
      min-height: 38px;
      border: 1px solid rgba(47, 156, 244, .16);
      border-radius: 14px;
      box-shadow: none;
      transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
    }
    .tabs button {
      color: #607086;
      background: rgba(255, 255, 255, .62);
    }
    .tabs button.active,
    .tabs button:hover {
      color: #fff;
      background: linear-gradient(135deg, #33a8ff, #236ff1);
      border-color: rgba(47, 156, 244, .32);
      box-shadow: 0 12px 26px rgba(47, 156, 244, .24);
      transform: translateY(-1px);
    }
    .header-upload {
      border-color: rgba(96, 116, 148, .14);
      background: rgba(247, 250, 255, .82);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.6);
    }
    .file-button,
    .analyze-btn,
    .print-btn,
    .apply-filters-btn,
    .isaias-chat button {
      color: #fff;
      background: linear-gradient(135deg, #32aaff, #236ff1);
      border-color: rgba(47, 156, 244, .3);
      box-shadow: 0 12px 26px rgba(47, 156, 244, .2);
    }
    .file-button:hover,
    .analyze-btn:hover,
    .print-btn:hover,
    .apply-filters-btn:hover,
    .isaias-chat button:hover {
      transform: translateY(-1px);
      box-shadow: 0 16px 30px rgba(47, 156, 244, .25);
    }
    .header-upload-status.ok {
      color: #10a875;
    }
    .header-upload-status.error {
      color: var(--red);
    }
    .shell {
      width: min(1540px, calc(100vw - 48px));
      padding-top: 18px;
    }
    .hero,
    .card,
    .panel,
    .composition-panel,
    .medal-board-panel,
    .brief-card,
    .benchmark-card,
    .cluster-unit-table-wrap {
      border: 1px solid rgba(255, 255, 255, .72);
      background: linear-gradient(145deg, rgba(255,255,255,.78), rgba(247,250,255,.62));
      box-shadow: var(--shadow);
      backdrop-filter: blur(22px);
    }
    .hero {
      padding: 22px 24px;
      border-radius: 30px;
      box-shadow: 0 26px 72px rgba(74, 94, 132, .14);
    }
    h1 {
      color: #202638;
      font-style: normal;
      font-size: clamp(28px, 2.2vw, 42px);
      text-shadow: none;
    }
    .source,
    .panel-subtitle,
    .card small,
    .brief-card p,
    .benchmark-card p,
    .isaias-chat p,
    .legend-row,
    .bar-label,
    .cluster-name small,
    .cluster-unit-cell small,
    .timeline-chart .axis {
      color: var(--muted);
    }
    .dashboard-filters {
      gap: 10px;
    }
    .filter-field span {
      color: #607086;
      font-size: 10px;
    }
    .filter-field input:not([type="checkbox"]),
    .filter-field select,
    .multi-select-toggle,
    .isaias-chat textarea {
      min-height: 38px;
      border: 1px solid rgba(96, 116, 148, .18);
      border-radius: 14px;
      color: #202638;
      background: rgba(255, 255, 255, .88);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.55);
    }
    .filter-field input:not([type="checkbox"]):focus,
    .filter-field select:focus,
    .multi-select-toggle:focus,
    .isaias-chat textarea:focus {
      border-color: rgba(47, 156, 244, .48);
      box-shadow: 0 0 0 4px rgba(47, 156, 244, .13);
    }
    .multi-select-menu {
      border-color: rgba(96, 116, 148, .18);
      background: rgba(255, 255, 255, .96);
      box-shadow: 0 18px 44px rgba(74, 94, 132, .18);
    }
    .multi-option {
      color: #202638;
    }
    .multi-option:hover {
      background: rgba(47, 156, 244, .1);
    }
    .card {
      min-height: 112px;
      padding: 18px;
      border-left: 0;
      position: relative;
      overflow: hidden;
    }
    .card::before {
      content: "";
      position: absolute;
      inset: 0 auto 0 0;
      width: 5px;
      background: var(--tone, var(--blue));
      opacity: .9;
    }
    .card span,
    .signal-card span,
    .brief-card span,
    .cluster-unit-table th {
      color: #6d7a8e;
    }
    .card strong,
    .panel h2,
    .brief-card h3,
    .benchmark-card h3,
    .isaias-chat h2,
    .isaias-sources h2,
    .cluster-value,
    .cluster-unit-name,
    .cluster-unit-cell strong,
    .cluster-unit-total,
    .bar-value,
    .multi-value,
    .legend-row strong {
      color: #202638;
      text-shadow: none;
    }
    .card strong {
      font-size: clamp(25px, 2vw, 34px);
      font-weight: 850;
      letter-spacing: 0;
    }
    .panel {
      padding: 18px;
      border-radius: 22px;
    }
    .panel h2 {
      font-size: 20px;
      letter-spacing: 0;
    }
    .bar-track,
    .cluster-track,
    .cluster-unit-mini-track {
      background: rgba(108, 125, 150, .16);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.55);
    }
    .bar-fill,
    .cluster-fill,
    .cluster-unit-mini-fill {
      box-shadow: 0 8px 18px color-mix(in srgb, var(--bar, var(--blue)), transparent 72%);
    }
    .donut {
      background: conic-gradient(var(--donut));
      box-shadow: 0 24px 50px rgba(47, 156, 244, .14);
    }
    .donut::after {
      background: rgba(255, 255, 255, .88);
      box-shadow: inset 0 0 0 1px rgba(96, 116, 148, .1);
    }
    .isaias-card-grid .card strong {
      color: #202638;
    }
    .isaias-answer,
    .cluster-unit-table-wrap,
    .line-canvas,
    .timeline-chart,
    .access-day-card {
      border-color: rgba(96, 116, 148, .14);
      background: rgba(255, 255, 255, .62);
      color: #202638;
    }
    .medal-board-panel {
      background: linear-gradient(145deg, rgba(255,255,255,.78), rgba(237,243,255,.72));
    }
    .medal-board-table {
      background: rgba(255,255,255,.42);
      border-radius: 18px;
      overflow: hidden;
    }
    .medal-row.head {
      background: linear-gradient(135deg, #2b6ff2, #32aaff);
      color: #fff;
    }
    .medal-row:nth-child(even):not(.head),
    .medal-row:nth-child(odd):not(.head) {
      background: rgba(255,255,255,.54);
    }
    .medal-row,
    .cluster-unit-table th,
    .cluster-unit-table td {
      border-color: rgba(96, 116, 148, .12);
    }
    .cluster-unit-table th {
      background: rgba(47, 156, 244, .07);
    }
    .timeline-line {
      filter: drop-shadow(0 8px 12px rgba(47, 156, 244, .12));
    }
    /* Dark BioFisic theme override: keeps the cleaner glass layout, but restores the academy identity. */
    :root {
      --bg: #050b0d;
      --panel: rgba(14, 27, 30, .90);
      --panel-2: rgba(7, 18, 21, .88);
      --green: #00f529;
      --blue: #36a8ff;
      --red: #ff514d;
      --orange: #ffbd22;
      --violet: #b16cff;
      --muted: #a9bac7;
      --ink: #f6fbff;
      --line: rgba(0, 245, 41, .28);
      --radius: 18px;
      --shadow: 0 24px 64px rgba(0, 0, 0, .38);
    }
    body {
      color: var(--ink);
      background:
        linear-gradient(rgba(0, 245, 41, .045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 245, 41, .045) 1px, transparent 1px),
        radial-gradient(circle at 78% 8%, rgba(0, 245, 41, .18), transparent 30%),
        radial-gradient(circle at 18% 18%, rgba(54, 168, 255, .12), transparent 26%),
        linear-gradient(180deg, #071113 0%, #03080a 100%);
      background-size: 84px 84px, 84px 84px, auto, auto, auto;
    }
    body::before {
      inset: 0;
      border-radius: 0;
      background: linear-gradient(115deg, rgba(0, 245, 41, .08), transparent 34%, rgba(54, 168, 255, .07));
      box-shadow: inset 0 0 120px rgba(0,0,0,.58);
    }
    .topbar {
      width: min(1540px, calc(100vw - 48px));
      min-height: 66px;
      margin: 14px auto 0;
      padding: 10px 14px;
      border: 1px solid rgba(0, 245, 41, .26);
      border-bottom: 1px solid rgba(0, 245, 41, .26);
      border-radius: 24px;
      background: rgba(13, 22, 24, .88);
      box-shadow: 0 24px 70px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.06);
      backdrop-filter: blur(18px);
    }
    .brand img {
      filter: drop-shadow(0 0 18px rgba(0, 245, 41, .34));
    }
    .tabs button {
      color: #d5e4ec;
      background: rgba(7, 18, 21, .86);
      border-color: rgba(0, 245, 41, .28);
    }
    .tabs button.active,
    .tabs button:hover {
      color: #021008;
      background: linear-gradient(135deg, #00f529, #18cf76);
      border-color: rgba(0, 245, 41, .76);
      box-shadow: 0 14px 28px rgba(0, 245, 41, .24);
    }
    .header-upload {
      border-color: rgba(0, 245, 41, .22);
      background: rgba(5, 15, 18, .76);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.035);
    }
    .file-button,
    .analyze-btn,
    .print-btn,
    .apply-filters-btn,
    .isaias-chat button {
      color: #021008;
      background: linear-gradient(135deg, #00f529, #21d981);
      border-color: rgba(0, 245, 41, .72);
      box-shadow: 0 14px 30px rgba(0, 245, 41, .20);
    }
    .file-button:hover,
    .analyze-btn:hover,
    .print-btn:hover,
    .apply-filters-btn:hover,
    .isaias-chat button:hover {
      box-shadow: 0 18px 36px rgba(0, 245, 41, .28);
    }
    .header-upload-status.ok {
      color: var(--green);
    }
    .hero,
    .card,
    .panel,
    .composition-panel,
    .medal-board-panel,
    .brief-card,
    .benchmark-card,
    .cluster-unit-table-wrap {
      border: 1px solid rgba(0, 245, 41, .22);
      background: linear-gradient(145deg, rgba(18, 31, 34, .90), rgba(7, 17, 20, .88));
      box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,.05);
      backdrop-filter: blur(18px);
    }
    .hero {
      border-radius: 28px;
      box-shadow: 0 30px 80px rgba(0,0,0,.38), 0 0 0 1px rgba(0,245,41,.08);
    }
    h1 {
      color: var(--green);
      font-style: italic;
      text-shadow: 0 0 22px rgba(0, 245, 41, .22);
    }
    .source,
    .panel-subtitle,
    .card small,
    .brief-card p,
    .benchmark-card p,
    .isaias-chat p,
    .legend-row,
    .bar-label,
    .cluster-name small,
    .cluster-unit-cell small,
    .timeline-chart .axis {
      color: var(--muted);
    }
    .filter-field span {
      color: var(--green);
    }
    .filter-field input:not([type="checkbox"]),
    .filter-field select,
    .multi-select-toggle,
    .isaias-chat textarea {
      color: var(--ink);
      background: rgba(5, 15, 18, .92);
      border-color: rgba(0, 245, 41, .24);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.035);
    }
    .filter-field input:not([type="checkbox"]):focus,
    .filter-field select:focus,
    .multi-select-toggle:focus,
    .isaias-chat textarea:focus {
      border-color: rgba(0, 245, 41, .62);
      box-shadow: 0 0 0 4px rgba(0, 245, 41, .12);
    }
    .multi-select-menu {
      background: rgba(8, 20, 23, .98);
      border-color: rgba(0, 245, 41, .28);
      box-shadow: 0 22px 52px rgba(0,0,0,.42);
    }
    .multi-option {
      color: var(--ink);
    }
    .multi-option:hover {
      background: rgba(0, 245, 41, .10);
    }
    .card::before {
      background: var(--tone, var(--green));
      box-shadow: 0 0 24px color-mix(in srgb, var(--tone, var(--green)), transparent 42%);
    }
    .card span,
    .signal-card span,
    .brief-card span,
    .cluster-unit-table th {
      color: #b6c9d5;
    }
    .card strong,
    .panel h2,
    .brief-card h3,
    .benchmark-card h3,
    .isaias-chat h2,
    .isaias-sources h2,
    .cluster-value,
    .cluster-unit-name,
    .cluster-unit-cell strong,
    .cluster-unit-total,
    .bar-value,
    .multi-value,
    .legend-row strong {
      color: var(--ink);
      text-shadow: 0 2px 0 rgba(255, 71, 71, .22);
    }
    .isaias-card-grid .card strong {
      color: var(--ink);
    }
    .bar-track,
    .cluster-track,
    .cluster-unit-mini-track {
      background: rgba(166, 184, 196, .18);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.045);
    }
    .donut {
      box-shadow: 0 26px 54px rgba(0,0,0,.28);
    }
    .donut::after {
      background: #071113;
      box-shadow: inset 0 0 0 1px rgba(0, 245, 41, .12);
    }
    .isaias-answer,
    .cluster-unit-table-wrap,
    .line-canvas,
    .timeline-chart,
    .access-day-card {
      border-color: rgba(0, 245, 41, .20);
      background: rgba(5, 15, 18, .78);
      color: var(--ink);
    }
    .medal-board-panel {
      background: linear-gradient(145deg, rgba(18, 31, 34, .92), rgba(7, 17, 20, .90));
    }
    .medal-board-table {
      background: rgba(3, 9, 11, .45);
    }
    .medal-row.head {
      background: linear-gradient(135deg, rgba(0,245,41,.95), rgba(54,168,255,.80));
      color: #031007;
    }
    .medal-row:nth-child(even):not(.head),
    .medal-row:nth-child(odd):not(.head) {
      background: rgba(255,255,255,.035);
    }
    .medal-row,
    .cluster-unit-table th,
    .cluster-unit-table td {
      border-color: rgba(0, 245, 41, .14);
    }
    .cluster-unit-table th {
      background: rgba(0, 245, 41, .08);
    }
    .timeline-line {
      filter: drop-shadow(0 8px 14px rgba(0, 245, 41, .12));
    }
    .hero {
      position: relative;
      z-index: 20;
      grid-template-columns: minmax(280px, 320px) minmax(0, 1fr);
      align-items: start;
      overflow: visible;
    }
    .hero-title {
      align-self: start;
      padding-top: 4px;
    }
    .source {
      max-width: 44ch;
      overflow-wrap: anywhere;
    }
    .dashboard-filters {
      grid-template-columns: minmax(175px, .9fr) minmax(210px, 1.15fr) minmax(180px, .95fr) 105px 115px;
      align-items: start;
      align-self: start;
      gap: 8px;
      width: 100%;
      max-width: 1030px;
      justify-self: end;
      position: relative;
    }
    .filter-field span {
      white-space: nowrap;
      line-height: 1;
    }
    .filter-field input:not([type="checkbox"]),
    .filter-field select,
    .multi-select-toggle {
      min-height: 36px;
      border-radius: 11px;
      padding-top: 7px;
      padding-bottom: 7px;
      font-size: 11px;
    }
    .apply-filters-btn {
      align-self: start;
      min-height: 38px;
      margin-top: 13px;
      border-radius: 12px;
      padding-inline: 14px;
    }
    .multi-select {
      z-index: 4;
    }
    .multi-select-menu {
      position: static;
      width: 100%;
      min-width: 0;
      max-height: 156px;
      margin-top: 7px;
      scrollbar-gutter: stable;
    }
    .multi-option {
      min-height: 24px;
      padding: 5px 6px;
      line-height: 1.15;
      white-space: normal;
    }
    .financial-matrix-panel {
      grid-column: 1 / -1;
      overflow: hidden;
    }
    .financial-matrix-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      margin-bottom: 14px;
    }
    .financial-month-control {
      display: grid;
      gap: 5px;
      min-width: 150px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 900;
      letter-spacing: .04em;
      text-transform: uppercase;
    }
    .financial-month-control select {
      border: 1px solid rgba(56, 163, 255, .34);
      border-radius: 10px;
      background: #142327;
      color: var(--text);
      padding: 9px 11px;
      font: inherit;
      cursor: pointer;
    }
    .financial-table-wrap {
      width: 100%;
      max-width: 100%;
      overflow-x: hidden;
      border: 1px solid rgba(56, 163, 255, .18);
      border-radius: 12px;
    }
    .financial-table {
      width: 100%;
      min-width: 0;
      table-layout: fixed;
      border-collapse: separate;
      border-spacing: 0;
      font-variant-numeric: tabular-nums;
    }
    .financial-table th,
    .financial-table td {
      min-width: 0;
      padding: 9px 2px;
      border-right: 1px solid rgba(255, 255, 255, .055);
      border-bottom: 1px solid rgba(255, 255, 255, .055);
      white-space: nowrap;
    }
    .financial-table thead th {
      position: sticky;
      top: 0;
      z-index: 2;
      background: #17282c;
      color: #a9bdc3;
      font-size: clamp(7px, .52vw, 9px);
      line-height: 1.18;
      text-align: center;
      text-transform: uppercase;
      letter-spacing: .015em;
      white-space: normal;
      overflow-wrap: anywhere;
    }
    .financial-table thead th:first-child,
    .financial-table tbody th:first-child {
      position: sticky;
      left: 0;
      z-index: 3;
      width: 18%;
      min-width: 0;
      text-align: left;
    }
    .financial-table thead th:first-child { z-index: 4; }
    .financial-table tbody th:first-child { background: #102024; }
    .financial-table td {
      min-width: 0;
      background: rgba(12, 28, 31, .56);
      color: #e9f5f7;
      font-size: clamp(7px, .54vw, 9px);
      letter-spacing: -.03em;
      font-weight: 750;
      text-align: center;
    }
    .financial-table .financial-network {
      background: rgba(0, 245, 41, .075);
      color: #4aff69;
      font-weight: 900;
    }
    .financial-indicator {
      display: grid;
      gap: 3px;
      color: #f2f8f9;
      font-size: 12px;
      line-height: 1.2;
      white-space: normal;
      overflow-wrap: anywhere;
      cursor: help;
    }
    .financial-indicator small {
      color: #748d94;
      font-size: 9px;
      font-weight: 800;
      letter-spacing: .04em;
    }
    .financial-section-row th {
      position: static !important;
      padding: 8px 12px;
      background: rgba(56, 163, 255, .12) !important;
      color: #60baff;
      font-size: 10px;
      font-weight: 900;
      letter-spacing: .08em;
      text-transform: uppercase;
    }
    .financial-data-row:hover th:first-child,
    .financial-data-row:hover td { background-color: rgba(56, 163, 255, .11); }
    .financial-note {
      margin-top: 10px;
      color: #789097;
      font-size: 10px;
      line-height: 1.5;
    }
    @media (max-width: 1240px) {
      .hero {
        grid-template-columns: 1fr;
        align-items: start;
      }
      .dashboard-filters {
        justify-self: stretch;
        max-width: none;
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
    }
    @media (max-width: 1080px) {
      .topbar { position: static; grid-template-columns: 1fr; }
      .brand, .tabs, .top-actions { grid-column: 1; justify-self: stretch; justify-content: center; }
      .header-upload { max-width: none; width: 100%; flex-wrap: wrap; }
      .header-upload-status { flex: 1 1 100%; max-width: none; text-align: center; }
      .grid, .active-summary, .active-unit-chart-pair, .active-chart-columns, .active-demographic-trio, .sales-month-contract-pair, .sales-primary-layout, .sales-chart-columns, .cancel-top-pair, .cancel-unit-retention-grid, .cancel-threshold-pair, .cancel-lower-grid, .financial-chart-pair, .frequency-main-grid, .frequency-pair-grid, .frequency-cluster-grid, .frequency-analysis-grid, .frequency-cluster-unit-final, .composition-panel, .isaias-hero, .isaias-grid, .analysis-executive { grid-template-columns: 1fr; }
      .churn-risk-unit-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .churn-risk-bands { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .churn-risk-donut-layout { grid-template-columns: 126px minmax(0, 1fr); }
      .churn-risk-unit-donut-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); grid-template-rows: auto; }
      .isaias-chat { position: static; }
      .overview, .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .active-footer-cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .isaias-card-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .brief-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .aggregator-cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .active-chart-grid .chart-active-units { grid-row: auto; }
      .active-goal-row,
      .active-goal-network { grid-template-columns: minmax(145px, 185px) minmax(140px, 1fr) 68px 108px 24px; }
      .aggregator-unique-row,
      .aggregator-unique-network { grid-template-columns: minmax(125px, 185px) 56px minmax(140px, 1fr) 56px; }
      .donut { width: 190px; justify-self: center; }
    }
    @media (max-width: 680px) {
      .shell { width: min(100vw - 20px, 1500px); }
      h1 { white-space: normal; }
      .period-range-fields { grid-template-columns: 1fr; }
      .overview, .cards, .aggregator-cards, .active-footer-cards { grid-template-columns: 1fr; }
      .sales-live-ticker { grid-template-columns: 1fr; }
      .sales-live-ticker-label { min-height: 32px; justify-content: center; }
      .sales-live-ticker-viewport { min-height: 50px; }
      .sales-live-ticker-item {
        min-width: 830px;
        grid-template-columns: 280px 170px 130px 90px 110px;
        gap: 12px;
        padding: 0 14px;
        font-size: 10px;
      }
      .churn-risk-header { display: grid; }
      .churn-risk-source { text-align: left; }
      .churn-risk-donut-legend { justify-content: flex-start; }
      .churn-risk-donut-layout { grid-template-columns: 1fr; }
      .churn-risk-network-slot .churn-risk-donut-card { min-height: 0; }
      .churn-risk-unit-donut-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .churn-risk-modal { padding: 8px; }
      .churn-risk-modal-dialog { width: 100%; max-height: 96vh; padding: 12px; }
      .churn-risk-modal-summary { grid-template-columns: 1fr; }
      .churn-risk-unit-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .churn-risk-bands,
      .churn-risk-rules { grid-template-columns: 1fr; }
      .isaias-signals,
      .isaias-card-grid,
      .brief-grid { grid-template-columns: 1fr; }
      .analysis-matrix .analysis-indicator-cell,
      .analysis-matrix thead th:first-child { width: 24%; min-width: 0; max-width: none; }
      .analysis-matrix th,
      .analysis-matrix td { padding-inline: 1px; }
      .analysis-alert-table { font-size: 7px; }
      .analysis-alert-table th,
      .analysis-alert-table td { padding: 6px 2px; }
      .bar-row { grid-template-columns: 1fr; gap: 5px; }
      .bar-value { text-align: left; }
      .chart-sales-success .bar-list { grid-template-columns: 1fr; }
      .chart-sales-success .bar-row { grid-template-columns: 1fr; }
      .chart-sales-success .bar-value { width: auto; }
      .cannibalization-header { align-items: stretch; flex-direction: column; }
      .cannibalization-period-control { align-self: stretch; }
      .cannibalization-period-control select { width: 100%; }
      .chart-cancel-cannibalization .bar-row { grid-template-columns: 1fr; }
      .chart-cancel-cannibalization .bar-value { text-align: left; }
      .cannibalization-total { justify-content: flex-start; flex-wrap: wrap; }
      .active-goals-header { align-items: stretch; flex-direction: column; }
      .active-goal-sort { align-self: flex-end; }
      .aggregator-unique-header { align-items: stretch; flex-direction: column; }
      .aggregator-unique-legend { justify-content: flex-start; }
      .active-goal-row {
        grid-template-columns: minmax(0, 1fr) 86px 98px 24px;
        grid-template-areas:
          "label attainment growth daily"
          "track track track track";
      }
      .active-goal-label { grid-area: label; }
      .active-goal-track { grid-area: track; }
      .active-goal-attainment { grid-area: attainment; }
      .active-goal-growth { grid-area: growth; }
      .active-goal-daily { grid-area: daily; }
      .active-goals-panel.active-only .active-goal-row,
      .active-goals-panel.active-only .active-goal-network {
        grid-template-columns: minmax(0, 1fr) 98px 24px;
        grid-template-areas:
          "label growth daily"
          "track track track";
      }
      .active-goals-panel.active-only .active-goal-label,
      .active-goals-panel.active-only .active-goal-track {
        grid-area: label;
      }
      .active-goals-panel.active-only .active-goal-track { grid-area: track; }
      .active-goal-network {
        grid-template-columns: minmax(0, 1fr) 86px 98px 24px;
        grid-template-areas:
          "label attainment growth daily"
          "track track track track";
      }
      .active-goal-network > strong { grid-area: label; }
      .aggregator-unique-row,
      .aggregator-unique-network {
        grid-template-columns: minmax(0, 1fr) 70px;
        grid-template-areas:
          "label total"
          "track track";
      }
      .aggregator-unique-label,
      .aggregator-unique-network > strong { grid-area: label; }
      .aggregator-unique-track { grid-area: track; }
      .aggregator-unique-total { grid-area: total; }
      .dashboard-filters { grid-template-columns: 1fr; }
      .medal-row { grid-template-columns: 42px minmax(130px, 1fr) repeat(4, minmax(48px, 1fr)); }
      .financial-matrix-header { display: grid; }
      .financial-month-control { width: 100%; }
      .financial-table thead th:first-child,
      .financial-table tbody th:first-child { width: 24%; min-width: 0; }
    }
    /* BioFisic workspace layout: light/dark themes and expandable visuals. */
    html[data-theme="light"] {
      --bg: #dfeceb;
      --panel: #ffffff;
      --panel-2: #f3f8f7;
      --green: #00e832;
      --blue: #2f8fd3;
      --red: #ed4f55;
      --orange: #00e832;
      --violet: #7858d7;
      --muted: #71817e;
      --ink: #263532;
      --line: rgba(48, 86, 80, .16);
      --radius: 16px;
      --shadow: 0 18px 46px rgba(43, 74, 70, .12);
      --sidebar: #365a55;
      --sidebar-2: #294743;
    }
    html[data-theme="dark"] {
      --bg: #171a19;
      --panel: #292d2c;
      --panel-2: #343837;
      --green: #00f529;
      --blue: #39a6e8;
      --red: #ff5b60;
      --orange: #00f529;
      --violet: #a98af2;
      --muted: #b7c3c0;
      --ink: #f7faf9;
      --line: rgba(0, 245, 41, .2);
      --radius: 16px;
      --shadow: 0 20px 52px rgba(0, 0, 0, .28);
      --sidebar: #252927;
      --sidebar-2: #1d211f;
    }
    html[data-theme] body {
      min-height: 100vh;
      color: var(--ink);
      background: var(--bg);
      background-size: auto;
      transition: color .22s ease, background .22s ease;
    }
    html[data-theme="light"] body {
      background:
        radial-gradient(circle at 4% 2%, rgba(0, 232, 50, .17), transparent 20%),
        radial-gradient(circle at 96% 92%, rgba(54, 90, 85, .12), transparent 28%),
        #dfeceb;
    }
    html[data-theme="dark"] body {
      background:
        radial-gradient(circle at 7% 4%, rgba(0, 245, 41, .10), transparent 22%),
        linear-gradient(140deg, #202422, #111412 72%);
    }
    html[data-theme] body::before {
      inset: 0;
      border-radius: 0;
      background: transparent;
      box-shadow: none;
    }
    html[data-theme] .topbar {
      position: fixed;
      inset: 18px auto 18px 18px;
      z-index: 80;
      width: 202px;
      min-height: 0;
      margin: 0;
      padding: 18px 14px;
      display: flex;
      flex-direction: column;
      align-items: stretch;
      gap: 16px;
      border: 1px solid rgba(255, 255, 255, .12);
      border-radius: 22px;
      color: #fff;
      background: linear-gradient(165deg, var(--sidebar), var(--sidebar-2));
      box-shadow: 0 24px 60px rgba(29, 57, 53, .25);
      backdrop-filter: blur(18px);
    }
    html[data-theme] .brand {
      order: 0;
      grid-column: auto;
      justify-self: auto;
      justify-content: center;
      min-width: 0;
      padding: 4px 0 8px;
    }
    html[data-theme] .brand img {
      width: 130px;
      max-height: 58px;
      filter: drop-shadow(0 7px 18px rgba(0,0,0,.2));
    }
    html[data-theme] .tabs {
      order: 1;
      grid-column: auto;
      width: 100%;
      display: grid;
      gap: 6px;
      overflow: visible;
    }
    html[data-theme] .tabs button {
      width: 100%;
      min-height: 42px;
      padding: 10px 12px;
      border: 0;
      border-radius: 11px;
      color: rgba(255,255,255,.82);
      background: transparent;
      box-shadow: none;
      text-align: left;
      font-size: 12px;
    }
    html[data-theme] .tabs button.active,
    html[data-theme] .tabs button:hover {
      color: #06200d;
      background: var(--green);
      border-color: transparent;
      box-shadow: 0 10px 24px rgba(0, 245, 41, .22);
      transform: none;
    }
    html[data-theme] .top-actions {
      order: 2;
      grid-column: auto;
      justify-self: auto;
      width: 100%;
      margin-top: auto;
      display: grid;
      gap: 8px;
    }
    html[data-theme] .header-upload {
      width: 100%;
      max-width: none;
      display: grid;
      gap: 7px;
      padding: 9px;
      border-color: rgba(255,255,255,.12);
      background: rgba(255,255,255,.07);
      box-shadow: none;
    }
    html[data-theme] .header-upload-status {
      width: 100%;
      max-width: none;
      color: rgba(255,255,255,.72);
      text-align: center;
    }
    html[data-theme] .file-button,
    html[data-theme] .analyze-btn,
    html[data-theme] .print-btn,
    html[data-theme] .apply-filters-btn,
    html[data-theme] .theme-toggle,
    html[data-theme] .isaias-chat button {
      width: 100%;
      min-height: 38px;
      border: 1px solid rgba(0, 245, 41, .44);
      border-radius: 10px;
      color: #06200d;
      background: var(--green);
      box-shadow: none;
      font-weight: 900;
      cursor: pointer;
    }
    html[data-theme] .theme-toggle {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      color: #fff;
      border-color: rgba(255,255,255,.18);
      background: rgba(255,255,255,.08);
    }
    .theme-toggle-icon { font-size: 17px; }
    html[data-theme] .shell {
      width: calc(100vw - 256px);
      max-width: none;
      margin: 0 20px 0 236px;
      padding: 18px 0 48px;
    }
    html[data-theme] .hero,
    html[data-theme] .card,
    html[data-theme] .panel,
    html[data-theme] .composition-panel,
    html[data-theme] .medal-board-panel,
    html[data-theme] .brief-card,
    html[data-theme] .benchmark-card,
    html[data-theme] .cluster-unit-table-wrap {
      border: 1px solid var(--line);
      color: var(--ink);
      background: var(--panel);
      box-shadow: var(--shadow);
      backdrop-filter: none;
    }
    html[data-theme] .hero {
      border-radius: 20px;
      box-shadow: var(--shadow);
    }
    html[data-theme] .brand-word { color: var(--green); text-shadow: none; }
    html[data-theme] .brand-sub,
    html[data-theme] .card strong,
    html[data-theme] .panel h2,
    html[data-theme] .brief-card h3,
    html[data-theme] .benchmark-card h3,
    html[data-theme] .isaias-chat h2,
    html[data-theme] .cluster-value,
    html[data-theme] .cluster-unit-name,
    html[data-theme] .cluster-unit-cell strong,
    html[data-theme] .cluster-unit-total,
    html[data-theme] .bar-value,
    html[data-theme] .multi-value,
    html[data-theme] .legend-row strong { color: var(--ink); text-shadow: none; }
    html[data-theme] .source,
    html[data-theme] .panel-subtitle,
    html[data-theme] .card small,
    html[data-theme] .brief-card p,
    html[data-theme] .benchmark-card p,
    html[data-theme] .isaias-chat p,
    html[data-theme] .legend-row,
    html[data-theme] .bar-label { color: var(--muted); }
    html[data-theme] .filter-field input:not([type="checkbox"]),
    html[data-theme] .filter-field select,
    html[data-theme] .multi-select-toggle,
    html[data-theme] .isaias-chat textarea,
    html[data-theme] .multi-select-menu,
    html[data-theme] .isaias-answer,
    html[data-theme] .line-canvas,
    html[data-theme] .timeline-chart,
    html[data-theme] .access-day-card {
      color: var(--ink);
      border-color: var(--line);
      background: var(--panel-2);
      box-shadow: none;
    }
    html[data-theme] .multi-select-toggle::after { color: var(--ink); }
    html[data-theme] .multi-option { color: var(--ink); }
    html[data-theme] .multi-option:hover { background: rgba(0, 232, 50, .12); }
    html[data-theme] .filter-popup {
      color: var(--ink);
      border-color: var(--line);
      background: var(--panel);
    }
    html[data-theme] .filter-popup-option,
    html[data-theme] .filter-popup-close,
    html[data-theme] .filter-popup-clear {
      color: var(--ink);
      border-color: var(--line);
      background: var(--panel-2);
    }
    html[data-theme] .bar-track,
    html[data-theme] .cluster-track,
    html[data-theme] .cluster-unit-mini-track { background: color-mix(in srgb, var(--muted), transparent 78%); }
    html[data-theme] .donut::after { background: var(--panel); }
    html[data-theme] .sales-live-ticker {
      border-color: var(--line);
      background: var(--panel);
    }
    html[data-theme] .sales-live-ticker-contract { color: var(--ink); }
    html[data-theme] .sales-live-ticker-value,
    html[data-theme] .analysis-matrix-delta.stable { color: var(--green); }
    html[data-theme="light"] .financial-table thead th,
    html[data-theme="light"] .analysis-matrix thead th,
    html[data-theme="light"] .medal-row.head { color: #fff; background: #3b5d58; }
    html[data-theme="light"] .financial-table tbody th:first-child,
    html[data-theme="light"] .financial-table td,
    html[data-theme="light"] .analysis-matrix .analysis-indicator-cell,
    html[data-theme="light"] .analysis-matrix td { color: var(--ink); background: #fff; }
    html[data-theme="light"] .financial-section-row th,
    html[data-theme="light"] .analysis-matrix-section td { color: #075e20; background: rgba(0, 232, 50, .12) !important; }
    html[data-theme="light"] .network-column,
    html[data-theme="light"] .financial-network { color: #075e20 !important; background: rgba(0, 232, 50, .1) !important; }
    html[data-theme="dark"] .financial-table thead th,
    html[data-theme="dark"] .analysis-matrix thead th { color: #edfff1; background: #34443f; }
    html[data-theme="dark"] .financial-table tbody th:first-child,
    html[data-theme="dark"] .financial-table td,
    html[data-theme="dark"] .analysis-matrix .analysis-indicator-cell,
    html[data-theme="dark"] .analysis-matrix td { color: var(--ink); background: #272d2b; }
    html[data-theme="dark"] .financial-section-row th,
    html[data-theme="dark"] .analysis-matrix-section td { color: var(--green); background: rgba(0,245,41,.1) !important; }
    .has-chart-expand { position: relative; padding-top: 52px !important; }
    .chart-expand-button {
      position: absolute;
      top: 12px;
      left: 14px;
      z-index: 8;
      width: 30px;
      height: 30px;
      display: grid;
      place-items: center;
      padding: 0;
      border: 1px solid var(--line);
      border-radius: 9px;
      color: var(--ink);
      background: var(--panel-2);
      cursor: pointer;
      transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
    }
    .chart-expand-button:hover {
      transform: scale(1.06);
      border-color: var(--green);
      box-shadow: 0 8px 20px rgba(0,245,41,.16);
    }
    .chart-expand-button svg { width: 17px; height: 17px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
    .chart-expand-modal {
      position: fixed;
      inset: 0;
      z-index: 500;
      display: grid;
      place-items: center;
      padding: 22px;
      background: rgba(9, 17, 15, .76);
      backdrop-filter: blur(12px);
    }
    .chart-expand-modal[hidden] { display: none; }
    .chart-expand-dialog {
      width: min(1840px, 97vw);
      height: min(930px, 94vh);
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      overflow: hidden;
      border: 1px solid rgba(0, 245, 41, .36);
      border-radius: 22px;
      color: var(--ink);
      background: var(--bg);
      box-shadow: 0 34px 110px rgba(0,0,0,.44);
    }
    .chart-expand-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      min-height: 58px;
      padding: 12px 16px 12px 22px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    .chart-expand-head h2 { margin: 0; color: var(--ink); font-size: 18px; text-transform: uppercase; }
    .chart-expand-close {
      width: 36px;
      height: 36px;
      border: 1px solid var(--line);
      border-radius: 50%;
      color: var(--ink);
      background: var(--panel-2);
      font-size: 24px;
      line-height: 1;
      cursor: pointer;
    }
    .chart-expand-content { min-height: 0; padding: 16px; overflow: auto; }
    .expanded-chart-clone {
      width: 100%;
      min-height: 100%;
      margin: 0 !important;
      padding: 24px !important;
      font-size: 1.08em;
    }
    .expanded-chart-clone .bar-list,
    .expanded-chart-clone .multi-bars { gap: 11px; }
    body.chart-modal-open { overflow: hidden; }
    html:has(body.chart-modal-open) { overflow: hidden; }
    @media (max-width: 1100px) {
      html[data-theme] .topbar {
        position: sticky;
        inset: auto;
        top: 8px;
        width: calc(100vw - 24px);
        min-height: 0;
        margin: 8px auto 0;
        padding: 10px 12px;
        display: grid;
        grid-template-columns: auto minmax(0, 1fr);
        border-radius: 18px;
      }
      html[data-theme] .brand { grid-column: 1; grid-row: 1; padding: 0; }
      html[data-theme] .brand img { width: 92px; }
      html[data-theme] .tabs { grid-column: 2; grid-row: 1; display: flex; overflow-x: auto; }
      html[data-theme] .tabs button { width: auto; min-height: 36px; padding: 8px 10px; text-align: center; }
      html[data-theme] .top-actions { grid-column: 1 / -1; grid-row: 2; display: flex; margin: 0; }
      html[data-theme] .header-upload { display: flex; width: auto; flex: 1; }
      html[data-theme] .theme-toggle,
      html[data-theme] .print-btn { width: auto; }
      html[data-theme] .shell { width: calc(100vw - 24px); margin: 0 auto; padding-top: 12px; }
    }
    @media (max-width: 680px) {
      html[data-theme] .topbar { display: flex; flex-direction: column; }
      html[data-theme] .tabs { width: 100%; }
      html[data-theme] .top-actions { width: 100%; flex-wrap: wrap; }
      html[data-theme] .header-upload { flex-basis: 100%; }
      .chart-expand-modal { padding: 6px; }
      .chart-expand-dialog { width: 100%; height: 97vh; border-radius: 14px; }
      .chart-expand-content { padding: 8px; }
      .expanded-chart-clone { padding: 16px !important; }
    }
    /* BioFisic Analytics 2026: horizontal executive workspace based on the supplied reference. */
    html[data-theme="dark"] {
      --bg: #050505;
      --panel: #232626;
      --panel-2: #323636;
      --green: #00e85a;
      --blue: #2d76ff;
      --red: #ff4d68;
      --orange: #00e85a;
      --violet: #933fe6;
      --muted: #aeb7b5;
      --ink: #f4f8ff;
      --line: rgba(190, 201, 198, .17);
      --radius: 13px;
      --shadow: none;
    }
    html[data-theme="light"] {
      --bg: #eef4f8;
      --panel: #ffffff;
      --panel-2: #f5f8fb;
      --green: #00bf4d;
      --blue: #256fed;
      --red: #e7435c;
      --orange: #00bf4d;
      --violet: #8436d9;
      --muted: #687b8f;
      --ink: #0c1c2f;
      --line: rgba(36, 70, 108, .16);
      --radius: 13px;
      --shadow: 0 8px 24px rgba(19, 48, 78, .06);
    }
    html[data-theme] body {
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      color: var(--ink);
      background: var(--bg);
      background-image: none;
    }
    html[data-theme="dark"] body {
      background:
        radial-gradient(circle at 82% -20%, rgba(0, 232, 90, .07), transparent 34%),
        #050505;
    }
    html[data-theme="light"] body {
      background:
        radial-gradient(circle at 84% -18%, rgba(0, 191, 77, .08), transparent 32%),
        #eef4f8;
    }
    html[data-theme] .topbar {
      position: sticky;
      inset: auto;
      top: 0;
      z-index: 90;
      width: 100%;
      min-height: 74px;
      margin: 0;
      padding: 0 22px;
      display: grid;
      grid-template-columns: 230px minmax(0, 1fr) auto;
      align-items: center;
      gap: 28px;
      border: 0;
      border-bottom: 1px solid var(--line);
      border-radius: 0;
      color: var(--ink);
      background: color-mix(in srgb, var(--bg) 92%, transparent);
      box-shadow: none;
      backdrop-filter: blur(18px);
    }
    html[data-theme] .brand {
      order: 0;
      grid-column: 1;
      grid-row: 1;
      min-width: 0;
      padding: 0;
      display: flex;
      align-items: baseline;
      justify-content: start;
      gap: 10px;
      line-height: 1;
    }
    .brand-mark {
      color: var(--green);
      font-size: 28px;
      font-weight: 1000;
      letter-spacing: -.045em;
    }
    .brand-analytics {
      margin-top: 0;
      color: var(--ink);
      font-size: 28px;
      font-weight: 400;
      font-style: italic;
      letter-spacing: -.035em;
    }
    html[data-theme] .tabs {
      order: 1;
      grid-column: 2;
      grid-row: 1;
      width: 100%;
      display: flex;
      align-items: stretch;
      gap: 30px;
      justify-content: center;
      overflow-x: auto;
      scrollbar-width: none;
    }
    html[data-theme] .tabs::-webkit-scrollbar { display: none; }
    html[data-theme] .tabs button {
      position: relative;
      width: auto;
      min-height: 73px;
      padding: 5px 0;
      border: 0;
      border-radius: 0;
      color: var(--muted);
      background: transparent;
      box-shadow: none;
      font-size: 14px;
      font-weight: 800;
      text-align: center;
      white-space: nowrap;
    }
    html[data-theme] .tabs button::after {
      content: "";
      position: absolute;
      right: 0;
      bottom: 0;
      left: 0;
      height: 2px;
      border-radius: 2px 2px 0 0;
      background: transparent;
    }
    html[data-theme] .tabs button.active,
    html[data-theme] .tabs button:hover {
      color: var(--ink);
      background: transparent;
      box-shadow: none;
      transform: none;
    }
    html[data-theme] .tabs button.active::after { background: var(--green); }
    .header-tools {
      grid-column: 3;
      grid-row: 1;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
    }
    html[data-theme] .header-tools .theme-toggle {
      width: 34px;
      min-height: 34px;
      padding: 0;
      border: 1px solid var(--line);
      border-radius: 9px;
      color: var(--ink);
      background: var(--panel);
    }
    .header-tools .theme-toggle-label { display: none; }
    .header-tools .theme-toggle-icon { font-size: 15px; }
    .header-notification {
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      color: var(--muted);
    }
    .header-notification svg {
      width: 18px;
      height: 18px;
      fill: none;
      stroke: currentColor;
      stroke-width: 1.8;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    .header-avatar {
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      border-radius: 50%;
      color: #021409;
      background: var(--green);
      font-size: 11px;
      font-weight: 1000;
    }
    html[data-theme] .shell {
      width: min(1820px, calc(100vw - 36px));
      max-width: none;
      margin: 0 auto;
      padding: 12px 0 36px;
    }
    html[data-theme] .hero {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      align-items: end;
      gap: 14px;
      margin: 0 0 12px;
      padding: 9px 10px;
      border: 1px solid var(--line);
      border-radius: 12px;
      color: var(--ink);
      background: var(--panel);
      box-shadow: var(--shadow);
    }
    html[data-theme] .hero-title {
      position: absolute;
      width: 1px;
      height: 1px;
      overflow: hidden;
      clip: rect(0 0 0 0);
      clip-path: inset(50%);
    }
    html[data-theme] .dashboard-filters {
      display: grid;
      grid-template-columns: minmax(180px, 1.25fr) minmax(145px, .9fr) minmax(145px, .9fr) minmax(112px, .65fr) auto;
      gap: 8px;
      align-items: end;
      justify-self: stretch;
      width: 100%;
    }
    html[data-theme] .filter-field { gap: 3px; }
    html[data-theme] .filter-field span {
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      text-transform: none;
    }
    html[data-theme] .filter-field:first-child span { color: var(--green); }
    html[data-theme] .filter-field input:not([type="checkbox"]),
    html[data-theme] .filter-field select,
    html[data-theme] .multi-select-toggle {
      min-height: 42px;
      padding: 9px 30px 9px 11px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--ink);
      background: var(--panel-2);
      box-shadow: none;
      font-size: 13px;
      font-weight: 800;
    }
    html[data-theme] .filter-field input:not([type="checkbox"]):focus,
    html[data-theme] .filter-field select:focus,
    html[data-theme] .multi-select-toggle:focus {
      border-color: var(--green);
      box-shadow: 0 0 0 2px color-mix(in srgb, var(--green), transparent 80%);
    }
    html[data-theme] .apply-filters-btn {
      width: auto;
      min-height: 42px;
      padding: 9px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--muted);
      background: transparent;
      box-shadow: none;
      font-size: 12px;
      font-weight: 800;
    }
    html[data-theme] .hero-actions {
      display: flex;
      align-items: flex-end;
      justify-content: flex-end;
      gap: 8px;
      min-width: max-content;
    }
    html[data-theme] .hero-actions .header-upload {
      width: auto;
      max-width: none;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0;
      border: 0;
      background: transparent;
    }
    html[data-theme] .hero-actions .header-upload-status {
      position: relative;
      width: auto;
      min-width: 0;
      max-width: 156px;
      padding-left: 10px;
      color: var(--muted);
      font-size: 11px;
      text-align: right;
    }
    html[data-theme] .hero-actions .header-upload-status::before {
      content: "";
      position: absolute;
      left: 0;
      top: 50%;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--green);
      transform: translateY(-50%);
      box-shadow: 0 0 8px color-mix(in srgb, var(--green), transparent 30%);
    }
    html[data-theme] .hero-actions .analyze-btn,
    html[data-theme] .hero-actions .print-btn {
      width: auto;
      min-height: 42px;
      padding: 9px 16px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 850;
      white-space: nowrap;
    }
    html[data-theme] .hero-actions .analyze-btn {
      color: var(--green);
      border: 1px solid color-mix(in srgb, var(--green), transparent 48%);
      background: transparent;
    }
    html[data-theme] .hero-actions .print-btn {
      color: #021409;
      border: 1px solid var(--green);
      background: var(--green);
    }
    .summary-strip {
      display: grid;
      gap: 10px;
      padding: 11px 12px 12px;
      border: 1px solid var(--line);
      border-radius: 13px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }
    .summary-strip-head {
      display: flex;
      align-items: baseline;
      gap: 9px;
    }
    .summary-strip-head strong {
      color: var(--green);
      font-size: 12px;
      font-weight: 950;
      letter-spacing: .01em;
    }
    .summary-strip-head small {
      color: var(--muted);
      font-size: 9px;
      font-weight: 700;
    }
    html[data-theme] .cards {
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 9px;
    }
    html[data-theme] .active-card-grid { grid-template-columns: repeat(6, minmax(0, 1fr)); }
    html[data-theme] .card {
      min-height: 102px;
      padding: 12px;
      display: grid;
      grid-template-columns: 36px minmax(0, 1fr);
      grid-template-rows: auto auto minmax(18px, 1fr);
      column-gap: 9px;
      align-content: start;
      border: 1px solid var(--line);
      border-left: 1px solid var(--line);
      border-radius: 10px;
      color: var(--ink);
      background: var(--panel-2);
      box-shadow: none;
      overflow: hidden;
    }
    html[data-theme] .card::before { display: none; }
    .card-icon {
      grid-column: 1;
      grid-row: 1 / span 2;
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      border: 1px solid color-mix(in srgb, var(--tone), transparent 66%);
      border-radius: 50%;
      color: var(--tone);
      background: color-mix(in srgb, var(--tone), transparent 86%);
      font-size: 11px;
      font-weight: 1000;
    }
    html[data-theme] .card .card-label {
      grid-column: 2;
      grid-row: 1;
      color: var(--muted);
      font-size: 9px;
      font-weight: 850;
      letter-spacing: .02em;
      line-height: 1.15;
      text-transform: uppercase;
    }
    html[data-theme] .card .card-value,
    html[data-theme] .card > strong {
      grid-column: 2;
      grid-row: 2;
      margin: 4px 0 0;
      color: var(--ink);
      font-size: clamp(22px, 1.65vw, 30px);
      font-weight: 900;
      line-height: 1;
      letter-spacing: -.035em;
      text-shadow: none;
    }
    html[data-theme] .card > small,
    html[data-theme] .card .card-subtitle,
    html[data-theme] .card-foot {
      grid-column: 1 / -1;
      grid-row: 3;
      align-self: end;
      margin-top: 8px;
      padding-top: 7px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 9px;
      line-height: 1.25;
    }
    html[data-theme] .card-foot { display: flex; }
    html[data-theme] .card-foot + small {
      grid-row: 4;
      margin-top: 0;
      border-top: 0;
    }
    html[data-theme] .card-foot .card-metric { font-size: 10px; }
    html[data-theme] .peak-sales-card { grid-template-rows: auto auto auto; }
    html[data-theme] .peak-sales-card .card-subtitle {
      grid-column: 2;
      grid-row: 2;
      margin: 3px 0 0;
      padding: 0;
      border: 0;
    }
    html[data-theme] .peak-sales-card .peak-sales-body {
      grid-column: 1 / -1;
      grid-row: 3;
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid var(--line);
    }
    html[data-theme] .active-card-grid {
      grid-template-columns: repeat(5, minmax(0, 1fr));
    }
    html[data-theme] .active-card-grid .card {
      min-height: 142px;
    }
    html[data-theme] .active-footer-cards {
      grid-template-columns: repeat(6, minmax(0, 1fr));
      margin-top: 0;
    }
    html[data-theme] .tab-panel.active { gap: 10px; }
    html[data-theme] .grid,
    html[data-theme] .sales-primary-layout,
    html[data-theme] .sales-chart-columns,
    html[data-theme] .frequency-main-grid,
    html[data-theme] .frequency-pair-grid,
    html[data-theme] .frequency-cluster-grid,
    html[data-theme] .cancel-layout,
    html[data-theme] .cancel-top-pair,
    html[data-theme] .cancel-unit-retention-grid,
    html[data-theme] .cancel-retention-stack,
    html[data-theme] .cancel-threshold-pair,
    html[data-theme] .financial-chart-pair,
    html[data-theme] .sales-month-contract-pair,
    html[data-theme] .active-demographic-trio { gap: 10px; }
    .active-overview-trio {
      display: grid;
      grid-template-columns: minmax(0, 1.18fr) minmax(300px, .84fr) minmax(0, 1.18fr);
      gap: 10px;
      align-items: stretch;
    }
    .active-overview-trio > .panel { min-width: 0; height: 100%; }
    .active-overview-trio .composition-panel {
      grid-template-columns: 1fr;
      align-content: start;
      justify-items: center;
    }
    .active-overview-trio .composition-title {
      width: 100%;
      text-align: left;
    }
    .active-overview-trio .composition-copy { width: 100%; }
    .active-overview-trio .donut { width: min(210px, 72%); }
    html[data-theme] .panel,
    html[data-theme] .composition-panel,
    html[data-theme] .medal-board-panel,
    html[data-theme] .brief-card,
    html[data-theme] .benchmark-card,
    html[data-theme] .cluster-unit-table-wrap {
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 13px;
      color: var(--ink);
      background: var(--panel);
      box-shadow: var(--shadow);
      backdrop-filter: none;
    }
    html[data-theme] .panel h2,
    html[data-theme] .composition-title,
    html[data-theme] .composition-copy h2,
    html[data-theme] .financial-matrix-header h2 {
      color: var(--ink);
      font-size: 14px;
      font-weight: 900;
      letter-spacing: 0;
      text-transform: uppercase;
    }
    html[data-theme] .panel-subtitle,
    html[data-theme] .composition-copy p {
      color: var(--muted);
      font-size: 10px;
      line-height: 1.35;
    }
    html[data-theme] .bar-track,
    html[data-theme] .cluster-track,
    html[data-theme] .cluster-unit-mini-track,
    html[data-theme] .active-goal-track,
    html[data-theme] .aggregator-unique-track {
      border-color: var(--line);
      background: var(--panel-2);
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.015);
    }
    html[data-theme] .bar-fill,
    html[data-theme] .cluster-fill,
    html[data-theme] .cluster-unit-mini-fill { box-shadow: none; }
    html[data-theme] .active-goal-fill { background: var(--blue); box-shadow: none; }
    html[data-theme] .active-goal-network .active-goal-fill { background: var(--green); }
    html[data-theme] .donut {
      box-shadow: inset 0 0 0 1px rgba(255,255,255,.04);
    }
    html[data-theme] .donut::after {
      background: var(--panel);
      box-shadow: inset 0 0 0 1px var(--line);
    }
    html[data-theme] .legend-row,
    html[data-theme] .bar-label,
    html[data-theme] .active-goal-label,
    html[data-theme] .aggregator-unique-label { color: var(--muted); }
    html[data-theme] .financial-table,
    html[data-theme] .analysis-matrix,
    html[data-theme] .churn-risk-table,
    html[data-theme] .cluster-unit-table { color: var(--ink); }
    html[data-theme] .financial-table thead th,
    html[data-theme] .analysis-matrix thead th,
    html[data-theme] .churn-risk-table thead th,
    html[data-theme] .cluster-unit-table th {
      color: var(--muted);
      background: var(--panel-2);
    }
    html[data-theme] .financial-table tbody th:first-child,
    html[data-theme] .financial-table td,
    html[data-theme] .analysis-matrix .analysis-indicator-cell,
    html[data-theme] .analysis-matrix td,
    html[data-theme] .churn-risk-table td,
    html[data-theme] .cluster-unit-table td {
      color: var(--ink);
      border-color: var(--line);
      background: var(--panel);
    }
    html[data-theme] .financial-section-row th,
    html[data-theme] .analysis-matrix-section td {
      color: var(--green);
      background: color-mix(in srgb, var(--green), transparent 90%) !important;
    }
    html[data-theme] .network-column,
    html[data-theme] .financial-network {
      color: var(--green) !important;
      background: color-mix(in srgb, var(--green), transparent 92%) !important;
    }
    html[data-theme] .sales-live-ticker {
      min-height: 42px;
      border-radius: 10px;
      border-color: var(--line);
      background: var(--panel);
      box-shadow: none;
    }
    html[data-theme] .sales-live-ticker-label {
      color: #021409;
      background: var(--green);
    }
    html[data-theme] .sales-live-ticker-contract { color: var(--ink); }
    html[data-theme] .has-chart-expand { padding-top: 46px !important; }
    html[data-theme] .chart-expand-button {
      top: 11px;
      left: 12px;
      width: 26px;
      height: 26px;
      border-radius: 7px;
      color: var(--muted);
      background: var(--panel-2);
    }
    html[data-theme] .chart-expand-button svg { width: 14px; height: 14px; }
    html[data-theme] .chart-expand-dialog {
      border-color: var(--line);
      border-radius: 16px;
      background: var(--bg);
    }
    html[data-theme] .chart-expand-head { background: var(--panel); }
    html[data-theme] .multi-select-menu,
    html[data-theme] .filter-popup,
    html[data-theme] .filter-popup-option,
    html[data-theme] .filter-popup-close,
    html[data-theme] .filter-popup-clear {
      color: var(--ink);
      border-color: var(--line);
      background: var(--panel);
    }
    @media (max-width: 1450px) {
      html[data-theme] .topbar { grid-template-columns: 205px minmax(0, 1fr) auto; gap: 16px; }
      html[data-theme] .tabs { gap: 20px; }
      html[data-theme] .hero { grid-template-columns: 1fr; align-items: stretch; }
      html[data-theme] .hero-actions { justify-content: flex-end; }
      html[data-theme] .active-card-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .active-overview-trio { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .active-overview-trio .composition-panel { grid-column: 1 / -1; }
    }
    @media (max-width: 900px) {
      html[data-theme] .topbar {
        min-height: 0;
        padding: 10px 12px 0;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 8px 14px;
      }
      html[data-theme] .brand { grid-column: 1; grid-row: 1; }
      html[data-theme] .header-tools { grid-column: 2; grid-row: 1; }
      html[data-theme] .tabs { grid-column: 1 / -1; grid-row: 2; }
      html[data-theme] .tabs button { min-height: 40px; }
      html[data-theme] .shell { width: calc(100vw - 20px); padding-top: 10px; }
      html[data-theme] .dashboard-filters { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      html[data-theme] .apply-filters-btn { width: 100%; }
      html[data-theme] .active-card-grid,
      html[data-theme] .active-footer-cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .active-overview-trio,
      html[data-theme] .active-demographic-trio,
      html[data-theme] .grid,
      html[data-theme] .sales-primary-layout,
      html[data-theme] .sales-chart-columns,
      html[data-theme] .frequency-main-grid,
      html[data-theme] .frequency-pair-grid,
      html[data-theme] .frequency-cluster-grid,
      html[data-theme] .frequency-analysis-grid,
      html[data-theme] .frequency-cluster-unit-final,
      html[data-theme] .cancel-top-pair,
      html[data-theme] .cancel-unit-retention-grid,
      html[data-theme] .cancel-threshold-pair,
      html[data-theme] .financial-chart-pair,
      html[data-theme] .sales-month-contract-pair { grid-template-columns: 1fr; }
      .active-overview-trio .composition-panel { grid-column: auto; }
    }
    @media (max-width: 560px) {
      html[data-theme] .hero-actions { align-items: stretch; flex-wrap: wrap; }
      html[data-theme] .hero-actions .header-upload { width: 100%; justify-content: space-between; }
      html[data-theme] .dashboard-filters { grid-template-columns: 1fr; }
      html[data-theme] .active-card-grid,
      html[data-theme] .active-footer-cards,
      html[data-theme] .cards { grid-template-columns: 1fr; }
      .summary-strip-head { display: grid; gap: 2px; }
    }
    /* Visual zoom and high-contrast chart system. Business calculations remain unchanged. */
    html[data-theme] .panel,
    html[data-theme] .composition-panel,
    html[data-theme] .medal-board-panel {
      padding: 18px;
    }
    html[data-theme] .panel h2,
    html[data-theme] .composition-title,
    html[data-theme] .composition-copy h2,
    html[data-theme] .financial-matrix-header h2 {
      font-size: 16px;
      line-height: 1.18;
    }
    html[data-theme] .panel-subtitle,
    html[data-theme] .composition-copy p {
      font-size: 11.5px;
      line-height: 1.45;
    }
    html[data-theme] .bar-list,
    html[data-theme] .active-goal-list,
    html[data-theme] .aggregator-unique-list { gap: 8px; }
    html[data-theme] .bar-row {
      min-height: 27px;
      font-size: 13px;
    }
    html[data-theme] .bar-label,
    html[data-theme] .bar-value,
    html[data-theme] .dual-value,
    html[data-theme] .multi-value,
    html[data-theme] .column-label,
    html[data-theme] .column-value,
    html[data-theme] .stacked-label,
    html[data-theme] .cluster-name,
    html[data-theme] .cluster-value,
    html[data-theme] .legend-row {
      font-size: 12.5px;
      font-variant-numeric: tabular-nums;
    }
    html[data-theme] .bar-value,
    html[data-theme] .dual-value,
    html[data-theme] .multi-value,
    html[data-theme] .column-value,
    html[data-theme] .cluster-value,
    html[data-theme] .legend-row strong {
      color: var(--ink);
      font-weight: 900;
      text-shadow: 0 1px 10px color-mix(in srgb, var(--blue), transparent 78%);
    }
    html[data-theme] .bar-track { height: 14px; }
    html[data-theme] .active-goal-row,
    html[data-theme] .active-goal-network {
      min-height: 29px;
      font-size: 12.5px;
    }
    html[data-theme] .aggregator-unique-row,
    html[data-theme] .aggregator-unique-network {
      min-height: 29px;
      font-size: 12.5px;
    }
    html[data-theme] .active-goal-track,
    html[data-theme] .aggregator-unique-track { height: 27px; }
    html[data-theme] .active-goal-bar-value,
    html[data-theme] .aggregator-unique-user-value,
    html[data-theme] .aggregator-unique-access { font-size: 11.5px; font-weight: 950; }
    html[data-theme] .line-axis-label { font-size: 12px; fill: var(--muted); }
    html[data-theme] .line-legend,
    html[data-theme] .multi-legend,
    html[data-theme] .column-legend,
    html[data-theme] .stacked-legend { font-size: 12px; }
    .donut-shell {
      position: relative;
      width: min(250px, 100%);
      aspect-ratio: 1;
      justify-self: center;
    }
    .donut-shell .donut { width: 100% !important; height: 100%; }
    .donut::after { z-index: 1; }
    .donut-center {
      position: absolute;
      inset: 31%;
      z-index: 2;
      display: grid;
      place-content: center;
      gap: 4px;
      color: var(--ink);
      text-align: center;
      pointer-events: none;
    }
    .donut-center strong {
      font-size: clamp(17px, 1.45vw, 26px);
      font-weight: 950;
      line-height: 1;
      letter-spacing: -.035em;
      font-variant-numeric: tabular-nums;
    }
    .donut-center span {
      color: var(--muted);
      font-size: 9px;
      font-weight: 800;
      line-height: 1.15;
    }
    .active-overview-trio .donut-shell { width: min(250px, 78%); }
    html[data-theme="dark"] .panel,
    html[data-theme="dark"] .composition-panel,
    html[data-theme="dark"] .summary-strip,
    html[data-theme="dark"] .card {
      background: linear-gradient(145deg, #292d2c 0%, #232626 100%);
      border-color: rgba(190, 201, 198, .17);
    }
    html[data-theme="dark"] .bar-track,
    html[data-theme="dark"] .active-goal-track,
    html[data-theme="dark"] .aggregator-unique-track,
    html[data-theme="dark"] .cluster-track {
      background: #343938;
      border-color: rgba(190, 201, 198, .18);
    }
    html[data-theme="dark"] .donut::after { background: #232626; }
    .chart-expand-modal { padding: 8px; background: rgba(0, 0, 0, .9); }
    .chart-expand-dialog {
      width: 99vw;
      height: 97vh;
      grid-template-rows: auto minmax(0, 1fr) auto;
      border-radius: 14px;
    }
    .chart-expand-head { min-height: 62px; padding: 13px 18px 13px 24px; }
    .chart-expand-head h2 { font-size: 20px; }
    .chart-expand-content {
      padding: 12px 16px;
      overflow: auto;
      background: color-mix(in srgb, var(--bg), var(--panel) 22%);
    }
    .chart-expand-scenario {
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      align-items: center;
      gap: 16px;
      min-height: 64px;
      padding: 12px 22px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      background: var(--panel);
    }
    .chart-expand-scenario strong {
      color: var(--green);
      font-size: 11px;
      letter-spacing: .08em;
      white-space: nowrap;
    }
    .chart-expand-scenario p { margin: 0; font-size: 12px; font-weight: 700; line-height: 1.4; }
    .expanded-chart-clone {
      min-height: 100%;
      padding: 30px !important;
      font-size: 1.22em;
    }
    .expanded-chart-clone h2,
    html[data-theme] .expanded-chart-clone h2,
    html[data-theme] .expanded-chart-clone .composition-title { font-size: 23px; }
    html[data-theme] .expanded-chart-clone .panel-subtitle,
    html[data-theme] .expanded-chart-clone .composition-copy p { font-size: 14px; }
    .expanded-chart-clone .bar-list,
    .expanded-chart-clone .active-goal-list,
    .expanded-chart-clone .aggregator-unique-list,
    .expanded-chart-clone .multi-bars { gap: 13px; }
    html[data-theme] .expanded-chart-clone .bar-row {
      min-height: 37px;
      grid-template-columns: minmax(100px, 190px) minmax(220px, 1fr) minmax(120px, auto);
      gap: 16px;
      font-size: 15px;
    }
    html[data-theme] .expanded-chart-clone .bar-label,
    html[data-theme] .expanded-chart-clone .bar-value,
    html[data-theme] .expanded-chart-clone .dual-value,
    html[data-theme] .expanded-chart-clone .multi-value,
    html[data-theme] .expanded-chart-clone .column-label,
    html[data-theme] .expanded-chart-clone .column-value,
    html[data-theme] .expanded-chart-clone .cluster-name,
    html[data-theme] .expanded-chart-clone .cluster-value,
    html[data-theme] .expanded-chart-clone .legend-row { font-size: 15px; }
    html[data-theme] .expanded-chart-clone .bar-track { height: 20px; border-radius: 7px; }
    html[data-theme] .expanded-chart-clone .active-goal-row,
    html[data-theme] .expanded-chart-clone .active-goal-network {
      min-height: 39px;
      grid-template-columns: minmax(90px, 150px) minmax(300px, 1fr) 88px 138px 28px;
      gap: 14px;
      font-size: 15px;
    }
    html[data-theme] .expanded-chart-clone.active-only .active-goal-row,
    html[data-theme] .expanded-chart-clone.active-only .active-goal-network {
      grid-template-columns: minmax(90px, 150px) minmax(300px, 1fr) 138px 28px;
    }
    html[data-theme] .expanded-chart-clone .aggregator-unique-row,
    html[data-theme] .expanded-chart-clone .aggregator-unique-network {
      min-height: 39px;
      grid-template-columns: minmax(90px, 150px) 78px minmax(300px, 1fr) 78px;
      gap: 12px;
      font-size: 15px;
    }
    html[data-theme] .expanded-chart-clone .active-goal-track,
    html[data-theme] .expanded-chart-clone .aggregator-unique-track { height: 34px; }
    html[data-theme] .expanded-chart-clone .active-goal-bar-value,
    html[data-theme] .expanded-chart-clone .aggregator-unique-user-value,
    html[data-theme] .expanded-chart-clone .aggregator-unique-access,
    html[data-theme] .expanded-chart-clone .active-goal-attainment,
    html[data-theme] .expanded-chart-clone .active-goal-growth { font-size: 14px; }
    .expanded-chart-clone.composition-panel {
      grid-template-columns: minmax(430px, .9fr) minmax(420px, 1.1fr);
      grid-template-rows: auto minmax(0, 1fr) auto;
      align-items: center;
      align-content: center;
      column-gap: 48px;
    }
    .expanded-chart-clone.composition-panel .donut-shell { width: min(490px, 56vh); }
    .expanded-chart-clone .donut-center strong { font-size: clamp(30px, 3vw, 54px); }
    .expanded-chart-clone .donut-center span { font-size: 14px; }
    .expanded-chart-clone .legend { display: grid; gap: 14px; }
    .expanded-chart-clone .dot { width: 15px; height: 15px; }
    .expanded-chart-clone .column-list,
    .expanded-chart-clone .stacked-column-list { min-height: 520px; }
    .expanded-chart-clone .column-track,
    .expanded-chart-clone .stacked-track { height: 410px; }
    .expanded-chart-clone .line-svg { min-height: 570px; }
    .expanded-chart-clone table { font-size: 14px; }
    @media (max-width: 900px) {
      .chart-expand-scenario { grid-template-columns: 1fr; gap: 4px; }
      .expanded-chart-clone.composition-panel { grid-template-columns: 1fr; }
      .expanded-chart-clone.composition-panel .donut-shell { width: min(390px, 68vw); }
    }
    /* Executive readability pass: centered titles, larger evidence and wider chart marks. */
    .summary-strip { gap: 0; padding: 10px 12px 12px; }
    html[data-theme] .panel h2,
    html[data-theme] .composition-title,
    html[data-theme] .composition-copy h2,
    html[data-theme] .financial-matrix-header h2 {
      width: 100%;
      margin-right: auto;
      margin-left: auto;
      color: var(--ink);
      font-size: 18px;
      line-height: 1.2;
      text-align: center;
    }
    html[data-theme] .panel-subtitle,
    html[data-theme] .composition-copy p {
      font-size: 13px;
      line-height: 1.5;
    }
    html[data-theme] .bar-label,
    html[data-theme] .column-label,
    html[data-theme] .stacked-label,
    html[data-theme] .cluster-name,
    html[data-theme] .legend-row,
    html[data-theme] .line-legend,
    html[data-theme] .multi-legend,
    html[data-theme] .column-legend,
    html[data-theme] .stacked-legend {
      font-size: 14px;
      line-height: 1.3;
    }
    html[data-theme] .bar-value,
    html[data-theme] .dual-value,
    html[data-theme] .multi-value,
    html[data-theme] .column-value,
    html[data-theme] .cluster-value,
    html[data-theme] .legend-row strong {
      font-size: 14.5px;
      font-weight: 950;
    }
    html[data-theme] .bar-row { min-height: 31px; font-size: 14px; }
    html[data-theme] .bar-track { height: 18px; }
    .active-goals-header {
      position: relative;
      min-height: 36px;
      justify-content: center;
    }
    .active-goals-header > div:first-child { width: 100%; padding: 0 112px; }
    .active-goals-header .active-goal-sort {
      position: absolute;
      top: 50%;
      right: 0;
      transform: translateY(-50%);
    }
    .active-goals-header .active-goal-sort:hover { transform: translateY(-50%); }
    .aggregator-unique-header {
      display: grid;
      justify-items: center;
      gap: 8px;
    }
    .aggregator-unique-header > div:first-child { width: 100%; }
    .aggregator-unique-legend { justify-content: center; font-size: 13px; }
    html[data-theme] .active-goal-row,
    html[data-theme] .active-goal-network {
      grid-template-columns: minmax(62px, 78px) minmax(210px, 1fr) 72px 116px 24px;
      min-height: 33px;
      gap: 8px;
      font-size: 14px;
    }
    html[data-theme] .active-goals-panel.active-only .active-goal-row,
    html[data-theme] .active-goals-panel.active-only .active-goal-network {
      grid-template-columns: minmax(62px, 78px) minmax(240px, 1fr) 116px 24px;
    }
    html[data-theme] .active-goal-track { height: 31px; }
    html[data-theme] .active-goal-network .active-goal-track { height: 37px; }
    html[data-theme] .active-goal-label,
    html[data-theme] .active-goal-growth,
    html[data-theme] .active-goal-attainment { font-size: 14px; }
    html[data-theme] .active-goal-bar-value { font-size: 13px; }
    html[data-theme] .aggregator-unique-row,
    html[data-theme] .aggregator-unique-network {
      grid-template-columns: minmax(62px, 78px) 68px minmax(230px, 1fr) 68px;
      min-height: 33px;
      gap: 7px;
      font-size: 14px;
    }
    html[data-theme] .aggregator-unique-track { height: 31px; }
    html[data-theme] .aggregator-unique-label,
    html[data-theme] .aggregator-unique-access,
    html[data-theme] .aggregator-unique-user-value { font-size: 13px; }
    .active-overview-trio .composition-panel {
      align-content: center;
      justify-content: center;
      min-height: 100%;
    }
    .active-overview-trio .composition-title { align-self: end; }
    .active-overview-trio .donut-shell { align-self: center; }
    .active-overview-trio .composition-copy { align-self: start; }
    .donut-callouts,
    .population-view { display: none; }
    html[data-theme] .expanded-chart-clone {
      font-size: 1.3em;
    }
    html[data-theme] .expanded-chart-clone h2,
    html[data-theme] .expanded-chart-clone .composition-title { font-size: 26px; }
    html[data-theme] .expanded-chart-clone .bar-label,
    html[data-theme] .expanded-chart-clone .bar-value,
    html[data-theme] .expanded-chart-clone .dual-value,
    html[data-theme] .expanded-chart-clone .multi-value,
    html[data-theme] .expanded-chart-clone .column-label,
    html[data-theme] .expanded-chart-clone .column-value,
    html[data-theme] .expanded-chart-clone .cluster-name,
    html[data-theme] .expanded-chart-clone .cluster-value,
    html[data-theme] .expanded-chart-clone .legend-row { font-size: 17px; }
    html[data-theme] .expanded-chart-clone .active-goal-row,
    html[data-theme] .expanded-chart-clone .active-goal-network {
      grid-template-columns: minmax(70px, 90px) minmax(360px, 1fr) 96px 150px 30px;
      min-height: 43px;
      font-size: 17px;
    }
    html[data-theme] .expanded-chart-clone.active-only .active-goal-row,
    html[data-theme] .expanded-chart-clone.active-only .active-goal-network {
      grid-template-columns: minmax(70px, 90px) minmax(400px, 1fr) 150px 30px;
    }
    html[data-theme] .expanded-chart-clone .aggregator-unique-row,
    html[data-theme] .expanded-chart-clone .aggregator-unique-network {
      grid-template-columns: minmax(70px, 90px) 86px minmax(380px, 1fr) 86px;
      min-height: 43px;
      font-size: 17px;
    }
    html[data-theme] .expanded-chart-clone .active-goal-track,
    html[data-theme] .expanded-chart-clone .aggregator-unique-track { height: 38px; }
    html[data-theme] .expanded-chart-clone .active-goal-bar-value,
    html[data-theme] .expanded-chart-clone .active-goal-growth,
    html[data-theme] .expanded-chart-clone .active-goal-attainment,
    html[data-theme] .expanded-chart-clone .aggregator-unique-user-value,
    html[data-theme] .expanded-chart-clone .aggregator-unique-access { font-size: 16px; }
    .expanded-chart-clone.composition-panel {
      grid-template-columns: 1fr;
      grid-template-rows: auto minmax(520px, 1fr) auto auto;
      justify-items: center;
      align-content: center;
      row-gap: 10px;
    }
    .expanded-chart-clone.composition-panel .donut-shell {
      width: min(900px, 94%);
      height: min(560px, 60vh);
      aspect-ratio: auto;
      overflow: visible;
    }
    .expanded-chart-clone.composition-panel .donut {
      position: absolute;
      top: 50%;
      left: 50%;
      width: min(440px, 46vh) !important;
      height: auto;
      transform: translate(-50%, -50%);
    }
    .expanded-chart-clone.composition-panel .donut-center {
      inset: auto;
      top: 50%;
      left: 50%;
      width: min(230px, 24vh);
      aspect-ratio: 1;
      transform: translate(-50%, -50%);
    }
    .expanded-chart-clone .donut-callouts { display: block; position: absolute; inset: 0; z-index: 4; }
    .expanded-chart-clone .donut-callout {
      position: absolute;
      top: var(--callout-y);
      left: var(--callout-x);
      width: 170px;
      display: grid;
      gap: 1px;
      color: var(--ink);
      line-height: 1.1;
    }
    .expanded-chart-clone .donut-callout.right { transform: translate(0, -50%); text-align: left; }
    .expanded-chart-clone .donut-callout.left { transform: translate(-100%, -50%); text-align: right; }
    .expanded-chart-clone .donut-callout::before {
      content: "";
      position: absolute;
      top: 50%;
      width: 58px;
      border-top: 2px solid var(--callout-color);
      opacity: .9;
    }
    .expanded-chart-clone .donut-callout.right::before { right: calc(100% + 7px); }
    .expanded-chart-clone .donut-callout.left::before { left: calc(100% + 7px); }
    .expanded-chart-clone .donut-callout span { color: var(--callout-color); font-size: 13px; font-weight: 900; }
    .expanded-chart-clone .donut-callout strong { font-size: 21px; font-weight: 950; font-variant-numeric: tabular-nums; }
    .expanded-chart-clone .donut-callout small { color: var(--muted); font-size: 14px; font-weight: 850; }
    .expanded-chart-clone.composition-panel .composition-copy { width: min(1100px, 100%); }
    .expanded-chart-clone.composition-panel .legend {
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px 22px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }
    .expanded-chart-clone.composition-panel .legend-row {
      min-width: 0;
      min-height: 38px;
      align-items: center;
    }
    .expanded-chart-clone.chart-profile-age .composition-copy { width: min(1160px, 100%); }
    .expanded-chart-clone.chart-profile-age .legend {
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px 28px;
    }
    .expanded-chart-clone.chart-profile-age .legend-row {
      min-height: 50px;
      align-items: start;
    }
    .expanded-chart-clone.chart-profile-gender .column-list { display: none; }
    .expanded-chart-clone.chart-profile-gender .population-view {
      min-height: 560px;
      display: grid;
      grid-template-columns: minmax(500px, 1.2fr) minmax(320px, .8fr);
      align-items: center;
      gap: 42px;
      padding: 30px 5%;
    }
    .population-grid {
      display: grid;
      grid-template-columns: repeat(20, minmax(14px, 1fr));
      gap: 10px;
      align-content: center;
    }
    .population-dot {
      width: 100%;
      aspect-ratio: 1;
      border-radius: 50%;
      background: var(--population-color);
      box-shadow: 0 0 12px color-mix(in srgb, var(--population-color), transparent 45%);
    }
    .population-legend { display: grid; gap: 16px; }
    .population-legend > div {
      display: grid;
      grid-template-columns: 18px minmax(120px, 1fr) auto;
      align-items: center;
      gap: 9px;
      padding: 12px 0;
      border-bottom: 1px solid var(--line);
    }
    .population-legend i { width: 14px; height: 14px; border-radius: 50%; background: var(--population-color); }
    .population-legend span { font-size: 16px; font-weight: 850; }
    .population-legend strong { font-size: 18px; font-weight: 950; }
    .population-legend small { grid-column: 2 / -1; color: var(--muted); font-size: 12px; }
    .population-view > p {
      grid-column: 1 / -1;
      margin: 0;
      color: var(--muted);
      text-align: center;
      font-size: 13px;
      font-weight: 750;
    }
    .contract-population-panel {
      display: flex;
      flex-direction: column;
      min-height: 390px;
    }
    .contract-population-panel > h2 { text-align: center; }
    .contract-population-panel > .panel-subtitle { text-align: center; }
    .contract-population-layout {
      display: grid;
      grid-template-columns: minmax(210px, .9fr) minmax(240px, 1.1fr);
      align-items: center;
      gap: 18px;
      flex: 1;
      padding: 8px 2% 4px;
    }
    .contract-population-grid {
      display: grid;
      grid-template-columns: repeat(10, minmax(10px, 1fr));
      gap: 7px;
      align-content: center;
    }
    .contract-population-dot {
      width: 100%;
      aspect-ratio: 1;
      border-radius: 50%;
      background: var(--population-color);
      box-shadow: 0 0 9px color-mix(in srgb, var(--population-color), transparent 50%);
    }
    .contract-population-legend { display: grid; gap: 2px; }
    .contract-population-legend > div {
      display: grid;
      grid-template-columns: 14px minmax(130px, 1fr) auto;
      align-items: center;
      gap: 9px;
      min-height: 34px;
      padding: 5px 0;
      border-bottom: 1px solid var(--line);
    }
    .contract-population-legend i {
      width: 11px;
      height: 11px;
      border-radius: 50%;
      background: var(--population-color);
    }
    .contract-population-legend span { font-size: 13px; font-weight: 850; }
    .contract-population-legend strong { font-size: 14px; font-weight: 950; white-space: nowrap; }
    .contract-population-note {
      margin: 9px 0 0;
      color: var(--muted);
      text-align: center;
      font-size: 11px;
      font-weight: 750;
    }
    @media (max-width: 1100px) {
      .expanded-chart-clone.chart-profile-gender .population-view { grid-template-columns: 1fr; }
      .population-grid { grid-template-columns: repeat(10, minmax(14px, 1fr)); }
      .expanded-chart-clone.chart-profile-age .legend { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .contract-population-layout { grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr); }
      .contract-population-grid { grid-template-columns: repeat(10, minmax(8px, 1fr)); }
    }
    /* Active overview alignment and KPI title readability. */
    .active-overview-trio .composition-panel {
      grid-template-rows: auto minmax(0, 1fr) auto;
      align-content: stretch;
    }
    .active-overview-trio .composition-title {
      grid-row: 1;
      align-self: start;
      width: 100%;
      margin: 0 auto 10px !important;
      text-align: center;
    }
    .active-overview-trio .donut-shell {
      grid-row: 2;
      align-self: center;
    }
    .active-overview-trio .composition-copy {
      grid-row: 3;
      align-self: end;
      width: 100%;
      margin-top: auto;
    }
    .active-overview-trio .composition-copy .legend {
      width: fit-content;
      max-width: 100%;
      margin-right: auto;
      margin-left: auto;
      grid-template-columns: repeat(2, max-content);
      grid-template-rows: repeat(2, auto);
      grid-auto-flow: column;
      justify-content: center;
      gap: 11px 48px;
    }
    .active-overview-trio .composition-copy .legend-row {
      min-width: 0;
      grid-template-columns: 12px max-content max-content;
      column-gap: 10px;
      justify-content: start;
    }
    .active-overview-trio .aggregator-unique-header {
      align-content: start;
      grid-template-columns: minmax(0, 1fr);
      justify-content: stretch;
      justify-items: center;
      width: 100%;
      margin-top: 0;
    }
    .active-overview-trio .aggregator-unique-header > div:first-child {
      width: 100%;
      justify-self: stretch;
    }
    .active-overview-trio .aggregator-unique-header h2 {
      width: 100%;
      margin-right: auto;
      margin-left: auto;
      text-align: center;
    }
    html[data-theme] .active-card-grid .card,
    html[data-theme] .active-footer-cards .card {
      min-height: 142px;
    }
    /* Dashboard-wide typography parity with the Ativos page. */
    html[data-theme] .card .card-label {
      font-size: clamp(11px, .72vw, 13px);
      line-height: 1.25;
    }
    html[data-theme] .card small,
    html[data-theme] .card .card-subtitle,
    html[data-theme] .card-foot .card-meta,
    html[data-theme] .card-foot .card-metric {
      font-size: 11.5px;
      line-height: 1.3;
    }
    html[data-theme] .chart-access-day .day-label strong,
    html[data-theme] .chart-access-day .day-label span,
    html[data-theme] .chart-access-day .column-split-values,
    html[data-theme] .chart-access-hour .column-label,
    html[data-theme] .chart-access-hour .column-split-values,
    html[data-theme] .cluster-name small,
    html[data-theme] .cluster-unit-cell small,
    html[data-theme] .dual-value small,
    html[data-theme] .multi-value span {
      font-size: 12.5px;
      line-height: 1.25;
    }
    html[data-theme] .line-series-selector-title,
    html[data-theme] .cluster-total span,
    html[data-theme] .cannibalization-period-control,
    html[data-theme] .financial-month-control,
    html[data-theme] .churn-risk-band-head span,
    html[data-theme] .churn-risk-band-head small {
      font-size: 12px;
      line-height: 1.3;
    }
    html[data-theme] .line-series-options label,
    html[data-theme] .composition-footer,
    html[data-theme] .chart-callout,
    html[data-theme] .cannibalization-total,
    html[data-theme] .financial-note,
    html[data-theme] .churn-risk-donut-hint {
      font-size: 12px;
      line-height: 1.4;
    }
    html[data-theme] .card .card-value.good { color: var(--green); }
    html[data-theme] .card .card-value.bad { color: var(--red); }
    html[data-theme] .card-foot .card-meta,
    html[data-theme] .card-foot .card-metric { white-space: nowrap; }
    /* Requested page composition and modal-specific readability. */
    .financial-layout {
      min-width: 0;
      display: grid;
      gap: 10px;
    }
    #tab-vendas .card .card-label,
    #tab-vendas .card .card-value,
    #tab-vendas .card > strong,
    #tab-vendas .card .card-subtitle {
      grid-column: 1 / -1;
      justify-self: center;
      width: 100%;
      text-align: center;
    }
    #tab-vendas .card { position: relative; }
    #tab-vendas .card .card-icon {
      position: absolute;
      top: 12px;
      left: 12px;
    }
    #tab-vendas .card-foot {
      grid-column: 1 / -1;
      width: 100%;
      justify-content: center;
      text-align: center;
    }
    #tab-vendas .card-foot:has(.card-meta + .card-metric) {
      justify-content: space-between;
    }
    #tab-vendas .peak-sales-body {
      justify-self: stretch;
      width: 100%;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      text-align: center;
    }
    #tab-vendas .peak-sales-count { text-align: center; }
    html[data-theme] .financial-table thead th {
      font-size: 11px;
      font-weight: 900;
    }
    html[data-theme] .financial-table td {
      font-size: 11px;
      font-weight: 850;
      letter-spacing: -.045em;
      line-height: 1.18;
      white-space: normal;
    }
    html[data-theme] .financial-indicator {
      font-size: 13px;
      font-weight: 900;
    }
    html[data-theme] .financial-indicator small {
      font-size: clamp(9px, .58vw, 10.5px);
    }
    html[data-theme] .financial-section-row th {
      font-size: 11.5px;
    }
    .chart-expand-modal[data-chart-kind="cancel-month"] .chart-expand-content,
    .chart-expand-modal[data-chart-kind="cancel-contracts"] .chart-expand-content,
    .chart-expand-modal[data-chart-kind="sales-contracts"] .chart-expand-content,
    .chart-expand-modal[data-chart-kind="sales-ticket"] .chart-expand-content {
      overflow: hidden;
    }
    .chart-expand-modal[data-chart-kind="cancel-month"] .expanded-chart-clone {
      height: 100%;
      min-height: 0;
      display: grid;
      grid-template-rows: auto auto auto minmax(0, 1fr);
      align-content: center;
      padding: 20px 28px !important;
      overflow: hidden;
    }
    .chart-expand-modal[data-chart-kind="cancel-month"] .expanded-chart-clone .column-list {
      width: 100%;
      height: 100%;
      min-height: 0;
      max-height: 520px;
      align-self: center;
      padding-top: 8px;
    }
    .chart-expand-modal[data-chart-kind="cancel-month"] .expanded-chart-clone .column-item {
      height: 100%;
      min-height: 0;
    }
    .chart-expand-modal[data-chart-kind="cancel-month"] .expanded-chart-clone .column-pair,
    .chart-expand-modal[data-chart-kind="cancel-month"] .expanded-chart-clone .column-track {
      height: min(390px, 43vh);
    }
    .chart-expand-modal[data-chart-kind="cancel-month"] .expanded-chart-clone .column-legend {
      justify-content: center;
      margin: 8px 0 2px;
    }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .expanded-chart-clone.composition-panel {
      height: 100%;
      min-height: 0;
      grid-template-columns: 1fr;
      grid-template-rows: auto minmax(330px, 1fr) auto;
      justify-items: center;
      align-content: stretch;
      row-gap: 4px;
      padding: 16px 28px !important;
      overflow: hidden;
    }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .donut-shell {
      width: min(1080px, 92%);
      height: min(475px, 50vh);
      min-height: 330px;
      align-self: center;
    }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .donut {
      width: min(390px, 39vh) !important;
    }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .donut-center {
      width: min(190px, 19vh);
    }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .donut-callout {
      width: 150px;
      line-height: 1.05;
    }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .donut-callout span { font-size: 11px; }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .donut-callout strong { font-size: 18px; }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .donut-callout small { font-size: 12px; }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .composition-copy {
      width: min(1280px, 100%);
      align-self: end;
    }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .composition-copy > p {
      margin: 0 0 8px;
      text-align: center;
    }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .legend {
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 7px 18px;
      padding-top: 9px;
    }
    .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .legend-row {
      min-height: 30px;
      font-size: 14px;
    }
    .chart-expand-modal[data-chart-kind="sales-contracts"] .expanded-chart-clone.contract-population-panel {
      height: 100%;
      min-height: 0;
      display: flex;
      padding: 18px 28px !important;
      overflow: hidden;
    }
    .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-layout {
      width: min(1420px, 96%);
      min-height: 0;
      margin: 0 auto;
      grid-template-columns: minmax(560px, 1.15fr) minmax(420px, .85fr);
      gap: 56px;
      padding: 12px 2%;
    }
    .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-grid {
      grid-template-columns: repeat(10, minmax(15px, 1fr));
      gap: 10px;
    }
    .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-legend > div {
      min-height: 43px;
      padding: 8px 0;
    }
    .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-legend span { font-size: 16px; }
    .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-legend strong { font-size: 17px; }
    .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-note { font-size: 13px; }
    @media (max-width: 1100px) {
      .chart-expand-modal[data-chart-kind="sales-contracts"] .expanded-chart-clone.contract-population-panel {
        padding: 14px 20px !important;
      }
      .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-layout {
        width: 100%;
        grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr);
        gap: 18px;
        padding: 8px 0;
      }
      .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-grid {
        grid-template-columns: repeat(10, minmax(8px, 1fr));
        gap: 6px;
      }
      .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-legend > div {
        grid-template-columns: 10px minmax(0, 1fr) auto;
        min-height: 34px;
        gap: 6px;
        padding: 4px 0;
      }
      .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-legend span,
      .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-legend strong { font-size: 12px; }
      .chart-expand-modal[data-chart-kind="sales-contracts"] .contract-population-note { font-size: 10px; }
    }
    .chart-expand-modal[data-chart-kind="sales-ticket"] .expanded-chart-clone {
      height: 100%;
      min-height: 0;
      display: grid;
      grid-template-rows: auto auto auto minmax(0, 1fr);
      padding: 16px 24px !important;
      overflow: hidden;
    }
    .chart-expand-modal[data-chart-kind="sales-ticket"] .expanded-chart-clone > h2 { display: none; }
    .chart-expand-modal[data-chart-kind="sales-ticket"] .expanded-chart-clone .bar-list {
      min-height: 0;
      align-content: stretch;
      gap: 3px;
    }
    html[data-theme] .chart-expand-modal[data-chart-kind="sales-ticket"] .expanded-chart-clone .bar-row {
      min-height: 27px;
      grid-template-columns: minmax(70px, 120px) minmax(320px, 1fr) minmax(110px, auto);
      gap: 12px;
    }
    .chart-expand-modal[data-chart-kind="sales-ticket"] .expanded-chart-clone .dual-bars { gap: 3px; }
    .chart-expand-modal[data-chart-kind="sales-ticket"] .expanded-chart-clone .dual-bars .bar-track { height: 8px; }
    .chart-expand-modal[data-chart-kind="sales-ticket"] .expanded-chart-clone .dual-bars .bar-track:first-child { height: 11px; }
    /* KPI cards: full-width title, centered evidence and a stable one-line heading. */
    html[data-theme] .card {
      position: relative;
      grid-template-columns: minmax(0, 1fr);
      grid-template-rows: auto minmax(0, 1fr) auto;
      row-gap: 2px;
      align-content: stretch;
    }
    html[data-theme] .card .card-label,
    html[data-theme] #tab-vendas .card .card-label {
      grid-column: 1;
      grid-row: 1;
      width: 100%;
      padding: 0;
      color: var(--muted);
      font-size: clamp(12px, .76vw, 14px);
      line-height: 1.15;
      letter-spacing: .005em;
      text-align: left;
      white-space: nowrap;
    }
    html[data-theme] .card .card-icon,
    html[data-theme] #tab-vendas .card .card-icon {
      position: absolute;
      top: 50%;
      left: 12px;
      grid-column: auto;
      grid-row: auto;
      transform: translateY(-50%);
    }
    html[data-theme] .card .card-value,
    html[data-theme] .card > strong,
    html[data-theme] #tab-vendas .card .card-value,
    html[data-theme] #tab-vendas .card > strong {
      position: absolute;
      top: 50%;
      right: 12px;
      left: 12px;
      grid-column: auto;
      grid-row: auto;
      justify-self: stretch;
      width: auto;
      margin: 0;
      text-align: center;
      transform: translateY(-50%);
    }
    html[data-theme] .card > small,
    html[data-theme] .card .card-subtitle,
    html[data-theme] .card .card-foot {
      grid-column: 1;
      width: 100%;
    }
    html[data-theme] .peak-sales-card { grid-template-rows: auto auto minmax(0, 1fr); }
    html[data-theme] .peak-sales-card .card-subtitle {
      grid-column: 1;
      grid-row: 2;
      justify-self: center;
      width: 100%;
      text-align: center;
    }
    html[data-theme] .cards:not(.active-card-grid):not(.active-footer-cards) {
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }
    html[data-theme] .active-footer-cards {
      grid-template-columns: minmax(250px, 1.22fr) repeat(4, minmax(0, 1fr));
    }
    /* Cards remain individual surfaces; the summary group has no enclosing box. */
    html[data-theme] .summary-strip,
    html[data-theme="dark"] .summary-strip {
      gap: 0;
      padding: 0;
      border: 0;
      border-radius: 0;
      background: transparent;
      box-shadow: none;
    }
    html[data-theme] .summary-strip > .cards { gap: 10px; }
    /* Five active-page expansions: fit the complete visual inside the viewport. */
    .chart-expand-modal:is([data-chart-kind="active-units"], [data-chart-kind="active-composition"], [data-chart-kind="active-aggregators"], [data-chart-kind="active-gender"], [data-chart-kind="active-age"]) .chart-expand-dialog {
      height: min(950px, 98vh);
    }
    .chart-expand-modal:is([data-chart-kind="active-units"], [data-chart-kind="active-composition"], [data-chart-kind="active-aggregators"], [data-chart-kind="active-gender"], [data-chart-kind="active-age"]) .chart-expand-head {
      min-height: 50px;
      padding: 8px 16px 8px 22px;
    }
    .chart-expand-modal:is([data-chart-kind="active-units"], [data-chart-kind="active-composition"], [data-chart-kind="active-aggregators"], [data-chart-kind="active-gender"], [data-chart-kind="active-age"]) .chart-expand-content {
      min-height: 0;
      padding: 8px 12px;
      overflow: hidden;
    }
    .chart-expand-modal:is([data-chart-kind="active-units"], [data-chart-kind="active-composition"], [data-chart-kind="active-aggregators"], [data-chart-kind="active-gender"], [data-chart-kind="active-age"]) .chart-expand-scenario {
      min-height: 48px;
      padding: 7px 18px;
    }
    .chart-expand-modal:is([data-chart-kind="active-units"], [data-chart-kind="active-composition"], [data-chart-kind="active-aggregators"], [data-chart-kind="active-gender"], [data-chart-kind="active-age"]) .expanded-chart-clone {
      height: 100%;
      min-height: 0;
      padding: 10px 18px !important;
      overflow: hidden;
    }
    .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone {
      display: grid;
      grid-template-rows: minmax(0, 1fr) auto;
      align-content: stretch;
    }
    .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone .active-goals-header { display: none; }
    .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone .active-goal-list {
      min-height: 0;
      display: grid;
      grid-template-rows: repeat(14, minmax(0, 1fr));
      align-content: stretch;
      gap: 3px;
    }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone .active-goal-row,
    html[data-theme] .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone .active-goal-network {
      min-height: 26px;
      grid-template-columns: minmax(55px, 78px) minmax(300px, 1fr) 70px 118px 24px;
      gap: 8px;
      font-size: 13px;
    }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone.active-only .active-goal-row,
    html[data-theme] .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone.active-only .active-goal-network {
      grid-template-columns: minmax(55px, 78px) minmax(300px, 1fr) 118px 24px;
    }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone .active-goal-track { height: 24px; }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone .active-goal-network {
      min-height: 33px;
      margin-top: 4px;
    }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone .active-goal-network .active-goal-track { height: 29px; }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone :is(.active-goal-label, .active-goal-bar-value, .active-goal-growth, .active-goal-attainment, .active-goal-main-goal) { font-size: 12.5px; }
    .chart-expand-modal[data-chart-kind="active-aggregators"] .expanded-chart-clone {
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      align-content: stretch;
    }
    .chart-expand-modal[data-chart-kind="active-aggregators"] .expanded-chart-clone .aggregator-unique-header {
      min-height: 28px;
      margin: 0 0 3px;
    }
    .chart-expand-modal[data-chart-kind="active-aggregators"] .expanded-chart-clone .aggregator-unique-header > div:first-child { display: none; }
    .chart-expand-modal[data-chart-kind="active-aggregators"] .expanded-chart-clone .aggregator-unique-list {
      min-height: 0;
      display: grid;
      grid-template-rows: repeat(14, minmax(0, 1fr));
      align-content: stretch;
      gap: 3px;
    }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-aggregators"] .expanded-chart-clone .aggregator-unique-row,
    html[data-theme] .chart-expand-modal[data-chart-kind="active-aggregators"] .expanded-chart-clone .aggregator-unique-network {
      min-height: 26px;
      grid-template-columns: minmax(55px, 78px) 70px minmax(300px, 1fr) 70px;
      gap: 8px;
      font-size: 13px;
    }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-aggregators"] .expanded-chart-clone .aggregator-unique-track { height: 24px; }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-aggregators"] .expanded-chart-clone .aggregator-unique-network {
      min-height: 33px;
      margin-top: 4px;
    }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-aggregators"] .expanded-chart-clone .aggregator-unique-network .aggregator-unique-track { height: 29px; }
    html[data-theme] .chart-expand-modal[data-chart-kind="active-aggregators"] .expanded-chart-clone :is(.aggregator-unique-label, .aggregator-unique-user-value, .aggregator-unique-access) { font-size: 12.5px; }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone.composition-panel {
      height: 100%;
      min-height: 0;
      grid-template-columns: 1fr;
      grid-template-rows: minmax(270px, 1fr) auto auto;
      align-content: stretch;
      justify-items: center;
      row-gap: 3px;
      padding: 8px 22px !important;
      overflow: hidden;
    }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .composition-title { display: none; }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .donut-shell {
      width: min(1020px, 92%);
      height: min(360px, 43vh);
      min-height: 270px;
      align-self: center;
    }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .donut { width: min(310px, 34vh) !important; }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .donut-center { width: min(152px, 17vh); }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .donut-callout {
      width: 138px;
      line-height: 1.02;
    }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .donut-callout::before { width: 42px; }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .donut-callout span { font-size: 10.5px; }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .donut-callout strong { font-size: 17px; }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .donut-callout small { font-size: 11.5px; }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .composition-copy {
      width: min(1200px, 100%);
      align-self: end;
    }
    .chart-expand-modal:is([data-chart-kind="active-composition"], [data-chart-kind="active-age"]) .expanded-chart-clone .composition-copy > p {
      margin: 0 0 5px;
      text-align: center;
    }
    .chart-expand-modal[data-chart-kind="active-composition"] .expanded-chart-clone .legend {
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px 18px;
      padding-top: 8px;
    }
    .chart-expand-modal[data-chart-kind="active-composition"] .expanded-chart-clone .legend-row { min-height: 28px; font-size: 13px; }
    .chart-expand-modal[data-chart-kind="active-age"] .expanded-chart-clone .donut-shell {
      height: min(350px, 42vh);
      min-height: 285px;
    }
    .chart-expand-modal[data-chart-kind="active-age"] .expanded-chart-clone .legend {
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 5px 18px;
      padding-top: 7px;
    }
    .chart-expand-modal[data-chart-kind="active-age"] .expanded-chart-clone .legend-row {
      min-height: 30px;
      align-items: center;
      font-size: 12.5px;
    }
    .chart-expand-modal[data-chart-kind="active-age"] .expanded-chart-clone .composition-footer {
      margin: 0;
      padding-top: 4px;
      font-size: 11.5px;
    }
    .chart-expand-modal[data-chart-kind="active-gender"] .expanded-chart-clone {
      display: grid;
      grid-template-rows: minmax(0, 1fr);
      align-content: stretch;
    }
    .chart-expand-modal[data-chart-kind="active-gender"] .expanded-chart-clone > h2,
    .chart-expand-modal[data-chart-kind="active-gender"] .expanded-chart-clone > .panel-subtitle,
    .chart-expand-modal[data-chart-kind="active-gender"] .expanded-chart-clone > .column-legend { display: none; }
    .chart-expand-modal[data-chart-kind="active-gender"] .expanded-chart-clone .population-view {
      width: min(1320px, 96%);
      height: 100%;
      min-height: 0;
      margin: 0 auto;
      display: grid;
      grid-template-columns: minmax(440px, 1.25fr) minmax(300px, .75fr);
      align-items: center;
      gap: 28px;
      padding: 8px 3%;
    }
    .chart-expand-modal[data-chart-kind="active-gender"] .population-grid {
      grid-template-columns: repeat(20, minmax(11px, 1fr));
      gap: 7px;
    }
    .chart-expand-modal[data-chart-kind="active-gender"] .population-legend { gap: 7px; }
    .chart-expand-modal[data-chart-kind="active-gender"] .population-legend > div { gap: 8px; padding: 7px 0; }
    .chart-expand-modal[data-chart-kind="active-gender"] .population-legend span { font-size: 14px; }
    .chart-expand-modal[data-chart-kind="active-gender"] .population-legend strong { font-size: 16px; }
    .chart-expand-modal[data-chart-kind="active-gender"] .population-view > p { font-size: 11.5px; }
    @media (max-width: 1100px) {
      .cancel-unit-retention-grid,
      .financial-chart-pair,
      .financial-collection-layout { grid-template-columns: 1fr; }
      .chart-expand-modal:is([data-chart-kind="cancel-contracts"], [data-chart-kind="sales-contracts"]) .legend { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    /* Page layout editor: editable chart grid on the main tabs only. */
    .layout-editor-actions {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .layout-edit-toggle,
    .layout-text-hide,
    .layout-reset {
      min-height: 42px;
      padding: 0 13px;
      border: 1px solid color-mix(in srgb, var(--green), transparent 48%);
      border-radius: 9px;
      color: var(--green);
      background: transparent;
      font: inherit;
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
      cursor: pointer;
      white-space: nowrap;
    }
    .layout-edit-toggle[aria-pressed="true"] {
      color: #021409;
      border-color: var(--green);
      background: var(--green);
    }
    .layout-text-hide:disabled {
      opacity: .45;
      cursor: not-allowed;
    }
    .layout-reset {
      color: var(--ink);
      border-color: var(--line);
    }
    .layout-editor-hint {
      position: sticky;
      top: 76px;
      z-index: 18;
      width: 100%;
      min-height: 46px;
      margin: 0 0 10px;
      padding: 9px 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 12px;
      border: 1px solid color-mix(in srgb, var(--green), transparent 55%);
      border-radius: 11px;
      color: var(--muted);
      background: color-mix(in srgb, var(--panel), #000 8%);
      box-shadow: var(--shadow);
      font-size: 12px;
      font-weight: 750;
      text-align: center;
    }
    .layout-editor-hint[hidden] { display: none; }
    .layout-editor-hint strong {
      color: var(--green);
      font-size: 12px;
      text-transform: uppercase;
      white-space: nowrap;
    }
    .dashboard-layout-grid {
      min-width: 0;
      display: grid;
      grid-template-columns: repeat(12, minmax(0, 1fr));
      grid-auto-flow: row;
      align-items: start;
      gap: 12px;
    }
    .dashboard-layout-grid.layout-masonry-ready {
      grid-auto-flow: row dense;
      grid-auto-rows: 8px;
    }
    .dashboard-layout-grid > .panel {
      min-width: 0;
      width: auto;
      height: var(--layout-height, auto);
      margin: 0;
      grid-column: span var(--layout-span, 6);
      grid-row: span var(--layout-row-span, 1);
      align-self: start;
    }
    .dashboard-layout-grid > .panel.user-sized-panel {
      min-height: 180px;
      overflow: auto;
      scrollbar-width: thin;
    }
    .dashboard-layout-grid > .layout-active-composition {
      grid-template-columns: 1fr;
      align-content: center;
      justify-items: center;
    }
    .dashboard-layout-grid > .layout-active-composition .composition-copy { width: 100%; }
    .dashboard-layout-grid > .layout-active-age-composition {
      grid-template-columns: minmax(140px, .72fr) minmax(0, 1.28fr);
    }
    .layout-source-shell[hidden] { display: none !important; }
    body.layout-edit-mode .dashboard-layout-grid {
      position: relative;
      padding: 10px;
      border: 1px dashed color-mix(in srgb, var(--green), transparent 38%);
      border-radius: 14px;
      background-image:
        linear-gradient(to right, color-mix(in srgb, var(--green), transparent 92%) 1px, transparent 1px),
        linear-gradient(to bottom, color-mix(in srgb, var(--green), transparent 94%) 1px, transparent 1px);
      background-size: calc(100% / 12) 100%, 100% 48px;
    }
    body.layout-edit-mode .dashboard-layout-grid > .panel {
      position: relative;
      outline: 1px solid color-mix(in srgb, var(--green), transparent 62%);
      outline-offset: 2px;
      transition: outline-color .16s ease, box-shadow .16s ease;
    }
    body.layout-edit-mode .dashboard-layout-grid > .panel.layout-drag-over {
      outline-color: var(--green);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--green), transparent 72%);
    }
    body.layout-edit-mode .chart-expand-button { display: none !important; }
    .layout-box-tools {
      position: absolute;
      top: 7px;
      right: 7px;
      z-index: 16;
      display: none;
      align-items: center;
      gap: 3px;
      padding: 3px;
      border: 1px solid var(--line);
      border-radius: 9px;
      color: var(--ink);
      background: color-mix(in srgb, var(--panel), #000 14%);
      box-shadow: 0 8px 22px rgba(0, 0, 0, .22);
    }
    body.layout-edit-mode .layout-box-tools { display: inline-flex; }
    .layout-box-tools button {
      width: 29px;
      height: 27px;
      display: grid;
      place-items: center;
      padding: 0;
      border: 1px solid transparent;
      border-radius: 6px;
      color: var(--ink);
      background: transparent;
      font: inherit;
      font-size: 9px;
      font-weight: 950;
      cursor: pointer;
    }
    .layout-box-tools button:hover,
    .layout-box-tools button:focus-visible {
      color: var(--green);
      border-color: var(--line);
      background: color-mix(in srgb, var(--green), transparent 90%);
      outline: none;
    }
    .layout-drag-handle { cursor: grab !important; }
    .layout-drag-handle:active { cursor: grabbing !important; }
    .layout-resize-handle {
      position: absolute;
      right: 2px;
      bottom: 2px;
      z-index: 17;
      width: 22px;
      height: 22px;
      display: none;
      border: 0;
      border-right: 3px solid var(--green);
      border-bottom: 3px solid var(--green);
      border-radius: 0 0 8px 0;
      background: transparent;
      cursor: nwse-resize;
    }
    body.layout-edit-mode .layout-resize-handle { display: block; }
    .text-editable {
      position: relative;
      border-radius: 4px;
    }
    body.layout-edit-mode .text-editable {
      cursor: text;
      outline: 1px dashed transparent;
      outline-offset: 3px;
    }
    body.layout-edit-mode .text-editable:hover {
      outline-color: color-mix(in srgb, var(--green), transparent 48%);
      background: color-mix(in srgb, var(--green), transparent 94%);
    }
    body.layout-edit-mode .text-editable:focus {
      outline: 2px solid var(--green);
      background: color-mix(in srgb, var(--green), transparent 90%);
    }
    .user-text-hidden { display: none !important; }
    body.layout-edit-mode .text-editable.user-text-hidden {
      min-width: 110px;
      min-height: 20px;
      display: inline-block !important;
      opacity: .62;
      font-style: italic;
    }
    body.layout-edit-mode .text-editable.user-text-hidden::after {
      content: "Texto oculto — clique para editar";
    }
    @media (max-width: 900px) {
      .layout-editor-actions { width: 100%; flex-wrap: wrap; }
      .layout-editor-actions > button { flex: 1 1 auto; }
      .layout-editor-hint { position: static; align-items: flex-start; flex-direction: column; gap: 3px; text-align: left; }
      .dashboard-layout-grid { grid-template-columns: 1fr; }
      .dashboard-layout-grid > .panel {
        height: auto !important;
        grid-column: 1 / -1 !important;
      }
    }
    /* Financeiro: altura dos KPIs alinhada ao padrão visual da página de Ativos. */
    html[data-theme] #tab-financeiro > .summary-strip > .cards {
      align-items: stretch;
    }
    html[data-theme] #tab-financeiro > .summary-strip .card {
      min-height: 142px;
      padding-top: 16px;
      padding-bottom: 14px;
    }
    /* Financeiro, Frequência e Análise: mesmo tema azul-ciano-verde das abas principais. */
    html[data-theme] {
      --active-blue: #1d4ed8;
      --active-cyan: #3491dc;
      --active-teal: #2fb8c4;
      --active-green: #62c776;
      --wellhub-pink: #d8385e;
    }
    html[data-theme] :is(#tab-financeiro, #tab-frequencia, #tab-isaias) .panel,
    html[data-theme] #tab-isaias .medal-board-panel,
    html[data-theme] #tab-isaias .analysis-matrix-panel {
      border-color: color-mix(in srgb, var(--active-teal), var(--line) 72%);
      background:
        linear-gradient(135deg, color-mix(in srgb, var(--active-blue), transparent 94%), transparent 46%),
        var(--panel);
    }
    html[data-theme] #tab-frequencia > .summary-strip .card {
      min-height: 142px;
      padding-top: 16px;
      padding-bottom: 14px;
    }
    html[data-theme] #tab-financeiro > .summary-strip .card:nth-child(1),
    html[data-theme] #tab-frequencia > .summary-strip .card:nth-child(1) { --tone: var(--active-blue) !important; }
    html[data-theme] #tab-financeiro > .summary-strip .card:nth-child(2),
    html[data-theme] #tab-frequencia > .summary-strip .card:nth-child(2) { --tone: var(--active-cyan) !important; }
    html[data-theme] #tab-financeiro > .summary-strip .card:nth-child(3),
    html[data-theme] #tab-frequencia > .summary-strip .card:nth-child(3) { --tone: var(--active-teal) !important; }
    html[data-theme] #tab-financeiro > .summary-strip .card:nth-child(4),
    html[data-theme] #tab-frequencia > .summary-strip .card:nth-child(4) { --tone: var(--active-green) !important; }
    html[data-theme] #tab-financeiro > .summary-strip .card:nth-child(5),
    html[data-theme] #tab-frequencia > .summary-strip .card:nth-child(5) { --tone: var(--active-cyan) !important; }
    html[data-theme] #tab-frequencia > .summary-strip .card:nth-child(6) { --tone: var(--active-green) !important; }
    html[data-theme] :is(#tab-financeiro, #tab-frequencia) .card-icon {
      color: var(--tone);
      border-color: color-mix(in srgb, var(--tone), transparent 42%);
      background: color-mix(in srgb, var(--tone), transparent 88%);
    }
    html[data-theme] #tab-financeiro .financial-table-wrap,
    html[data-theme] #tab-isaias .analysis-matrix-wrap,
    html[data-theme] #tab-frequencia :is(.churn-risk-table-wrap, .cluster-unit-table-wrap) {
      border-color: color-mix(in srgb, var(--active-cyan), transparent 72%);
      background: color-mix(in srgb, var(--panel-2), transparent 18%);
    }
    html[data-theme] #tab-financeiro .financial-table thead th,
    html[data-theme] #tab-isaias .analysis-matrix thead th,
    html[data-theme] #tab-frequencia :is(.churn-risk-table, .cluster-unit-table) thead th {
      color: var(--ink);
      background: color-mix(in srgb, var(--active-blue), var(--panel-2) 78%);
      border-color: color-mix(in srgb, var(--active-cyan), transparent 82%);
    }
    html[data-theme] #tab-financeiro .financial-section-row th,
    html[data-theme] #tab-isaias .analysis-matrix-section td {
      color: var(--active-green);
      background: color-mix(in srgb, var(--active-teal), var(--panel) 86%) !important;
    }
    html[data-theme] #tab-financeiro .financial-network,
    html[data-theme] #tab-isaias .network-column {
      color: var(--active-green) !important;
      background: color-mix(in srgb, var(--active-green), transparent 91%) !important;
    }
    html[data-theme] #tab-financeiro .financial-revenue-tabs button.active {
      color: #f8fffb;
      border-color: var(--active-teal);
      background: var(--active-teal);
    }
    html[data-theme] #tab-frequencia .churn-risk-source {
      border-color: color-mix(in srgb, var(--active-cyan), transparent 62%);
      background: color-mix(in srgb, var(--active-blue), transparent 92%);
    }
    html[data-theme] #tab-frequencia .churn-risk-donut-track {
      stroke: color-mix(in srgb, var(--active-cyan), transparent 88%);
    }
    html[data-theme] #tab-frequencia .churn-risk-donut-center {
      border-color: color-mix(in srgb, var(--active-cyan), transparent 78%);
      background: color-mix(in srgb, var(--panel), transparent 4%);
    }
    html[data-theme] #tab-isaias .medal-board-panel {
      box-shadow: var(--glass-shadow);
    }
    html[data-theme] #tab-isaias .medal-board-table {
      border-color: color-mix(in srgb, var(--active-cyan), transparent 76%);
      background: color-mix(in srgb, var(--panel-2), transparent 12%);
    }
    html[data-theme] #tab-isaias .medal-row.head {
      color: var(--ink);
      background: color-mix(in srgb, var(--active-blue), var(--panel-2) 76%);
    }
    html[data-theme] #tab-isaias .medal-row:nth-child(even):not(.head) {
      background: color-mix(in srgb, var(--active-cyan), transparent 94%);
    }
    html[data-theme] #tab-isaias .medal-row:nth-child(odd):not(.head) {
      background: color-mix(in srgb, var(--active-green), transparent 96%);
    }
    html[data-theme] #tab-isaias .medal-row {
      border-color: color-mix(in srgb, var(--active-cyan), transparent 86%);
    }
    html[data-theme] #tab-isaias .analysis-matrix-delta.positive { color: var(--active-green); }
    html[data-theme] #tab-isaias .analysis-matrix-delta.negative { color: var(--wellhub-pink); }
    html[data-theme] #tab-isaias .isaias-chat textarea {
      border-color: color-mix(in srgb, var(--active-cyan), transparent 58%);
      background: color-mix(in srgb, var(--panel-2), transparent 8%);
    }
    html[data-theme] #tab-isaias .isaias-chat textarea:focus {
      border-color: var(--active-teal);
      box-shadow: 0 0 0 4px color-mix(in srgb, var(--active-teal), transparent 84%);
    }
    html[data-theme] #tab-isaias .isaias-chat button {
      color: #f8fffb;
      border-color: var(--active-teal);
      background: var(--active-teal);
    }
    @media print {
      .layout-editor-actions,
      .layout-editor-hint,
      .layout-box-tools,
      .layout-resize-handle { display: none !important; }
    }
    /* Cancellation overview: independent KPI cards and balanced first-row charts. */
    html[data-theme],
    html[data-theme] body {
      max-width: 100%;
      overflow-x: clip;
    }
    html[data-theme] #tab-cancelamentos > .summary-strip {
      margin: 0 0 12px;
      padding: 0;
      border: 0;
      background: transparent;
      box-shadow: none;
    }
    html[data-theme] #tab-cancelamentos > .summary-strip > .cards {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      align-items: stretch;
    }
    html[data-theme] #tab-cancelamentos > .summary-strip .card {
      min-width: 0;
      min-height: 132px;
      padding: 15px 14px 13px;
      border-radius: 13px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }
    html[data-theme] #tab-cancelamentos > .summary-strip .card-label {
      width: 100%;
      padding-right: 0;
      overflow: hidden;
      color: var(--ink);
      font-size: clamp(12px, .76vw, 14px);
      line-height: 1.15;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    html[data-theme] #tab-cancelamentos > .summary-strip .card:nth-child(4) .card-label {
      font-size: clamp(11.25px, .7vw, 13.25px);
      letter-spacing: -.02em;
    }
    html[data-theme] #tab-cancelamentos > .summary-strip .card-icon {
      left: 14px;
      width: 38px;
      height: 38px;
    }
    html[data-theme] #tab-cancelamentos > .summary-strip .card-value {
      right: 14px;
      left: 14px;
      font-size: clamp(28px, 1.75vw, 35px);
      line-height: 1;
    }
    html[data-theme] #tab-cancelamentos > .summary-strip .card > small,
    html[data-theme] #tab-cancelamentos > .summary-strip .card-foot {
      align-self: end;
      min-height: 22px;
      padding-top: 9px;
      border-top: 1px solid var(--line);
      font-size: 11.5px;
      line-height: 1.15;
      white-space: normal;
    }
    html[data-theme] #tab-cancelamentos .cancel-top-pair {
      grid-template-columns: minmax(0, 1.72fr) minmax(430px, .88fr);
      gap: 12px;
      align-items: stretch;
    }
    html[data-theme] #tab-cancelamentos .cancel-top-pair > .panel {
      min-height: 405px;
      height: 100%;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-month {
      display: grid;
      grid-template-rows: auto auto auto minmax(235px, 1fr);
      align-content: stretch;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-month .panel-subtitle,
    html[data-theme] #tab-cancelamentos .chart-cancel-month .column-legend {
      justify-content: center;
      text-align: center;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-month .column-list {
      width: 100%;
      min-height: 235px;
      align-self: end;
      padding-top: 8px;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-month .column-pair,
    html[data-theme] #tab-cancelamentos .chart-cancel-month .column-track {
      height: 172px;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-contracts {
      min-width: 0;
      display: grid;
      grid-template-columns: minmax(205px, .78fr) minmax(245px, 1.22fr);
      grid-template-rows: auto minmax(0, 1fr);
      align-items: center;
      gap: 10px 18px;
      padding: 16px 18px;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-contracts .composition-title {
      grid-column: 1 / -1;
      align-self: start;
      margin-bottom: 2px !important;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-contracts .donut-shell {
      width: min(235px, 100%);
      justify-self: center;
      align-self: center;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-contracts .donut {
      width: min(225px, 100%);
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-contracts .composition-copy {
      min-width: 0;
      width: 100%;
      align-self: center;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-contracts .composition-copy > p {
      margin: 0 0 12px;
      text-align: center;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-contracts .legend {
      gap: 7px;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-contracts .legend-row {
      min-width: 0;
      grid-template-columns: 12px minmax(0, 1fr) auto;
      gap: 8px;
      font-size: 13px;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-contracts .legend-row > span:nth-child(2) {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    html[data-theme] #tab-cancelamentos .cancel-unit-retention-grid {
      gap: 12px;
    }
    @media (max-width: 1500px) {
      html[data-theme] #tab-cancelamentos .cancel-top-pair {
        grid-template-columns: minmax(0, 1.5fr) minmax(390px, .9fr);
      }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts {
        grid-template-columns: 1fr;
        grid-template-rows: auto auto minmax(0, 1fr);
      }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .composition-title,
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .donut-shell,
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .composition-copy {
        grid-column: 1;
      }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .donut-shell { width: min(190px, 70%); }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .donut { width: min(185px, 100%); }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .composition-copy > p { display: none; }
    }
    @media (max-width: 1050px) {
      html[data-theme] #tab-cancelamentos > .summary-strip > .cards {
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }
    }
    @media (max-width: 1100px) {
      html[data-theme] #tab-cancelamentos .cancel-top-pair { grid-template-columns: 1fr; }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts {
        grid-template-columns: minmax(200px, .8fr) minmax(260px, 1.2fr);
        grid-template-rows: auto minmax(0, 1fr);
      }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .composition-title { grid-column: 1 / -1; }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .donut-shell { grid-column: 1; width: min(220px, 100%); }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .donut { width: min(210px, 100%); }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .composition-copy { grid-column: 2; }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts .composition-copy > p { display: block; }
    }
    @media (max-width: 760px) {
      html[data-theme] #tab-cancelamentos > .summary-strip > .cards { grid-template-columns: 1fr; }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts {
        grid-template-columns: 1fr;
        grid-template-rows: auto auto auto;
      }
      html[data-theme] #tab-cancelamentos .chart-cancel-contracts :is(.composition-title, .donut-shell, .composition-copy) { grid-column: 1; }
    }
    /* BioFisic glass workspace: translucent layers, soft blur and detached cards. */
    html[data-theme="dark"] {
      --bg: #071011;
      --panel: rgba(32, 40, 40, .72);
      --panel-2: rgba(47, 56, 56, .56);
      --line: rgba(232, 255, 249, .13);
      --glass-highlight: rgba(255, 255, 255, .075);
      --glass-shadow: 0 18px 42px rgba(0, 0, 0, .30), inset 0 1px 0 rgba(255, 255, 255, .055);
      --glass-shadow-soft: 0 10px 26px rgba(0, 0, 0, .22), inset 0 1px 0 rgba(255, 255, 255, .045);
      --shadow: var(--glass-shadow);
    }
    html[data-theme="light"] {
      --bg: #d9ece9;
      --panel: rgba(247, 253, 252, .64);
      --panel-2: rgba(255, 255, 255, .52);
      --line: rgba(255, 255, 255, .72);
      --glass-highlight: rgba(255, 255, 255, .52);
      --glass-shadow: 0 20px 46px rgba(49, 88, 91, .15), inset 0 1px 0 rgba(255, 255, 255, .78);
      --glass-shadow-soft: 0 11px 28px rgba(49, 88, 91, .11), inset 0 1px 0 rgba(255, 255, 255, .68);
      --shadow: var(--glass-shadow);
    }
    html[data-theme] body {
      min-height: 100vh;
      background-attachment: fixed;
      background-color: var(--bg);
      background-image:
        radial-gradient(circle at 8% 3%, color-mix(in srgb, var(--green), transparent 79%) 0, transparent 29%),
        radial-gradient(circle at 90% 6%, color-mix(in srgb, var(--violet), transparent 80%) 0, transparent 31%),
        radial-gradient(circle at 54% 94%, color-mix(in srgb, var(--blue), transparent 88%) 0, transparent 34%),
        linear-gradient(145deg, color-mix(in srgb, var(--bg), #fff 3%), var(--bg));
    }
    html[data-theme="dark"] body {
      background-image:
        radial-gradient(circle at 7% 2%, rgba(0, 232, 90, .14) 0, transparent 28%),
        radial-gradient(circle at 92% 4%, rgba(147, 63, 230, .14) 0, transparent 31%),
        radial-gradient(circle at 54% 96%, rgba(45, 118, 255, .08) 0, transparent 35%),
        linear-gradient(145deg, #081112, #050909 66%, #091010);
    }
    html[data-theme] .topbar {
      top: 10px;
      width: calc(100% - 24px);
      min-height: 72px;
      margin: 10px auto 0;
      border: 1px solid var(--line);
      border-radius: 19px;
      background:
        linear-gradient(135deg, var(--glass-highlight), transparent 42%),
        color-mix(in srgb, var(--panel), transparent 5%);
      box-shadow: var(--glass-shadow-soft);
      -webkit-backdrop-filter: blur(24px) saturate(145%);
      backdrop-filter: blur(24px) saturate(145%);
    }
    html[data-theme] .header-tools .theme-toggle,
    html[data-theme] .filter-field input:not([type="checkbox"]),
    html[data-theme] .filter-field select,
    html[data-theme] .multi-select-toggle,
    html[data-theme] .apply-filters-btn,
    html[data-theme] .layout-edit-toggle,
    html[data-theme] .layout-text-hide,
    html[data-theme] .layout-reset {
      border-color: var(--line);
      background:
        linear-gradient(135deg, var(--glass-highlight), transparent 58%),
        var(--panel-2);
      box-shadow: inset 0 1px 0 color-mix(in srgb, #fff, transparent 82%);
      -webkit-backdrop-filter: blur(14px) saturate(130%);
      backdrop-filter: blur(14px) saturate(130%);
    }
    html[data-theme] .shell {
      width: min(1820px, calc(100vw - 40px));
      padding-top: 20px;
    }
    html[data-theme] .hero {
      margin-bottom: 18px;
      padding: 13px 14px;
      border-color: var(--line);
      border-radius: 18px;
      background:
        linear-gradient(135deg, var(--glass-highlight), transparent 46%),
        var(--panel);
      box-shadow: var(--glass-shadow-soft);
      -webkit-backdrop-filter: blur(22px) saturate(140%);
      backdrop-filter: blur(22px) saturate(140%);
    }
    html[data-theme] .summary-strip,
    html[data-theme] #tab-cancelamentos > .summary-strip {
      margin-bottom: 4px;
      padding: 0;
      border: 0;
      border-radius: 0;
      background: transparent;
      box-shadow: none;
      -webkit-backdrop-filter: none;
      backdrop-filter: none;
    }
    html[data-theme] .cards,
    html[data-theme] .active-card-grid,
    html[data-theme] .active-footer-cards,
    html[data-theme] #tab-cancelamentos > .summary-strip > .cards {
      gap: 15px;
    }
    html[data-theme] .card,
    html[data-theme] #tab-cancelamentos > .summary-strip .card {
      border: 1px solid var(--line);
      border-radius: 17px;
      background:
        linear-gradient(135deg, var(--glass-highlight), transparent 48%),
        var(--panel-2);
      box-shadow: var(--glass-shadow-soft);
      -webkit-backdrop-filter: blur(20px) saturate(140%);
      backdrop-filter: blur(20px) saturate(140%);
      transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
    }
    @media (hover: hover) {
      html[data-theme] .card:hover {
        border-color: color-mix(in srgb, var(--green), var(--line) 60%);
        box-shadow: var(--glass-shadow);
        transform: translateY(-2px);
      }
    }
    html[data-theme] .tab-panel.active,
    html[data-theme] .dashboard-layout-grid {
      gap: 16px;
    }
    html[data-theme] .grid,
    html[data-theme] .sales-primary-layout,
    html[data-theme] .sales-chart-columns,
    html[data-theme] .frequency-main-grid,
    html[data-theme] .frequency-pair-grid,
    html[data-theme] .frequency-cluster-grid,
    html[data-theme] .cancel-layout,
    html[data-theme] .cancel-top-pair,
    html[data-theme] .cancel-unit-retention-grid,
    html[data-theme] .cancel-retention-stack,
    html[data-theme] .cancel-threshold-pair,
    html[data-theme] .financial-chart-pair,
    html[data-theme] .sales-month-contract-pair,
    html[data-theme] .active-demographic-trio,
    html[data-theme] .active-overview-trio {
      gap: 16px;
    }
    html[data-theme] .panel,
    html[data-theme] .composition-panel,
    html[data-theme] .medal-board-panel,
    html[data-theme] .brief-card,
    html[data-theme] .benchmark-card,
    html[data-theme] .cluster-unit-table-wrap,
    html[data-theme] #tab-cancelamentos .cancel-top-pair > .panel {
      border-color: var(--line);
      border-radius: 19px;
      background:
        linear-gradient(135deg, var(--glass-highlight), transparent 44%),
        var(--panel);
      box-shadow: var(--glass-shadow);
      -webkit-backdrop-filter: blur(24px) saturate(145%);
      backdrop-filter: blur(24px) saturate(145%);
    }
    html[data-theme] .bar-track,
    html[data-theme] .cluster-track,
    html[data-theme] .cluster-unit-mini-track,
    html[data-theme] .active-goal-track,
    html[data-theme] .aggregator-unique-track,
    html[data-theme] .line-canvas,
    html[data-theme] .timeline-chart,
    html[data-theme] .access-day-card {
      background: color-mix(in srgb, var(--panel-2), transparent 12%);
      -webkit-backdrop-filter: blur(10px);
      backdrop-filter: blur(10px);
    }
    html[data-theme] .financial-table thead th,
    html[data-theme] .analysis-matrix thead th,
    html[data-theme] .churn-risk-table thead th,
    html[data-theme] .cluster-unit-table th {
      background: color-mix(in srgb, var(--panel-2), transparent 6%);
    }
    html[data-theme] .financial-table tbody th:first-child,
    html[data-theme] .financial-table td,
    html[data-theme] .analysis-matrix .analysis-indicator-cell,
    html[data-theme] .analysis-matrix td,
    html[data-theme] .churn-risk-table td,
    html[data-theme] .cluster-unit-table td {
      background: color-mix(in srgb, var(--panel), transparent 8%);
    }
    html[data-theme] .sales-live-ticker,
    html[data-theme] .layout-editor-hint {
      border-color: var(--line);
      background:
        linear-gradient(135deg, var(--glass-highlight), transparent 55%),
        var(--panel);
      box-shadow: var(--glass-shadow-soft);
      -webkit-backdrop-filter: blur(18px) saturate(135%);
      backdrop-filter: blur(18px) saturate(135%);
    }
    html[data-theme] .chart-expand-button {
      border: 1px solid var(--line);
      background: color-mix(in srgb, var(--panel-2), transparent 5%);
      box-shadow: var(--glass-shadow-soft);
      -webkit-backdrop-filter: blur(12px);
      backdrop-filter: blur(12px);
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-cannibalization .bar-row {
      grid-template-columns: minmax(50px, 64px) minmax(0, 1fr) 52px;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-units .stacked-column-frame {
      padding-inline: 0;
      border: 0;
      background: transparent;
    }
    html[data-theme] #tab-cancelamentos .chart-cancel-units .stacked-track {
      background: transparent;
    }
    /* Cleaner unit charts: numbers stay neutral; visual direction remains in bars and icons. */
    html[data-theme] .active-goal-main-goal,
    html[data-theme] .active-goal-attainment,
    html[data-theme] .active-goal-growth,
    html[data-theme] .active-goal-growth.positive,
    html[data-theme] .active-goal-growth.negative,
    html[data-theme] .active-goal-growth.stable,
    html[data-theme] .aggregator-unique-access,
    html[data-theme] .aggregator-unique-access.wellhub,
    html[data-theme] .aggregator-unique-access.totalpass {
      color: var(--ink);
    }
    html[data-theme] .active-card-grid {
      grid-template-columns: repeat(5, minmax(0, 1fr));
    }
    html[data-theme] .active-footer-cards {
      grid-template-columns: repeat(5, minmax(0, 1fr));
      grid-auto-rows: 1fr;
      align-items: stretch;
    }
    html[data-theme] .active-footer-cards .card {
      width: 100%;
      min-height: 136px;
      height: 100%;
    }
    /* Active page summaries: compact on the canvas, analytical detail on expansion. */
    .active-goals-panel:not(.expanded-chart-clone) > .active-goals-detail {
      display: none !important;
    }
    .active-goals-panel:not(.expanded-chart-clone) {
      padding-top: 44px !important;
      padding-bottom: 12px !important;
    }
    .active-goals-compact {
      display: grid;
      gap: 11px;
      align-content: center;
      min-height: 100px;
      padding: 0 2px;
    }
    .active-goals-compact h2 {
      margin: 0;
      text-align: center;
      transform: translateY(-7px);
    }
    .active-overview-trio {
      grid-template-columns: minmax(300px, .82fr) minmax(0, 1.18fr);
      align-items: stretch;
    }
    .active-overview-trio > .chart-active-units {
      grid-column: 1 / -1;
      align-self: start;
      height: auto;
    }
    .active-overview-trio > .composition-panel {
      grid-column: 1;
      grid-row: 2;
      align-self: start;
      height: auto;
      min-height: 0;
    }
    .active-overview-trio > .chart-profile-age {
      grid-column: 1;
      grid-row: 3;
      align-self: stretch;
      min-height: 420px;
    }
    .active-overview-trio > .aggregator-unique-panel {
      grid-column: 2;
      grid-row: 2;
      align-self: start;
      height: auto;
    }
    .active-overview-trio > .chart-profile-gender {
      grid-column: 2;
      grid-row: 3;
      align-self: start;
      height: auto;
    }
    .active-overview-column {
      min-width: 0;
      display: flex;
      flex-direction: column;
      align-self: stretch;
      gap: 16px;
    }
    .active-overview-column.left {
      grid-column: 1;
      grid-row: 2;
    }
    .active-overview-column.right {
      grid-column: 2;
      grid-row: 2;
    }
    .active-overview-column > .panel {
      min-width: 0;
      width: 100%;
      height: auto;
      min-height: 0;
      margin: 0;
    }
    .active-overview-column > .chart-profile-age {
      flex: 1 1 auto;
      min-height: 420px;
    }
    .active-lower-layout {
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(390px, .65fr);
      align-items: stretch;
      gap: 16px;
    }
    .active-lower-contract {
      min-width: 0;
    }
    .active-lower-contract > .panel {
      min-width: 0;
      height: 100%;
      margin: 0;
    }
    html[data-theme] .active-lower-layout > .active-footer-cards {
      min-width: 0;
      margin: 0;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      grid-template-rows: repeat(2, minmax(0, 1fr));
      grid-auto-rows: minmax(0, 1fr);
      align-items: stretch;
      gap: 12px;
    }
    html[data-theme] .active-lower-layout > .active-footer-cards .card {
      min-width: 0;
      min-height: 0;
      height: 100%;
    }
    .active-network-summary-row {
      min-width: 0;
      display: grid;
      grid-template-columns: 42px 62px minmax(72px, 1fr) 62px 94px 20px;
      align-items: center;
      gap: 7px;
      color: var(--ink);
      font-size: 11.5px;
      font-weight: 900;
      font-variant-numeric: tabular-nums;
    }
    .active-network-summary-row > strong {
      color: var(--green);
      text-transform: uppercase;
    }
    .active-network-summary-value,
    .active-network-summary-goal,
    .active-network-summary-growth {
      color: var(--ink);
      white-space: nowrap;
      text-align: center;
    }
    .active-network-summary-chart {
      min-width: 0;
      display: grid;
      gap: 5px;
    }
    .active-network-summary-line {
      min-width: 0;
      height: 9px;
      display: flex;
      overflow: hidden;
      border-radius: 999px;
      background: color-mix(in srgb, var(--muted), transparent 82%);
      box-shadow: inset 0 0 0 1px var(--line);
    }
    .active-network-summary-segment {
      min-width: 0;
      height: 100%;
      flex: 0 0 var(--segment-width);
      box-sizing: border-box;
      border-right: 1px solid color-mix(in srgb, var(--bg), #000 25%);
      background: var(--segment-color);
    }
    .active-network-summary-segment:last-child {
      border-right: 0;
    }
    .active-network-summary-units {
      min-width: 0;
      display: flex;
      align-items: flex-start;
    }
    .active-network-summary-unit {
      min-width: 0;
      flex: 0 0 var(--segment-width);
      overflow: hidden;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      line-height: 1.1;
      text-align: center;
      white-space: nowrap;
    }
    /* Financeiro: resumo proporcional no painel e matriz completa na expansão. */
    .financial-matrix-panel:not(.expanded-chart-clone) {
      min-height: 170px;
      padding-top: 44px !important;
      padding-bottom: 16px !important;
    }
    .financial-matrix-panel:not(.expanded-chart-clone) .financial-matrix-header {
      align-items: center;
      margin-bottom: 14px;
    }
    .financial-matrix-panel:not(.expanded-chart-clone) .financial-matrix-header > div:first-child {
      flex: 1 1 auto;
      padding-left: 150px;
      text-align: center;
    }
    .financial-matrix-panel:not(.expanded-chart-clone) .financial-matrix-header .panel-subtitle,
    .financial-matrix-panel:not(.expanded-chart-clone) .financial-matrix-detail,
    .financial-matrix-panel:not(.expanded-chart-clone) .financial-note {
      display: none !important;
    }
    .financial-matrix-compact { display: block; }
    .financial-network-summary-row {
      min-width: 0;
      display: grid;
      grid-template-columns: 50px 128px minmax(0, 1fr);
      align-items: center;
      gap: 12px;
      color: var(--ink);
      font-size: 12px;
      font-weight: 900;
      font-variant-numeric: tabular-nums;
    }
    .financial-network-summary-row > strong {
      color: var(--green);
      text-align: center;
    }
    .financial-network-summary-total {
      color: var(--ink);
      text-align: center;
      white-space: nowrap;
    }
    .financial-network-summary-chart {
      min-width: 0;
      display: grid;
      gap: 7px;
    }
    .financial-network-summary-line {
      min-width: 0;
      height: 12px;
      display: flex;
      overflow: hidden;
      border-radius: 999px;
      background: color-mix(in srgb, var(--muted), transparent 82%);
      box-shadow: inset 0 0 0 1px var(--line);
    }
    .financial-network-summary-segment {
      min-width: 0;
      height: 100%;
      flex: 0 0 var(--segment-width);
      box-sizing: border-box;
      border-right: 1px solid color-mix(in srgb, var(--bg), #000 25%);
      background: var(--segment-color);
    }
    .financial-network-summary-segment:last-child { border-right: 0; }
    .financial-network-summary-units {
      min-width: 0;
      display: flex;
      align-items: flex-start;
    }
    .financial-network-summary-unit {
      min-width: 0;
      flex: 0 0 var(--segment-width);
      overflow: hidden;
      color: var(--muted);
      font-size: 11px;
      font-weight: 900;
      line-height: 1.1;
      text-align: center;
      white-space: nowrap;
    }
    .expanded-chart-clone.financial-matrix-panel .financial-matrix-compact { display: none !important; }
    .expanded-chart-clone.financial-matrix-panel .financial-matrix-detail { display: block !important; }
    .expanded-chart-clone.financial-matrix-panel {
      min-height: 100%;
      padding: 24px !important;
    }
    .expanded-chart-clone.financial-matrix-panel .financial-matrix-header {
      align-items: center;
      margin-bottom: 18px;
    }
    .expanded-chart-clone.financial-matrix-panel .financial-table-wrap {
      overflow: auto;
      border-radius: 14px;
    }
    .expanded-chart-clone.financial-matrix-panel .financial-table th,
    .expanded-chart-clone.financial-matrix-panel .financial-table td {
      padding: 13px 5px;
    }
    .expanded-chart-clone.financial-matrix-panel .financial-table thead th {
      font-size: clamp(12px, .82vw, 14px) !important;
      line-height: 1.25;
    }
    .expanded-chart-clone.financial-matrix-panel .financial-table td {
      font-size: clamp(12px, .82vw, 14px) !important;
      line-height: 1.25;
      letter-spacing: -.015em;
    }
    .expanded-chart-clone.financial-matrix-panel .financial-indicator {
      font-size: clamp(15px, 1vw, 17px) !important;
      line-height: 1.25;
    }
    .expanded-chart-clone.financial-matrix-panel .financial-indicator small {
      font-size: clamp(11px, .72vw, 13px) !important;
    }
    .expanded-chart-clone.financial-matrix-panel .financial-section-row th {
      padding: 11px 14px;
      font-size: clamp(11px, .78vw, 14px) !important;
    }
    .expanded-chart-clone.financial-matrix-panel .financial-note {
      font-size: 12px;
      line-height: 1.55;
    }
    html[data-theme] #tab-isaias .analysis-matrix-wrap {
      border-radius: 14px;
    }
    html[data-theme] #tab-isaias .analysis-matrix {
      font-size: clamp(12px, .82vw, 14px);
      font-variant-numeric: tabular-nums;
    }
    html[data-theme] #tab-isaias .analysis-matrix th,
    html[data-theme] #tab-isaias .analysis-matrix td {
      padding: 13px 5px;
      line-height: 1.25;
    }
    html[data-theme] #tab-isaias .analysis-matrix thead th {
      font-size: clamp(12px, .82vw, 14px) !important;
      line-height: 1.25;
    }
    html[data-theme] #tab-isaias .analysis-matrix .analysis-indicator-cell {
      padding-inline: 12px;
      font-size: clamp(15px, 1vw, 17px);
      font-weight: 900;
      line-height: 1.25;
    }
    html[data-theme] #tab-isaias .analysis-matrix-value {
      font-size: clamp(12px, .82vw, 14px);
      line-height: 1.25;
    }
    html[data-theme] #tab-isaias .analysis-matrix-delta {
      margin-top: 5px;
      font-size: clamp(11px, .72vw, 13px);
      line-height: 1.2;
    }
    html[data-theme] #tab-isaias .analysis-matrix-section td {
      padding: 11px 14px;
      font-size: clamp(11px, .78vw, 14px) !important;
      line-height: 1.25;
    }
    @media (max-width: 980px) {
      .financial-matrix-panel:not(.expanded-chart-clone) .financial-matrix-header > div:first-child { padding-left: 0; }
      .financial-network-summary-row { grid-template-columns: 46px 105px minmax(0, 1fr); gap: 7px; }
      .financial-network-summary-unit { font-size: 9px; }
    }
    .expanded-chart-clone .active-goals-compact { display: none !important; }
    .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone > .active-goals-detail {
      display: grid;
    }
    .chart-expand-modal[data-chart-kind="active-units"] .expanded-chart-clone > .active-goals-header.active-goals-detail {
      display: none;
    }
    .chart-profile-gender:not(.expanded-chart-clone) .column-list,
    .chart-profile-gender:not(.expanded-chart-clone) > .column-legend,
    .chart-profile-gender:not(.expanded-chart-clone) > .panel-subtitle {
      display: none;
    }
    .gender-summary-card {
      min-height: 170px;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      align-items: stretch;
      gap: 12px;
      margin-top: 16px;
    }
    .gender-summary-metric {
      min-width: 0;
      display: grid;
      grid-template-rows: auto 1fr auto;
      align-items: center;
      justify-items: center;
      gap: 6px;
      padding: 18px 12px;
      border: 1px solid var(--line);
      border-radius: 15px;
      color: var(--ink);
      background:
        linear-gradient(135deg, color-mix(in srgb, var(--gender-color), transparent 90%), transparent 58%),
        var(--panel-2);
      box-shadow: var(--glass-shadow-soft);
      text-align: center;
    }
    .gender-summary-metric span {
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .gender-summary-metric strong {
      color: var(--ink);
      font-size: clamp(28px, 3vw, 46px);
      font-weight: 950;
      line-height: 1;
      letter-spacing: -.04em;
    }
    .gender-summary-metric small {
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
    }
    .expanded-chart-clone .gender-summary-card { display: none !important; }
    .age-gender-pyramid-panel {
      min-width: 0;
      display: grid;
      grid-template-rows: auto auto minmax(0, 1fr) auto auto;
      align-content: start;
      gap: 10px;
    }
    .age-gender-pyramid-panel > h2 {
      width: 100%;
      margin: 0;
      text-align: center;
    }
    .age-pyramid-head,
    .age-pyramid-row {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(58px, 72px) minmax(0, 1fr);
      align-items: center;
      gap: 8px;
    }
    .age-pyramid-head {
      min-height: 25px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 950;
      letter-spacing: .04em;
      text-align: center;
      text-transform: uppercase;
    }
    .age-pyramid-head strong:first-child { color: var(--blue); text-align: right; }
    .age-pyramid-head strong:last-child { color: var(--green); text-align: left; }
    .age-pyramid-list {
      min-height: 0;
      display: grid;
      align-content: center;
      gap: 8px;
    }
    .age-pyramid-row { min-height: 31px; }
    .age-pyramid-side {
      min-width: 0;
      display: grid;
      align-items: center;
      gap: 6px;
    }
    .age-pyramid-men { grid-template-columns: 68px minmax(0, 1fr); }
    .age-pyramid-women { grid-template-columns: minmax(0, 1fr) 68px; }
    .age-pyramid-track {
      min-width: 0;
      height: 24px;
      display: flex;
      align-items: stretch;
      overflow: hidden;
      background: color-mix(in srgb, var(--muted), transparent 88%);
      box-shadow: inset 0 0 0 1px var(--line);
    }
    .age-pyramid-men .age-pyramid-track {
      justify-content: flex-end;
      border-radius: 8px 2px 2px 8px;
    }
    .age-pyramid-women .age-pyramid-track {
      justify-content: flex-start;
      border-radius: 2px 8px 8px 2px;
    }
    .age-pyramid-track i {
      width: var(--age-width);
      min-width: 2px;
      height: 100%;
      display: block;
      background: var(--age-color);
      box-shadow: 0 0 16px color-mix(in srgb, var(--age-color), transparent 55%);
    }
    .age-pyramid-men .age-pyramid-track i { border-radius: 8px 2px 2px 8px; }
    .age-pyramid-women .age-pyramid-track i { border-radius: 2px 8px 8px 2px; }
    .age-pyramid-band {
      min-width: 0;
      color: var(--ink);
      font-size: 11px;
      line-height: 1.05;
      text-align: center;
    }
    .age-pyramid-value {
      min-width: 0;
      display: grid;
      line-height: 1;
      font-variant-numeric: tabular-nums;
    }
    .age-pyramid-men .age-pyramid-value { text-align: right; }
    .age-pyramid-women .age-pyramid-value { text-align: left; }
    .age-pyramid-value strong { color: var(--ink); font-size: 12px; font-weight: 950; }
    .age-pyramid-value small { margin-top: 2px; color: var(--muted); font-size: 9px; font-weight: 850; }
    .age-pyramid-summary {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: center;
      gap: 8px 16px;
      padding-top: 8px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 10px;
      font-weight: 800;
    }
    .age-pyramid-summary span { display: inline-flex; align-items: center; gap: 5px; }
    .age-pyramid-summary strong { color: var(--ink); font-size: 11px; }
    .age-sex-dot { width: 8px; height: 8px; border-radius: 50%; }
    .age-sex-dot.male { background: var(--blue); }
    .age-sex-dot.female { background: var(--green); }
    .age-pyramid-footer {
      margin: 0;
      color: var(--muted);
      font-size: 9px;
      font-weight: 750;
      line-height: 1.3;
      text-align: center;
    }
    .chart-expand-modal[data-chart-kind="active-age"] .chart-expand-content { overflow: hidden; }
    .chart-expand-modal[data-chart-kind="active-age"] .expanded-chart-clone.age-gender-pyramid-panel {
      height: 100%;
      min-height: 0;
      grid-template-rows: auto auto minmax(0, 1fr) auto auto;
      gap: 16px;
      overflow: hidden;
    }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-head,
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-row {
      grid-template-columns: minmax(0, 1fr) minmax(100px, 130px) minmax(0, 1fr);
      gap: 18px;
    }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-head { font-size: 16px; }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-list { gap: 13px; }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-row { min-height: 55px; }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-men { grid-template-columns: 110px minmax(0, 1fr); }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-women { grid-template-columns: minmax(0, 1fr) 110px; }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-track { height: 44px; }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-band { font-size: 17px; }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-value strong { font-size: 19px; }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-value small { font-size: 13px; }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-summary { font-size: 15px; }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-summary strong { font-size: 17px; }
    .chart-expand-modal[data-chart-kind="active-age"] .age-pyramid-footer { font-size: 13px; }
    @media (max-width: 900px) {
      html[data-theme] .topbar {
        top: 6px;
        width: calc(100% - 12px);
        margin-top: 6px;
        border-radius: 15px;
      }
      html[data-theme] .shell { width: calc(100vw - 16px); padding-top: 14px; }
      html[data-theme] .cards,
      html[data-theme] .tab-panel.active,
      html[data-theme] .dashboard-layout-grid { gap: 12px; }
      html[data-theme] .active-footer-cards {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
      html[data-theme] .active-card-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
      .active-network-summary-row {
        grid-template-columns: 42px 58px minmax(90px, 1fr) 58px 86px 18px;
        font-size: 10.5px;
      }
      .active-overview-trio { grid-template-columns: 1fr; }
      .active-overview-trio > :is(.chart-active-units, .composition-panel, .chart-profile-age, .aggregator-unique-panel, .chart-profile-gender, .active-overview-column) {
        grid-column: 1;
        grid-row: auto;
      }
      .chart-sales-units .column-list {
        grid-template-columns: repeat(14, minmax(24px, 1fr));
        gap: 4px;
      }
      .chart-sales-units .column-label { font-size: 10px; }
      .chart-sales-units .column-value { font-size: 11px; }
      .active-demographic-trio { grid-template-columns: 1fr; }
      .active-lower-layout { grid-template-columns: 1fr; }
    }
    @media (max-width: 560px) {
      html[data-theme] .active-card-grid,
      html[data-theme] .active-footer-cards { grid-template-columns: 1fr; }
      .active-network-summary-row {
        grid-template-columns: 42px minmax(0, 1fr) 20px;
        grid-template-areas:
          "label line daily"
          "value goal growth";
        row-gap: 10px;
      }
      .active-network-summary-row > strong { grid-area: label; }
      .active-network-summary-value { grid-area: value; text-align: left; }
      .active-network-summary-chart { grid-area: line; }
      .active-network-summary-goal { grid-area: goal; }
      .active-network-summary-growth { grid-area: growth; text-align: right; }
      .active-network-summary-row > .active-goal-daily { grid-area: daily; }
      .gender-summary-card { grid-template-columns: 1fr; }
      html[data-theme] .active-lower-layout > .active-footer-cards { grid-template-columns: 1fr; grid-template-rows: none; }
      .age-pyramid-head,
      .age-pyramid-row { grid-template-columns: minmax(0, 1fr) 52px minmax(0, 1fr); gap: 5px; }
      .age-pyramid-men { grid-template-columns: 46px minmax(0, 1fr); }
      .age-pyramid-women { grid-template-columns: minmax(0, 1fr) 46px; }
      .age-pyramid-value strong { font-size: 10px; }
      .age-pyramid-value small { display: none; }
      .active-overview-trio .composition-copy .legend {
        width: min(330px, 100%);
        grid-template-columns: 1fr;
        grid-template-rows: none;
        grid-auto-flow: row;
      }
    }
    @media print {
      .topbar { display: none; }
      body { background: #fff; }
      .shell { width: 100%; padding: 0; }
      .tab-panel { display: grid !important; break-inside: avoid; }
    }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <span class="brand-mark">BIOFISIC</span>
      <span class="brand-analytics">ANALYTICS</span>
    </div>
    <nav class="tabs" id="tabs" aria-label="Abas do dashboard"></nav>
    <div class="header-tools">
      <button class="theme-toggle" id="themeToggle" type="button" aria-label="Alternar tema" title="Alternar tema">
        <span class="theme-toggle-icon" aria-hidden="true">☾</span>
        <span class="theme-toggle-label">Modo escuro</span>
      </button>
      <span class="header-notification" title="Notificações" aria-hidden="true">
        <svg viewBox="0 0 24 24"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></svg>
      </span>
      <span class="header-avatar" title="Análise BioFisic">IA</span>
    </div>
  </header>
  <main class="shell">
    <section class="hero">
      <div class="hero-title">
        <h1><span class="brand-word">BioFisic</span><span class="brand-sub">Analytics</span></h1>
        <div class="source" id="sourceText"></div>
      </div>
      <form class="dashboard-filters" id="dashboardFilters">
        <label class="filter-field">
          <span>Período</span>
          <div class="multi-select" id="periodFilterMulti">
            <button class="multi-select-toggle" id="periodFilterToggle" type="button" data-filter-open="period">Todo o período</button>
            <input id="periodStart" name="periodStart" type="hidden" value="" />
            <input id="periodEnd" name="periodEnd" type="hidden" value="" />
          </div>
        </label>
        <label class="filter-field">
          <span>Unidade</span>
          <div class="multi-select" id="unitFilterMulti">
            <button class="multi-select-toggle" id="unitFilterToggle" type="button" data-filter-open="unit">Todas as unidades</button>
            <input id="unitFilter" name="unitFilter" type="hidden" value="" />
            <input id="unitFilters" name="unitFilters" type="hidden" value="" />
          </div>
        </label>
        <label class="filter-field">
          <span>Faixa etária</span>
          <div class="multi-select" id="ageFilterMulti">
            <button class="multi-select-toggle" id="ageFilterToggle" type="button" data-filter-open="age">Todas as faixas</button>
            <input id="ageFilter" name="ageFilter" type="hidden" value="" />
            <input id="ageFilters" name="ageFilters" type="hidden" value="" />
          </div>
        </label>
        <label class="filter-field">
          <span>Sexo</span>
          <div class="multi-select" id="genderFilterMulti">
            <button class="multi-select-toggle" id="genderFilterToggle" type="button" data-filter-open="gender">Todos</button>
            <input id="genderFilter" name="genderFilter" type="hidden" value="" />
            <input id="genderFilters" name="genderFilters" type="hidden" value="" />
          </div>
        </label>
        <button class="apply-filters-btn" id="applyFiltersButton" type="button">Limpar filtros</button>
      </form>
      <div class="hero-actions">
        <div class="layout-editor-actions" aria-label="Edição da página">
          <button class="layout-edit-toggle" id="layoutEditToggle" type="button" aria-pressed="false">Editar página</button>
          <button class="layout-text-hide" id="layoutTextHide" type="button" hidden disabled>Ocultar texto</button>
          <button class="layout-reset" id="layoutReset" type="button" hidden>Restaurar aba</button>
        </div>
        <div class="header-upload" aria-label="Sincronização com o Supabase">
          <span class="header-upload-status" id="csvUploadStatus">Supabase</span>
          <button class="analyze-btn" id="analyzeCsvButton" type="button">Sincronizar agora</button>
        </div>
        <button class="print-btn" id="exportXlsxButton" type="button">Exportar XLSX</button>
      </div>
    </section>
    <aside class="layout-editor-hint" id="layoutEditorHint" hidden>
      <strong>Modo de edição</strong>
      <span>Arraste as caixas pelo controle, redimensione pelo canto inferior direito e clique em títulos ou descrições para editar.</span>
    </aside>
    <div class="filter-popup-backdrop" id="filterPopup" hidden>
      <section class="filter-popup" role="dialog" aria-modal="true" aria-labelledby="filterPopupTitle">
        <div class="filter-popup-head">
          <h2 id="filterPopupTitle">Selecionar filtro</h2>
          <button class="filter-popup-close" id="filterPopupClose" type="button" aria-label="Fechar">×</button>
        </div>
        <div class="filter-popup-list" id="filterPopupList"></div>
        <div class="filter-popup-actions">
          <button class="filter-popup-clear" id="filterPopupClear" type="button">Limpar seleção</button>
          <button class="filter-popup-apply" id="filterPopupApply" type="button">Aplicar seleção</button>
        </div>
      </section>
    </div>
    <section id="tabPanels"></section>
    <section id="medalBoard" hidden></section>
  </main>
  <div class="chart-expand-modal" id="chartExpandModal" hidden role="dialog" aria-modal="true" aria-labelledby="chartExpandTitle">
    <section class="chart-expand-dialog">
      <header class="chart-expand-head">
        <h2 id="chartExpandTitle">Visualização ampliada</h2>
        <button class="chart-expand-close" id="chartExpandClose" type="button" aria-label="Fechar visualização ampliada">×</button>
      </header>
      <div class="chart-expand-content" id="chartExpandContent"></div>
      <footer class="chart-expand-scenario">
        <strong>LEITURA DO CENÁRIO</strong>
        <p id="chartExpandScenario">A visualização ampliada preserva os filtros e o período atualmente selecionados.</p>
      </footer>
    </section>
  </div>
  <script type="application/json" id="dashboardData">__DATA__</script>
  <script type="module">
    if (window.location.protocol === "file:") {
      window.location.replace("http://127.0.0.1:8765/dashboard_vendas_mar_abr_mai_2026.html");
      await new Promise(() => {});
    }
    let data = JSON.parse(document.getElementById("dashboardData").textContent);
    const fmtInt = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
    const fmtPct = new Intl.NumberFormat("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    const fmtMoney = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const colors = { green:"#00f529", blue:"#38a3ff", red:"#ff5049", orange:"#00f529", violet:"#b56cff", graphite:"#3a4447" };
    const wellhubColor = "#d8385e";
    const activeUnitPalette = ["#1d4ed8", "#245bdc", "#2968df", "#2e75e0", "#3283df", "#3491dc", "#349fd6", "#32accf", "#2fb8c4", "#2bc2b7", "#2ac9a7", "#35cb95", "#4aca82", "#62c776"];
    const activePaletteColor = (index, total) => activeUnitPalette[Math.round(Math.max(0, index) * (activeUnitPalette.length - 1) / Math.max(1, Number(total || 1) - 1))];
    const layoutStoragePrefix = "biofisic.dashboard.layout.v1";
    const layoutStorageVersion = 3;
    const textStoragePrefix = "biofisic.dashboard.text.v1";
    let layoutEditMode = false;
    let selectedEditableText = null;
    let draggedLayoutPanel = null;
    const layoutMasonryFrames = new WeakMap();
    const tone = {
      green: colors.green,
      blue: colors.blue,
      red: colors.red,
      orange: colors.orange,
      violet: colors.violet,
      graphite: colors.graphite,
      wellhub: wellhubColor,
      growthOrange: "#ff9f43",
      activeBlue: activePaletteColor(0, activeUnitPalette.length),
      activeCyan: activePaletteColor(5, activeUnitPalette.length),
      activeTeal: activePaletteColor(9, activeUnitPalette.length),
      activeGreen: activePaletteColor(13, activeUnitPalette.length),
    };
    const chartUsesActivePalette = chart => chart?.palette === "active" || chart?.palette === "cancellation";
    const semanticPaletteColor = (chart, item, index, total) => {
      if (chart?.palette === "cancellation" && item?.tone === "red") return wellhubColor;
      return chartUsesActivePalette(chart) ? activePaletteColor(index, total) : null;
    };
    const tabs = [
      ["ativos", "Visão Geral"],
      ["vendas", "Vendas"],
      ["cancelamentos", "Cancelamentos"],
      ["financeiro", "Financeiro"],
      ["frequencia", "Frequência"],
      ["isaias", "Análise"],
    ];
    const themeStorageKey = "biofisic-theme-glass-2026";
    let selectedTheme = "dark";
    try {
      selectedTheme = localStorage.getItem(themeStorageKey) || "light";
    } catch (error) {
      selectedTheme = "dark";
    }
    if (!new Set(["light", "dark"]).has(selectedTheme)) selectedTheme = "dark";
    document.documentElement.dataset.theme = selectedTheme;
    let isaiasHistory = [];
    let activeUnitSortMode = "opening";
    const loadedTabKeys = new Set(Object.entries(data.tabs || {})
      .filter(([key, tab]) => !tab?.loading && !(key === "vendas" && data.salesSnapshot))
      .map(([key]) => key));
    const tabLoadPromises = new Map();
    let requestDashboardTab = async () => {};
    const churnRiskRegistry = new Map();
    const lineChartSelections = new Map();
    const int = value => fmtInt.format(Number(value || 0));
    const pct = value => `${fmtPct.format(Number(value || 0))}%`;
    const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, ch => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;" }[ch]));
    const unitAbbreviations = {
      "Capitão Gomes":"CG", "Itajubá Centro":"CE", "Itajubá Varginha":"VG",
      "Pouso Alegre Foch":"PA", "Poços de Caldas":"PC", "Três Corações RP":"TC1",
      "Batatais":"BAT", "Itu":"ITU", "Guaratinguetá BR":"GUA1", "Guaratinguetá JK":"GUA2",
      "Três Corações CE":"TC2", "Lorena":"LOR", "Pouso Alegre Fátima":"PA2",
      "Jacareí":"JAC", "Rede":"REDE",
    };
    const unitAbbreviation = unit => unitAbbreviations[String(unit || "")] || String(unit || "");
    const compactUnitLabel = label => unitAbbreviation(String(label || "").trim());
    function cardGlyph(label) {
      const text = String(label || "").toLocaleLowerCase("pt-BR");
      if (text.includes("adimpl")) return text.includes("inadimpl") ? "!" : "✓";
      if (text.includes("wellhub")) return "W";
      if (text.includes("totalpass")) return "TP";
      if (text.includes("idade") || text.includes("dias")) return "D";
      if (text.includes("ativo")) return "A";
      if (text.includes("cancel") || text.includes("churn")) return "C";
      if (text.includes("fatur") || text.includes("receita") || text.includes("ticket")) return "R$";
      if (text.includes("venda") || text.includes("contrato")) return "V";
      if (text.includes("acesso") || text.includes("frequ")) return "F";
      return "•";
    }
    function cardHtml(card) {
      if (card.kind === "peakSales") {
        return `<article class="card peak-sales-card" style="--tone:${tone[card.tone] || colors.green}">
          <span class="card-icon" aria-hidden="true">${escapeHtml(cardGlyph(card.label))}</span>
          <span class="card-label">${escapeHtml(card.label)}</span>
          <small class="card-subtitle">${escapeHtml(card.sub || "")}</small>
          <div class="peak-sales-body">
            <div class="peak-sales-day"><em>Dia</em><strong>${escapeHtml(card.day || "—")}</strong></div>
            <div class="peak-sales-count"><em>Vendas</em><strong>${int(card.quantity)}</strong><div class="peak-sales-share">${pct(card.share)} do período</div></div>
          </div>
        </article>`;
      }
      const metricClass = ["good", "bad", "violet"].includes(card.status) ? card.status : "";
      const valueClass = ["good", "bad"].includes(card.valueStatus) ? card.valueStatus : "";
      const metric = card.metric ? `<span class="card-metric ${metricClass}">${escapeHtml(card.metric)}</span>` : "";
      const meta = card.meta ? `<span class="card-meta">${escapeHtml(card.meta)}</span>` : "";
      return `<article class="card" style="--tone:${tone[card.tone] || colors.green}">
        <span class="card-icon" aria-hidden="true">${escapeHtml(cardGlyph(card.label))}</span>
        <span class="card-label">${escapeHtml(card.label)}</span>
        <strong class="card-value ${valueClass}">${escapeHtml(card.value)}</strong>
        ${card.metric || card.meta ? `<div class="card-foot">${meta}${metric}</div>` : `<small>${escapeHtml(card.sub || "")}</small>`}
        ${card.metric && card.sub ? `<small>${escapeHtml(card.sub || "")}</small>` : ""}
      </article>`;
    }
    function summaryCardsHtml(cards, gridClass = "") {
      const rows = cards || [];
      if (!rows.length) return "";
      return `<section class="summary-strip">
        <div class="cards ${gridClass}">${rows.map(cardHtml).join("")}</div>
      </section>`;
    }
    function barPanel(chart) {
      const rows = chart.rows || [];
      const max = Number(chart.maxValue) || Math.max(...rows.map(row => Number(row.value) || 0), 1);
      const panelClass = chart.className ? ` ${chart.className}` : "";
      return `<article class="panel${panelClass}">
        <h2>${escapeHtml(chart.title)}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        <div class="bar-list">
          ${rows.length ? rows.map((row, index) => {
            const value = Number(row.value) || 0;
            const width = Math.max(1, value / max * 100);
            const barColor = chartUsesActivePalette(chart)
              ? activePaletteColor(index, rows.length)
              : row.tone ? (tone[row.tone] || colors.blue) : chart.barTone ? (tone[chart.barTone] || colors.blue) : [colors.green, colors.blue, colors.orange, colors.violet, colors.red][index % 5];
            const label = `${row.medal ? `${row.medal} ` : ""}${compactUnitLabel(row.label)}`;
            const valueHtml = row.display != null
              ? escapeHtml(row.display)
              : row.pct != null
                ? `<span class="bar-count">${escapeHtml(int(value))}</span><strong>${escapeHtml(pct(row.pct))}</strong>`
                : escapeHtml(int(value));
            const valueClass = row.valueClass ? ` ${escapeHtml(row.valueClass)}` : "";
            const labelTitle = row.description || label;
            return `<div class="bar-row" ${row.display != null ? `data-display="${escapeHtml(row.display)}"` : ""}>
              <div class="bar-label" title="${escapeHtml(labelTitle)}">${escapeHtml(label)}</div>
              <div class="bar-track"><div class="bar-fill" style="--w:${width}%;--bar:${barColor}"></div></div>
              <div class="bar-value${valueClass}">${valueHtml}</div>
            </div>`;
          }).join("") : `<div class="source">Sem dados suficientes para este gráfico.</div>`}
        </div>
      </article>`;
    }
    function signedInt(value) {
      const numeric = Number(value || 0);
      return `${numeric > 0 ? "+" : ""}${int(numeric)}`;
    }
    function signedPct(value) {
      const numeric = Number(value || 0);
      return `${numeric > 0 ? "+" : ""}${pct(numeric)}`;
    }
    function activeDailyIndicator(value) {
      if (value == null || Number.isNaN(Number(value))) return { icon: "–", cls: "missing", title: "Sem comparação com o dia anterior" };
      const numeric = Number(value);
      if (numeric > 0) return { icon: "↑", cls: "up", title: `Cresceu ${int(numeric)} desde o dia anterior` };
      if (numeric < 0) return { icon: "↓", cls: "down", title: `Caiu ${int(Math.abs(numeric))} desde o dia anterior` };
      return { icon: "●", cls: "stable", title: "Estável em relação ao dia anterior" };
    }
    function activeGoalsPanel(chart) {
      const sourceRows = Array.isArray(chart.rows) ? chart.rows : [];
      const openingOrder = row => Number.isFinite(Number(row.openingOrder)) ? Number(row.openingOrder) : Number.MAX_SAFE_INTEGER;
      const rows = [...sourceRows].sort((a, b) => {
        const inaugurationOrder = openingOrder(a) - openingOrder(b);
        if (activeUnitSortMode === "opening") return inaugurationOrder;
        return (Number(b.value || 0) - Number(a.value || 0)) || inaugurationOrder;
      });
      const activeOnly = activeUnitSortMode === "active";
      const activeScaleMax = Math.max(...rows.map(row => Number(row.value) || 0), 1);
      const sortLabel = activeUnitSortMode === "active" ? "ATIVOS" : "INAUGURAÇÃO";
      const network = chart.network || {};
      const networkDaily = activeDailyIndicator(network.dailyDelta);
      const networkGoalPct = Number(network.goalPct || 0);
      const networkWidth = activeOnly ? 100 : (Number(network.goal || 0) > 0 ? Math.max(1, Math.min(networkGoalPct, 100)) : 0);
      const networkGrowthClass = Number(network.growthDelta || 0) > 0 ? "positive" : Number(network.growthDelta || 0) < 0 ? "negative" : "stable";
      const networkLinePalette = activeUnitPalette;
      const networkLineTotal = Math.max(rows.reduce((sum, row) => sum + Math.max(0, Number(row.value || 0)), 0), 1);
      const networkLineSegments = rows.map((row, index) => {
        const current = Math.max(0, Number(row.value || 0));
        const share = current / networkLineTotal * 100;
        const segmentColor = networkLinePalette[index % networkLinePalette.length];
        return `<span class="active-network-summary-segment" style="--segment-width:${share}%;--segment-color:${segmentColor}" title="${escapeHtml(`${row.label}: ${int(current)} ativos (${pct(share)})`)}"></span>`;
      }).join("");
      const networkLineLabels = rows.map(row => {
        const current = Math.max(0, Number(row.value || 0));
        const share = current / networkLineTotal * 100;
        return `<span class="active-network-summary-unit" style="--segment-width:${share}%" title="${escapeHtml(`${row.label}: ${int(current)} ativos`)}">${escapeHtml(compactUnitLabel(row.label))}</span>`;
      }).join("");
      const panelClass = chart.className ? ` ${chart.className}` : "";
      return `<article class="panel active-goals-panel${activeOnly ? " active-only" : ""}${panelClass}">
        <div class="active-goals-compact">
          <h2>${escapeHtml(chart.title)}</h2>
          <div class="active-network-summary-row">
            <strong>Rede</strong>
            <span class="active-network-summary-value" title="Alunos ativos da rede">${int(network.value)}</span>
            <div class="active-network-summary-chart" title="Composição proporcional dos alunos ativos por unidade">
              <div class="active-network-summary-line">${networkLineSegments}</div>
              <div class="active-network-summary-units" aria-label="Siglas das unidades">${networkLineLabels}</div>
            </div>
            <span class="active-network-summary-goal" title="Meta de ativos da rede">${int(network.goal)}</span>
            <span class="active-network-summary-growth" title="Variação da rede desde o fechamento do mês anterior">${signedInt(network.growthDelta)} · ${signedPct(network.growthPct)}</span>
            <div class="active-goal-daily ${networkDaily.cls}" title="${escapeHtml(networkDaily.title)}">${networkDaily.icon}</div>
          </div>
        </div>
        <div class="active-goals-header active-goals-detail">
          <div>
            <h2>${escapeHtml(chart.title)}</h2>
          </div>
          <button class="active-goal-sort" type="button" data-active-goal-sort title="Alternar entre ordem de inauguração e quantidade de ativos">
            <span>⇅</span><span>${escapeHtml(sortLabel)}</span>
          </button>
        </div>
        <div class="active-goal-list active-goals-detail">
          ${rows.length ? rows.map((row, rowIndex) => {
            const current = Number(row.value || 0);
            const goal = Number(row.goal || 0);
            const goalPct = Number(row.goalPct || 0);
            const growthDelta = Number(row.growthDelta || 0);
            const growthPct = Number(row.growthPct || 0);
            const width = activeOnly ? Math.max(1, current / activeScaleMax * 100) : (goal > 0 ? Math.max(1, Math.min(goalPct, 100)) : 0);
            const growthClass = growthDelta > 0 ? "positive" : growthDelta < 0 ? "negative" : "stable";
            const daily = activeDailyIndicator(row.dailyDelta);
            const stars = "★".repeat(Math.max(0, Math.min(3, Number(row.stars || 0))));
            return `<div class="active-goal-row${activeOnly ? " active-only" : ""}">
              <div class="active-goal-label" title="${escapeHtml(row.label)}">${stars ? `<span class="active-goal-stars">${stars}</span>` : ""}${escapeHtml(compactUnitLabel(row.label))}</div>
              <div class="active-goal-track" title="${escapeHtml(activeOnly ? `${row.label}: ${int(current)} ativos` : `${row.label}: ${int(current)} de ${goal ? int(goal) : "meta pendente"}`)}">
                <div class="active-goal-fill" style="--w:${width}%"></div>
                <span class="active-goal-bar-value real">${int(current)}</span>
                ${activeOnly ? "" : `<span class="active-goal-bar-value goal">${goal > 0 ? int(goal) : "—"}</span>`}
              </div>
              ${activeOnly ? "" : `<div class="active-goal-target">
                <span class="active-goal-main-goal" title="Meta de ativos">${goal > 0 ? int(goal) : "—"}</span>
                <span class="active-goal-attainment" title="Atingimento da meta">${goal > 0 ? pct(goalPct) : "—"}</span>
              </div>`}
              <div class="active-goal-growth ${growthClass}" title="Variação desde o fechamento do mês anterior">${signedInt(growthDelta)} · ${signedPct(growthPct)}</div>
              <div class="active-goal-daily ${daily.cls}" title="${escapeHtml(daily.title)}">${daily.icon}</div>
            </div>`;
          }).join("") : `<div class="source">Sem snapshots suficientes no HISTORICO ATIVOS.</div>`}
        </div>
        ${rows.length ? `<div class="active-goal-network active-goals-detail">
          <strong>Rede</strong>
          <div class="active-goal-track" title="${activeOnly ? `Rede: ${int(network.value)} ativos` : `Rede: ${int(network.value)} de ${int(network.goal)}`}">
            <div class="active-goal-fill" style="--w:${networkWidth}%"></div>
            <span class="active-goal-bar-value real">${int(network.value)}</span>
            ${activeOnly ? "" : `<span class="active-goal-bar-value goal">${int(network.goal)}</span>`}
          </div>
          ${activeOnly ? "" : `<div class="active-goal-target">
            <span class="active-goal-main-goal" title="Meta de ativos da rede">${int(network.goal)}</span>
            <span class="active-goal-attainment" title="Atingimento da meta da rede">${pct(networkGoalPct)}</span>
          </div>`}
          <div class="active-goal-growth ${networkGrowthClass}" title="Variação da rede desde o fechamento do mês anterior">${signedInt(network.growthDelta)} · ${signedPct(network.growthPct)}</div>
          <div class="active-goal-daily ${networkDaily.cls}" title="${escapeHtml(networkDaily.title)}">${networkDaily.icon}</div>
        </div>` : ""}
      </article>`;
    }
    function aggregatorUniquePanel(chart) {
      const rows = Array.isArray(chart.rows) ? chart.rows : [];
      const network = chart.network || {};
      const stackedTrack = (wellhubValue, totalpassValue, label, wellhubAccesses, totalpassAccesses) => {
        const wellhub = Math.max(0, Number(wellhubValue || 0));
        const totalpass = Math.max(0, Number(totalpassValue || 0));
        const total = wellhub + totalpass;
        const wellhubPct = total > 0 ? wellhub / total * 100 : 0;
        const totalpassPct = total > 0 ? totalpass / total * 100 : 0;
        return `<div class="aggregator-unique-track" title="${escapeHtml(`${label}: Wellhub ${int(wellhub)} usuários e ${int(wellhubAccesses)} acessos · TotalPass ${int(totalpass)} usuários e ${int(totalpassAccesses)} acessos`)}">
          <div class="aggregator-unique-stack" style="--w:100%">
            ${wellhub > 0 ? `<div class="aggregator-unique-segment wellhub" style="width:${wellhubPct}%"></div>` : ""}
            ${totalpass > 0 ? `<div class="aggregator-unique-segment totalpass" style="width:${totalpassPct}%"></div>` : ""}
          </div>
          <span class="aggregator-unique-user-value wellhub" title="Usuários Wellhub">${int(wellhub)}</span>
          <span class="aggregator-unique-user-value totalpass" title="Usuários TotalPass">${int(totalpass)}</span>
        </div>`;
      };
      const panelClass = chart.className ? ` ${chart.className}` : "";
      const networkWellhub = Number(network.wellhub || 0);
      const networkTotalpass = Number(network.totalpass || 0);
      const networkWellhubAccesses = Number(network.wellhubAccesses || 0);
      const networkTotalpassAccesses = Number(network.totalpassAccesses || 0);
      return `<article class="panel aggregator-unique-panel${panelClass}">
        <div class="aggregator-unique-header">
          <div>
            <h2>${escapeHtml(chart.title || "Agregadores por unidade")}</h2>
          </div>
          <div class="aggregator-unique-legend" aria-label="Legenda dos agregadores">
            <span><i class="wellhub"></i>Wellhub</span>
            <span><i class="totalpass"></i>TotalPass</span>
          </div>
        </div>
        <div class="aggregator-unique-list">
          ${rows.length ? rows.map(row => {
            const wellhub = Number(row.wellhub || 0);
            const totalpass = Number(row.totalpass || 0);
            const wellhubAccesses = Number(row.wellhubAccesses || 0);
            const totalpassAccesses = Number(row.totalpassAccesses || 0);
            const stars = "★".repeat(Math.max(0, Math.min(3, Number(row.stars || 0))));
            const averageVisits = Number(row.averageVisits || 0);
            return `<div class="aggregator-unique-row">
              <div class="aggregator-unique-label" title="${escapeHtml(`${row.label} · média ${averageVisits.toFixed(2).replace('.', ',')} visitas por usuário`)}">${stars ? `<span class="aggregator-unique-stars">${stars}</span>` : ""}${escapeHtml(compactUnitLabel(row.label))}</div>
              <div class="aggregator-unique-access wellhub" title="Acessos Wellhub">${int(wellhubAccesses)}</div>
              ${stackedTrack(wellhub, totalpass, row.label, wellhubAccesses, totalpassAccesses)}
              <div class="aggregator-unique-access totalpass" title="Acessos TotalPass">${int(totalpassAccesses)}</div>
            </div>`;
          }).join("") : `<div class="source">Sem IDs válidos de Wellhub ou TotalPass.</div>`}
        </div>
        ${rows.length ? `<div class="aggregator-unique-network">
          <strong>Rede</strong>
          <div class="aggregator-unique-access wellhub" title="Acessos Wellhub da rede">${int(networkWellhubAccesses)}</div>
          ${stackedTrack(networkWellhub, networkTotalpass, "Rede", networkWellhubAccesses, networkTotalpassAccesses)}
          <div class="aggregator-unique-access totalpass" title="Acessos TotalPass da rede">${int(networkTotalpassAccesses)}</div>
        </div>` : ""}
      </article>`;
    }
    function populationPanel(chart) {
      const rows = Array.isArray(chart?.rows) ? chart.rows : [];
      const values = rows.map(row => Math.max(0, Number(row.value) || 0));
      const total = values.reduce((sum, value) => sum + value, 0);
      const exactCounts = values.map(value => total ? value / total * 100 : 0);
      const counts = exactCounts.map(value => Math.floor(value));
      let remaining = Math.max(0, 100 - counts.reduce((sum, value) => sum + value, 0));
      exactCounts
        .map((value, index) => ({ index, fraction: value - Math.floor(value) }))
        .sort((a, b) => b.fraction - a.fraction)
        .slice(0, remaining)
        .forEach(item => { counts[item.index] += 1; });
      const dots = rows.flatMap((row, index) => {
        const color = activePaletteColor(index, rows.length);
        return Array.from({ length: counts[index] }, () => `<span class="contract-population-dot" style="--population-color:${color}" title="${escapeHtml(row.label)} · ${int(values[index])} vendas"></span>`);
      }).join("");
      const panelClass = chart.className ? ` ${chart.className}` : "";
      return `<article class="panel contract-population-panel${panelClass}">
        <h2>${escapeHtml(chart.title || "Contratos vendidos no mês")}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        <div class="contract-population-layout">
          <div class="contract-population-grid" aria-label="Distribuição dos contratos vendidos representada em 100 esferas">${dots}</div>
          <div class="contract-population-legend">
            ${rows.map((row, index) => {
              const color = activePaletteColor(index, rows.length);
              const share = row.pct != null ? Number(row.pct) : (total ? values[index] / total * 100 : 0);
              return `<div style="--population-color:${color}"><i style="--population-color:${color}"></i><span>${escapeHtml(row.label)}</span><strong>${int(values[index])} · ${pct(share)}</strong></div>`;
            }).join("")}
          </div>
        </div>
        <p class="contract-population-note">Cada esfera representa aproximadamente 1% das vendas válidas no período.</p>
      </article>`;
    }
    function columnPanel(chart) {
      const rows = chart.rows || [];
      const hasSegments = rows.some(row => Array.isArray(row.segments));
      const max = Number(chart.maxValue) || (hasSegments
        ? Math.max(...rows.flatMap(row => (row.segments || []).map(segment => Number(segment.value) || 0)), 1)
        : Math.max(...rows.map(row => Number(row.value) || 0), 1));
      const panelClass = chart.className ? ` ${chart.className}` : "";
      const barColor = chart.barTone ? (tone[chart.barTone] || colors.orange) : colors.orange;
      const legendRows = chart.legend || (hasSegments ? (rows[0]?.segments || []).map(segment => ({
        label: segment.label,
        color: segment.color,
        tone: segment.tone,
      })) : []);
      const isGenderChart = String(chart.className || "").includes("chart-profile-gender");
      const genderPopulationView = isGenderChart && rows.length ? (() => {
        const genderColor = (row, rowIndex) => {
          const label = String(row.label || "").toLocaleLowerCase("pt-BR");
          if (label.includes("mascul")) return colors.blue;
          if (label.includes("feminin")) return wellhubColor;
          return "#5f6f7d";
        };
        const rawShares = rows.map(row => Math.max(0, Number(row.pct) || 0));
        const shareTotal = rawShares.reduce((sum, value) => sum + value, 0) || 1;
        const exactCounts = rawShares.map(value => value / shareTotal * 100);
        const counts = exactCounts.map(value => Math.floor(value));
        let remaining = 100 - counts.reduce((sum, value) => sum + value, 0);
        exactCounts
          .map((value, index) => ({ index, fraction: value - Math.floor(value) }))
          .sort((a, b) => b.fraction - a.fraction)
          .slice(0, remaining)
          .forEach(item => { counts[item.index] += 1; });
        const dots = rows.flatMap((row, rowIndex) => {
          const dotColor = genderColor(row, rowIndex);
          return Array.from({ length: counts[rowIndex] }, () => `<span class="population-dot" style="--population-color:${dotColor}" title="${escapeHtml(row.label)}"></span>`);
        }).join("");
        return `<div class="population-view" aria-label="Distribuição por sexo representada em 100 esferas">
          <div class="population-grid">${dots}</div>
          <div class="population-legend">
            ${rows.map((row, rowIndex) => {
              const dotColor = genderColor(row, rowIndex);
              return `<div><i style="--population-color:${dotColor}"></i><span>${escapeHtml(row.label)}</span><strong>${int(row.value)} · ${pct(row.pct)}</strong><small>${counts[rowIndex]} de 100 esferas</small></div>`;
            }).join("")}
          </div>
          <p>Cada esfera representa aproximadamente 1% da base selecionada.</p>
        </div>`;
      })() : "";
      const genderSummaryCard = isGenderChart && rows.length ? (() => {
        const findGender = term => rows.find(row => String(row.label || "").toLocaleLowerCase("pt-BR").includes(term));
        const summaryRows = [
          { label: "Masculino", row: findGender("mascul"), color: colors.blue },
          { label: "Feminino", row: findGender("feminin"), color: wellhubColor },
        ].filter(item => item.row);
        return `<div class="gender-summary-card" aria-label="Resumo da distribuição por sexo">
          ${summaryRows.map(item => `<div class="gender-summary-metric" style="--gender-color:${item.color}">
            <span>${item.label}</span>
            <strong>${pct(item.row.pct)}</strong>
            <small>${int(item.row.value)} alunos</small>
          </div>`).join("")}
        </div>`;
      })() : "";
      return `<article class="panel column-panel${panelClass}">
        <h2>${escapeHtml(chart.title)}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        ${legendRows.length ? `<div class="column-legend">
          ${legendRows.map((item, index) => {
            const legendColor = semanticPaletteColor(chart, item, index, legendRows.length) || item.color || tone[item.tone] || barColor;
            return `<span style="--legend-color:${legendColor}">${escapeHtml(item.label)}</span>`;
          }).join("")}
        </div>` : ""}
        ${genderSummaryCard}
        <div class="column-list">
          ${rows.length ? rows.map((row, rowIndex) => {
            if (Array.isArray(row.segments)) {
              const labelHtml = row.weekday && row.dateLabel
                ? `<div class="column-label day-label" title="${escapeHtml(row.label)}"><strong>${escapeHtml(row.weekday)}</strong><span>${escapeHtml(row.dateLabel)}</span></div>`
                : `<div class="column-label" title="${escapeHtml(row.label)}">${escapeHtml(compactUnitLabel(row.label))}</div>`;
              return `<div class="column-item grouped-column-item">
                <div class="column-pair" style="--cols:${row.segments.length || 1}">
                  ${row.segments.map((segment, segmentIndex) => {
                    const segmentValue = Number(segment.value) || 0;
                    const height = Math.max(2, segmentValue / max * 100);
                    const segmentColor = semanticPaletteColor(chart, segment, segmentIndex, row.segments.length) || segment.color || tone[segment.tone] || barColor;
                    return `<div class="column-track" title="${escapeHtml(segment.label)}: ${int(segmentValue)}"><div class="column-fill" style="--h:${height}%;--bar:${segmentColor}"></div></div>`;
                  }).join("")}
                </div>
                <div class="column-value column-split-values" style="--cols:${row.segments.length || 1}">
                  ${row.segments.map((segment, segmentIndex) => {
                    const segmentColor = semanticPaletteColor(chart, segment, segmentIndex, row.segments.length) || segment.color || tone[segment.tone] || barColor;
                    const segmentText = `${segment.medal ? `${segment.medal} ` : ""}${segment.display || int(segment.value)}`;
                    return `<span style="--value-color:${segmentColor}" title="${escapeHtml(segment.label)}">${escapeHtml(segmentText)}</span>`;
                  }).join("")}
                </div>
                ${labelHtml}
              </div>`;
            }
            const value = Number(row.value) || 0;
            const height = Math.max(2, value / max * 100);
            const rowColor = chartUsesActivePalette(chart)
              ? activePaletteColor(rowIndex, rows.length)
              : row.color || tone[row.tone] || tone[(chart.rowTones || [])[rowIndex]] || barColor;
            return `<div class="column-item">
              <div class="column-track"><div class="column-fill" style="--h:${height}%;--bar:${rowColor}"></div></div>
              <div class="column-value"><span>${int(value)}</span>${chart.showPct ? `<small>${pct(row.pct)}</small>` : ""}</div>
              <div class="column-label" title="${escapeHtml(row.label)}">${escapeHtml(compactUnitLabel(row.label))}</div>
            </div>`;
          }).join("") : `<div class="source">Sem dados suficientes para este gráfico.</div>`}
        </div>
        ${genderPopulationView}
      </article>`;
    }
    function collectionComboPanel(chart) {
      const rows = chart.rows || [];
      const panelClass = chart.className ? ` ${chart.className}` : "";
      if (!rows.length) {
        return `<article class="panel${panelClass}"><h2>${escapeHtml(chart.title)}</h2><div class="source">Sem dados suficientes para este gráfico.</div></article>`;
      }
      const width = 1120;
      const height = 390;
      const pad = { left: 54, right: 26, top: 42, bottom: 58 };
      const innerW = width - pad.left - pad.right;
      const innerH = height - pad.top - pad.bottom;
      const max = Math.max(...rows.map(row => Math.max(Number(row.scheduled) || 0, Number(row.received) || 0)), 1);
      const step = innerW / rows.length;
      const barWidth = Math.min(44, step * .56);
      const x = index => pad.left + step * index + step / 2;
      const y = value => pad.top + (1 - (Number(value) || 0) / max) * innerH;
      const baseline = pad.top + innerH;
      const barColor = activePaletteColor(2, 14);
      const lineColor = wellhubColor;
      const curvePoints = rows.map((row, index) => ({ x: x(index), y: y(row.received) }));
      const clampCurveY = value => Math.max(pad.top, Math.min(baseline, value));
      const smoothCurvePath = points => {
        if (!points.length) return "";
        if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;
        let path = `M ${points[0].x} ${points[0].y}`;
        for (let index = 0; index < points.length - 1; index += 1) {
          const previous = points[index - 1] || points[index];
          const current = points[index];
          const next = points[index + 1];
          const following = points[index + 2] || next;
          const controlOneX = current.x + (next.x - previous.x) / 6;
          const controlOneY = clampCurveY(current.y + (next.y - previous.y) / 6);
          const controlTwoX = next.x - (following.x - current.x) / 6;
          const controlTwoY = clampCurveY(next.y - (following.y - current.y) / 6);
          path += ` C ${controlOneX} ${controlOneY}, ${controlTwoX} ${controlTwoY}, ${next.x} ${next.y}`;
        }
        return path;
      };
      const curvePath = smoothCurvePath(curvePoints);
      const grid = [0, .25, .5, .75, 1].map(fraction => {
        const gridY = pad.top + (1 - fraction) * innerH;
        return `<line class="collection-combo-grid" x1="${pad.left}" y1="${gridY}" x2="${width - pad.right}" y2="${gridY}"></line><text class="collection-combo-axis" x="${pad.left - 10}" y="${gridY + 4}" text-anchor="end">${int(max * fraction)}</text>`;
      }).join("");
      const bars = rows.map((row, index) => {
        const scheduled = Number(row.scheduled) || 0;
        const top = y(scheduled);
        const label = `${row.medal ? `${row.medal} ` : ""}${compactUnitLabel(row.label)}`;
        return `<rect class="collection-combo-bar" style="--bar-color:${barColor}" x="${x(index) - barWidth / 2}" y="${top}" width="${barWidth}" height="${Math.max(1, baseline - top)}" rx="6"><title>${escapeHtml(row.label)} · previstas: ${int(scheduled)}</title></rect>
          <text class="collection-combo-value" x="${x(index)}" y="${Math.max(pad.top + 12, top - 8)}">${int(scheduled)}</text>
          <text class="collection-combo-unit" x="${x(index)}" y="${baseline + 30}" text-anchor="middle">${escapeHtml(label)}</text>`;
      }).join("");
      const points = rows.map((row, index) => {
        const received = Number(row.received) || 0;
        const pointY = y(received);
        return `<circle class="collection-combo-point" style="--line-color:${lineColor}" cx="${x(index)}" cy="${pointY}" r="6"><title>${escapeHtml(row.label)} · recebidas: ${int(received)} (${pct(row.rate)})</title></circle>
          <text class="collection-combo-rate" style="--line-color:${lineColor}" x="${x(index)}" y="${Math.min(baseline - 8, pointY + 20)}">${int(received)}</text>`;
      }).join("");
      return `<article class="panel collection-combo-panel${panelClass}">
        <h2>${escapeHtml(chart.title)}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        <div class="collection-combo-legend">
          <span><i style="--series-color:${barColor}"></i>Parcelas previstas</span>
          <span><i style="--series-color:${lineColor}"></i>Parcelas recebidas</span>
        </div>
        <div class="collection-combo-frame">
          <svg class="collection-combo-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Parcelas previstas e recebidas por unidade">
            ${grid}${bars}
            <path class="collection-combo-line" style="--line-color:${lineColor}" d="${curvePath}"></path>
            ${points}
          </svg>
        </div>
      </article>`;
    }
    function dualBarPanel(chart) {
      const rows = chart.rows || [];
      const max = Math.max(...rows.flatMap(row => [Number(row.medianValue) || 0, Number(row.meanValue) || 0]), 1);
      const primaryMax = chart.primaryMaxValue != null ? Number(chart.primaryMaxValue) : chart.separateScales ? Math.max(...rows.map(row => Number(row.medianValue) || 0), 1) : max;
      const secondaryMax = chart.secondaryMaxValue != null ? Number(chart.secondaryMaxValue) : chart.separateScales ? Math.max(...rows.map(row => Number(row.meanValue) || 0), 1) : max;
      const panelClass = chart.className ? ` ${chart.className}` : "";
      const primaryLabel = chart.primaryLabel || "Mediana";
      const secondaryLabel = chart.secondaryLabel || "Média";
      const useActivePalette = chartUsesActivePalette(chart) || String(chart.className || "").includes("chart-sales-ticket");
      const primaryColor = useActivePalette ? activePaletteColor(1, 5) : colors.blue;
      const secondaryColor = useActivePalette ? activePaletteColor(10, 14) : colors.green;
      return `<article class="panel${panelClass}">
        <h2>${escapeHtml(chart.title)}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        <div class="dual-legend">
          <span style="--legend-color:${primaryColor}">${escapeHtml(primaryLabel)}</span>
          <span style="--legend-color:${secondaryColor}">${escapeHtml(secondaryLabel)}</span>
        </div>
        <div class="bar-list">
          ${rows.length ? rows.map(row => {
            const median = Number(row.medianValue) || 0;
            const mean = Number(row.meanValue) || 0;
            const medianWidth = Math.max(1, median / primaryMax * 100);
            const meanWidth = Math.max(1, mean / secondaryMax * 100);
            const label = `${row.medal ? `${row.medal} ` : ""}${compactUnitLabel(row.label)}`;
            return `<div class="bar-row dual-row">
              <div class="bar-label" title="${escapeHtml(label)}">${escapeHtml(label)}</div>
              <div class="dual-bars">
                <div class="bar-track" title="${escapeHtml(primaryLabel)}"><div class="bar-fill" style="--w:${medianWidth}%;--bar:${primaryColor}"></div></div>
                <div class="bar-track" title="${escapeHtml(secondaryLabel)}"><div class="bar-fill" style="--w:${meanWidth}%;--bar:${secondaryColor}"></div></div>
              </div>
              <div class="dual-value">
                <span>${escapeHtml(row.medianDisplay || "")}</span>
                <small>${escapeHtml(row.meanDisplay || "")}</small>
              </div>
            </div>`;
          }).join("") : `<div class="source">Sem dados suficientes para este gráfico.</div>`}
        </div>
      </article>`;
    }
    function multiBarPanel(chart) {
      const rows = chart.rows || [];
      const bars = rows.flatMap(row => row.bars || []);
      const max = Number(chart.maxValue) || Math.max(...bars.map(bar => Number(bar.value) || 0), 1);
      const panelClass = chart.className ? ` ${chart.className}` : "";
      const legendItems = chart.legend || (rows[0]?.bars || []).map(bar => ({
        label: bar.label,
        color: bar.color,
        tone: bar.tone,
      }));
      return `<article class="panel${panelClass}">
        <h2>${escapeHtml(chart.title)}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        ${legendItems.length ? `<div class="multi-legend">
          ${legendItems.map((item, index) => {
            const legendColor = semanticPaletteColor(chart, item, index, legendItems.length) || item.color || tone[item.tone] || colors.blue;
            return `<span style="--legend-color:${legendColor}">${escapeHtml(item.label)}</span>`;
          }).join("")}
        </div>` : ""}
        <div class="bar-list">
          ${rows.length ? rows.map((row, rowIndex) => {
            const label = `${row.medal ? `${row.medal} ` : ""}${compactUnitLabel(row.label)}`;
            return `<div class="bar-row multi-row">
              <div class="bar-label" title="${escapeHtml(label)}">${escapeHtml(label)}</div>
              <div class="multi-bars">
                ${(row.bars || []).map((bar, barIndex) => {
                  const value = Number(bar.value) || 0;
                  const width = Math.max(1, value / max * 100);
                  const barColor = semanticPaletteColor(chart, bar, barIndex, Math.max((row.bars || []).length, 2)) || bar.color || tone[bar.tone] || colors.blue;
                  return `<div class="bar-track" title="${escapeHtml(bar.label)}: ${escapeHtml(bar.display || int(value))}"><div class="bar-fill" style="--w:${width}%;--bar:${barColor}"></div></div>`;
                }).join("")}
              </div>
              <div class="multi-value">
                ${(row.bars || []).map((bar, barIndex) => {
                  const barColor = semanticPaletteColor(chart, bar, barIndex, Math.max((row.bars || []).length, 2)) || bar.color || tone[bar.tone] || colors.blue;
                  const barText = `${bar.medal ? `${bar.medal} ` : ""}${bar.display || int(bar.value)}`;
                  return `<span style="--value-color:${barColor}">${escapeHtml(barText)}</span>`;
                }).join("")}
              </div>
            </div>`;
          }).join("") : `<div class="source">Sem dados suficientes para este gráfico.</div>`}
        </div>
      </article>`;
    }
    function linePanel(chart) {
      const rows = chart.rows || [];
      const allSeries = chart.series || [];
      const panelClass = chart.className ? ` ${chart.className}` : "";
      const chartKey = chart.className || chart.title || "line-chart";
      if (chart.selectableSeries && !lineChartSelections.has(chartKey)) {
        lineChartSelections.set(chartKey, new Set(chart.defaultSelectedKeys || []));
      }
      const selectedKeys = lineChartSelections.get(chartKey) || new Set();
      const series = chart.selectableSeries
        ? allSeries.filter(item => item.fixed || selectedKeys.has(item.key))
        : allSeries;
      if (!rows.length || !allSeries.length) {
        return `<article class="panel${panelClass}"><h2>${escapeHtml(chart.title)}</h2><div class="source">Sem dados suficientes para este gráfico.</div></article>`;
      }
      const width = 1000;
      const height = 330;
      const pad = { left: 44, right: 24, top: 22, bottom: 54 };
      const innerW = width - pad.left - pad.right;
      const innerH = height - pad.top - pad.bottom;
      const allValues = rows.flatMap(row => series.map(item => Number(row[item.key]) || 0));
      const max = Math.max(...allValues, 1);
      const x = index => pad.left + (rows.length === 1 ? innerW / 2 : index / (rows.length - 1) * innerW);
      const y = value => pad.top + (1 - (Number(value) || 0) / max) * innerH;
      const gridTicks = [0, .25, .5, .75, 1];
      const labelEvery = Math.max(1, Math.ceil(rows.length / 10));
      const seriesColor = item => chart.palette === "active"
        ? activePaletteColor(Math.max(0, allSeries.indexOf(item)), allSeries.length)
        : item.color || tone[item.tone] || colors.blue;
      const lineMarkup = series.map(item => {
        const color = seriesColor(item);
        const points = rows.map((row, index) => `${x(index)},${y(row[item.key])}`).join(" ");
        const circles = rows.map((row, index) => `<circle class="line-point" style="--line:${color}" cx="${x(index)}" cy="${y(row[item.key])}" r="4"><title>${escapeHtml(item.label)} · ${escapeHtml(row.label)}: ${int(row[item.key])}</title></circle>`).join("");
        return `<polyline class="line-path" style="--line:${color}" points="${points}"></polyline>${circles}`;
      }).join("");
      return `<article class="panel${panelClass}">
        <h2>${escapeHtml(chart.title)}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        ${chart.selectableSeries ? `<div class="line-series-selector" data-line-series-selector="${escapeHtml(chartKey)}">
          <div class="line-series-selector-title">Unidades exibidas (${selectedKeys.size})</div>
          <div class="line-series-options">
            ${allSeries.filter(item => item.selectable).map(item => `<label>
              <input type="checkbox" data-line-series-key="${escapeHtml(item.key)}" ${selectedKeys.has(item.key) ? "checked" : ""}>
              <span title="${escapeHtml(item.label)}">${escapeHtml(compactUnitLabel(item.label))}</span>
            </label>`).join("")}
          </div>
        </div>` : ""}
        <div class="line-chart-frame">
          <svg class="line-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(chart.title)}">
            ${gridTicks.map(tick => {
              const gy = pad.top + (1 - tick) * innerH;
              return `<line class="line-grid" x1="${pad.left}" y1="${gy}" x2="${width - pad.right}" y2="${gy}"></line><text class="line-axis-label" x="${pad.left - 10}" y="${gy + 4}" text-anchor="end">${int(max * tick)}</text>`;
            }).join("")}
            ${rows.map((row, index) => index % labelEvery === 0 || index === rows.length - 1 ? `<text class="line-axis-label" x="${x(index)}" y="${height - 20}" text-anchor="middle">${escapeHtml(compactUnitLabel(row.label))}</text>` : "").join("")}
            ${lineMarkup}
          </svg>
          <div class="line-legend">
            ${series.map(item => `<span style="--legend-color:${seriesColor(item)}" title="${escapeHtml(item.label)}">${escapeHtml(compactUnitLabel(item.label))}</span>`).join("")}
          </div>
        </div>
      </article>`;
    }
    function stackedColumnPanel(chart) {
      const rows = chart.rows || [];
      const segments = rows.flatMap(row => row.segments || []);
      const max = Math.max(...rows.map(row => Number(row.value) || 0), 1);
      const panelClass = chart.className ? ` ${chart.className}` : "";
      const legendItems = chart.legend || (rows[0]?.segments || []).map(segment => ({
        label: segment.label,
        color: segment.color,
        tone: segment.tone,
      }));
      return `<article class="panel column-panel${panelClass}">
        <h2>${escapeHtml(chart.title)}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        <div class="stacked-column-frame">
          ${legendItems.length ? `<div class="stacked-legend">
            ${legendItems.map((item, index) => {
              const legendColor = chart.palette === "active"
                ? activePaletteColor(index, legendItems.length)
                : chart.palette === "cancellation" && item.tone === "red"
                  ? wellhubColor
                  : item.color || tone[item.tone] || colors.blue;
              return `<span style="--legend-color:${legendColor}">${escapeHtml(item.label)}</span>`;
            }).join("")}
          </div>` : ""}
          <div class="stacked-column-list">
            ${rows.length ? rows.map(row => {
              const total = Number(row.value) || 0;
              return `<div class="stacked-column-item">
                <div class="stacked-total">${int(total)}</div>
                <div class="stacked-track" title="${escapeHtml(row.label)}: ${int(total)}">
                  ${(row.segments || []).map((segment, segmentIndex) => {
                    const value = Number(segment.value) || 0;
                    const height = value > 0 ? value / max * 100 : 0;
                    const segmentColor = chart.palette === "active"
                      ? activePaletteColor(segmentIndex, Math.max((row.segments || []).length, 1))
                      : chart.palette === "cancellation" && segment.tone === "red"
                        ? wellhubColor
                        : segment.color || tone[segment.tone] || colors.blue;
                    return `<div class="stacked-segment" style="--h:${height}%;--min-h:${value > 0 ? 2 : 0}px;--bar:${segmentColor}">${value > 0 && height >= 8 ? int(value) : ""}<title>${escapeHtml(segment.label)}: ${int(value)}</title></div>`;
                  }).join("")}
                </div>
                <div class="stacked-label" title="${escapeHtml(row.label)}">${escapeHtml(compactUnitLabel(row.label))}</div>
              </div>`;
            }).join("") : `<div class="source">Sem dados suficientes para este gráfico.</div>`}
          </div>
          ${chart.callout ? `<div class="chart-callout">${escapeHtml(chart.callout).replace(/Pico às ([^\\.]+)\\./, "<strong>Pico às $1.</strong>")}</div>` : ""}
        </div>
      </article>`;
    }
    function clusterPanel(chart) {
      const rows = chart.rows || [];
      const panelClass = chart.className ? ` ${chart.className}` : "";
      const total = Number(chart.total) || rows.reduce((sum, row) => sum + (Number(row.value) || 0), 0) || 1;
      return `<article class="panel${panelClass}">
        <h2>${escapeHtml(chart.title)}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        <div class="cluster-total">
          <span>${escapeHtml(chart.totalLabel || "Total")}</span>
          <strong>${int(total)}</strong>
        </div>
        <div class="cluster-list">
          ${rows.length ? rows.map((row, rowIndex) => {
            const value = Number(row.value) || 0;
            const percent = row.pct != null ? Number(row.pct) : value / total * 100;
            const barColor = chartUsesActivePalette(chart) ? activePaletteColor(rowIndex, rows.length) : row.color || tone[row.tone] || colors.blue;
            return `<div class="cluster-row">
              <div class="cluster-name"><span title="${escapeHtml(row.label)}">${escapeHtml(compactUnitLabel(row.label))}</span><small>${escapeHtml(row.range || "")}</small></div>
              <div class="cluster-track"><div class="cluster-fill" style="--w:${Math.max(1, percent)}%;--bar:${barColor}"></div></div>
              <div class="cluster-value">${int(value)} · ${pct(percent)}</div>
            </div>`;
          }).join("") : `<div class="source">Sem dados suficientes para este quadro.</div>`}
        </div>
      </article>`;
    }
    function clusterUnitTablePanel(chart) {
      const rows = chart.rows || [];
      const clusters = chart.clusters || [];
      const panelClass = chart.className ? ` ${chart.className}` : "";
      return `<article class="panel${panelClass}">
        <h2>${escapeHtml(chart.title)}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        <div class="cluster-unit-table-wrap">
          <table class="cluster-unit-table">
            <thead>
              <tr>
                <th>Unidade</th>
                ${clusters.map(cluster => `<th>${escapeHtml(cluster.label)}<br><small>${escapeHtml(cluster.range || "")}</small></th>`).join("")}
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              ${rows.length ? rows.map(row => `<tr>
                <td class="cluster-unit-name" title="${escapeHtml(row.unit)}">${escapeHtml(compactUnitLabel(row.unit))}</td>
                ${(row.clusters || []).map((cluster, clusterIndex) => {
                  const value = Number(cluster.value) || 0;
                  const percent = Number(cluster.pct) || 0;
                  const barColor = chart.palette === "active" ? activePaletteColor(clusterIndex, Math.max(clusters.length, 1)) : cluster.color || tone[cluster.tone] || colors.blue;
                  return `<td>
                    <div class="cluster-unit-cell">
                      <strong>${int(value)} · ${pct(percent)}</strong>
                      <div class="cluster-unit-mini-track"><div class="cluster-unit-mini-fill" style="--w:${Math.max(1, percent)}%;--bar:${barColor}"></div></div>
                    </div>
                  </td>`;
                }).join("")}
                <td class="cluster-unit-total">${int(row.total)}</td>
              </tr>`).join("") : `<tr><td colspan="${clusters.length + 2}" class="source">Sem dados suficientes para este quadro.</td></tr>`}
            </tbody>
          </table>
        </div>
      </article>`;
    }
    function cannibalizationPanel(chart) {
      const periods = Array.isArray(chart.periods) ? chart.periods : [];
      const overall = chart.overall || { key: "all", label: "Todos os períodos", total: 0, rows: [] };
      const views = [overall, ...periods];
      const validKeys = new Set(views.map(view => String(view.key)));
      const defaultKey = validKeys.has(String(chart.defaultPeriod)) ? String(chart.defaultPeriod) : "all";
      const panelClass = chart.className ? ` ${chart.className}` : "";
      const options = [overall, ...[...periods].reverse()];
      const viewHtml = views.map(view => {
        const rows = [...(view.rows || [])].sort((a, b) =>
          (Number(b.value || 0) - Number(a.value || 0))
          || (Number(a.openingOrder || 0) - Number(b.openingOrder || 0))
        );
        const max = Math.max(...rows.map(row => Number(row.value) || 0), 1);
        return `<div class="cannibalization-period-view" data-cannibalization-period="${escapeHtml(view.key)}" ${String(view.key) === defaultKey ? "" : "hidden"}>
          <div class="bar-list">
            ${rows.length ? rows.map((row, rowIndex) => {
              const value = Number(row.value) || 0;
              const width = value > 0 ? value / max * 100 : 0;
              return `<div class="bar-row">
                <div class="bar-label" title="${escapeHtml(row.label)}">${escapeHtml(compactUnitLabel(row.label))}</div>
                <div class="bar-track"><div class="bar-fill" style="--w:${width}%;--bar:${activePaletteColor(rowIndex, rows.length)}"></div></div>
                <div class="bar-value">${int(value)}</div>
              </div>`;
            }).join("") : `<div class="source">Sem alunos identificados para este período.</div>`}
          </div>
          <div class="cannibalization-total">
            <span>Total da rede em ${escapeHtml(view.label)}</span>
            <strong>${int(view.total)}</strong>
            <small>alunos únicos</small>
          </div>
        </div>`;
      }).join("");
      return `<article class="panel cannibalization-panel${panelClass}" data-cannibalization-panel>
        <div class="cannibalization-header">
          <div>
            <h2>${escapeHtml(chart.title)}</h2>
            ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
          </div>
          <label class="cannibalization-period-control">
            <span>Período do cancelamento</span>
            <select data-cannibalization-select>
              ${options.map(view => `<option value="${escapeHtml(view.key)}" ${String(view.key) === defaultKey ? "selected" : ""}>${escapeHtml(view.label)}</option>`).join("")}
            </select>
          </label>
        </div>
        ${viewHtml}
      </article>`;
    }
    function financialMatrixPanel(chart) {
      const views = chart.views || [];
      const units = chart.units || [];
      const defaultKey = String(chart.defaultMonth || views[0]?.key || "");
      const formatValue = (value, kind) => {
        if (kind === "count") return int(value);
        const formatted = fmtMoney.format(Number(value || 0));
        return `R$<br>${formatted.replace("R$", "").trim()}`;
      };
      const header = `<thead><tr><th>Indicador</th>${units.map(unit => `<th title="${escapeHtml(unit)}">${escapeHtml(unitAbbreviation(unit))}</th>`).join("")}<th class="financial-network" title="Rede">REDE</th></tr></thead>`;
      const compactViewHtml = views.map(view => {
        const totalRow = (view.rows || []).find(row => String(row.key || "") === "total") || { values: [], total: 0 };
        const values = units.map((unit, index) => Math.max(Number(totalRow.values?.[index] || 0), 0));
        const unitTotal = values.reduce((sum, value) => sum + value, 0) || 1;
        return `<div class="financial-matrix-compact-view" data-financial-month="${escapeHtml(view.key)}" ${String(view.key) === defaultKey ? "" : "hidden"}>
          <div class="financial-network-summary-row">
            <strong>REDE</strong>
            <span class="financial-network-summary-total">${escapeHtml(fmtMoney.format(Number(totalRow.total || 0)))}</span>
            <div class="financial-network-summary-chart" aria-label="Participação do faturamento total por unidade em ${escapeHtml(view.label)}">
              <div class="financial-network-summary-line">
                ${units.map((unit, index) => {
                  const share = values[index] / unitTotal * 100;
                  return `<i class="financial-network-summary-segment" style="--segment-width:${share}%;--segment-color:${activePaletteColor(index, units.length)}" title="${escapeHtml(unit)}: ${escapeHtml(fmtMoney.format(values[index]))} (${pct(share)})"></i>`;
                }).join("")}
              </div>
              <div class="financial-network-summary-units">
                ${units.map((unit, index) => {
                  const share = values[index] / unitTotal * 100;
                  return `<span class="financial-network-summary-unit" style="--segment-width:${share}%" title="${escapeHtml(unit)} · ${escapeHtml(fmtMoney.format(values[index]))}">${escapeHtml(unitAbbreviation(unit))}</span>`;
                }).join("")}
              </div>
            </div>
          </div>
        </div>`;
      }).join("");
      const viewHtml = views.map(view => {
        let currentSection = "";
        const rows = (view.rows || []).map(row => {
          const section = row.section || "";
          const sectionRow = section !== currentSection
            ? `<tr class="financial-section-row"><th colspan="${units.length + 2}">${escapeHtml(section)}</th></tr>`
            : "";
          currentSection = section;
          const values = row.values || [];
          return `${sectionRow}<tr class="financial-data-row">
            <th><span class="financial-indicator" title="${escapeHtml(row.rule || "")}">${escapeHtml(row.label)}<small>${escapeHtml(row.source || "")}</small></span></th>
            ${units.map((unit, index) => `<td>${formatValue(values[index], row.kind)}</td>`).join("")}
            <td class="financial-network">${formatValue(row.total, row.kind)}</td>
          </tr>`;
        }).join("");
        return `<div data-financial-month="${escapeHtml(view.key)}" ${String(view.key) === defaultKey ? "" : "hidden"}>
          <div class="financial-table-wrap"><table class="financial-table">${header}<tbody>${rows}</tbody></table></div>
        </div>`;
      }).join("");
      const panelClass = chart.className ? ` ${chart.className}` : "";
      return `<article class="panel financial-matrix-panel${panelClass}" data-financial-panel>
        <div class="financial-matrix-header">
          <div><h2>${escapeHtml(chart.title)}</h2>${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}</div>
          <label class="financial-month-control"><span>Competência</span><select data-financial-select>
            ${views.map(view => `<option value="${escapeHtml(view.key)}" ${String(view.key) === defaultKey ? "selected" : ""}>${escapeHtml(view.label)}</option>`).join("")}
          </select></label>
        </div>
        <div class="financial-matrix-compact">${compactViewHtml || `<div class="source">Sem dados financeiros para o período.</div>`}</div>
        <div class="financial-matrix-detail">${viewHtml || `<div class="source">Sem dados financeiros para o período.</div>`}</div>
        <p class="financial-note">Dados atualizados pelo Supabase. Recorrência é atribuída ao mês do pagamento e separada pelo mês de vencimento. Os tetos de agregadores são aplicados por ID, unidade e competência.</p>
      </article>`;
    }
    function churnRiskPanel(chart) {
      const views = Array.isArray(chart.views) ? chart.views : [];
      const registryKey = String(chart.className || "chart-frequency-churn-risk");
      churnRiskRegistry.set(registryKey, chart);
      const riskColors = { "Baixo": "#00f529", "Médio": "#f4d68a", "Alto": "#ff9f1c", "Crítico": "#ff4658" };
      const visibleRiskBands = distribution => (distribution || []).filter(band => ["Médio", "Alto", "Crítico"].includes(String(band.label)));
      const legendBands = visibleRiskBands(views[0]?.distribution);
      const legend = legendBands.map(band => `<span><i style="--legend-color:${riskColors[band.label] || "#38a3ff"}"></i>${escapeHtml(band.label)} ${escapeHtml(band.range)}</span>`).join("");
      const donutHtml = view => {
        let offset = 0;
        const displayBands = visibleRiskBands(view.distribution);
        const riskTotal = displayBands.reduce((sum, band) => sum + Number(band.value || 0), 0);
        const segments = displayBands.map(band => {
          const segmentPct = riskTotal ? Math.max(0, Math.min(100 - offset, Number(band.value || 0) * 100 / riskTotal)) : 0;
          const segmentOffset = offset;
          offset += segmentPct;
          if (segmentPct <= 0) return "";
          const label = `${view.label}, risco ${band.label}: ${int(band.value)} alunos, ${pct(segmentPct)} dos alunos em risco`;
          return `<circle class="churn-risk-donut-segment" cx="60" cy="60" r="45" pathLength="100"
            transform="rotate(-90 60 60)" style="--segment-color:${riskColors[band.label] || "#38a3ff"};stroke-dasharray:${segmentPct} ${100 - segmentPct};stroke-dashoffset:${-segmentOffset}"
            data-churn-risk-segment data-view-key="${escapeHtml(view.key)}" data-risk-band="${escapeHtml(band.label)}"
            role="button" tabindex="0" aria-label="${escapeHtml(label)}"><title>${escapeHtml(label)}</title></circle>`;
        }).join("");
        return `<div class="churn-risk-donut-card ${String(view.key) === "network" ? "is-network" : ""}">
          <div class="churn-risk-donut">
            <svg viewBox="0 0 120 120" aria-label="Distribuição de risco de ${escapeHtml(view.label)}" data-churn-risk-ring data-view-key="${escapeHtml(view.key)}">
              <circle class="churn-risk-donut-track" cx="60" cy="60" r="45"></circle>
              ${segments}
            </svg>
            <div class="churn-risk-donut-center"><strong>${escapeHtml(view.code || "")}</strong></div>
          </div>
          <div class="churn-risk-donut-label" title="${escapeHtml(view.label)}">${escapeHtml(compactUnitLabel(view.label))}</div>
        </div>`;
      };
      const networkView = views.find(view => String(view.key) === "network");
      const unitViews = views.filter(view => String(view.key) !== "network");
      const donutLayout = views.length ? `<div class="churn-risk-donut-layout">
        <div class="churn-risk-network-slot">${networkView ? donutHtml(networkView) : ""}</div>
        <div class="churn-risk-unit-donut-grid">${unitViews.map(donutHtml).join("")}</div>
      </div>` : "";
      return `<article class="panel churn-risk-panel ${escapeHtml(chart.className || "")}" data-churn-risk-panel data-churn-risk-chart="${escapeHtml(registryKey)}">
        <div class="churn-risk-header">
          <div class="churn-risk-header-copy"><h2>${escapeHtml(chart.title)}</h2><p class="panel-subtitle">${escapeHtml(chart.subtitle || "")}</p></div>
        </div>
        <div class="churn-risk-donut-legend" aria-label="Legenda das faixas de risco">${legend}</div>
        ${donutLayout ? `${donutLayout}<p class="churn-risk-donut-hint">Clique em uma cor da rosca para abrir os alunos daquela faixa.</p>` : `<div class="source">Sem dados suficientes para calcular o score.</div>`}
        <div class="churn-risk-modal" data-churn-risk-modal hidden>
          <section class="churn-risk-modal-dialog" role="dialog" aria-modal="true" aria-labelledby="churnRiskModalTitle">
            <div class="churn-risk-modal-head">
              <div><h3 id="churnRiskModalTitle" data-churn-risk-modal-title>Detalhes do risco</h3><p data-churn-risk-modal-subtitle></p></div>
              <button type="button" class="churn-risk-modal-close" data-churn-risk-modal-close aria-label="Fechar">×</button>
            </div>
            <div class="churn-risk-modal-summary" data-churn-risk-modal-summary></div>
            <div class="churn-risk-table-wrap">
              <table class="churn-risk-table">
                <thead><tr><th>Aluno</th><th>Score</th><th>Saldo vencido</th><th>Parcelas vencidas</th><th>Máx. dias</th><th>Visitas</th><th>Frequência</th><th>Pts. saldo</th><th>Pts. atraso</th><th>Pts. frequência</th></tr></thead>
                <tbody data-churn-risk-modal-rows></tbody>
              </table>
            </div>
            <div class="churn-risk-modal-foot" data-churn-risk-modal-foot></div>
          </section>
        </div>
      </article>`;
    }
    function ageGenderPyramidPanel(chart) {
      const rows = Array.isArray(chart?.rows) ? chart.rows : [];
      const largest = Math.max(1, ...rows.flatMap(row => [Number(row.male) || 0, Number(row.female) || 0]));
      const panelClass = chart?.className ? ` ${chart.className}` : "";
      const rowHtml = rows.map((row, index) => {
        const male = Number(row.male) || 0;
        const female = Number(row.female) || 0;
        const maleWidth = Math.max(0, Math.min(100, male / largest * 100));
        const femaleWidth = Math.max(0, Math.min(100, female / largest * 100));
        const color = activePaletteColor(index, rows.length);
        const label = row.shortLabel || row.label || "Faixa";
        return `<div class="age-pyramid-row" title="${escapeHtml(row.label || label)}">
          <div class="age-pyramid-side age-pyramid-men" aria-label="${escapeHtml(label)}: ${int(male)} homens, ${pct(row.malePct)} da base identificada">
            <span class="age-pyramid-value"><strong>${int(male)}</strong><small>${pct(row.malePct)}</small></span>
            <span class="age-pyramid-track"><i style="--age-width:${maleWidth.toFixed(2)}%;--age-color:${color}"></i></span>
          </div>
          <div class="age-pyramid-band"><strong>${escapeHtml(label)}</strong></div>
          <div class="age-pyramid-side age-pyramid-women" aria-label="${escapeHtml(label)}: ${int(female)} mulheres, ${pct(row.femalePct)} da base identificada">
            <span class="age-pyramid-track"><i style="--age-width:${femaleWidth.toFixed(2)}%;--age-color:${color}"></i></span>
            <span class="age-pyramid-value"><strong>${int(female)}</strong><small>${pct(row.femalePct)}</small></span>
          </div>
        </div>`;
      }).join("");
      return `<article class="panel age-gender-pyramid-panel${panelClass}">
        <h2>${escapeHtml(chart?.title || "Faixa etária por sexo")}</h2>
        <div class="age-pyramid-head" aria-hidden="true">
          <strong>Homens</strong><span>Idade</span><strong>Mulheres</strong>
        </div>
        <div class="age-pyramid-list">${rowHtml || `<p class="source">Sem idades válidas para o recorte selecionado.</p>`}</div>
        <div class="age-pyramid-summary">
          <span><b class="age-sex-dot male"></b>Homens <strong>${int(chart?.maleTotal || 0)}</strong></span>
          <span><b class="age-sex-dot female"></b>Mulheres <strong>${int(chart?.femaleTotal || 0)}</strong></span>
          <span>Não informado <strong>${int(chart?.unreportedTotal || 0)}</strong></span>
        </div>
        ${chart?.subtitle ? `<p class="age-pyramid-footer">${escapeHtml(chart.subtitle)}</p>` : ""}
      </article>`;
    }
    function chartPanel(chart) {
      if (!chart) return "";
      if (chart.type === "waterfall") return waterfallPanel(chart);
      if (chart.type === "financialRevenueFilter") return financialRevenueFilterPanel(chart);
      if (chart.type === "population") return populationPanel(chart);
      if (chart.type === "activeGoals") return activeGoalsPanel(chart);
      if (chart.type === "aggregatorUnique") return aggregatorUniquePanel(chart);
      if (chart.type === "cannibalizationPeriod") return cannibalizationPanel(chart);
      if (chart.type === "financialMatrix") return financialMatrixPanel(chart);
      if (chart.type === "churnRisk") return churnRiskPanel(chart);
      if (chart.type === "clusterUnitTable") return clusterUnitTablePanel(chart);
      if (chart.type === "clusterPanel") return clusterPanel(chart);
      if (chart.type === "stackedColumn") return stackedColumnPanel(chart);
      if (chart.type === "lineChart") return linePanel(chart);
      if (chart.type === "collectionCombo") return collectionComboPanel(chart);
      if (chart.type === "multiBar") return multiBarPanel(chart);
      if (chart.type === "dualBar") return dualBarPanel(chart);
      if (chart.type === "columnBar") return columnPanel(chart);
      if (chart.type === "ageGenderPyramid") return ageGenderPyramidPanel(chart);
      if (chart.type === "donut") return compositionPanel(chart);
      return barPanel(chart);
    }
    function activeChartsHtml(charts, composition, footerCards = []) {
      const list = charts || [];
      const byClass = name => list.find(chart => String(chart.className || "").includes(name));
      const used = new Set();
      const pick = name => {
        const chart = byClass(name);
        if (chart) used.add(chart);
        return chart;
      };
      const activeUnits = pick("chart-active-units");
      const activeAggregators = pick("chart-active-aggregators");
      const gender = pick("chart-profile-gender");
      const age = pick("chart-profile-age");
      const contract = pick("chart-active-contract");
      const extra = list.filter(chart => !used.has(chart));
      const footer = Array.isArray(footerCards) ? footerCards : [];
      return `${activeUnits || activeAggregators || composition || age || gender ? `<div class="active-overview-trio">${activeUnits ? chartPanel(activeUnits) : ""}<div class="active-overview-column left">${composition ? compositionPanel(composition) : ""}${age ? chartPanel(age) : ""}</div><div class="active-overview-column right">${activeAggregators ? chartPanel(activeAggregators) : ""}${gender ? chartPanel(gender) : ""}</div></div>` : ""}${contract || footer.length ? `<div class="active-lower-layout">${footer.length ? `<div class="cards active-footer-cards">${footer.map(cardHtml).join("")}</div>` : ""}${contract ? `<div class="active-lower-contract">${chartPanel(contract)}</div>` : ""}</div>` : ""}${extra.length ? `<div class="grid">${extra.map(chartPanel).join("")}</div>` : ""}`;
    }
    function salesChartsHtml(charts) {
      const list = (charts || []).filter(chart => {
        const className = String(chart?.className || "");
        return !className.includes("chart-sales-success") && !className.includes("chart-sales-open-values");
      });
      const byClass = name => list.find(chart => String(chart.className || "").includes(name));
      const used = new Set();
      const pick = name => {
        const chart = byClass(name);
        if (chart) used.add(chart);
        return chart;
      };
      const month = pick("chart-sales-month");
      const contracts = pick("chart-sales-contracts");
      const ticket = pick("chart-sales-ticket");
      const growth = pick("chart-sales-growth");
      const units = pick("chart-sales-units");
      const swaps = pick("chart-contract-swaps");
      const left = [month, contracts].filter(Boolean);
      const right = [ticket, growth, units, swaps].filter(Boolean);
      const extra = list.filter(chart => !used.has(chart));
      return `<div class="sales-primary-layout">
        <div class="chart-stack">${left.map(chartPanel).join("")}</div>
        <div class="chart-stack">${right.map(chartPanel).join("")}</div>
      </div>${extra.length ? `<div class="grid">${extra.map(chartPanel).join("")}</div>` : ""}`;
    }
    function salesTickerHtml(items) {
      const rows = Array.isArray(items) ? items.slice(0, 10) : [];
      if (!rows.length) return "";
      const itemHtml = item => `<span class="sales-live-ticker-item">
        <span class="sales-live-ticker-contract" title="Contrato: ${escapeHtml(item.contract || "Contrato")}">${escapeHtml(item.contract || "Contrato")}</span>
        <span class="sales-live-ticker-seller" title="Colaborador: ${escapeHtml(item.seller || "Colaborador não informado")}">${escapeHtml(item.seller || "Colaborador não informado")}</span>
        <span class="sales-live-ticker-unit" title="Unidade: ${escapeHtml(item.unit || "Sem unidade")}">${escapeHtml(item.unit || "Sem unidade")}</span>
        <strong class="sales-live-ticker-value" title="Valor: ${escapeHtml(item.value || "")}">${escapeHtml(item.value || "")}</strong>
        <time class="sales-live-ticker-date" datetime="${escapeHtml(item.saleDate || "")}" title="Data e horário: ${escapeHtml(item.saleDate || "")} ${escapeHtml(item.time || "--:--")}">${escapeHtml(item.saleDate || "")}</time>
      </span>`;
      const feed = rows.map(itemHtml).join("");
      return `<aside class="sales-live-ticker" aria-label="10 últimos contratos vendidos em tempo real">
        <div class="sales-live-ticker-label"><span class="sales-live-ticker-pulse" aria-hidden="true"></span>Vendas em tempo real</div>
        <div class="sales-live-ticker-viewport">
          <div class="sales-live-ticker-track">
            <div class="sales-live-ticker-group">${feed}</div>
            <div class="sales-live-ticker-group" aria-hidden="true">${feed}</div>
          </div>
        </div>
      </aside>`;
    }
    function cancelChartsHtml(charts) {
      const list = (charts || []).filter(chart => !String(chart.className || "").includes("chart-cancel-before-"));
      const byClass = name => list.find(chart => String(chart.className || "").includes(name));
      const used = new Set();
      const pick = name => {
        const chart = byClass(name);
        if (chart) used.add(chart);
        return chart;
      };
      const cannibalization = pick("chart-cancel-cannibalization");
      const month = pick("chart-cancel-month");
      const contracts = pick("chart-cancel-contracts");
      const units = pick("chart-cancel-units");
      const churn = pick("chart-cancel-churn");
      const reasons = pick("chart-cancel-reasons");
      const extra = list.filter(chart => !used.has(chart));
      return `<div class="cancel-layout">
        ${month || contracts ? `<div class="cancel-top-pair">${month ? chartPanel(month) : ""}${contracts ? chartPanel(contracts) : ""}</div>` : ""}
        ${units ? chartPanel(units) : ""}
        ${churn || cannibalization || reasons ? `<div class="cancel-lower-grid">
          ${churn ? chartPanel(churn) : ""}
          ${cannibalization ? chartPanel(cannibalization) : ""}
          ${reasons ? chartPanel(reasons) : ""}
        </div>` : ""}
        ${extra.length ? `<div class="grid">${extra.map(chartPanel).join("")}</div>` : ""}
      </div>`;
    }
    function financialChartsHtml(charts) {
      const list = charts || [];
      const byClass = name => list.find(chart => String(chart.className || "").includes(name));
      const used = new Set();
      const pick = name => {
        const chart = byClass(name);
        if (chart) used.add(chart);
        return chart;
      };
      const matrix = pick("chart-financial-matrix");
      const revenue = pick("chart-profile-revenue");
      const collectionSuccess = pick("chart-profile-charge-success");
      const delinquencyDays = pick("chart-profile-delinquency-days");
      const paymentStatus = pick("chart-payment-status");
      const recovery = pick("chart-profile-recovery-success");
      // O indicador de recuperacao foi removido da apresentacao, mas permanece no payload para auditoria.
      if (recovery) used.add(recovery);
      const extra = list.filter(chart => !used.has(chart));
      return `<div class="financial-layout">
        ${matrix ? chartPanel(matrix) : ""}
        ${revenue || collectionSuccess || paymentStatus ? `<div class="financial-collection-layout">
          ${revenue ? chartPanel(revenue) : ""}
          <div class="financial-collection-stack">
            ${collectionSuccess ? chartPanel(collectionSuccess) : ""}
            ${paymentStatus ? chartPanel(paymentStatus) : ""}
          </div>
        </div>` : ""}
        ${delinquencyDays ? `<div class="financial-delinquency-full">${chartPanel(delinquencyDays)}</div>` : ""}
        ${extra.length ? `<div class="grid">${extra.map(chartPanel).join("")}</div>` : ""}
      </div>`;
    }
    function frequencyChartsHtml(charts) {
      const list = charts || [];
      const used = new Set();
      const byClass = name => list.find(chart => String(chart.className || "").includes(name));
      const pick = name => {
        const chart = byClass(name);
        if (chart) used.add(chart);
        return chart;
      };
      const accessDay = pick("chart-access-day");
      const churnRisk = pick("chart-frequency-churn-risk");
      const hourly = pick("chart-access-hour");
      const weekday = pick("chart-weekday-access");
      const ltvPlan = pick("chart-ltv-plan");
      const ltvUnit = pick("chart-ltv-unit");
      const dailyComparison = pick("chart-access-daily-comparison");
      const clusterPanels = list.filter(chart => chart.type === "clusterPanel");
      const ownCluster = clusterPanels[0];
      const aggregatorCluster = clusterPanels[1];
      clusterPanels.forEach(chart => used.add(chart));
      const clusterUnitTables = list.filter(chart => chart.type === "clusterUnitTable");
      clusterUnitTables.forEach(chart => used.add(chart));
      const extra = list.filter(chart => !used.has(chart));
      return `<div class="frequency-layout">
        ${accessDay ? chartPanel(accessDay) : ""}
        ${churnRisk ? chartPanel(churnRisk) : ""}
        ${dailyComparison ? chartPanel(dailyComparison) : ""}
        ${hourly || weekday || ownCluster || aggregatorCluster || ltvPlan || ltvUnit ? `<div class="frequency-analysis-grid">
          <div class="frequency-analysis-column frequency-analysis-left">
            ${hourly ? chartPanel(hourly) : ""}
            ${ltvPlan ? chartPanel(ltvPlan) : ""}
          </div>
          <div class="frequency-analysis-right">
            ${weekday ? chartPanel(weekday) : ""}
            ${ownCluster ? chartPanel(ownCluster) : ""}
            ${aggregatorCluster ? chartPanel(aggregatorCluster) : ""}
            ${ltvUnit ? chartPanel(ltvUnit) : ""}
          </div>
        </div>` : ""}
        ${extra.length ? `<div class="grid">${extra.map(chartPanel).join("")}</div>` : ""}
        ${clusterUnitTables.length ? `<div class="frequency-cluster-unit-final">${clusterUnitTables.map(chartPanel).join("")}</div>` : ""}
      </div>`;
    }
    function financialRevenueFilterPanel(chart) {
      const views = Array.isArray(chart.views) ? chart.views : [];
      const defaultKey = String(chart.defaultView || views[0]?.key || "total");
      const panelClass = chart.className ? ` ${chart.className}` : "";
      const viewHtml = views.map(view => {
        const rows = view.rows || [];
        const max = Math.max(...rows.map(row => Number(row.value) || 0), 1);
        return `<div class="financial-revenue-view" data-revenue-view="${escapeHtml(view.key)}" ${String(view.key) === defaultKey ? "" : "hidden"}>
          <div class="financial-revenue-total">Total do filtro: <strong>${fmtMoney.format(Number(view.total || 0))}</strong></div>
          <div class="bar-list">${rows.map((row, index) => {
            const value = Number(row.value) || 0;
            const width = value > 0 ? value / max * 100 : 0;
            const color = activePaletteColor(index, rows.length);
            return `<div class="bar-row">
              <div class="bar-label" title="${escapeHtml(row.label)}">${escapeHtml(compactUnitLabel(row.label))}</div>
              <div class="bar-track"><div class="bar-fill" style="--w:${width}%;--bar:${color}"></div></div>
              <div class="bar-value">${escapeHtml(row.display || fmtMoney.format(value))}</div>
            </div>`;
          }).join("")}</div>
        </div>`;
      }).join("");
      return `<article class="panel financial-revenue-panel${panelClass}" data-revenue-panel>
        <div class="financial-revenue-header">
          <div><h2>${escapeHtml(chart.title)}</h2>${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}</div>
          <div class="financial-revenue-tabs" role="group" aria-label="Filtro do faturamento">
            ${views.map(view => `<button type="button" data-revenue-filter="${escapeHtml(view.key)}" class="${String(view.key) === defaultKey ? "active" : ""}">${escapeHtml(view.label)}</button>`).join("")}
          </div>
        </div>
        ${viewHtml}
      </article>`;
    }
    function waterfallPanel(chart) {
      const rows = chart.rows || [];
      const steps = rows.map((row, index) => {
        const rawValue = Number(row.value) || 0;
        const kind = row.kind || "increase";
        const value = kind === "decrease" ? -Math.abs(rawValue) : Math.abs(rawValue);
        return { ...row, value, kind, index };
      });
      const min = Math.min(0, ...steps.map(step => step.value));
      const max = Math.max(1, ...steps.map(step => step.value));
      const range = max - min || 1;
      const zero = ((0 - min) / range) * 100;
      const panelClass = chart.className ? ` ${chart.className}` : "";
      return `<article class="panel waterfall-panel${panelClass}">
        <h2>${escapeHtml(chart.title)}</h2>
        ${chart.subtitle ? `<p class="panel-subtitle">${escapeHtml(chart.subtitle)}</p>` : ""}
        <div class="waterfall-chart" style="--wf-columns:${Math.max(steps.length, 1)}">${steps.map((step, index) => {
          const height = Math.max(3, (Math.abs(step.value) / range) * 100);
          const bottom = step.value < 0 ? Math.max(0, zero - height) : zero;
          const color = step.color || tone[step.tone] || (step.kind === "decrease" ? activePaletteColor(2, 5) : step.kind === "result" ? activePaletteColor(12, 14) : activePaletteColor(index, 6));
          const signed = step.kind === "increase" ? `+${int(step.value)}` : step.kind === "decrease" ? `-${int(Math.abs(step.value))}` : int(step.value);
          return `<div class="waterfall-step">
            <strong>${escapeHtml(signed)}</strong>
            <div class="waterfall-track" style="--wf-zero:${zero}%"><i style="--wf-bottom:${bottom}%;--wf-height:${height}%;--wf-color:${color}"></i></div>
            <span>${escapeHtml(step.label)}</span>
          </div>`;
        }).join("")}</div>
        <p class="waterfall-note">Saldo estimado = ativos + vendas válidas - cancelamentos válidos.</p>
      </article>`;
    }
    function compositionPanel(chart) {
      const rows = chart?.rows || [];
      const displayTotal = rows.reduce((sum, row) => sum + (Number(row.value) || 0), 0);
      const total = displayTotal || 1;
      const panelClass = chart?.className ? ` ${chart.className}` : "";
      const usesActivePalette = chartUsesActivePalette(chart) || String(chart?.title || "").toLocaleLowerCase("pt-BR").includes("base ativa");
      const palette = usesActivePalette
        ? activeUnitPalette
        : chart?.palette === "blue"
        ? ["#38a3ff", "#2f8fe7", "#52b5ff", "#2478ca", "#84cbff", "#1c65a8", "#6bbfff", "#17568f", "#a9dbff", "#11416e"]
        : [colors.green, colors.blue, colors.orange, colors.violet, colors.red];
      const rowColor = (row, index) => usesActivePalette
        ? activePaletteColor(index, rows.length)
        : row.color || tone[row.tone] || palette[index % palette.length];
      let start = 0;
      const callouts = [];
      const segments = rows.map((row, index) => {
        const value = Number(row.value) || 0;
        const end = start + value / total * 360;
        const color = rowColor(row, index);
        const middle = (start + end) / 2;
        const radians = middle * Math.PI / 180;
        callouts.push({
          label: row.label,
          value,
          percent: row.pct != null ? Number(row.pct) : value / total * 100,
          color,
          x: 50 + Math.sin(radians) * 43,
          y: 50 - Math.cos(radians) * 39,
          side: Math.sin(radians) >= 0 ? "right" : "left",
        });
        const segment = `${color} ${start}deg ${end}deg`;
        start = end;
        return segment;
      }).join(", ") || `${colors.green} 0deg 360deg`;
      ["left", "right"].forEach(side => {
        const sideItems = callouts
          .filter(item => item.side === side)
          .sort((a, b) => a.y - b.y);
        if (!sideItems.length) return;
        const minimumY = 11;
        const maximumY = 89;
        const minimumGap = sideItems.length > 3 ? 14 : 18;
        sideItems[0].y = Math.max(minimumY, sideItems[0].y);
        for (let index = 1; index < sideItems.length; index += 1) {
          sideItems[index].y = Math.max(sideItems[index].y, sideItems[index - 1].y + minimumGap);
        }
        const overflow = sideItems[sideItems.length - 1].y - maximumY;
        if (overflow > 0) sideItems.forEach(item => { item.y -= overflow; });
        const underflow = minimumY - sideItems[0].y;
        if (underflow > 0) sideItems.forEach(item => { item.y += underflow; });
        sideItems.forEach(item => { item.x = side === "left" ? 21 : 79; });
      });
      return `<article class="panel composition-panel${panelClass}">
        <h2 class="composition-title">${escapeHtml(chart?.title || "Base")}</h2>
        <div class="donut-shell">
          <div class="donut" style="--donut:${segments}"></div>
          <div class="donut-center" aria-hidden="true">
            <strong>${int(displayTotal)}</strong>
            <span>${String(chart?.title || "").toLocaleLowerCase("pt-BR").includes("base ativa") ? "Total de alunos" : "Total"}</span>
          </div>
          <div class="donut-callouts" aria-hidden="true">
            ${callouts.map(item => `<div class="donut-callout ${item.side}" style="--callout-color:${item.color};--callout-x:${item.x}%;--callout-y:${item.y}%">
              <span>${escapeHtml(item.label)}</span>
              <strong>${int(item.value)}</strong>
              <small>(${pct(item.percent)})</small>
            </div>`).join("")}
          </div>
        </div>
        <div class="composition-copy">
          ${chart?.subtitle && chart?.subtitlePosition !== "footer" ? `<p>${escapeHtml(chart.subtitle)}</p>` : ""}
          <div class="legend">
            ${rows.map((row, index) => {
              const color = rowColor(row, index);
              return `<div class="legend-row">
                <span class="dot" style="--dot:${color}"></span>
                <span>${escapeHtml(row.label)}</span>
                <strong>${int(row.value)} · ${pct(row.pct)}</strong>
              </div>`;
            }).join("")}
          </div>
        </div>
        ${chart?.subtitle && chart?.subtitlePosition === "footer" ? `<p class="composition-footer">${escapeHtml(chart.subtitle)}</p>` : ""}
      </article>`;
    }
    function medalBoardHtml(rows) {
      const list = (rows || []).map((row, sourceIndex) => ({
        ...row,
        sourceIndex,
        calculatedTotal: Number(row.total ?? (Number(row.gold || 0) * 3 + Number(row.silver || 0) * 2 + Number(row.bronze || 0))),
      })).sort((left, right) =>
        right.calculatedTotal - left.calculatedTotal
        || Number(right.gold || 0) - Number(left.gold || 0)
        || Number(right.silver || 0) - Number(left.silver || 0)
        || Number(right.bronze || 0) - Number(left.bronze || 0)
        || left.sourceIndex - right.sourceIndex
      );
      if (!list.length) return "";
      const medalNumber = value => String(Number(value || 0)).padStart(2, "0");
      const unitHeaders = list.map((row, index) => `<th scope="col" title="${escapeHtml(row.unit)}">
        <span class="medal-unit-head"><span class="medal-rank">${index + 1}º</span><strong>${escapeHtml(compactUnitLabel(row.unit))}</strong></span>
      </th>`).join("");
      const matrixRow = (label, cssClass, field) => `<tr>
        <th scope="row" class="${cssClass}">${label}</th>
        ${list.map(row => `<td>${medalNumber(row[field])}</td>`).join("")}
      </tr>`;
      return `<article class="panel medal-board-panel">
        <h2>Quadro de estrelas da rede</h2>
        <div class="medal-board-table">
          <table class="medal-board-matrix" aria-label="Unidades ordenadas da maior para a menor pontuação de estrelas">
            <thead><tr><th scope="col">Estrelas</th>${unitHeaders}</tr></thead>
            <tbody>
              ${matrixRow("★★★ 3 estrelas", "medal-gold", "gold")}
              ${matrixRow("★★ 2 estrelas", "medal-silver", "silver")}
              ${matrixRow("★ 1 estrela", "medal-bronze", "bronze")}
              <tr class="medal-points-row"><th scope="row">Pontos</th>${list.map(row => `<td>${medalNumber(row.calculatedTotal)}</td>`).join("")}</tr>
            </tbody>
          </table>
        </div>
      </article>`;
    }
    function analysisValue(value, format) {
      const number = Number(value || 0);
      if (format === "money") return fmtMoney.format(number);
      if (format === "pct") return pct(number);
      if (format === "signed_pct") return `${number > 0 ? "+" : ""}${pct(number)}`;
      if (format === "decimal" || format === "score") return number.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
      if (format === "signed_int") return `${number > 0 ? "+" : ""}${int(number)}`;
      return int(number);
    }
    function analysisDelta(value, format) {
      const number = Number(value || 0);
      if (format === "money") return `${number > 0 ? "+" : number < 0 ? "−" : ""}${fmtMoney.format(Math.abs(number))}`;
      if (format === "pct" || format === "signed_pct") return `${number > 0 ? "+" : ""}${pct(number)}`;
      if (format === "decimal" || format === "score") return `${number > 0 ? "+" : ""}${number.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 })}`;
      return `${number > 0 ? "+" : ""}${int(number)}`;
    }
    function analysisAlertsHtml(alerts) {
      const rows = alerts || [];
      return `<section class="panel analysis-alerts-panel">
        <h2>UNIDADES FORA DO COMPORTAMENTO DA REDE</h2>
        <p class="panel-subtitle">Desvios relevantes em relação ao resultado consolidado. Use estas observações como fila de investigação, não como conclusão isolada.</p>
        ${rows.length ? `<div class="analysis-alert-table-wrap"><table class="analysis-alert-table">
          <thead><tr><th>Unidade</th><th>Indicador</th><th>Resultado</th><th>Rede</th><th>Leitura</th></tr></thead>
          <tbody>${rows.map(item => `<tr class="${escapeHtml(item.tone || "attention")}">
            <td class="analysis-alert-unit"><strong>${escapeHtml(item.unit || "")}</strong></td>
            <td>${escapeHtml(item.indicator || "")}</td>
            <td>${escapeHtml(analysisValue(item.value, item.format))}</td>
            <td>${escapeHtml(analysisValue(item.network, item.format))}</td>
            <td>${escapeHtml(item.observation || "")}</td>
          </tr>`).join("")}</tbody>
        </table></div>` : `<div class="empty">Nenhum desvio relevante identificado no recorte atual.</div>`}
      </section>`;
    }
    function analysisMatrixHtml(matrix) {
      const units = matrix?.units || [];
      const rows = matrix?.rows || [];
      const history = matrix?.history || {};
      const deltas = history?.deltas || {};
      const firstDate = history?.firstDate ? String(history.firstDate).split("-").reverse().join("/") : "início do período";
      let currentSection = "";
      const body = [];
      rows.forEach(row => {
        if (row.section !== currentSection) {
          currentSection = row.section;
          body.push(`<tr class="analysis-matrix-section"><td colspan="${units.length + 1}">${escapeHtml(currentSection)}</td></tr>`);
        }
        body.push(`<tr>
          <th class="analysis-indicator-cell" title="Fonte: ${escapeHtml(row.source || "Dashboard")}">${escapeHtml(row.label || row.key)}</th>
          ${units.map(unit => {
            const value = Number(row.values?.[unit] || 0);
            const delta = deltas?.[row.key]?.[unit];
            const deltaNumber = Number(delta || 0);
            const deltaClass = deltaNumber > 0 ? "positive" : deltaNumber < 0 ? "negative" : "stable";
            const networkClass = unit === "Rede" ? "network-column" : "";
            return `<td class="${networkClass}">
              <span class="analysis-matrix-value">${escapeHtml(analysisValue(value, row.format))}</span>
              ${delta !== undefined && delta !== null ? `<small class="analysis-matrix-delta ${deltaClass}" title="Variação desde ${escapeHtml(firstDate)}">${escapeHtml(analysisDelta(deltaNumber, row.format))}</small>` : ""}
            </td>`;
          }).join("")}
        </tr>`);
      });
      return `<section class="panel analysis-matrix-panel">
        <h2>MATRIZ CONSOLIDADA POR UNIDADE</h2>
        <p class="panel-subtitle">${escapeHtml(matrix?.subtitle || "Indicadores das cinco áreas operacionais.")} Valores menores abaixo do dado atual mostram a evolução desde ${escapeHtml(firstDate)}.</p>
        <div class="analysis-matrix-wrap">
          <table class="analysis-matrix">
            <thead><tr><th>Indicador</th>${units.map(unit => `<th class="${unit === "Rede" ? "network-column" : ""}" title="${escapeHtml(unit)}">${escapeHtml(unitAbbreviation(unit))}</th>`).join("")}</tr></thead>
            <tbody>${body.join("")}</tbody>
          </table>
        </div>
      </section>`;
    }
    function isaiasPanel(tab) {
      return `<div class="isaias-shell">
        ${analysisMatrixHtml(tab.indicatorMatrix || {})}
        ${medalBoardHtml(tab.starBoard || data.medalBoard || [])}
      </div>`;
    }
    function compactChartRows(chart) {
      return (chart.rows || []).slice(0, 40).map(row => ({
        label: row.label || row.unit || "",
        value: row.value ?? row.total ?? "",
        pct: row.pct ?? "",
        display: row.display || row.medianDisplay || row.meanDisplay || "",
        medal: row.medal || "",
        bars: (row.bars || []).map(bar => ({ label: bar.label, value: bar.value, display: bar.display })),
        clusters: (row.clusters || []).map(cluster => ({ label: cluster.label, value: cluster.value, pct: cluster.pct })),
      }));
    }
    function buildIsaiasDashboardContext() {
      const tabSummary = {};
      Object.entries(data.tabs || {}).forEach(([key, tab]) => {
        tabSummary[key] = {
          cards: (tab.cards || []).concat(tab.aggregatorCards || []).map(card => ({
            label: card.label,
            value: card.value,
            detail: card.sub || card.metric || card.meta || "",
          })),
          composition: tab.composition ? compactChartRows(tab.composition) : [],
          charts: (tab.charts || []).slice(0, 10).map(chart => ({
            title: chart.title,
            subtitle: chart.subtitle || "",
            type: chart.type,
            rows: compactChartRows(chart),
          })),
        };
      });
      return {
        sourceFile: data.sourceFile,
        filters: collectFilters(),
        medalBoard: (data.medalBoard || []).slice(0, 14),
        chatContext: data.tabs?.isaias?.chatContext || {},
        unitAlerts: data.tabs?.isaias?.unitAlerts || [],
        indicatorMatrix: {
          units: data.tabs?.isaias?.indicatorMatrix?.units || [],
          rows: data.tabs?.isaias?.indicatorMatrix?.rows || [],
          history: data.tabs?.isaias?.indicatorMatrix?.history || {},
        },
        tabs: tabSummary,
      };
    }
    async function answerIsaiasOnline(question) {
      const controller = new AbortController();
      const timeoutId = window.setTimeout(() => controller.abort(), 20000);
      const response = await fetch("/api/ask-isaias", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          question,
          dashboard: buildIsaiasDashboardContext(),
          history: isaiasHistory.slice(-8),
          useSearch: false,
        }),
      }).finally(() => window.clearTimeout(timeoutId));
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.error || "Nao foi possivel acionar a isa IA local.");
      }
      return payload;
    }
    function answerIsaiasLegacy(question) {
      const ctx = data.tabs?.isaias?.chatContext || {};
      const q = String(question || "").toLowerCase();
      const base = `Base analisada: ${int(ctx.active)} ativos, ${int(ctx.sales)} contratos vendidos, ${int(ctx.cancellations)} cancelamentos e ${int(ctx.access)} acessos.`;
      const finance = `Qualidade de caixa: ticket vendido ${ctx.salesTicket || "R$ 0,00"} versus ticket recebido ${ctx.receivedTicket || "R$ 0,00"}; maior faturamento em ${ctx.topRevenueUnit || "sem unidade"} (${ctx.topRevenueDisplay || "sem leitura"}).`;
      const retention = `Retenção: melhor churn em ${ctx.bestChurnUnit || "sem unidade"} (${ctx.bestChurnDisplay || "sem leitura"}), enquanto ${int(ctx.inadimplentes)} ativos estão marcados como inadimplentes (${pct(ctx.inadimplentesPct)}).`;
      const frequency = `Frequência: média de ${Number(ctx.ownAccessMean || 0).toFixed(1).replace(".", ",")} acessos por aluno próprio e ${Number(ctx.aggregatorAccessMean || 0).toFixed(1).replace(".", ",")} por agregador.`;
      const market = `Mercado: HFA cita o Brasil com mais de 31 mil clubes e 7,9 milhões de membros; Wellhub informa rede global com 100 mil+ academias/estúdios e que 61% dos usuários não tinham academia antes do benefício. A leitura prática é usar agregadores como funil e frequência como prova de retenção.`;
      if (!q.trim()) return "Me diga qual decisão você quer tomar: vender mais, reduzir churn, recuperar inadimplência, comparar unidades ou avaliar expansão.";
      const dashboardTerms = ["venda", "fatur", "receita", "ticket", "cancel", "churn", "reten", "inadimpl", "cobran", "frequ", "acesso", "unidade", "plano", "ltv", "wellhub", "totalpass", "aluno", "cliente", "biofisic", "mercado fitness"];
      if (!dashboardTerms.some(term => q.includes(term))) {
        return `${base}\n\nEssa pergunta parece estar fora do contexto direto do dashboard. Em modo local, eu consigo orientar melhor quando a pergunta estiver conectada a vendas, retencao, cobranca, frequencia, perfil, expansao ou mercado fitness.\n\nA isa IA local usa apenas os dados carregados, sem API externa e sem custo de tokens.`;
      }
      if (q.includes("fatur") || q.includes("receita") || q.includes("caixa") || q.includes("ticket")) {
        return `${base}\n\n${finance}\n\nLeitura crítica: faturamento alto precisa ser separado entre venda de entrada, recorrência recebida e agregadores. Se uma unidade aparece forte em venda mas fraca em recebimento/frequência, ela pode estar comprando crescimento com risco futuro.`;
      }
      if (q.includes("churn") || q.includes("cancel") || q.includes("reten")) {
        return `${base}\n\n${retention}\n\nDireção isaIAs: priorize unidades com cancelamento alto, baixa frequência e inadimplência simultânea. O primeiro ganho costuma vir de rotina de contato nos primeiros 30 dias e recuperação antes do vencimento seguinte.`;
      }
      if (q.includes("inadimpl") || q.includes("cobran") || q.includes("devedor")) {
        return `${base}\n\n${retention}\n\nCobrança deve ser lida como operação, não só financeiro: baixa visita + mensalidade aberta indica risco de abandono; visita recorrente + atraso indica caso de recuperação com maior chance de sucesso.`;
      }
      if (q.includes("frequ") || q.includes("acesso") || q.includes("visita")) {
        return `${base}\n\n${frequency}\n\nTese: frequência é o principal sinal comportamental de retenção. Alunos sem visita após compra devem ser tratados como pré-cancelamento, não como base ativa saudável.`;
      }
      if (q.includes("mercado") || q.includes("benchmark") || q.includes("concorr") || q.includes("rede")) {
        return `${base}\n\n${market}\n\nComparação estratégica: redes que escalam melhor combinam padronização comercial, baixo atrito de acesso, rotina de uso e dados para antecipar churn.`;
      }
      if (q.includes("unidade") || q.includes("prioridade") || q.includes("expans")) {
        return `${base}\n\n${finance}\n${retention}\n\nPrioridade executiva: compare top faturamento, sucesso de venda e menor churn. Unidade boa para expansão não é só a que vende mais; é a que vende, recebe, gera visita e retém.`;
      }
      return `${base}\n\n${finance}\n${retention}\n${frequency}\n\n${market}\n\nRecomendação: transforme a pergunta em uma decisão operacional concreta: qual unidade, qual público, qual prazo e qual métrica vai provar melhora.`;
    }
    const isaiasStopwords = new Set(["a", "ao", "aos", "as", "ate", "com", "como", "da", "das", "de", "do", "dos", "e", "em", "essa", "esse", "esta", "este", "eu", "me", "na", "nas", "no", "nos", "o", "os", "ou", "para", "por", "qual", "quais", "que", "se", "sobre", "tem", "ter", "um", "uma"]);
    const isaiasIntentTerms = {
      financeiro: ["fatur", "receita", "caixa", "ticket", "receb", "pagamento", "mensalidade", "cobranca"],
      vendas: ["venda", "contrato", "comercial", "checkout", "sv plus", "sangue verde", "plano"],
      retencao: ["cancel", "churn", "retenc", "ltv", "risco", "abandono", "90", "120"],
      frequencia: ["frequ", "acesso", "visita", "entrada", "horario", "wellhub", "totalpass", "agregador"],
      perfil: ["perfil", "idade", "sexo", "faixa", "aluno", "cliente", "ativo", "inadimpl"],
      unidades: ["unidade", "ranking", "melhor", "pior", "compar", "prioridade", "expans"],
    };
    function isaiasNorm(value) {
      return String(value ?? "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }
    function isaiasTokens(value) {
      return new Set((isaiasNorm(value).match(/[a-z0-9]{3,}/g) || []).filter(token => !isaiasStopwords.has(token)));
    }
    function isaiasNumber(value) {
      if (value === undefined || value === null || value === "") return null;
      if (typeof value === "number") return value;
      const raw = String(value);
      const text = raw.includes(",") ? raw.replace(/[.]/g, "").replace(",", ".") : raw;
      const match = text.match(/-?[0-9]+(?:[.,][0-9]+)?/);
      return match ? Number(String(match[0]).replace(",", ".")) : null;
    }
    function isaiasDisplayValue(value) {
      const raw = String(value || "").trim();
      if (raw.includes("R$") || raw.includes("%")) return raw;
      const number = isaiasNumber(value);
      if (number === null || Number.isNaN(number)) return raw;
      if (Math.abs(number) >= 1000 && Number.isInteger(number)) return int(number);
      if (Number.isInteger(number)) return String(number);
      return number.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    }
    function isaiasPctDetail(value) {
      const text = String(value || "0");
      return text.includes("%") ? text : `${text}%`;
    }
    function isaiasItemText(item) {
      const parts = [item.tab, item.kind, item.title, item.label, item.value, item.display, item.detail, item.subtitle];
      (item.bars || []).forEach(bar => parts.push(bar.label, bar.display, bar.value));
      (item.clusters || []).forEach(cluster => parts.push(cluster.label, cluster.value, cluster.pct));
      return parts.filter(part => part !== undefined && part !== null && part !== "").join(" | ");
    }
    function isaiasSemanticItems() {
      const context = buildIsaiasDashboardContext();
      const ctx = context.chatContext || {};
      const items = [];
      const summaryPairs = [
        ["Alunos ativos", ctx.active, "base ativa atual"],
        ["Adimplentes", ctx.adimplentes, isaiasPctDetail(ctx.adimplentesPct)],
        ["Inadimplentes", ctx.inadimplentes, isaiasPctDetail(ctx.inadimplentesPct)],
        ["Contratos vendidos", ctx.sales, `${ctx.salesClients || 0} clientes`],
        ["Cancelamentos", ctx.cancellations, `${ctx.cancelClients || 0} clientes`],
        ["Acessos", ctx.access, `${ctx.accessClients || 0} clientes`],
        ["Ticket vendido", ctx.salesTicket, "ticket medio de venda"],
        ["Ticket recebido", ctx.receivedTicket, "ticket medio de recebimento"],
        ["SV Plus", ctx.svPlusPct, "mix premium nas vendas"],
        ["Maior faturamento", ctx.topRevenueUnit, ctx.topRevenueDisplay],
        ["Melhor sucesso de venda", ctx.topSalesSuccessUnit, ctx.topSalesSuccessDisplay],
        ["Menor churn", ctx.bestChurnUnit, ctx.bestChurnDisplay],
        ["Cobranca critica", ctx.paymentAlert, ctx.paymentAlertDisplay],
      ];
      summaryPairs.forEach(([label, value, detail]) => {
        if (value !== undefined && value !== null && value !== "") items.push({ tab: "Resumo executivo", kind: "indicador", title: label, label, value, detail });
      });
      (context.medalBoard || []).forEach(row => {
        items.push({ tab: "Ranking", kind: "estrelas", title: "Quadro de estrelas", label: row.unit, value: `3 estrelas ${row.gold || 0}, 2 estrelas ${row.silver || 0}, 1 estrela ${row.bronze || 0}`, detail: `pontos ${row.total || 0}` });
      });
      Object.entries(context.tabs || {}).forEach(([tabKey, tab]) => {
        (tab.cards || []).forEach(card => {
          items.push({ tab: tabKey, kind: "card", title: card.label, label: card.label, value: card.value, detail: card.detail });
        });
        (tab.composition || []).forEach(row => {
          items.push({ tab: tabKey, kind: "composicao", title: "Composicao", label: row.label, value: row.display || row.value, detail: row.detail });
        });
        (tab.charts || []).forEach(chart => {
          (chart.rows || []).forEach(row => {
            items.push({
              tab: tabKey,
              kind: "grafico",
              title: chart.title || "Grafico",
              subtitle: chart.subtitle || "",
              label: row.label || row.unit || row.name,
              value: row.display || row.value || row.total || row.pct,
              display: row.display || row.medianDisplay || row.meanDisplay,
              detail: row.detail || row.sub || "",
              bars: row.bars || [],
              clusters: row.clusters || [],
            });
          });
        });
      });
      return items.map(item => {
        const text = isaiasItemText(item);
        return { ...item, text, tokens: isaiasTokens(text) };
      }).filter(item => item.text);
    }
    function isaiasRankItems(question, items) {
      const queryTokens = isaiasTokens(question);
      const queryNorm = isaiasNorm(question);
      const wantLow = ["menor", "menos", "baixo", "baixa"].some(term => queryNorm.includes(term));
      const ranked = items.map(item => {
        const overlap = Array.from(queryTokens).filter(token => item.tokens.has(token)).length;
        const phrase = Array.from(queryTokens).filter(token => isaiasNorm(item.text).includes(token)).length * 2;
        const tab = item.tab && queryNorm.includes(isaiasNorm(item.tab)) ? 2 : 0;
        const number = isaiasNumber(item.display || item.value);
        return { item, score: overlap * 4 + phrase + tab, number: number === null || Number.isNaN(number) ? -1 : number };
      }).filter(pair => pair.score > 0).sort((a, b) => {
        if (b.score !== a.score) return b.score - a.score;
        return wantLow ? a.number - b.number : b.number - a.number;
      });
      return ranked.length ? ranked.slice(0, 10).map(pair => pair.item) : items.slice(0, 8);
    }
    function isaiasIntent(question) {
      const q = isaiasNorm(question);
      let best = "geral";
      let bestScore = 0;
      Object.entries(isaiasIntentTerms).forEach(([name, terms]) => {
        const score = terms.filter(term => q.includes(term)).length;
        if (score > bestScore) {
          best = name;
          bestScore = score;
        }
      });
      return best;
    }
    function isaiasInterpretation(intent) {
      const messages = {
        financeiro: "Leitura critica: se receita, recebimento e frequencia nao caminham juntos, o faturamento pode esconder fragilidade de caixa.",
        vendas: "Leitura critica: volume comercial so e crescimento quando vira aluno ativo, frequente e pagante.",
        retencao: "Leitura critica: cancelamento e sintoma tardio. O risco nasce antes, na combinacao de baixa visita, inadimplencia e pouco tempo ativo.",
        frequencia: "Leitura critica: frequencia e a prova de valor percebido. Aluno que compra e nao entra precisa ser tratado como pre-churn.",
        perfil: "Leitura critica: perfil so vira decisao quando conectado a comportamento: idade, sexo, canal e status financeiro devem orientar acao por unidade.",
        unidades: "Leitura critica: a melhor unidade nao e necessariamente a que mais vende; e a que combina venda, recebimento, frequencia, baixa inadimplencia e menor churn.",
      };
      return messages[intent] || "Leitura critica: o dashboard deve ser lido como sistema. Venda cria entrada, frequencia prova valor, cobranca confirma receita e cancelamento mostra onde a operacao chegou tarde.";
    }
    function isaiasRecommendation(intent) {
      const messages = {
        financeiro: "Proximo passo: separar receita confirmada de venda de entrada, acompanhar recuperacao de meses anteriores e criar rotina diaria para parcelas vencidas do mes.",
        vendas: "Proximo passo: avaliar quais unidades vendem com maior sucesso depois da compra, replicar o playbook e auditar ofertas que geram inadimplencia.",
        retencao: "Proximo passo: montar lista de risco com alunos sem visita, inadimplentes e recem-vendidos, atacando antes do pedido de cancelamento.",
        frequencia: "Proximo passo: cruzar horario, unidade e canal para ajustar equipe, campanhas de ativacao e conversao de agregadores em relacionamento recorrente.",
        perfil: "Proximo passo: transformar perfil em acao segmentada por faixa etaria, sexo, unidade, canal e comportamento de acesso.",
        unidades: "Proximo passo: comparar as tres melhores e as tres piores na mesma metrica e buscar o processo operacional que explica a diferenca.",
      };
      return messages[intent] || "Proximo passo: formule a decisao desejada com unidade, periodo e metrica. A isa IA local consegue cruzar os indicadores carregados sem custo de API.";
    }
    function answerIsaias(question) {
      const ctx = data.tabs?.isaias?.chatContext || {};
      const q = String(question || "").trim();
      const base = `Base analisada: ${int(ctx.active)} ativos, ${int(ctx.sales)} contratos vendidos, ${int(ctx.cancellations)} cancelamentos e ${int(ctx.access)} acessos.`;
      if (!q) return "Digite qual decisao voce quer tomar: vender mais, reduzir churn, recuperar inadimplencia, comparar unidades, entender frequencia ou avaliar perfil.";
      const items = isaiasSemanticItems();
      const matches = isaiasRankItems(q, items);
      const intent = isaiasIntent(q);
      const seen = new Set();
      const evidence = [];
      matches.forEach(item => {
        const label = String(item.label || item.title || "").trim();
        const value = isaiasDisplayValue(item.display || item.value || "");
        const detail = String(item.detail || item.subtitle || "").trim();
        const tab = String(item.tab || "dashboard").trim();
        const key = `${tab}|${label}|${value}|${detail}`;
        if (!label || seen.has(key) || evidence.length >= 6) return;
        seen.add(key);
        evidence.push(`- ${tab}: ${label}: ${value}${detail && detail !== value ? ` - ${detail}` : ""}`);
      });
      if (!evidence.length) {
        evidence.push(`- Resumo executivo: ativos ${int(ctx.active)}, vendas ${int(ctx.sales)}, cancelamentos ${int(ctx.cancellations)} e acessos ${int(ctx.access)}.`);
        evidence.push(`- Financeiro: ticket vendido ${ctx.salesTicket || "sem leitura"}; ticket recebido ${ctx.receivedTicket || "sem leitura"}; maior faturamento em ${ctx.topRevenueUnit || "sem unidade"} (${ctx.topRevenueDisplay || "sem leitura"}).`);
      }
      return [
        "Modo local semantico gratuito: analisei a pergunta usando apenas os dados carregados no dashboard, sem API externa e sem custo de tokens.",
        "",
        base,
        "",
        "O que encontrei nos dados:",
        ...evidence,
        "",
        isaiasInterpretation(intent),
        "",
        isaiasRecommendation(intent),
      ].join("\\n");
    }
    function setupIsaiasChat() {
      const input = document.getElementById("isaiasQuestion");
      const output = document.getElementById("isaiasAnswer");
      const ask = document.getElementById("isaiasAsk");
      if (!input || !output || !ask) return;
      const submit = async question => {
        input.value = question || input.value;
        const currentQuestion = input.value.trim();
        if (!currentQuestion) {
          output.textContent = "";
          output.classList.add("is-hidden");
          return;
        }
        ask.disabled = true;
        output.classList.remove("is-hidden");
        output.textContent = "Análise em andamento com os dados carregados...";
        try {
          const payload = await answerIsaiasOnline(currentQuestion);
          const answer = String(payload.answer || "").trim() || answerIsaias(currentQuestion);
          const modeLabel = payload.mode === "local_semantic"
            ? "Modo local semantico"
            : "Modo local";
          const warning = payload.warning ? `\nAviso: ${payload.warning}` : "";
          output.textContent = `${answer}\n\nFonte da resposta: ${modeLabel}${warning}`;
          isaiasHistory.push({ role: "user", content: currentQuestion });
          isaiasHistory.push({ role: "assistant", content: answer });
          isaiasHistory = isaiasHistory.slice(-10);
        } catch (error) {
          const fallback = answerIsaias(currentQuestion);
          output.textContent = `${fallback}\n\nModo local ativado no navegador: ${error.message || "endpoint indisponivel"}`;
        } finally {
          ask.disabled = false;
        }
      };
      ask.addEventListener("click", () => submit());
      input.addEventListener("keydown", event => {
        if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) submit();
      });
    }
    const filterKinds = {
      period: { title: "Selecionar período", empty: "Todo o período", toggle: "periodFilterToggle", type: "range" },
      periodStart: { title: "Selecionar data de início", empty: "Data inicial", toggle: "periodStartToggle", hidden: "periodStart", type: "date" },
      periodEnd: { title: "Selecionar data de fim", empty: "Data final", toggle: "periodEndToggle", hidden: "periodEnd", type: "date" },
      unit: { title: "Selecionar unidades", empty: "Todas as unidades", plural: "unidades", toggle: "unitFilterToggle", hidden: "unitFilter", hiddenList: "unitFilters", optionKey: "units" },
      age: { title: "Selecionar faixas etárias", empty: "Todas as faixas", plural: "faixas", toggle: "ageFilterToggle", hidden: "ageFilter", hiddenList: "ageFilters", optionKey: "ageBands" },
      gender: { title: "Selecionar sexo", empty: "Todos", plural: "opções", toggle: "genderFilterToggle", hidden: "genderFilter", hiddenList: "genderFilters", optionKey: "genders" },
    };
    let activePopupFilter = "";
    let scheduleDashboardFilterUpdate = () => {};
    function splitFilterValues(value) {
      if (Array.isArray(value)) return value.filter(Boolean);
      return String(value || "").split("||").filter(Boolean);
    }
    function formatDateLabel(value) {
      const parts = String(value || "").split("-");
      if (parts.length !== 3) return "";
      return `${parts[2]}/${parts[1]}/${parts[0]}`;
    }
    function setPeriodValues(startValue = "", endValue = "") {
      const start = document.getElementById("periodStart");
      const end = document.getElementById("periodEnd");
      const toggle = document.getElementById("periodFilterToggle");
      if (start) start.value = startValue || "";
      if (end) end.value = endValue || "";
      const startLabel = formatDateLabel(startValue);
      const endLabel = formatDateLabel(endValue);
      const label = startLabel && endLabel
        ? `${startLabel} — ${endLabel}`
        : startLabel
          ? `A partir de ${startLabel}`
          : endLabel
            ? `Até ${endLabel}`
            : "Todo o período";
      if (toggle) {
        toggle.textContent = label;
        toggle.title = label;
      }
    }
    function periodRangeHtml() {
      const startValue = document.getElementById("periodStart")?.value || "";
      const endValue = document.getElementById("periodEnd")?.value || "";
      return `<div class="period-range-fields">
        <label class="filter-popup-date"><span>Data inicial</span><input id="filterPopupPeriodStart" type="date" value="${escapeHtml(startValue)}" /></label>
        <label class="filter-popup-date"><span>Data final</span><input id="filterPopupPeriodEnd" type="date" value="${escapeHtml(endValue)}" /></label>
      </div>`;
    }
    const calendarMonths = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
    const calendarWeekdays = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"];
    function parseIsoDate(value) {
      const match = String(value || "").match(/^(\\d{4})-(\\d{2})-(\\d{2})$/);
      if (!match) return null;
      const year = Number(match[1]);
      const month = Number(match[2]) - 1;
      const day = Number(match[3]);
      const date = new Date(year, month, day);
      if (date.getFullYear() !== year || date.getMonth() !== month || date.getDate() !== day) return null;
      return date;
    }
    function toIsoDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, "0");
      const day = String(date.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    }
    function monthStartIso(date) {
      return toIsoDate(new Date(date.getFullYear(), date.getMonth(), 1));
    }
    function shiftMonth(viewIso, delta) {
      const view = parseIsoDate(viewIso) || new Date();
      return monthStartIso(new Date(view.getFullYear(), view.getMonth() + delta, 1));
    }
    function initialCalendarView(kind) {
      const selected = selectedFilterValues(kind)[0] || "";
      const paired = kind === "periodEnd"
        ? document.getElementById("periodStart")?.value || ""
        : document.getElementById("periodEnd")?.value || "";
      return monthStartIso(parseIsoDate(selected) || parseIsoDate(paired) || new Date());
    }
    function dateCalendarHtml(kind, viewIso) {
      const view = parseIsoDate(viewIso) || new Date();
      const selectedValue = selectedFilterValues(kind)[0] || "";
      const selectedDate = parseIsoDate(selectedValue);
      const todayIso = toIsoDate(new Date());
      const year = view.getFullYear();
      const month = view.getMonth();
      const daysInMonth = new Date(year, month + 1, 0).getDate();
      const firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7;
      const selectedMonthText = selectedDate ? formatDateLabel(selectedValue) : "Nenhuma data selecionada";
      const blanks = Array.from({ length: firstWeekday }, () => `<span class="date-calendar-empty" aria-hidden="true"></span>`).join("");
      const days = Array.from({ length: daysInMonth }, (_, index) => {
        const day = index + 1;
        const iso = toIsoDate(new Date(year, month, day));
        const selectedClass = iso === selectedValue ? " is-selected" : "";
        const todayClass = iso === todayIso ? " is-today" : "";
        return `<button class="date-calendar-day${selectedClass}${todayClass}" type="button" data-calendar-day="${iso}" aria-label="${formatDateLabel(iso)}">${day}</button>`;
      }).join("");
      return `<div class="date-calendar" data-calendar-kind="${kind}" data-calendar-view="${monthStartIso(view)}">
        <input id="filterPopupDate" type="hidden" value="${escapeHtml(selectedValue)}" />
        <div class="date-calendar-head">
          <button class="date-calendar-nav" type="button" data-calendar-nav="-1" aria-label="Mes anterior">‹</button>
          <div class="date-calendar-title">
            <strong>${calendarMonths[month]} ${year}</strong>
            <span>${selectedMonthText}</span>
          </div>
          <button class="date-calendar-nav" type="button" data-calendar-nav="1" aria-label="Proximo mes">›</button>
        </div>
        <div class="date-calendar-week">${calendarWeekdays.map(day => `<span>${day}</span>`).join("")}</div>
        <div class="date-calendar-grid">${blanks}${days}</div>
        <div class="date-calendar-note">Clique em um dia para aplicar o filtro automaticamente.</div>
      </div>`;
    }
    function mountDateCalendar(kind, viewIso) {
      const list = document.getElementById("filterPopupList");
      if (!list) return;
      list.innerHTML = dateCalendarHtml(kind, viewIso);
      list.querySelectorAll("[data-calendar-nav]").forEach(button => {
        button.addEventListener("click", () => mountDateCalendar(kind, shiftMonth(list.querySelector(".date-calendar")?.dataset.calendarView || viewIso, Number(button.dataset.calendarNav || 0))));
      });
      list.querySelectorAll("[data-calendar-day]").forEach(button => {
        button.addEventListener("click", () => {
          const value = button.dataset.calendarDay || "";
          const field = document.getElementById("filterPopupDate");
          if (field) field.value = value;
          commitDateFilter(kind, value);
        });
      });
    }
    function commitDateFilter(kind, value) {
      setFilterValues(kind, value ? [value] : []);
      const openEndAfterStart = kind === "periodStart" && value && !document.getElementById("periodEnd")?.value;
      closeFilterPopup();
      if (openEndAfterStart) {
        window.setTimeout(() => openFilterPopup("periodEnd"), 80);
        return;
      }
      scheduleDashboardFilterUpdate();
    }
    function selectedFilterValues(kind) {
      const config = filterKinds[kind];
      if (config?.type === "date") {
        return splitFilterValues(document.getElementById(config.hidden)?.value || "");
      }
      return splitFilterValues(document.getElementById(config.hiddenList)?.value || document.getElementById(config.hidden)?.value || "");
    }
    function setFilterValues(kind, values) {
      const config = filterKinds[kind];
      const unique = Array.from(new Set((values || []).filter(Boolean)));
      const joined = unique.join("||");
      const hidden = document.getElementById(config.hidden);
      const hiddenList = document.getElementById(config.hiddenList);
      const toggle = document.getElementById(config.toggle);
      if (config.type === "date") {
        const value = unique[0] || "";
        if (hidden) hidden.value = value;
        if (toggle) {
          const label = formatDateLabel(value);
          toggle.textContent = label || config.empty;
          toggle.title = label || config.empty;
        }
        return;
      }
      if (hidden) hidden.value = joined;
      if (hiddenList) hiddenList.value = joined;
      if (toggle) {
        if (!unique.length) {
          toggle.textContent = config.empty;
        } else if (unique.length <= 2) {
          toggle.textContent = unique.join(", ");
        } else {
          toggle.textContent = `${unique.length} ${config.plural}`;
        }
        toggle.title = unique.length ? unique.join(", ") : config.empty;
      }
    }
    function popupOptions(kind) {
      const config = filterKinds[kind];
      const options = data.filterOptions || {};
      return options[config.optionKey] || [];
    }
    function openFilterPopup(kind) {
      const config = filterKinds[kind];
      if (!config) return;
      activePopupFilter = kind;
      const selected = new Set(selectedFilterValues(kind));
      const popup = document.getElementById("filterPopup");
      const title = document.getElementById("filterPopupTitle");
      const list = document.getElementById("filterPopupList");
      if (!popup || !title || !list) return;
      title.textContent = config.title;
      if (config.type === "range") {
        list.innerHTML = periodRangeHtml();
        popup.hidden = false;
        return;
      }
      if (config.type === "date") {
        popup.hidden = false;
        mountDateCalendar(kind, initialCalendarView(kind));
        return;
      }
      list.innerHTML = popupOptions(kind).map((option, index) => {
        const id = `popup-${kind}-${index}`;
        const checked = selected.has(option) ? "checked" : "";
        return `<label class="filter-popup-option" for="${id}">
          <input id="${id}" type="checkbox" value="${escapeHtml(option)}" ${checked} />
          <span>${escapeHtml(option)}</span>
        </label>`;
      }).join("");
      popup.hidden = false;
    }
    function closeFilterPopup() {
      const popup = document.getElementById("filterPopup");
      if (popup) popup.hidden = true;
      activePopupFilter = "";
    }
    function applyFilterPopup() {
      if (!activePopupFilter) return closeFilterPopup();
      const kind = activePopupFilter;
      const config = filterKinds[kind];
      if (config?.type === "range") {
        let startValue = document.getElementById("filterPopupPeriodStart")?.value || "";
        let endValue = document.getElementById("filterPopupPeriodEnd")?.value || "";
        if (startValue && endValue && startValue > endValue) [startValue, endValue] = [endValue, startValue];
        setPeriodValues(startValue, endValue);
        closeFilterPopup();
        scheduleDashboardFilterUpdate();
        return;
      }
      if (config?.type === "date") {
        const value = document.getElementById("filterPopupDate")?.value || "";
        commitDateFilter(kind, value);
        return;
      }
      const values = Array.from(document.querySelectorAll("#filterPopupList input[type='checkbox']:checked"))
        .map(input => input.value)
        .filter(Boolean);
      setFilterValues(kind, values);
      closeFilterPopup();
      scheduleDashboardFilterUpdate();
    }
    function clearFilterPopup() {
      if (filterKinds[activePopupFilter]?.type === "range") {
        const start = document.getElementById("filterPopupPeriodStart");
        const end = document.getElementById("filterPopupPeriodEnd");
        if (start) start.value = "";
        if (end) end.value = "";
        return;
      }
      if (filterKinds[activePopupFilter]?.type === "date") {
        const field = document.getElementById("filterPopupDate");
        if (field) field.value = "";
        document.querySelectorAll(".date-calendar-day.is-selected").forEach(day => day.classList.remove("is-selected"));
        return;
      }
      document.querySelectorAll("#filterPopupList input[type='checkbox']").forEach(input => { input.checked = false; });
    }
    function setupFilters() {
      const filters = data.filters || {};
      setPeriodValues(filters.periodStart || "", filters.periodEnd || "");
      setFilterValues("unit", filters.unitFilters || splitFilterValues(filters.unitFilter));
      setFilterValues("age", filters.ageFilters || splitFilterValues(filters.ageFilter));
      setFilterValues("gender", filters.genderFilters || splitFilterValues(filters.genderFilter));
    }
    function collectFilters() {
      const unitFilters = selectedFilterValues("unit");
      const ageFilters = selectedFilterValues("age");
      const genderFilters = selectedFilterValues("gender");
      return {
        periodStart: document.getElementById("periodStart")?.value || "",
        periodEnd: document.getElementById("periodEnd")?.value || "",
        unitFilter: unitFilters.join("||"),
        unitFilters: unitFilters.join("||"),
        ageFilter: ageFilters.join("||"),
        ageFilters: ageFilters.join("||"),
        genderFilter: genderFilters.join("||"),
        genderFilters: genderFilters.join("||"),
      };
    }
    function activeTabKey() {
      return document.querySelector("[data-tab].active")?.dataset.tab || "ativos";
    }
    function tabPanelHtml(key, index = 0, isActive = false) {
      const tab = data.tabs?.[key] || { cards: [], charts: [] };
      if (tab.loadError) {
        return `<section class="tab-panel ${isActive ? "active" : ""}" id="tab-${key}">
          <article class="panel progressive-loading-panel is-error">
            <strong>Não foi possível carregar ${escapeHtml(tabs.find(([tabKey]) => tabKey === key)?.[1] || key)}</strong>
            <small>${escapeHtml(tab.loadError)}</small>
            <button class="progressive-load-retry" type="button" data-retry-tab="${escapeHtml(key)}">Tentar novamente</button>
          </article>
        </section>`;
      }
      if (tab.loading) {
        return `<section class="tab-panel ${isActive ? "active" : ""}" id="tab-${key}">
          <article class="panel progressive-loading-panel">
            <div class="progressive-loading-spinner" aria-hidden="true"></div>
            <strong>Carregando ${escapeHtml(tabs.find(([tabKey]) => tabKey === key)?.[1] || key)}</strong>
            <small>Os dados necessários desta aba estão sendo preparados em segundo plano.</small>
          </article>
        </section>`;
      }
      if (tab.layout === "active_summary") {
        return `<section class="tab-panel ${isActive ? "active" : ""}" id="tab-${key}">
          ${summaryCardsHtml((tab.cards || []).concat(tab.aggregatorCards || []), "active-card-grid")}
          ${activeChartsHtml(tab.charts || [], tab.composition, tab.footerCards || [])}
        </section>`;
      }
      if (tab.layout === "sales_summary") {
        return `<section class="tab-panel ${isActive ? "active" : ""}" id="tab-${key}">
          ${summaryCardsHtml(tab.cards || [])}
          ${salesTickerHtml(tab.ticker || [])}
          ${salesChartsHtml(tab.charts || [])}
        </section>`;
      }
      if (tab.layout === "cancel_summary") {
        return `<section class="tab-panel ${isActive ? "active" : ""}" id="tab-${key}">
          ${summaryCardsHtml(tab.cards || [])}
          ${cancelChartsHtml(tab.charts || [])}
        </section>`;
      }
      if (tab.layout === "financial_summary") {
        return `<section class="tab-panel ${isActive ? "active" : ""}" id="tab-${key}">
          ${summaryCardsHtml(tab.cards || [])}
          ${financialChartsHtml(tab.charts || [])}
        </section>`;
      }
      if (tab.layout === "frequency_summary") {
        return `<section class="tab-panel ${isActive ? "active" : ""}" id="tab-${key}">
          ${summaryCardsHtml(tab.cards || [])}
          ${frequencyChartsHtml(tab.charts || [])}
        </section>`;
      }
      if (tab.layout === "isaias") {
        return `<section class="tab-panel ${isActive ? "active" : ""}" id="tab-${key}">
          ${isaiasPanel(tab)}
        </section>`;
      }
      return `<section class="tab-panel ${isActive ? "active" : ""}" id="tab-${key}">
        <div class="cards">${(tab.cards || []).map(cardHtml).join("")}</div>
        <div class="grid">${(tab.charts || []).map(chartPanel).join("")}</div>
      </section>`;
    }
    function refreshDisplayRows(scope = document) {
      scope.querySelectorAll("[data-display]").forEach(row => {
        const value = row.querySelector(".bar-value");
        if (value) value.textContent = row.dataset.display;
      });
    }
    function bindTabButtons() {
      document.querySelectorAll("[data-tab]").forEach(button => {
        button.addEventListener("click", async () => {
          document.querySelectorAll("[data-tab]").forEach(item => item.classList.remove("active"));
          document.querySelectorAll(".tab-panel").forEach(panel => panel.classList.remove("active"));
          button.classList.add("active");
          const activatedPanel = document.getElementById(`tab-${button.dataset.tab}`);
          activatedPanel?.classList.add("active");
          if (!loadedTabKeys.has(button.dataset.tab)) {
            try {
              await requestDashboardTab(button.dataset.tab, false, false);
            } catch (error) {
              console.warn(`Falha ao carregar ${button.dataset.tab}:`, error);
            }
          } else {
            window.requestAnimationFrame(() => activateEditorForTab(activatedPanel));
          }
        });
      });
    }
    function bindActiveGoalSort(scope = document) {
      scope.querySelectorAll("[data-active-goal-sort]").forEach(button => {
        button.addEventListener("click", () => {
          activeUnitSortMode = activeUnitSortMode === "opening" ? "active" : "opening";
          render();
        });
      });
    }
    function bindCannibalizationPeriods(scope = document) {
      scope.querySelectorAll("[data-cannibalization-select]").forEach(select => {
        const panel = select.closest("[data-cannibalization-panel]");
        if (!panel) return;
        const update = () => {
          panel.querySelectorAll("[data-cannibalization-period]").forEach(view => {
            view.hidden = view.dataset.cannibalizationPeriod !== select.value;
          });
        };
        select.addEventListener("change", update);
        update();
      });
    }
    function bindFinancialPeriods(scope = document) {
      scope.querySelectorAll("[data-financial-select]").forEach(select => {
        const panel = select.closest("[data-financial-panel]");
        if (!panel) return;
        const update = () => {
          panel.querySelectorAll("[data-financial-month]").forEach(view => {
            view.hidden = view.dataset.financialMonth !== select.value;
          });
        };
        select.addEventListener("change", update);
        update();
      });
    }
    function bindFinancialRevenueFilters(scope = document) {
      scope.querySelectorAll("[data-revenue-panel]").forEach(panel => {
        const buttons = [...panel.querySelectorAll("[data-revenue-filter]")];
        const update = key => {
          panel.querySelectorAll("[data-revenue-view]").forEach(view => {
            view.hidden = view.dataset.revenueView !== key;
          });
          buttons.forEach(button => button.classList.toggle("active", button.dataset.revenueFilter === key));
        };
        buttons.forEach(button => button.addEventListener("click", () => update(button.dataset.revenueFilter)));
      });
    }
    function bindLineSeriesSelectors(scope = document) {
      scope.querySelectorAll("[data-line-series-selector]").forEach(control => {
        const chartKey = control.dataset.lineSeriesSelector;
        control.querySelectorAll("[data-line-series-key]").forEach(input => {
          input.addEventListener("change", () => {
            const checked = Array.from(control.querySelectorAll("[data-line-series-key]:checked"));
            if (!checked.length) {
              input.checked = true;
              return;
            }
            lineChartSelections.set(chartKey, new Set(checked.map(item => item.dataset.lineSeriesKey)));
            replaceActiveTab(activeTabKey(), true);
          });
        });
      });
    }
    function churnRiskStudentRows(students) {
      const riskClass = risk => ({ "Médio": "risk-medium", "Alto": "risk-high", "Crítico": "risk-critical" }[risk] || "risk-low");
      return students.map(student => `<tr>
        <td><span class="churn-risk-name"><strong>${escapeHtml(student.name)}</strong><small>ID ${escapeHtml(student.id)}</small></span></td>
        <td><span class="churn-risk-score ${riskClass(student.risk)}">${int(student.score)}</span></td>
        <td>${fmtMoney.format(Number(student.debt || 0))}</td>
        <td>${int(student.overdueParcels)}</td>
        <td>${int(student.maxOverdueDays)}</td>
        <td>${int(student.visits)}</td>
        <td>${pct(student.frequencyPct)}</td>
        <td>+${int(student.financialPoints)}</td>
        <td>+${int(student.delayPoints)}</td>
        <td>+${int(student.frequencyPoints)}</td>
      </tr>`).join("");
    }
    function closeChurnRiskModal(modal) {
      if (!modal) return;
      modal.hidden = true;
      document.body.classList.remove("churn-risk-modal-open");
      modal._returnFocus?.focus?.();
      modal._returnFocus = null;
    }
    function openChurnRiskModal(panel, segment) {
      const chart = churnRiskRegistry.get(panel.dataset.churnRiskChart || "");
      const view = (chart?.views || []).find(item => String(item.key) === String(segment.dataset.viewKey));
      const band = (view?.distribution || []).find(item => String(item.label) === String(segment.dataset.riskBand));
      const modal = panel._churnRiskModal || Array.from(document.body.querySelectorAll("[data-churn-risk-modal]"))
        .find(item => item.dataset.churnRiskOwner === panel.dataset.churnRiskChart);
      if (!chart || !view || !band || !modal) return;
      const students = Array.isArray(view.studentsByRisk?.[band.label]) ? view.studentsByRisk[band.label] : [];
      modal.dataset.tone = band.tone || "green";
      modal.querySelector("[data-churn-risk-modal-title]").textContent = `${view.label} · Risco ${band.label}`;
      modal.querySelector("[data-churn-risk-modal-subtitle]").textContent = `Distribuição dos ${int(view.total)} alunos ativos da unidade. A tabela está filtrada em ${band.label} (${band.range}), com dados até ${chart.referenceDate || "a data mais recente"}.`;
      modal.querySelector("[data-churn-risk-modal-summary]").innerHTML = (view.distribution || []).filter(item => ["Médio", "Alto", "Crítico"].includes(String(item.label))).map(item => `
        <div class="churn-risk-band ${String(item.label) === String(band.label) ? "is-selected" : ""}" data-tone="${escapeHtml(item.tone || "green")}">
          <div class="churn-risk-band-head"><span>${escapeHtml(item.label)}</span><small>${escapeHtml(item.range)}</small></div>
          <strong>${int(item.value)}</strong>
          <div class="churn-risk-band-track"><div class="churn-risk-band-fill" style="--w:${Math.max(0, Math.min(100, Number(item.pct || 0)))}%"></div></div>
          <small>${pct(item.pct)} da base selecionada</small>
        </div>`).join("");
      modal.querySelector("[data-churn-risk-modal-rows]").innerHTML = churnRiskStudentRows(students) || `<tr><td colspan="10">Nenhum aluno encontrado nesta faixa.</td></tr>`;
      modal.querySelector("[data-churn-risk-modal-foot]").textContent = Number(band.value || 0) > students.length
        ? `Exibindo os ${int(students.length)} maiores scores de ${int(band.value)} alunos da faixa selecionada.`
        : `Exibindo ${int(students.length)} alunos da faixa selecionada.`;
      modal._returnFocus = segment;
      modal.hidden = false;
      document.body.classList.add("churn-risk-modal-open");
      modal.querySelector("[data-churn-risk-modal-close]")?.focus();
    }
    function bindChurnRiskInteractions(scope = document) {
      scope.querySelectorAll("[data-churn-risk-panel]").forEach(panel => {
        const modal = panel.querySelector("[data-churn-risk-modal]");
        if (modal) {
          document.body.querySelectorAll("[data-churn-risk-modal]").forEach(previous => {
            if (previous !== modal) previous.remove();
          });
          modal.dataset.churnRiskOwner = panel.dataset.churnRiskChart || "";
          document.body.appendChild(modal);
          panel._churnRiskModal = modal;
        }
        panel.querySelectorAll("[data-churn-risk-segment]").forEach(segment => {
          segment.addEventListener("click", event => {
            event.preventDefault();
            event.stopPropagation();
            openChurnRiskModal(panel, segment);
          });
          segment.addEventListener("keydown", event => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              openChurnRiskModal(panel, segment);
            }
          });
        });
        panel.querySelectorAll("[data-churn-risk-ring]").forEach(ring => {
          ring.addEventListener("click", event => {
            const bounds = ring.getBoundingClientRect();
            const centerX = bounds.left + bounds.width / 2;
            const centerY = bounds.top + bounds.height / 2;
            const dx = event.clientX - centerX;
            const dy = event.clientY - centerY;
            const distance = Math.hypot(dx, dy);
            const outerRadius = Math.min(bounds.width, bounds.height) * .46;
            const innerRadius = Math.min(bounds.width, bounds.height) * .29;
            if (distance < innerRadius || distance > outerRadius) return;
            const chart = churnRiskRegistry.get(panel.dataset.churnRiskChart || "");
            const view = (chart?.views || []).find(item => String(item.key) === String(ring.dataset.viewKey));
            if (!view) return;
            const angle = (Math.atan2(dy, dx) * 180 / Math.PI + 450) % 360;
            const clickedPct = angle / 360 * 100;
            let cumulative = 0;
            const bands = (view.distribution || []).filter(band => ["Médio", "Alto", "Crítico"].includes(String(band.label)));
            const riskTotal = bands.reduce((sum, band) => sum + Number(band.value || 0), 0);
            const bandIndex = bands.findIndex(band => {
              cumulative += riskTotal ? Number(band.value || 0) * 100 / riskTotal : 0;
              return clickedPct <= cumulative + .0001;
            });
            const clickedBand = bandIndex >= 0 ? bands[bandIndex] : null;
            const segment = Array.from(ring.querySelectorAll("[data-churn-risk-segment]"))
              .find(item => item.dataset.riskBand === String(clickedBand?.label || ""));
            if (segment) openChurnRiskModal(panel, segment);
          });
        });
        modal?.querySelector("[data-churn-risk-modal-close]")?.addEventListener("click", () => closeChurnRiskModal(modal));
        modal?.addEventListener("click", event => {
          if (event.target === modal) closeChurnRiskModal(modal);
        });
        modal?.addEventListener("keydown", event => {
          if (event.key === "Escape") closeChurnRiskModal(modal);
        });
      });
    }
    function applyTheme(theme, persist = true) {
      selectedTheme = theme === "dark" ? "dark" : "light";
      document.documentElement.dataset.theme = selectedTheme;
      const button = document.getElementById("themeToggle");
      if (button) {
        const dark = selectedTheme === "dark";
        button.querySelector(".theme-toggle-icon").textContent = dark ? "☀" : "☾";
        button.querySelector(".theme-toggle-label").textContent = dark ? "Modo claro" : "Modo escuro";
        button.setAttribute("aria-pressed", dark ? "true" : "false");
        button.title = dark ? "Ativar modo claro" : "Ativar modo escuro";
      }
      if (persist) {
        try { localStorage.setItem(themeStorageKey, selectedTheme); } catch (error) { /* armazenamento opcional */ }
      }
    }
    function setupThemeToggle() {
      applyTheme(selectedTheme, false);
      const button = document.getElementById("themeToggle");
      if (!button || button.dataset.bound === "true") return;
      button.dataset.bound = "true";
      button.addEventListener("click", () => applyTheme(selectedTheme === "dark" ? "light" : "dark"));
    }
    function isExpandablePanel(panel) {
      if (!panel || panel.matches(".progressive-loading-panel, .isaias-chat, .analysis-executive, .analysis-alerts-panel, .analysis-observations-panel, .churn-risk-panel")) return false;
      if (Array.from(panel.classList).some(name => name.startsWith("chart-") || name === "composition-panel" || name === "financial-matrix-panel" || name === "medal-board-panel" || name === "analysis-matrix-panel")) return true;
      return Boolean(panel.querySelector("table, .donut, .bar-list, .multi-bars, .line-canvas, .timeline-chart, .active-goal-list, .aggregator-unique-list, .churn-risk-donut-layout"));
    }
    function chartExpandIcon() {
      return `<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4h6v6M20 4l-7 7M10 20H4v-6M4 20l7-7"/></svg>`;
    }
    function localizedNumberFromText(value) {
      const normalized = String(value || "").replace(/\\./g, "").replace(",", ".").replace(/[^0-9+\\-.]/g, "");
      const parsed = Number(normalized);
      return Number.isFinite(parsed) ? parsed : 0;
    }
    function activeEvolutionScenario(panel) {
      const readGrowth = element => {
        const text = element?.textContent?.trim() || "0 · 0%";
        const [absoluteText = "0", percentText = "0"] = text.split("·");
        return { absolute: localizedNumberFromText(absoluteText), percent: localizedNumberFromText(percentText) };
      };
      const units = Array.from(panel.querySelectorAll(".active-goal-row")).map(row => ({
        name: row.querySelector(".active-goal-label")?.getAttribute("title") || row.querySelector(".active-goal-label")?.textContent?.trim() || "Unidade",
        ...readGrowth(row.querySelector(".active-goal-growth")),
      }));
      const network = readGrowth(panel.querySelector(".active-goal-network .active-goal-growth"));
      const best = [...units].sort((a, b) => b.percent - a.percent)[0];
      const worst = [...units].sort((a, b) => a.percent - b.percent)[0];
      const movement = item => item.absolute > 0
        ? `cresceu ${int(item.absolute)} alunos (${signedPct(item.percent)})`
        : item.absolute < 0
          ? `recuou ${int(Math.abs(item.absolute))} alunos (${signedPct(item.percent)})`
          : "permaneceu estável";
      const networkText = `No mês, a rede ${movement(network)} em relação ao fechamento anterior.`;
      const bestText = best ? ` A melhor evolução foi de ${best.name}, que ${movement(best)}.` : "";
      const worstText = worst ? ` A menor performance foi de ${worst.name}, que ${movement(worst)}.` : "";
      return `${networkText}${bestText}${worstText}`;
    }
    function chartScenarioDescription(panelTitle, panel) {
      const title = String(panelTitle || "").toLocaleLowerCase("pt-BR");
      const context = panel.querySelector(".panel-subtitle, .composition-copy > p")?.textContent?.trim() || "";
      let description = "Este cenário apresenta os dados consolidados do gráfico conforme o período e os filtros aplicados no painel.";
      if (title.includes("ativos por unidade")) description = activeEvolutionScenario(panel);
      else if (title.includes("agregadores por unidade")) description = "Compara alunos e acessos de Wellhub e TotalPass por unidade, preservando as cores de cada plataforma e o total consolidado da rede.";
      else if (title.includes("base ativa") || title.includes("agregadores")) description = "Mostra a composição da base entre alunos próprios e agregadores, permitindo avaliar participação e concentração de cada grupo.";
      else if (title.includes("faixa etária")) description = "Compara homens e mulheres em cada faixa etária da base ativa: as barras à esquerda representam homens e as barras à direita representam mulheres, usando a mesma escala para permitir leitura direta das diferenças de perfil.";
      else if (title.includes("sexo")) description = "Apresenta a distribuição da base por gênero informado, incluindo registros sem classificação disponível.";
      else if (title.includes("venda") || title.includes("contrato")) description = "Resume o comportamento comercial no período selecionado, respeitando as regras de validação, limpeza e deduplicação de vendas.";
      else if (title.includes("cancel") || title.includes("churn") || title.includes("canibal")) description = "Evidencia perdas, cancelamentos ou migrações da base no período para apoiar a leitura de retenção por unidade.";
      else if (title.includes("fatur") || title.includes("finance") || title.includes("receb")) description = "Consolida os valores financeiros do período conforme as fontes e regras específicas de faturamento e recebimento.";
      else if (title.includes("frequ") || title.includes("acesso") || title.includes("visita")) description = "Compara o comportamento de frequência e acessos no período, destacando diferenças entre unidades e perfis de aluno.";
      else if (title.includes("risco") || title.includes("evasão")) description = "Distribui os alunos pelas faixas de risco calculadas a partir de cobrança e frequência, direcionando a priorização de retenção.";
      else if (title.includes("ltv")) description = "Compara a permanência e o valor de vida do aluno entre os agrupamentos apresentados no recorte selecionado.";
      return context ? `${description} Contexto do indicador: ${context}` : description;
    }
    function closeChartExpansion() {
      const modal = document.getElementById("chartExpandModal");
      if (!modal) return;
      modal.hidden = true;
      delete modal.dataset.chartKind;
      document.getElementById("chartExpandContent").replaceChildren();
      const scenario = document.getElementById("chartExpandScenario");
      if (scenario) scenario.textContent = "A visualização ampliada preserva os filtros e o período atualmente selecionados.";
      document.body.classList.remove("chart-modal-open");
    }
    function openChartExpansion(panel) {
      const modal = document.getElementById("chartExpandModal");
      const content = document.getElementById("chartExpandContent");
      const title = document.getElementById("chartExpandTitle");
      if (!modal || !content || !title) return;
      const clone = panel.cloneNode(true);
      clone.classList.remove("has-chart-expand");
      clone.classList.add("expanded-chart-clone");
      clone.querySelectorAll(".chart-expand-button").forEach(button => button.remove());
      clone.querySelectorAll("[id]").forEach(node => node.removeAttribute("id"));
      clone.querySelectorAll("[data-active-goal-sort]").forEach(button => button.remove());
      const panelTitle = panel.querySelector("h2")?.textContent?.trim() || "";
      const normalizedPanelTitle = panelTitle.toLocaleLowerCase("pt-BR");
      const chartKind = panel.classList.contains("chart-cancel-month") ? "cancel-month"
        : panel.classList.contains("chart-cancel-contracts") ? "cancel-contracts"
          : panel.classList.contains("chart-sales-contracts") ? "sales-contracts"
            : panel.classList.contains("chart-sales-ticket") ? "sales-ticket"
              : panel.classList.contains("chart-active-units") ? "active-units"
                : panel.classList.contains("chart-active-aggregators") ? "active-aggregators"
                  : panel.classList.contains("chart-profile-gender") ? "active-gender"
                    : panel.classList.contains("chart-profile-age") ? "active-age"
                      : normalizedPanelTitle.includes("base ativa") && panel.classList.contains("composition-panel") ? "active-composition"
                        : "default";
      modal.dataset.chartKind = chartKind;
      title.textContent = panelTitle || "Visualização ampliada";
      content.replaceChildren(clone);
      const scenario = document.getElementById("chartExpandScenario");
      if (scenario) scenario.textContent = chartScenarioDescription(title.textContent, panel);
      bindCannibalizationPeriods(clone);
      bindFinancialPeriods(clone);
      modal.hidden = false;
      document.body.classList.add("chart-modal-open");
      document.getElementById("chartExpandClose")?.focus();
    }
    function decorateExpandablePanels(scope = document) {
      scope.querySelectorAll(".panel").forEach(panel => {
        if (!isExpandablePanel(panel) || panel.querySelector(":scope > .chart-expand-button")) return;
        panel.classList.add("has-chart-expand");
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chart-expand-button";
        button.setAttribute("aria-label", "Ampliar gráfico");
        button.title = "Ampliar visualização";
        button.innerHTML = chartExpandIcon();
        button.addEventListener("click", event => {
          event.preventDefault();
          event.stopPropagation();
          openChartExpansion(panel);
        });
        panel.prepend(button);
      });
    }
    function setupChartExpansion() {
      const modal = document.getElementById("chartExpandModal");
      const close = document.getElementById("chartExpandClose");
      close?.addEventListener("click", closeChartExpansion);
      modal?.addEventListener("click", event => {
        if (event.target === modal) closeChartExpansion();
      });
      document.addEventListener("keydown", event => {
        if (event.key === "Escape" && modal && !modal.hidden) closeChartExpansion();
      });
    }
    function readStoredJson(key, fallback = {}) {
      try {
        const stored = localStorage.getItem(key);
        return stored ? JSON.parse(stored) : fallback;
      } catch (error) {
        return fallback;
      }
    }
    function writeStoredJson(key, value) {
      try { localStorage.setItem(key, JSON.stringify(value)); } catch (error) { /* armazenamento opcional */ }
    }
    function editableSlug(value) {
      return String(value || "item")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLocaleLowerCase("pt-BR")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "")
        .slice(0, 54) || "item";
    }
    function layoutTabKey(tabPanel) {
      return String(tabPanel?.id || "tab-pagina").replace(/^tab-/, "");
    }
    function isLayoutPanel(panel) {
      if (!panel?.matches?.(".panel")) return false;
      return !panel.matches(".progressive-loading-panel, .isaias-chat, .analysis-executive, .analysis-alerts-panel, .analysis-observations-panel");
    }
    function topLevelLayoutShell(node, tabPanel) {
      let shell = node;
      while (shell?.parentElement && shell.parentElement !== tabPanel) shell = shell.parentElement;
      return shell;
    }
    function storedLayoutForTab(tabKey) {
      const stored = readStoredJson(`${layoutStoragePrefix}.${tabKey}`, { items: {} });
      if (tabKey === "ativos" && Number(stored.version || 0) < 2) return { version: layoutStorageVersion, items: {} };
      if (tabKey === "vendas" && Number(stored.version || 0) < layoutStorageVersion) {
        const items = {};
        Object.entries(stored.items || {}).forEach(([id, item]) => {
          items[id] = { ...item, height: null };
        });
        return { version: layoutStorageVersion, items };
      }
      return stored;
    }
    function hasStoredLayoutForTab(tabKey) {
      try {
        const raw = localStorage.getItem(`${layoutStoragePrefix}.${tabKey}`);
        if (!raw) return false;
        if (tabKey !== "ativos") return true;
        return Number(JSON.parse(raw)?.version || 0) >= 2;
      } catch (error) { return false; }
    }
    function defaultLayoutSpan(panel, rect, tabWidth) {
      if (panel.closest(".active-overview-trio")) {
        if (panel.classList.contains("chart-active-units")) return 5;
        if (panel.classList.contains("composition-panel")) return 3;
        if (panel.classList.contains("chart-active-aggregators")) return 4;
      }
      if (panel.closest(".active-demographic-trio")) {
        if (panel.classList.contains("chart-profile-gender")) return 3;
        if (panel.classList.contains("chart-profile-age")) return 5;
        return 4;
      }
      if (panel.closest(".cancel-top-pair")) return panel.classList.contains("chart-cancel-month") ? 8 : 4;
      if (panel.closest(".cancel-unit-retention-grid")) return panel.classList.contains("chart-cancel-units") ? 8 : 4;
      if (panel.closest(".sales-month-contract-pair, .sales-chart-columns, .financial-chart-pair, .frequency-main-grid, .frequency-pair-grid, .frequency-cluster-grid, .cancel-threshold-pair")) return 6;
      if (panel.matches(".financial-matrix-panel, .analysis-matrix-panel, .churn-risk-panel, .chart-access-day")) return 12;
      return Math.max(3, Math.min(12, Math.round((rect.width || tabWidth) / tabWidth * 12)));
    }
    function saveTabLayout(tabPanel) {
      const tabKey = layoutTabKey(tabPanel);
      const grid = tabPanel.querySelector(":scope > .dashboard-layout-grid");
      if (!grid) return;
      const items = {};
      grid.querySelectorAll(":scope > .panel[data-layout-id]").forEach(panel => {
        items[panel.dataset.layoutId] = {
          order: Number(panel.dataset.layoutOrder || panel.style.order || 0),
          span: Number(panel.dataset.layoutSpan || 6),
          height: panel.classList.contains("user-sized-panel") ? Math.round(panel.getBoundingClientRect().height) : null,
        };
      });
      writeStoredJson(`${layoutStoragePrefix}.${tabKey}`, { version: layoutStorageVersion, items });
    }
    function scheduleLayoutMasonry(grid) {
      if (!grid || grid.dataset.layoutTab !== "vendas") return;
      const currentFrame = layoutMasonryFrames.get(grid);
      if (currentFrame) window.cancelAnimationFrame(currentFrame);
      grid.classList.remove("layout-masonry-ready");
      grid.querySelectorAll(":scope > .panel").forEach(panel => panel.style.removeProperty("--layout-row-span"));
      const frame = window.requestAnimationFrame(() => {
        layoutMasonryFrames.delete(grid);
        const gridStyle = window.getComputedStyle(grid);
        const rowHeight = Number.parseFloat(gridStyle.gridAutoRows) || 8;
        const rowGap = Number.parseFloat(gridStyle.rowGap) || 0;
        grid.querySelectorAll(":scope > .panel").forEach(panel => {
          const explicitHeight = panel.classList.contains("user-sized-panel")
            ? Number.parseFloat(panel.style.getPropertyValue("--layout-height"))
            : 0;
          const measuredHeight = explicitHeight || panel.getBoundingClientRect().height || panel.scrollHeight || 180;
          const span = Math.max(1, Math.ceil((measuredHeight + rowGap) / (rowHeight + rowGap)));
          panel.style.setProperty("--layout-row-span", String(span));
        });
        grid.classList.add("layout-masonry-ready");
      });
      layoutMasonryFrames.set(grid, frame);
    }
    function setPanelSpan(panel, span, persist = true) {
      const normalized = Math.max(3, Math.min(12, Math.round(Number(span) || 6)));
      panel.dataset.layoutSpan = String(normalized);
      panel.style.gridColumn = `span ${normalized}`;
      scheduleLayoutMasonry(panel.closest(".dashboard-layout-grid"));
      if (persist) saveTabLayout(panel.closest(".tab-panel"));
    }
    function setPanelHeight(panel, height, persist = true) {
      const normalized = Math.max(180, Math.min(1600, Math.round(Number(height) || panel.getBoundingClientRect().height || 260)));
      panel.classList.add("user-sized-panel");
      panel.style.setProperty("--layout-height", `${normalized}px`);
      scheduleLayoutMasonry(panel.closest(".dashboard-layout-grid"));
      if (persist) saveTabLayout(panel.closest(".tab-panel"));
    }
    function swapLayoutPanels(first, second) {
      if (!first || !second || first === second) return;
      const firstOrder = Number(first.dataset.layoutOrder || first.style.order || 0);
      const secondOrder = Number(second.dataset.layoutOrder || second.style.order || 0);
      first.dataset.layoutOrder = String(secondOrder);
      second.dataset.layoutOrder = String(firstOrder);
      first.style.order = String(secondOrder);
      second.style.order = String(firstOrder);
      saveTabLayout(first.closest(".tab-panel"));
    }
    function ensureLayoutPanelControls(panel) {
      if (panel.querySelector(":scope > .layout-box-tools")) return;
      const tools = document.createElement("div");
      tools.className = "layout-box-tools";
      tools.setAttribute("aria-label", "Controles da caixa");
      tools.innerHTML = `<button class="layout-drag-handle" type="button" draggable="true" title="Arrastar caixa" aria-label="Arrastar caixa">M</button>
        <button type="button" data-layout-span-step="-1" title="Diminuir largura" aria-label="Diminuir largura">L-</button>
        <button type="button" data-layout-span-step="1" title="Aumentar largura" aria-label="Aumentar largura">L+</button>
        <button type="button" data-layout-height-step="-60" title="Diminuir altura" aria-label="Diminuir altura">A-</button>
        <button type="button" data-layout-height-step="60" title="Aumentar altura" aria-label="Aumentar altura">A+</button>`;
      const resize = document.createElement("button");
      resize.type = "button";
      resize.className = "layout-resize-handle";
      resize.setAttribute("aria-label", "Redimensionar caixa");
      resize.title = "Arraste para redimensionar";
      panel.append(tools, resize);
      const dragHandle = tools.querySelector(".layout-drag-handle");
      dragHandle.addEventListener("dragstart", event => {
        if (!layoutEditMode) return event.preventDefault();
        draggedLayoutPanel = panel;
        panel.classList.add("layout-is-dragging");
        event.dataTransfer.effectAllowed = "move";
        event.dataTransfer.setData("text/plain", panel.dataset.layoutId || "painel");
      });
      dragHandle.addEventListener("dragend", () => {
        panel.classList.remove("layout-is-dragging");
        panel.closest(".dashboard-layout-grid")?.querySelectorAll(".layout-drag-over").forEach(item => item.classList.remove("layout-drag-over"));
        draggedLayoutPanel = null;
      });
      panel.addEventListener("dragover", event => {
        if (!layoutEditMode || !draggedLayoutPanel || draggedLayoutPanel === panel) return;
        event.preventDefault();
        event.dataTransfer.dropEffect = "move";
        panel.classList.add("layout-drag-over");
      });
      panel.addEventListener("dragleave", () => panel.classList.remove("layout-drag-over"));
      panel.addEventListener("drop", event => {
        if (!layoutEditMode || !draggedLayoutPanel) return;
        event.preventDefault();
        panel.classList.remove("layout-drag-over");
        swapLayoutPanels(draggedLayoutPanel, panel);
      });
      tools.querySelectorAll("[data-layout-span-step]").forEach(button => {
        button.addEventListener("click", event => {
          event.preventDefault();
          event.stopPropagation();
          setPanelSpan(panel, Number(panel.dataset.layoutSpan || 6) + Number(button.dataset.layoutSpanStep || 0));
        });
      });
      tools.querySelectorAll("[data-layout-height-step]").forEach(button => {
        button.addEventListener("click", event => {
          event.preventDefault();
          event.stopPropagation();
          setPanelHeight(panel, panel.getBoundingClientRect().height + Number(button.dataset.layoutHeightStep || 0));
        });
      });
      resize.addEventListener("pointerdown", event => {
        if (!layoutEditMode) return;
        event.preventDefault();
        event.stopPropagation();
        resize.setPointerCapture?.(event.pointerId);
        const grid = panel.closest(".dashboard-layout-grid");
        const gridRect = grid?.getBoundingClientRect();
        const panelRect = panel.getBoundingClientRect();
        const startX = event.clientX;
        const startY = event.clientY;
        const startWidth = panelRect.width;
        const startHeight = panelRect.height;
        const move = moveEvent => {
          const columnWidth = Math.max(1, (gridRect?.width || startWidth) / 12);
          setPanelSpan(panel, (startWidth + moveEvent.clientX - startX) / columnWidth, false);
          setPanelHeight(panel, startHeight + moveEvent.clientY - startY, false);
        };
        const stop = () => {
          window.removeEventListener("pointermove", move);
          window.removeEventListener("pointerup", stop);
          window.removeEventListener("pointercancel", stop);
          saveTabLayout(panel.closest(".tab-panel"));
        };
        window.addEventListener("pointermove", move);
        window.addEventListener("pointerup", stop, { once: true });
        window.addEventListener("pointercancel", stop, { once: true });
      });
    }
    function prepareTabLayout(tabPanel) {
      if (!tabPanel || !tabPanel.classList.contains("active")) return;
      let grid = tabPanel.querySelector(":scope > .dashboard-layout-grid");
      if (grid) {
        grid.querySelectorAll(":scope > .panel").forEach(ensureLayoutPanelControls);
        scheduleLayoutMasonry(grid);
        configureEditableTexts(tabPanel);
        return;
      }
      const panels = Array.from(tabPanel.querySelectorAll(".panel")).filter(panel => isLayoutPanel(panel) && !panel.closest(".chart-expand-modal, [data-churn-risk-modal]"));
      if (!panels.length) {
        configureEditableTexts(tabPanel);
        return;
      }
      const tabKey = layoutTabKey(tabPanel);
      const tabRect = tabPanel.getBoundingClientRect();
      const tabWidth = Math.max(tabRect.width, 1);
      const sourceShells = [...new Set(panels.map(panel => topLevelLayoutShell(panel, tabPanel)).filter(Boolean))];
      const firstShell = sourceShells[0] || panels[0];
      const stored = storedLayoutForTab(tabKey).items || {};
      const duplicateCounts = new Map();
      const panelState = panels.map((panel, index) => {
        const rect = panel.getBoundingClientRect();
        if (panel.classList.contains("composition-panel") && panel.closest(".active-overview-trio")) panel.classList.add("layout-active-composition");
        if (panel.classList.contains("composition-panel") && panel.closest(".active-demographic-trio")) panel.classList.add("layout-active-age-composition");
        const title = panel.querySelector("h2, .composition-title")?.textContent?.trim() || Array.from(panel.classList).find(name => name.startsWith("chart-")) || `grafico-${index + 1}`;
        const base = panel.classList.contains("chart-active-units") ? `${editableSlug(title)}-resumo-rede` : editableSlug(title);
        const occurrence = duplicateCounts.get(base) || 0;
        duplicateCounts.set(base, occurrence + 1);
        const id = `${tabKey}.${base}.${occurrence}`;
        const defaultSpan = panel.classList.contains("chart-active-units") ? 12 : defaultLayoutSpan(panel, rect, tabWidth);
        return { panel, id, index, defaultSpan };
      });
      grid = document.createElement("div");
      grid.className = "dashboard-layout-grid";
      grid.dataset.layoutTab = tabKey;
      tabPanel.insertBefore(grid, firstShell);
      panelState.forEach(({ panel, id, index, defaultSpan }) => {
        const saved = stored[id] || {};
        const span = Number(saved.span || defaultSpan);
        const order = Number.isFinite(Number(saved.order)) ? Number(saved.order) : index;
        panel.dataset.layoutId = id;
        panel.dataset.layoutSpan = String(span);
        panel.dataset.layoutOrder = String(order);
        panel.style.gridColumn = `span ${Math.max(3, Math.min(12, span))}`;
        panel.style.order = String(order);
        if (saved.height) {
          panel.classList.add("user-sized-panel");
          panel.style.setProperty("--layout-height", `${Math.max(180, Number(saved.height))}px`);
        }
        grid.appendChild(panel);
        ensureLayoutPanelControls(panel);
      });
      scheduleLayoutMasonry(grid);
      sourceShells.forEach(shell => {
        if (shell === grid || shell.parentElement === grid) return;
        if (!shell.querySelector(".panel") && !shell.textContent.trim()) {
          shell.classList.add("layout-source-shell");
          shell.hidden = true;
        }
      });
      configureEditableTexts(tabPanel);
    }
    function textOverridesForTab(tabKey) {
      return readStoredJson(`${textStoragePrefix}.${tabKey}`, {});
    }
    function repairLegacyEditableText(value) {
      return String(value ?? "").replace(/M\u00c3\u00a9dia de dias Ativos/g, "M\u00e9dia de dias Ativos");
    }
    function saveTextOverride(element, override) {
      const tabPanel = element.closest(".tab-panel");
      if (!tabPanel || !element.dataset.editId) return;
      const tabKey = layoutTabKey(tabPanel);
      const overrides = textOverridesForTab(tabKey);
      overrides[element.dataset.editId] = override;
      writeStoredJson(`${textStoragePrefix}.${tabKey}`, overrides);
    }
    function setSelectedEditableText(element) {
      selectedEditableText = element || null;
      const hideButton = document.getElementById("layoutTextHide");
      if (hideButton) hideButton.disabled = !layoutEditMode || !selectedEditableText;
    }
    function editableTextCandidates(tabPanel) {
      const selector = [
        ".panel h2",
        ".panel > .panel-subtitle",
        ".panel .composition-copy > p",
        ".panel > .composition-footer",
        ".panel .chart-callout",
        ".card .card-label",
        ".card > small",
        ".card .card-meta",
        ".card .card-subtitle",
        ".summary-strip-head strong",
        ".summary-strip-head small",
      ].join(",");
      return Array.from(tabPanel.querySelectorAll(selector)).filter(element => !element.closest(".layout-box-tools, .chart-expand-modal, [data-churn-risk-modal]"));
    }
    function configureEditableTexts(tabPanel) {
      if (!tabPanel) return;
      const tabKey = layoutTabKey(tabPanel);
      const overrides = textOverridesForTab(tabKey);
      editableTextCandidates(tabPanel).forEach((element, index) => {
        if (!element.dataset.editId) {
          const original = element.textContent.trim();
          element.dataset.originalText = original;
          element.dataset.editId = `${tabKey}.text.${index}.${editableSlug(original)}`;
        }
        const override = overrides[element.dataset.editId];
        if (override) {
          element.textContent = override.hidden ? "" : repairLegacyEditableText(override.text || "");
          element.classList.toggle("user-text-hidden", Boolean(override.hidden));
        }
        element.classList.add("text-editable");
        if (layoutEditMode) {
          element.setAttribute("contenteditable", "plaintext-only");
          element.setAttribute("spellcheck", "true");
          element.setAttribute("tabindex", "0");
          element.title = "Clique para editar este texto";
        } else {
          element.removeAttribute("contenteditable");
          element.removeAttribute("spellcheck");
          element.removeAttribute("tabindex");
          if (element.title === "Clique para editar este texto") element.removeAttribute("title");
        }
        if (element.dataset.editBound === "true") return;
        element.dataset.editBound = "true";
        element.addEventListener("click", event => {
          if (!layoutEditMode) return;
          event.stopPropagation();
          if (element.classList.contains("user-text-hidden")) {
            element.classList.remove("user-text-hidden");
            element.textContent = "";
          }
          element.focus();
          setSelectedEditableText(element);
        });
        element.addEventListener("focus", () => {
          if (layoutEditMode) setSelectedEditableText(element);
        });
        element.addEventListener("blur", () => {
          if (!layoutEditMode) return;
          const text = element.textContent.trim();
          const hidden = !text;
          element.classList.toggle("user-text-hidden", hidden);
          saveTextOverride(element, { text, hidden });
          window.setTimeout(() => {
            if (selectedEditableText === element && document.activeElement !== element) setSelectedEditableText(null);
          }, 0);
        });
        element.addEventListener("keydown", event => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            element.blur();
          }
          if (event.key === "Escape") {
            event.preventDefault();
            element.blur();
          }
        });
      });
    }
    function activateEditorForTab(tabPanel) {
      if (!tabPanel) return;
      const tabKey = layoutTabKey(tabPanel);
      if (layoutEditMode || hasStoredLayoutForTab(tabKey)) prepareTabLayout(tabPanel);
      configureEditableTexts(tabPanel);
    }
    function updateLayoutEditorUi() {
      document.body.classList.toggle("layout-edit-mode", layoutEditMode);
      const toggle = document.getElementById("layoutEditToggle");
      const hide = document.getElementById("layoutTextHide");
      const reset = document.getElementById("layoutReset");
      const hint = document.getElementById("layoutEditorHint");
      if (toggle) {
        toggle.setAttribute("aria-pressed", layoutEditMode ? "true" : "false");
        toggle.textContent = layoutEditMode ? "Concluir edição" : "Editar página";
      }
      if (hide) {
        hide.hidden = !layoutEditMode;
        hide.disabled = !selectedEditableText;
      }
      if (reset) reset.hidden = !layoutEditMode;
      if (hint) hint.hidden = !layoutEditMode;
      const activePanel = document.querySelector(".tab-panel.active");
      if (activePanel) configureEditableTexts(activePanel);
    }
    function setupLayoutEditor() {
      const toggle = document.getElementById("layoutEditToggle");
      const hide = document.getElementById("layoutTextHide");
      const reset = document.getElementById("layoutReset");
      if (!toggle || toggle.dataset.bound === "true") return;
      toggle.dataset.bound = "true";
      toggle.addEventListener("click", () => {
        layoutEditMode = !layoutEditMode;
        if (!layoutEditMode) {
          selectedEditableText?.blur?.();
          setSelectedEditableText(null);
        }
        activateEditorForTab(document.querySelector(".tab-panel.active"));
        updateLayoutEditorUi();
      });
      hide?.addEventListener("pointerdown", event => event.preventDefault());
      hide?.addEventListener("click", () => {
        if (!layoutEditMode || !selectedEditableText) return;
        const element = selectedEditableText;
        element.textContent = "";
        element.classList.add("user-text-hidden");
        saveTextOverride(element, { text: "", hidden: true });
        element.blur();
        setSelectedEditableText(null);
      });
      reset?.addEventListener("click", () => {
        const tabKey = activeTabKey();
        if (!window.confirm("Restaurar o layout e os textos originais desta aba?")) return;
        try {
          localStorage.removeItem(`${layoutStoragePrefix}.${tabKey}`);
          localStorage.removeItem(`${textStoragePrefix}.${tabKey}`);
        } catch (error) { /* armazenamento opcional */ }
        setSelectedEditableText(null);
        replaceActiveTab(tabKey, true);
        updateLayoutEditorUi();
      });
      window.addEventListener("resize", () => scheduleLayoutMasonry(document.querySelector(".tab-panel.active > .dashboard-layout-grid")));
      updateLayoutEditorUi();
    }
    function replaceActiveTab(tabKey, activate = activeTabKey() === tabKey) {
      const index = Math.max(0, tabs.findIndex(([key]) => key === tabKey));
      const current = document.getElementById(`tab-${tabKey}`);
      if (!current) return render();
      const shouldActivate = activate || document.querySelector(`[data-tab="${tabKey}"]`)?.classList.contains("active");
      const wrapper = document.createElement("div");
      wrapper.innerHTML = tabPanelHtml(tabKey, index, shouldActivate).trim();
      const nextPanel = wrapper.firstElementChild;
      current.replaceWith(nextPanel);
      refreshDisplayRows(nextPanel);
      bindActiveGoalSort(nextPanel);
      bindCannibalizationPeriods(nextPanel);
      bindFinancialPeriods(nextPanel);
      bindFinancialRevenueFilters(nextPanel);
      bindLineSeriesSelectors(nextPanel);
      bindChurnRiskInteractions(nextPanel);
      decorateExpandablePanels(nextPanel);
      if (shouldActivate) window.requestAnimationFrame(() => activateEditorForTab(nextPanel));
      if (tabKey === "isaias") setupIsaiasChat();
    }
    function render() {
      document.getElementById("sourceText").textContent = data.sourceFile || "Aguardando Supabase";
      document.getElementById("tabs").innerHTML = tabs.map(([key, label], index) => `<button class="${index === 0 ? "active" : ""}" data-tab="${key}">${label}</button>`).join("");
      document.getElementById("tabPanels").innerHTML = tabs.map(([key], index) => tabPanelHtml(key, index, index === 0)).join("");
      document.getElementById("medalBoard").innerHTML = "";
      refreshDisplayRows();
      bindTabButtons();
      bindActiveGoalSort();
      bindCannibalizationPeriods();
      bindFinancialPeriods();
      bindFinancialRevenueFilters();
      bindLineSeriesSelectors();
      bindChurnRiskInteractions();
      decorateExpandablePanels();
      window.requestAnimationFrame(() => activateEditorForTab(document.querySelector(".tab-panel.active")));
      setupIsaiasChat();
    }
    function setupUpload() {
      const button = document.getElementById("analyzeCsvButton");
      const applyButton = document.getElementById("applyFiltersButton");
      const status = document.getElementById("csvUploadStatus");
      const setStatus = (message, kind = "") => {
        status.textContent = message;
        status.className = `header-upload-status ${kind}`.trim();
      };
      let filterTimer = null;
      const buildRequestPayload = (tabKey = activeTabKey()) => ({
        activeTab: tabKey,
        ...collectFilters(),
      });
      const mergeTabPayload = (payload, activate = activeTabKey() === payload.tabKey) => {
        data = {
          ...data,
          filters: payload.filters || data.filters,
          filterOptions: payload.filterOptions || data.filterOptions,
          sourceFile: payload.sourceFile || data.sourceFile,
          sourcePath: payload.sourcePath || data.sourcePath,
          validation: payload.validation || data.validation,
          medalBoard: payload.medalBoard?.length ? payload.medalBoard : data.medalBoard,
          tabs: { ...(data.tabs || {}), [payload.tabKey]: { ...(payload.tab || {}), loading: false } },
        };
        loadedTabKeys.add(payload.tabKey);
        document.getElementById("sourceText").textContent = data.sourceFile || "Aguardando Supabase";
        replaceActiveTab(payload.tabKey, activate);
        document.getElementById("medalBoard").innerHTML = "";
      };
      const showTabLoadError = (tabKey, message) => {
        const current = data.tabs?.[tabKey] || { cards: [], charts: [] };
        data.tabs = {
          ...(data.tabs || {}),
          [tabKey]: { ...current, loading: false, loadError: message || "Falha de conexão com o servidor local." },
        };
        replaceActiveTab(tabKey, activeTabKey() === tabKey);
      };
      const fetchTabData = async (tabKey, force = false, background = false) => {
        if (tabLoadPromises.has(tabKey)) return tabLoadPromises.get(tabKey);
        const request = (async () => {
          const requestPayload = {
            ...buildRequestPayload(tabKey),
            force: force ? "true" : "false",
          };
          if (!background) {
            button.disabled = true;
            if (applyButton) applyButton.disabled = true;
            setStatus(`Carregando ${tabKey}...`, "ok");
          }
          const controller = new AbortController();
          const requestTimeout = window.setTimeout(() => controller.abort(), 90000);
          try {
            const response = await fetch("/api/render-tab", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(requestPayload),
              signal: controller.signal,
            });
            const contentType = response.headers.get("content-type") || "";
            if (!response.ok) {
              const payload = contentType.includes("application/json") ? await response.json() : { error: await response.text() };
              throw new Error(payload.error || `Não foi possível carregar ${tabKey}.`);
            }
            const payload = await response.json();
            mergeTabPayload(payload, activeTabKey() === tabKey);
            if (!background) setStatus("Supabase atualizado", "ok");
            return payload;
          } catch (error) {
            if (!background) {
              const message = error.name === "AbortError"
                ? `Tempo excedido ao carregar ${tabKey}. Tente sincronizar novamente.`
                : (error.message || "Erro ao atualizar");
              setStatus(message, "error");
              showTabLoadError(tabKey, message);
            }
            throw error;
          } finally {
            window.clearTimeout(requestTimeout);
            tabLoadPromises.delete(tabKey);
            if (!background) {
              button.disabled = false;
              if (applyButton) applyButton.disabled = false;
            }
          }
        })();
        tabLoadPromises.set(tabKey, request);
        return request;
      };
      const waitForIdle = () => new Promise(resolve => {
        if ("requestIdleCallback" in window) window.requestIdleCallback(() => resolve(), { timeout: 1200 });
        else window.setTimeout(resolve, 250);
      });
      const prefetchRemainingTabs = async () => {
        const queue = ["vendas", "cancelamentos", "financeiro", "frequencia", "isaias"];
        let failed = 0;
        for (const tabKey of queue) {
          if (loadedTabKeys.has(tabKey)) continue;
          await waitForIdle();
          try {
            await fetchTabData(tabKey, false, true);
          } catch (error) {
            failed += 1;
            console.warn(`Falha ao pré-carregar ${tabKey}:`, error);
          }
        }
        setStatus(failed ? `Conectado · ${failed} abas pendentes` : "Conectado", failed ? "error" : "ok");
      };
      requestDashboardTab = fetchTabData;
      document.getElementById("tabPanels")?.addEventListener("click", event => {
        const retry = event.target.closest("[data-retry-tab]");
        if (!retry) return;
        const tabKey = retry.dataset.retryTab;
        const current = data.tabs?.[tabKey] || { cards: [], charts: [] };
        data.tabs = { ...(data.tabs || {}), [tabKey]: { ...current, loading: true, loadError: "" } };
        replaceActiveTab(tabKey, true);
        fetchTabData(tabKey, true, false).catch(error => console.warn(`Nova tentativa de ${tabKey} falhou:`, error));
      });
      const syncAll = async () => {
        loadedTabKeys.clear();
        tabLoadPromises.clear();
        Object.keys(data.tabs || {}).forEach(key => {
          data.tabs[key] = { ...(data.tabs[key] || {}), loading: true };
        });
        render();
        try {
          await fetchTabData("ativos", true, false);
          setStatus("Ativos prontos · carregando demais abas", "ok");
          prefetchRemainingTabs();
        } catch (error) {
          setStatus(error.message || "Erro ao sincronizar", "error");
        }
      };
      const submitUpdate = async () => {
        const currentTab = activeTabKey();
        loadedTabKeys.clear();
        try {
          await fetchTabData(currentTab, false, false);
          prefetchRemainingTabs();
        } catch (error) {
          setStatus(error.message || "Erro ao atualizar", "error");
        }
      };
      button.addEventListener("click", syncAll);
      const scheduleFilterUpdate = () => {
        window.clearTimeout(filterTimer);
        filterTimer = window.setTimeout(() => submitUpdate(), 450);
      };
      scheduleDashboardFilterUpdate = scheduleFilterUpdate;
      const clearFilters = () => {
        setPeriodValues("", "");
        setFilterValues("unit", []);
        setFilterValues("age", []);
        setFilterValues("gender", []);
        scheduleFilterUpdate();
      };
      applyButton?.addEventListener("click", clearFilters);
      document.querySelectorAll("[data-filter-open]").forEach(button => {
        button.addEventListener("click", () => openFilterPopup(button.dataset.filterOpen));
      });
      document.getElementById("filterPopupApply")?.addEventListener("click", applyFilterPopup);
      document.getElementById("filterPopupClear")?.addEventListener("click", clearFilterPopup);
      document.getElementById("filterPopupClose")?.addEventListener("click", closeFilterPopup);
      document.getElementById("filterPopup")?.addEventListener("click", event => {
        if (event.target?.id === "filterPopup") closeFilterPopup();
      });
      document.addEventListener("keydown", event => {
        if (event.key === "Escape") closeFilterPopup();
      });
      const exportButton = document.getElementById("exportXlsxButton");
      exportButton?.addEventListener("click", async () => {
        const requestPayload = buildRequestPayload(activeTabKey());
        exportButton.disabled = true;
        setStatus("Gerando XLSX por unidade...", "ok");
        try {
          const response = await fetch("/api/export-xlsx", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestPayload),
          });
          const contentType = response.headers.get("content-type") || "";
          if (!response.ok) {
            const payload = contentType.includes("application/json") ? await response.json() : { error: await response.text() };
            throw new Error(payload.error || "NÃ£o foi possÃ­vel exportar o XLSX.");
          }
          const blob = await response.blob();
          const disposition = response.headers.get("content-disposition") || "";
          const match = disposition.match(/filename="?([^"]+)"?/i);
          const filename = match?.[1] || "dashboard_biofisic_por_unidade.xlsx";
          const url = URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          link.remove();
          URL.revokeObjectURL(url);
          setStatus("XLSX gerado", "ok");
        } catch (error) {
          setStatus(error.message || "Erro ao exportar XLSX", "error");
        } finally {
          exportButton.disabled = false;
        }
      });
      if (data.progressive) {
        const hasActiveSnapshot = loadedTabKeys.has("ativos");
        if (hasActiveSnapshot) {
          setStatus("Ativos disponíveis · atualizando em segundo plano", "ok");
        }
        fetchTabData("ativos", false, hasActiveSnapshot)
          .then(() => {
            setStatus("Ativos prontos · carregando demais abas", "ok");
            prefetchRemainingTabs();
          })
          .catch(error => setStatus(error.message || "Erro ao carregar Ativos", "error"));
      } else if (String(data.sourcePath || "").startsWith("supabase://")) {
        setStatus("Conectado", "ok");
      } else {
        syncAll();
      }
    }
    setupThemeToggle();
    setupChartExpansion();
    setupLayoutEditor();
    render();
    setupFilters();
    setupUpload();
  </script>
</body>
</html>"""
    return template.replace("__DATA__", data)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    HTML_OUT.write_text(build_html(payload), encoding="utf-8")
    print(HTML_OUT)


if __name__ == "__main__":
    main()
