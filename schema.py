import strawberry
import datetime
import sqlite3
import os
import base64
from typing import List, Optional, Any, Tuple

DATABASE_FILE = 'database.db'
DEFAULT_PAGE_SIZE = 20 # Default number of items per page

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

# --- Cursor Encoding/Decoding ---
def encode_cursor(timestamp: int, id_visita: int) -> str:
    """Encodes timestamp and id into a base64 cursor."""
    return base64.b64encode(f"{timestamp}:{id_visita}".encode('utf-8')).decode('utf-8')

def decode_cursor(cursor: str) -> Tuple[int, int]:
    """Decodes a base64 cursor into timestamp and id."""
    try:
        decoded_bytes = base64.b64decode(cursor)
        decoded_str = decoded_bytes.decode('utf-8')
        timestamp_str, id_str = decoded_str.split(':')
        return int(timestamp_str), int(id_str)
    except (ValueError, TypeError, base64.binascii.Error):
        raise ValueError("Invalid cursor format.")

# --- Filter Clause Builder ---
def build_where_clause(filter: Any) -> tuple[str, list]:
    """Builds the SQL WHERE clause and parameters from the VisitaFilterInput."""
    local_params = [] # Use local params list for this specific build instance

    # Mapping (remains the same)
    field_mapping = {
        "nome_dominio": ("dd", "nome_dominio"), "caminho_pagina": ("dp", "caminho_pagina"),
        "url_completa": ("du", "url_completa"), "nome_navegador": ("dn", "nome_navegador"),
        "versao_navegador": ("dn", "versao_navegador"), "motor_renderizacao_navegador": ("dn", "motor_renderizacao"),
        "so_usuario_navegador": ("dn", "sistema_operacional_usuario"), "utm_source": ("dut", "utm_source"),
        "utm_medium": ("dut", "utm_medium"), "utm_campaign": ("dut", "utm_campaign"),
        "utm_term": ("dut", "utm_term"), "utm_content": ("dut", "utm_content"),
        "id_usuario_sessao": ("ds", "id_usuario_sessao"), "id_sessao_navegador": ("ds", "id_sessao_navegador"),
        "tipo_dispositivo": ("ddi", "tipo_dispositivo"), "marca_dispositivo": ("ddi", "marca_dispositivo"),
        "modelo_dispositivo": ("ddi", "modelo_dispositivo"), "resolucao_tela": ("ddi", "resolucao_tela"),
        "endereco_ip": ("dip", "endereco_ip"), "data_completa": ("dt", "data_completa"),
        "ano": ("dt", "ano"), "mes": ("dt", "mes"), "dia": ("dt", "dia"), "dia_semana": ("dt", "dia_semana"),
        "hora": ("dt", "hora"), "minuto": ("dt", "minuto"), "pais_geografia": ("dg", "pais"),
        "regiao_geografia": ("dg", "regiao"), "cidade_geografia": ("dg", "cidade"),
        "url_referencia": ("dr", "url_referencia"), "tipo_referencia": ("dr", "tipo_referencia"),
        "id_visita": ("fv", "id_visita"), "timestamp_visita": ("fv", "timestamp_visita")
    }

    # Condition builders (modify to use local_params)
    def build_string_condition(field_name, filter_input):
        alias, column = field_mapping[field_name]
        field_conditions = []
        if filter_input.equals is not None:
            field_conditions.append(f"{alias}.{column} = ?")
            local_params.append(filter_input.equals)
        # ... (other string conditions appending to local_params) ...
        if filter_input.notEquals is not None: field_conditions.append(f"{alias}.{column} != ?"); local_params.append(filter_input.notEquals)
        if filter_input.contains is not None: field_conditions.append(f"{alias}.{column} LIKE ?"); local_params.append(f"%{filter_input.contains}%")
        if filter_input.startsWith is not None: field_conditions.append(f"{alias}.{column} LIKE ?"); local_params.append(f"{filter_input.startsWith}%")
        if filter_input.endsWith is not None: field_conditions.append(f"{alias}.{column} LIKE ?"); local_params.append(f"%{filter_input.endsWith}")
        if filter_input.In is not None:
            placeholders = ', '.join('?' for _ in filter_input.In); field_conditions.append(f"{alias}.{column} IN ({placeholders})"); local_params.extend(filter_input.In)
        if filter_input.notIn is not None:
            placeholders = ', '.join('?' for _ in filter_input.notIn); field_conditions.append(f"{alias}.{column} NOT IN ({placeholders})"); local_params.extend(filter_input.notIn)
        return " AND ".join(field_conditions) if field_conditions else ""

    def build_int_condition(field_name, filter_input):
        alias, column = field_mapping[field_name]
        field_conditions = []
        if filter_input.equals is not None: field_conditions.append(f"{alias}.{column} = ?"); local_params.append(filter_input.equals)
        if filter_input.notEquals is not None: field_conditions.append(f"{alias}.{column} != ?"); local_params.append(filter_input.notEquals)
        if filter_input.greaterThan is not None: field_conditions.append(f"{alias}.{column} > ?"); local_params.append(filter_input.greaterThan)
        if filter_input.greaterThanOrEqual is not None: field_conditions.append(f"{alias}.{column} >= ?"); local_params.append(filter_input.greaterThanOrEqual)
        if filter_input.lessThan is not None: field_conditions.append(f"{alias}.{column} < ?"); local_params.append(filter_input.lessThan)
        if filter_input.lessThanOrEqual is not None: field_conditions.append(f"{alias}.{column} <= ?"); local_params.append(filter_input.lessThanOrEqual)
        if filter_input.In is not None:
            placeholders = ', '.join('?' for _ in filter_input.In); field_conditions.append(f"{alias}.{column} IN ({placeholders})"); local_params.extend(filter_input.In)
        if filter_input.notIn is not None:
            placeholders = ', '.join('?' for _ in filter_input.notIn); field_conditions.append(f"{alias}.{column} NOT IN ({placeholders})"); local_params.extend(filter_input.notIn)
        if filter_input.between is not None and len(filter_input.between) == 2:
            field_conditions.append(f"{alias}.{column} BETWEEN ? AND ?"); local_params.extend(filter_input.between)
        if filter_input.notBetween is not None and len(filter_input.notBetween) == 2:
            field_conditions.append(f"{alias}.{column} NOT BETWEEN ? AND ?"); local_params.extend(filter_input.notBetween)
        return " AND ".join(field_conditions) if field_conditions else ""

    def build_datetime_condition(field_name, filter_input):
        alias, column = field_mapping[field_name]
        field_conditions = []
        if filter_input.equals is not None: field_conditions.append(f"{alias}.{column} = ?"); local_params.append(int(filter_input.equals.timestamp()))
        if filter_input.notEquals is not None: field_conditions.append(f"{alias}.{column} != ?"); local_params.append(int(filter_input.notEquals.timestamp()))
        if filter_input.greaterThan is not None: field_conditions.append(f"{alias}.{column} > ?"); local_params.append(int(filter_input.greaterThan.timestamp()))
        if filter_input.greaterThanOrEqual is not None: field_conditions.append(f"{alias}.{column} >= ?"); local_params.append(int(filter_input.greaterThanOrEqual.timestamp()))
        if filter_input.lessThan is not None: field_conditions.append(f"{alias}.{column} < ?"); local_params.append(int(filter_input.lessThan.timestamp()))
        if filter_input.lessThanOrEqual is not None: field_conditions.append(f"{alias}.{column} <= ?"); local_params.append(int(filter_input.lessThanOrEqual.timestamp()))
        if filter_input.In is not None:
            timestamps = [int(dt.timestamp()) for dt in filter_input.In]; placeholders = ', '.join('?'*len(timestamps)); field_conditions.append(f"{alias}.{column} IN ({placeholders})"); local_params.extend(timestamps)
        if filter_input.notIn is not None:
            timestamps = [int(dt.timestamp()) for dt in filter_input.notIn]; placeholders = ', '.join('?'*len(timestamps)); field_conditions.append(f"{alias}.{column} NOT IN ({placeholders})"); local_params.extend(timestamps)
        if filter_input.between is not None and len(filter_input.between) == 2:
            timestamps = [int(dt.timestamp()) for dt in filter_input.between]; field_conditions.append(f"{alias}.{column} BETWEEN ? AND ?"); local_params.extend(timestamps)
        if filter_input.notBetween is not None and len(filter_input.notBetween) == 2:
            timestamps = [int(dt.timestamp()) for dt in filter_input.notBetween]; field_conditions.append(f"{alias}.{column} NOT BETWEEN ? AND ?"); local_params.extend(timestamps)
        return " AND ".join(field_conditions) if field_conditions else ""

    # Recursive helper (uses local_params via condition builders)
    def _build_clause_recursively(current_filter_obj):
        parts = []
        direct_field_strings = []
        for field_name, f_input_val in current_filter_obj.__dict__.items():
            if field_name in ["AND", "OR"] or f_input_val is None: continue
            cond_str = ""
            if isinstance(f_input_val, StringFilterInput): cond_str = build_string_condition(field_name, f_input_val)
            elif isinstance(f_input_val, IntFilterInput): cond_str = build_int_condition(field_name, f_input_val)
            elif isinstance(f_input_val, DateTimeFilterInput) and field_name == "timestamp_visita": cond_str = build_datetime_condition(field_name, f_input_val)
            if cond_str: direct_field_strings.append(f"({cond_str})" if " AND " in cond_str else cond_str)
        if direct_field_strings: parts.append(f"({' AND '.join(direct_field_strings)})" if len(direct_field_strings) > 1 else direct_field_strings[0])
        if current_filter_obj.AND:
            sub_clauses = [_build_clause_recursively(sub) for sub in current_filter_obj.AND if sub]
            if sub_clauses: parts.append(f"({' AND '.join(s for s in sub_clauses if s)})")
        if current_filter_obj.OR:
            sub_clauses = [_build_clause_recursively(sub) for sub in current_filter_obj.OR if sub]
            if sub_clauses: parts.append(f"({' OR '.join(s for s in sub_clauses if s)})")
        return " AND ".join(p for p in parts if p)

    # Main part
    if filter:
        final_clause_str = _build_clause_recursively(filter)
        if final_clause_str:
            where_clause = " WHERE " + final_clause_str
            return where_clause, local_params
    return "", local_params


