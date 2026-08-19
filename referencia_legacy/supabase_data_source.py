from __future__ import annotations

import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest
from zoneinfo import ZoneInfo

import pandas as pd


PROJECT_REF = "rxwkwmqnbvtzewplbujp"
DEFAULT_SUPABASE_URL = f"https://{PROJECT_REF}.supabase.co"


@dataclass(frozen=True)
class TableSpec:
    role: str
    table: str
    order: str
    select: str = "*"
    active_history_window: bool = False
    row_limit: int | None = None


TABLE_SPECS = (
    TableSpec("active", "Ativos_LTV", "idMember.asc"),
    TableSpec(
        "active_history",
        "HISTORICO ATIVOS",
        "dia.desc,idFilial.asc",
        select="dia,idFilial,quantidade,Filial",
        active_history_window=True,
    ),
    TableSpec(
        "billing",
        "FATURAMENTO",
        "id_recibo.asc.nullslast,idMember.asc",
        select="idMember,dataVenda,item_vendido,id_unidade,valor_real,id_recibo,observa",
    ),
    # dataVenda is the authoritative sales date. Ordering by it first keeps
    # offset pagination stable while new sales are appended.
    TableSpec("sales", "VENDAS", "dataVenda.asc,id_venda.asc.nullslast,idMember.asc"),
    TableSpec(
        "sales_realtime",
        "CONTRATO VENDA TEMPO REAL",
        "dataSale.desc,idSale.desc.nullslast",
        select="dataSale,idSale,idBranch,item,observation,saleValue,itemValue,nomeColaborador",
        row_limit=30,
    ),
    TableSpec("cancellations", "CANCELAMENTO", "idSale.asc.nullslast,idMember.asc"),
    TableSpec(
        "non_renewed",
        "N\u00c3O RENOVADOS",
        "DataFim.asc.nullslast,id.asc",
        select="idCliente,idFilial,NomeFilial,Status,ContratoAnterior,ContratoAtivo,DataInicio,DataFim,id",
    ),
    # COBRANÇA has no single row identifier. Use every installment-defining
    # field as a tie-breaker so offset pagination cannot skip/swap rows that
    # belong to the same member at a page boundary.
    TableSpec(
        "charges",
        "COBRANÇA",
        "idMember.asc,dataVencimento.asc.nullslast,id_venda.asc.nullslast,"
        "status.asc,valorCompet.asc.nullslast,diasInad.asc.nullslast,"
        "dataPagamento.asc.nullslast,tipo_pagamento.asc.nullslast",
    ),
    TableSpec("access_unit", "controle_acesso", "id.asc"),
    TableSpec("access_wellhub", "controle_acesso_wellhub", "id.asc"),
    TableSpec("access_totalpass", "controle_acesso_totalpass", "id.asc"),
)


def load_local_env(project_dir: Path) -> None:
    """Load local configuration without overwriting process environment values."""
    for env_path in (project_dir / ".env", project_dir / "supabase.env"):
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key.startswith("SUPABASE_") and value and not os.environ.get(key):
                os.environ[key] = value


@dataclass(frozen=True)
class SupabaseConfig:
    url: str
    api_key: str
    page_size: int = 1000
    timeout_seconds: int = 60

    @classmethod
    def from_environment(cls, project_dir: Path) -> "SupabaseConfig":
        load_local_env(project_dir)
        url = os.environ.get("SUPABASE_URL", DEFAULT_SUPABASE_URL).rstrip("/")
        api_key = (
            os.environ.get("SUPABASE_SECRET_KEY")
            or os.environ.get("SUPABASE_PUBLISHABLE_KEY")
            or os.environ.get("SUPABASE_ANON_KEY")
            or ""
        ).strip()
        if not api_key:
            raise RuntimeError(
                "Configure SUPABASE_PUBLISHABLE_KEY ou SUPABASE_SECRET_KEY no arquivo .env. "
                "Nunca coloque uma secret/service_role key dentro do HTML."
            )
        try:
            page_size = int(os.environ.get("SUPABASE_PAGE_SIZE", "1000"))
        except ValueError:
            page_size = 1000
        page_size = max(100, min(page_size, 5000))
        return cls(url=url, api_key=api_key, page_size=page_size)