# --- GraphQL Types ---

# Define generic InputFilter types
@strawberry.input
class StringFilterInput:
    equals: Optional[str] = None; notEquals: Optional[str] = None; contains: Optional[str] = None
    startsWith: Optional[str] = None; endsWith: Optional[str] = None
    In: Optional[List[str]] = None; notIn: Optional[List[str]] = None

@strawberry.input
class IntFilterInput:
    equals: Optional[int] = None; notEquals: Optional[int] = None
    greaterThan: Optional[int] = None; greaterThanOrEqual: Optional[int] = None
    lessThan: Optional[int] = None; lessThanOrEqual: Optional[int] = None
    In: Optional[List[int]] = None; notIn: Optional[List[int]] = None
    between: Optional[tuple[int, int]] = None; notBetween: Optional[tuple[int, int]] = None

@strawberry.input
class DateTimeFilterInput:
    equals: Optional[datetime.datetime] = None; notEquals: Optional[datetime.datetime] = None
    greaterThan: Optional[datetime.datetime] = None; greaterThanOrEqual: Optional[datetime.datetime] = None
    lessThan: Optional[datetime.datetime] = None; lessThanOrEqual: Optional[datetime.datetime] = None
    In: Optional[List[datetime.datetime]] = None; notIn: Optional[List[datetime.datetime]] = None
    between: Optional[tuple[datetime.datetime, datetime.datetime]] = None
    notBetween: Optional[tuple[datetime.datetime, datetime.datetime]] = None