class SupabaseTableLoader:
    def __init__(self, config: SupabaseConfig):
        self.config = config

    def fetch_table(
        self,
        spec: TableSpec,
        extra_filters: list[tuple[str, str]] | None = None,
    ) -> pd.DataFrame:
        def fetch_page(offset: int, include_count: bool = False) -> tuple[list[dict], int | None]:
            page_limit = spec.row_limit or self.config.page_size
            query_items = [
                ("select", spec.select),
                ("order", spec.order),
                ("limit", str(page_limit)),
                ("offset", str(offset)),
            ]
            if spec.active_history_window:
                today = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
                current_month_start = today.replace(day=1)
                previous_month_end = current_month_start - timedelta(days=1)
                tomorrow = today + timedelta(days=1)
                query_items.extend(
                    [
                        ("dia", f"gte.{previous_month_end:%Y-%m-%d} 00:00:00"),
                        ("dia", f"lt.{tomorrow:%Y-%m-%d} 00:00:00"),
                    ]
                )
            query_items.extend(extra_filters or [])
            query = urlparse.urlencode(query_items)
            table_path = urlparse.quote(spec.table, safe="")
            request = urlrequest.Request(
                f"{self.config.url}/rest/v1/{table_path}?{query}",
                headers={
                    "Accept": "application/json",
                    "apikey": self.config.api_key,
                    "Authorization": f"Bearer {self.config.api_key}",
                    **({"Prefer": "count=exact"} if include_count else {}),
                },
                method="GET",
            )
            try:
                with urlrequest.urlopen(request, timeout=self.config.timeout_seconds) as response:
                    page = json.loads(response.read().decode("utf-8"))
                    content_range = response.headers.get("Content-Range", "")
            except urlerror.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:800]
                raise RuntimeError(
                    f"Supabase recusou a leitura de {spec.table} (HTTP {exc.code}): {detail}"
                ) from exc
            except urlerror.URLError as exc:
                raise RuntimeError(f"Falha de rede ao ler {spec.table}: {exc.reason}") from exc
            if not isinstance(page, list):
                raise RuntimeError(f"Resposta inesperada ao ler {spec.table}.")
            total = None
            if "/" in content_range:
                total_text = content_range.rsplit("/", 1)[1]
                if total_text.isdigit():
                    total = int(total_text)
            return page, total

        first_page, total = fetch_page(0, include_count=True)
        rows: list[dict] = list(first_page)
        if spec.row_limit is not None:
            return pd.DataFrame.from_records(rows[: spec.row_limit])
        if not first_page or (total is not None and total <= len(first_page)):
            return pd.DataFrame.from_records(rows)

        page_step = len(first_page)
        if total is not None:
            if total > 2_000_000:
                raise RuntimeError(f"Limite de segurança excedido ao ler {spec.table}.")
            offsets = list(range(page_step, total, page_step))
            pages: dict[int, list[dict]] = {}
            with ThreadPoolExecutor(max_workers=min(4, len(offsets)), thread_name_prefix=f"{spec.role}-page") as executor:
                pending = {executor.submit(fetch_page, offset): offset for offset in offsets}
                for future in as_completed(pending):
                    offset = pending[future]
                    pages[offset] = future.result()[0]
            for offset in offsets:
                rows.extend(pages.get(offset, []))
            return pd.DataFrame.from_records(rows)

        offset = page_step
        while len(rows) <= 2_000_000:
            page, _ = fetch_page(offset)
            rows.extend(page)
            if len(page) < page_step:
                break
            offset += len(page)
        else:
            raise RuntimeError(f"Limite de segurança excedido ao ler {spec.table}.")
        return pd.DataFrame.from_records(rows)

    def fetch_roles(
        self,
        roles: set[str] | list[str] | tuple[str, ...],
        filters_by_role: dict[str, list[tuple[str, str]]] | None = None,
    ) -> tuple[dict[str, pd.DataFrame], list[dict]]:
        """Fetch only the source roles required by the requested dashboard stage."""
        selected = [spec for spec in TABLE_SPECS if spec.role in set(roles)]
        filters_by_role = filters_by_role or {}
        frames: dict[str, pd.DataFrame] = {}
        errors: list[str] = []
        lock = threading.Lock()
        with ThreadPoolExecutor(max_workers=min(4, max(len(selected), 1)), thread_name_prefix="supabase") as executor:
            pending = {
                executor.submit(self.fetch_table, spec, filters_by_role.get(spec.role)): spec
                for spec in selected
            }
            for future in as_completed(pending):
                spec = pending[future]
                try:
                    frame = future.result()
                    with lock:
                        frames[spec.role] = frame
                except Exception as exc:
                    errors.append(str(exc))
        if errors:
            raise RuntimeError(" | ".join(errors))

        validation = [
            {
                "arquivo": spec.table,
                "papel": spec.role,
                "status": "ok",
                "colunas": int(len(frames[spec.role].columns)),
                "linhas": int(len(frames[spec.role].index)),
            }
            for spec in selected
        ]
        return frames, validation

    def fetch_all(self) -> tuple[dict[str, pd.DataFrame], list[dict]]:
        return self.fetch_roles({spec.role for spec in TABLE_SPECS})


def supabase_source_label() -> str:
    return f"Supabase · sincronizado em {datetime.now():%d/%m/%Y %H:%M}"