# Define generic InputFilter types
@strawberry.input
class CursorModeInput:
    first: Optional[int] = None
    after: Optional[str] = None
    last: Optional[int] = None
    before: Optional[str] = None

@strawberry.input
class PaginationModeInput:
    limit: Optional[int] = None
    offset: Optional[int] = None

# Define the consolidated VisitaType
@strawberry.type
class VisitaType:
    id_visita: int; timestamp_visita: datetime.datetime; nome_dominio: str; caminho_pagina: str
    url_completa: str; nome_navegador: str; versao_navegador: Optional[str]
    motor_renderizacao_navegador: Optional[str]; so_usuario_navegador: str
    utm_source: Optional[str]; utm_medium: Optional[str]; utm_campaign: Optional[str]
    utm_term: Optional[str]; utm_content: Optional[str]; id_usuario_sessao: Optional[str]
    id_sessao_navegador: str; tipo_dispositivo: str; marca_dispositivo: Optional[str]
    modelo_dispositivo: Optional[str]; resolucao_tela: Optional[str]; endereco_ip: str
    data_completa: str; ano: int; mes: int; dia: int; dia_semana: int; hora: int; minuto: int
    pais_geografia: Optional[str]; regiao_geografia: Optional[str]; cidade_geografia: Optional[str]
    url_referencia: Optional[str]; tipo_referencia: Optional[str]

# --- Relay Connection Types ---
@strawberry.type
class PageInfo:
    has_next_page: bool; has_previous_page: bool
    start_cursor: Optional[str] = None; end_cursor: Optional[str] = None

@strawberry.type
class VisitaEdge:
    node: VisitaType; cursor: str

@strawberry.type
class VisitaConnection:
    edges: List[VisitaEdge]; pageInfo: PageInfo; totalCount: int

# Define the VisitaFilterInput
@strawberry.input
class VisitaFilterInput:
    id_visita: Optional[IntFilterInput] = None; timestamp_visita: Optional[DateTimeFilterInput] = None
    nome_dominio: Optional[StringFilterInput] = None; caminho_pagina: Optional[StringFilterInput] = None
    url_completa: Optional[StringFilterInput] = None; nome_navegador: Optional[StringFilterInput] = None
    versao_navegador: Optional[StringFilterInput] = None; motor_renderizacao_navegador: Optional[StringFilterInput] = None
    so_usuario_navegador: Optional[StringFilterInput] = None; utm_source: Optional[StringFilterInput] = None
    utm_medium: Optional[StringFilterInput] = None; utm_campaign: Optional[StringFilterInput] = None
    utm_term: Optional[StringFilterInput] = None; utm_content: Optional[StringFilterInput] = None
    id_usuario_sessao: Optional[StringFilterInput] = None; id_sessao_navegador: Optional[StringFilterInput] = None
    tipo_dispositivo: Optional[StringFilterInput] = None; marca_dispositivo: Optional[StringFilterInput] = None
    modelo_dispositivo: Optional[StringFilterInput] = None; resolucao_tela: Optional[StringFilterInput] = None
    endereco_ip: Optional[StringFilterInput] = None; data_completa: Optional[StringFilterInput] = None
    ano: Optional[IntFilterInput] = None; mes: Optional[IntFilterInput] = None; dia: Optional[IntFilterInput] = None
    dia_semana: Optional[IntFilterInput] = None; hora: Optional[IntFilterInput] = None; minuto: Optional[IntFilterInput] = None
    pais_geografia: Optional[StringFilterInput] = None; regiao_geografia: Optional[StringFilterInput] = None
    cidade_geografia: Optional[StringFilterInput] = None; url_referencia: Optional[StringFilterInput] = None
    tipo_referencia: Optional[StringFilterInput] = None
    AND: Optional[List['VisitaFilterInput']] = None; OR: Optional[List['VisitaFilterInput']] = None

# Define the Query type
@strawberry.type
class Query:
    @strawberry.field
    def get_visitas(
        self,
        filter: Optional[VisitaFilterInput] = None,
        cursor_args: Optional[CursorModeInput] = None,
        offset_args: Optional[PaginationModeInput] = None
    ) -> VisitaConnection:
        # --- Argument Validation ---
        if cursor_args and offset_args:
            raise ValueError("Cannot use `cursorArgs` and `offsetArgs` simultaneously.")

        # Validate cursor_args
        if cursor_args:
            if cursor_args.first is not None and cursor_args.last is not None:
                raise ValueError("Cannot use `first` and `last` arguments together in `cursorArgs`.")
            if cursor_args.after is not None and cursor_args.first is None:
                raise ValueError("`after` cursor must be used with `first` argument in `cursorArgs`.")
            if cursor_args.before is not None and cursor_args.last is None:
                raise ValueError("`before` cursor must be used with `last` argument in `cursorArgs`.")
            if cursor_args.first is not None and cursor_args.first < 0:
                raise ValueError("`first` argument in `cursorArgs` must be non-negative.")
            if cursor_args.last is not None and cursor_args.last < 0:
                raise ValueError("`last` argument in `cursorArgs` must be non-negative.")

        # Validate offset_args
        if offset_args:
            if offset_args.limit is not None and offset_args.limit < 0:
                raise ValueError("`limit` argument in `offsetArgs` must be non-negative.")
            if offset_args.offset is not None and offset_args.offset < 0:
                raise ValueError("`offset` argument in `offsetArgs` must be non-negative.")

        # --- Determine Pagination Mode & Variables ---
        pagination_mode = "default"
        sql_limit = DEFAULT_PAGE_SIZE
        sql_offset = 0
        order_by_clause = " ORDER BY fv.timestamp_visita ASC, fv.id_visita ASC "
        pagination_conditions = []
        pagination_params = []
        fetch_extra_for_page_info = False

        if cursor_args:
            pagination_mode = "cursor"
            fetch_extra_for_page_info = True
            after_timestamp, after_id = decode_cursor(cursor_args.after) if cursor_args.after else (None, None)
            before_timestamp, before_id = decode_cursor(cursor_args.before) if cursor_args.before else (None, None)

            if cursor_args.first is not None:
                sql_limit = cursor_args.first + 1
                if after_timestamp is not None:
                    pagination_conditions.append("(fv.timestamp_visita > ? OR (fv.timestamp_visita = ? AND fv.id_visita > ?))")
                    pagination_params.extend([after_timestamp, after_timestamp, after_id])
            elif cursor_args.last is not None:
                sql_limit = cursor_args.last + 1
                order_by_clause = " ORDER BY fv.timestamp_visita DESC, fv.id_visita DESC "
                if before_timestamp is not None:
                    pagination_conditions.append("(fv.timestamp_visita < ? OR (fv.timestamp_visita = ? AND fv.id_visita < ?))")
                    pagination_params.extend([before_timestamp, before_timestamp, before_id])
            # If only 'after' or 'before' is provided without 'first' or 'last',
            # it's an invalid state caught by earlier validation.
            # If no cursor pagination args are provided within cursor_args (e.g. empty object),
            # it might fall through, but the intent is for specific args to be present.
            # For safety, if cursor_args is present but no first/last, apply a default limit.
            elif not cursor_args.first and not cursor_args.last:
                 sql_limit = DEFAULT_PAGE_SIZE + 1


        elif offset_args:
            pagination_mode = "offset"
            sql_limit = offset_args.limit if offset_args.limit is not None else DEFAULT_PAGE_SIZE
            sql_offset = offset_args.offset if offset_args.offset is not None else 0
        else: # Default mode (no pagination args provided)
            pagination_mode = "offset" # Treat default as offset
            sql_limit = DEFAULT_PAGE_SIZE
            sql_offset = 0

        conn = None
        try:
            conn = get_db_connection()

            # --- Calculate Total Count (with filter) ---
            count_query_from_join = """
            FROM FatoVisitas fv
            JOIN DimDominio dd ON fv.id_dim_dominio = dd.id_dim_dominio
            JOIN DimPagina dp ON fv.id_dim_pagina = dp.id_dim_pagina
            JOIN DimUrl du ON fv.id_dim_url = du.id_dim_url
            JOIN DimNavegador dn ON fv.id_dim_navegador = dn.id_dim_navegador
            LEFT JOIN DimUtm dut ON fv.id_dim_utm = dut.id_dim_utm
            JOIN DimSessao ds ON fv.id_dim_sessao = ds.id_dim_sessao
            JOIN DimDispositivo ddi ON fv.id_dim_dispositivo = ddi.id_dim_dispositivo
            JOIN DimIp dip ON fv.id_dim_ip = dip.id_dim_ip
            JOIN DimTempo dt ON fv.id_dim_tempo = dt.id_dim_tempo
            LEFT JOIN DimGeografia dg ON fv.id_dim_geografia = dg.id_dim_geografia
            LEFT JOIN DimReferencia dr ON fv.id_dim_referencia = dr.id_dim_referencia
            """
            filter_where_clause_for_count, filter_params_for_count = build_where_clause(filter)
            count_query = f"SELECT COUNT(fv.id_visita) {count_query_from_join} {filter_where_clause_for_count}"
            count_cursor = conn.cursor()
            count_cursor.execute(count_query, filter_params_for_count)
            total_count = count_cursor.fetchone()[0]
            count_cursor.close()

            # --- Build and Execute Main Data Query ---
            cursor = conn.cursor()
            select_part = """ SELECT fv.id_visita, fv.timestamp_visita, dd.nome_dominio, dp.caminho_pagina, du.url_completa, dn.nome_navegador, dn.versao_navegador, dn.motor_renderizacao, dn.sistema_operacional_usuario, dut.utm_source, dut.utm_medium, dut.utm_campaign, dut.utm_term, dut.utm_content, ds.id_usuario_sessao, ds.id_sessao_navegador, ddi.tipo_dispositivo, ddi.marca_dispositivo, ddi.modelo_dispositivo, ddi.resolucao_tela, dip.endereco_ip, dt.data_completa, dt.ano, dt.mes, dt.dia, dt.dia_semana, dt.hora, dt.minuto, dg.pais AS pais_geografia, dg.regiao AS regiao_geografia, dg.cidade AS cidade_geografia, dr.url_referencia, dr.tipo_referencia """
            from_join_part = count_query_from_join # Reuse from count query

            # Build filter clause again for main query (params list is managed locally by build_where_clause)
            filter_where_clause, filter_params = build_where_clause(filter)

            # Combine filter and pagination conditions
            all_conditions = []
            if filter_where_clause: all_conditions.append(filter_where_clause[7:]) # Strip " WHERE "
            if pagination_conditions: all_conditions.extend(pagination_conditions)
            final_where_clause = " WHERE " + " AND ".join(all_conditions) if all_conditions else ""

            all_params = filter_params + pagination_params # Combine params

            # Add LIMIT/OFFSET based on mode
            limit_offset_clause = ""
            if pagination_mode == "cursor":
                limit_offset_clause = f" LIMIT ?"
                all_params.append(sql_limit) # Use limit potentially increased by 1
            elif pagination_mode == "offset":
                limit_offset_clause = f" LIMIT ? OFFSET ?"
                all_params.append(sql_limit)
                all_params.append(sql_offset)

            final_query = select_part + from_join_part + final_where_clause + order_by_clause + limit_offset_clause

            # print(f"Executing SQL: {final_query}") # Debug
            # print(f"With params: {all_params}") # Debug
            cursor.execute(final_query, all_params)
            rows = cursor.fetchall()

            # --- Process results for Connection ---
            has_next = False
            has_previous = False
            
            # Cursor mode page info logic
            if pagination_mode == "cursor" and fetch_extra_for_page_info and len(rows) == sql_limit:
                if cursor_args and cursor_args.last is not None: # Backward pagination
                    has_previous = True
                    rows = rows[:-1] # Remove extra item fetched for check
                else: # Forward pagination (or if cursor_args is None but somehow in cursor_mode)
                    has_next = True
                    rows = rows[:-1] # Remove extra item fetched for check
            
            # Offset mode page info logic
            elif pagination_mode == "offset":
                 has_previous = sql_offset > 0
                 has_next = (sql_offset + len(rows)) < total_count

            # Reverse results if backward pagination was used (cursor mode only)
            if pagination_mode == "cursor" and cursor_args and cursor_args.last is not None:
                rows.reverse()

            # Build Edges
            edges = []
            for row in rows:
                node = VisitaType(
                    id_visita=row['id_visita'], timestamp_visita=datetime.datetime.fromtimestamp(row['timestamp_visita']),
                    nome_dominio=row['nome_dominio'], caminho_pagina=row['caminho_pagina'], url_completa=row['url_completa'],
                    nome_navegador=row['nome_navegador'], versao_navegador=row['versao_navegador'], motor_renderizacao_navegador=row['motor_renderizacao'],
                    so_usuario_navegador=row['sistema_operacional_usuario'], utm_source=row['utm_source'], utm_medium=row['utm_medium'],
                    utm_campaign=row['utm_campaign'], utm_term=row['utm_term'], utm_content=row['utm_content'],
                    id_usuario_sessao=row['id_usuario_sessao'], id_sessao_navegador=row['id_sessao_navegador'],
                    tipo_dispositivo=row['tipo_dispositivo'], marca_dispositivo=row['marca_dispositivo'], modelo_dispositivo=row['modelo_dispositivo'],
                    resolucao_tela=row['resolucao_tela'], endereco_ip=row['endereco_ip'], data_completa=row['data_completa'],
                    ano=row['ano'], mes=row['mes'], dia=row['dia'], dia_semana=row['dia_semana'], hora=row['hora'], minuto=row['minuto'],
                    pais_geografia=row['pais_geografia'], regiao_geografia=row['regiao_geografia'], cidade_geografia=row['cidade_geografia'],
                    url_referencia=row['url_referencia'], tipo_referencia=row['tipo_referencia']
                )
                cursor_str = encode_cursor(row['timestamp_visita'], row['id_visita'])
                edges.append(VisitaEdge(node=node, cursor=cursor_str))

            # Build PageInfo
            page_info = PageInfo(
                has_next_page=has_next,
                has_previous_page=has_previous,
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None
            )

            # Return Connection
            return VisitaConnection(edges=edges, pageInfo=page_info, totalCount=total_count)

        except ValueError as e: # Catch specific validation/cursor errors
             print(f"Input error: {e}")
             raise e # Re-raise for Strawberry to handle
        except sqlite3.Error as e:
            print(f"Database error in resolver: {e}")
            # In a real API, you might want to return a more specific GraphQL error
            # For now, return an empty connection on DB errors
            return VisitaConnection(edges=[], pageInfo=PageInfo(has_next_page=False, has_previous_page=False), totalCount=0)
        finally:
            if conn:
                conn.close()

# Create the schema
schema = strawberry.Schema(query=Query)

# Notes:
# - build_where_clause now uses a local params list to avoid side effects between count and data queries.
# - totalCount is calculated based only on the filter.
# - Pagination logic (cursor or offset) is applied conditionally.
# - PageInfo calculation differs slightly between cursor and offset modes.
