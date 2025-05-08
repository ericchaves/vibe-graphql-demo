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

def build_where_clause(filter: Any) -> tuple[str, list]:
    """Builds the SQL WHERE clause and parameters from the VisitaFilterInput."""
    conditions = []
    params = []

    # Mapping of GraphQL filter fields to DB columns and tables
    # This mapping is crucial for building the JOINs and WHERE clauses
    # It maps GraphQL fields to (TABLE_ALIAS, DB_COLUMN_NAME)
    field_mapping = {
        "nome_dominio": ("dd", "nome_dominio"),
        "caminho_pagina": ("dp", "caminho_pagina"),
        "url_completa": ("du", "url_completa"),
        "nome_navegador": ("dn", "nome_navegador"),
        "versao_navegador": ("dn", "versao_navegador"),
        "motor_renderizacao_navegador": ("dn", "motor_renderizacao"),
        "so_usuario_navegador": ("dn", "sistema_operacional_usuario"),
        "utm_source": ("dut", "utm_source"),
        "utm_medium": ("dut", "utm_medium"),
        "utm_campaign": ("dut", "utm_campaign"),
        "utm_term": ("dut", "utm_term"),
        "utm_content": ("dut", "utm_content"),
        "id_usuario_sessao": ("ds", "id_usuario_sessao"),
        "id_sessao_navegador": ("ds", "id_sessao_navegador"),
        "tipo_dispositivo": ("ddi", "tipo_dispositivo"),
        "marca_dispositivo": ("ddi", "marca_dispositivo"),
        "modelo_dispositivo": ("ddi", "modelo_dispositivo"),
        "resolucao_tela": ("ddi", "resolucao_tela"),
        "endereco_ip": ("dip", "endereco_ip"),
        "data_completa": ("dt", "data_completa"),
        "ano": ("dt", "ano"),
        "mes": ("dt", "mes"),
        "dia": ("dt", "dia"),
        "dia_semana": ("dt", "dia_semana"),
        "hora": ("dt", "hora"),
        "minuto": ("dt", "minuto"),
        "pais_geografia": ("dg", "pais"),
        "regiao_geografia": ("dg", "regiao"),
        "cidade_geografia": ("dg", "cidade"),
        "url_referencia": ("dr", "url_referencia"),
        "tipo_referencia": ("dr", "tipo_referencia"),
        "id_visita": ("fv", "id_visita"),
        "timestamp_visita": ("fv", "timestamp_visita")
    }

    # Build conditions for StringFilterInput
    def build_string_condition(field_name, filter_input):
        alias, column = field_mapping[field_name]
        field_conditions = []
        if filter_input.equals is not None:
            field_conditions.append(f"{alias}.{column} = ?")
            params.append(filter_input.equals)
        if filter_input.notEquals is not None:
            field_conditions.append(f"{alias}.{column} != ?")
            params.append(filter_input.notEquals)
        if filter_input.contains is not None:
            field_conditions.append(f"{alias}.{column} LIKE ?")
            params.append(f"%{filter_input.contains}%")
        if filter_input.startsWith is not None:
            field_conditions.append(f"{alias}.{column} LIKE ?")
            params.append(f"{filter_input.startsWith}%")
        if filter_input.endsWith is not None:
            field_conditions.append(f"{alias}.{column} LIKE ?")
            params.append(f"%{filter_input.endsWith}")
        if filter_input.In is not None:
            placeholders = ', '.join('?' for _ in filter_input.In)
            field_conditions.append(f"{alias}.{column} IN ({placeholders})")
            params.extend(filter_input.In)
        if filter_input.notIn is not None:
            placeholders = ', '.join('?' for _ in filter_input.notIn)
            field_conditions.append(f"{alias}.{column} NOT IN ({placeholders})")
            params.extend(filter_input.notIn)
        return " AND ".join(field_conditions) if field_conditions else ""

    # Build conditions for IntFilterInput
    def build_int_condition(field_name, filter_input):
        alias, column = field_mapping[field_name]
        field_conditions = []
        if filter_input.equals is not None:
            field_conditions.append(f"{alias}.{column} = ?")
            params.append(filter_input.equals)
        if filter_input.notEquals is not None:
            field_conditions.append(f"{alias}.{column} != ?")
            params.append(filter_input.notEquals)
        if filter_input.greaterThan is not None:
            field_conditions.append(f"{alias}.{column} > ?")
            params.append(filter_input.greaterThan)
        if filter_input.greaterThanOrEqual is not None:
            field_conditions.append(f"{alias}.{column} >= ?")
            params.append(filter_input.greaterThanOrEqual)
        if filter_input.lessThan is not None:
            field_conditions.append(f"{alias}.{column} < ?")
            params.append(filter_input.lessThan)
        if filter_input.lessThanOrEqual is not None:
            field_conditions.append(f"{alias}.{column} <= ?")
            params.append(filter_input.lessThanOrEqual)
        if filter_input.In is not None:
            placeholders = ', '.join('?' for _ in filter_input.In)
            field_conditions.append(f"{alias}.{column} IN ({placeholders})")
            params.extend(filter_input.In)
        if filter_input.notIn is not None:
            placeholders = ', '.join('?' for _ in filter_input.notIn)
            field_conditions.append(f"{alias}.{column} NOT IN ({placeholders})")
            params.extend(filter_input.notIn)
        if filter_input.between is not None and len(filter_input.between) == 2:
            field_conditions.append(f"{alias}.{column} BETWEEN ? AND ?")
            params.extend(filter_input.between)
        if filter_input.notBetween is not None and len(filter_input.notBetween) == 2:
            field_conditions.append(f"{alias}.{column} NOT BETWEEN ? AND ?")
            params.extend(filter_input.notBetween)
        return " AND ".join(field_conditions) if field_conditions else ""

    # Build conditions for DateTimeFilterInput (assuming timestamp_visita is INTEGER Unix timestamp)
    def build_datetime_condition(field_name, filter_input):
        alias, column = field_mapping[field_name]
        field_conditions = []
        # Convert datetime objects to Unix timestamps for comparison
        if filter_input.equals is not None:
            field_conditions.append(f"{alias}.{column} = ?")
            params.append(int(filter_input.equals.timestamp()))
        if filter_input.notEquals is not None:
            field_conditions.append(f"{alias}.{column} != ?")
            params.append(int(filter_input.notEquals.timestamp()))
        if filter_input.greaterThan is not None:
            field_conditions.append(f"{alias}.{column} > ?")
            params.append(int(filter_input.greaterThan.timestamp()))
        if filter_input.greaterThanOrEqual is not None:
            field_conditions.append(f"{alias}.{column} >= ?")
            params.append(int(filter_input.greaterThanOrEqual.timestamp()))
        if filter_input.lessThan is not None:
            field_conditions.append(f"{alias}.{column} < ?")
            params.append(int(filter_input.lessThan.timestamp()))
        if filter_input.lessThanOrEqual is not None:
            field_conditions.append(f"{alias}.{column} <= ?")
            params.append(int(filter_input.lessThanOrEqual.timestamp()))
        if filter_input.In is not None:
            placeholders = ', '.join('?' for _ in filter_input.In)
            timestamps = [int(dt.timestamp()) for dt in filter_input.In]
            field_conditions.append(f"{alias}.{column} IN ({placeholders})")
            params.extend(timestamps)
        if filter_input.notIn is not None:
            placeholders = ', '.join('?' for _ in filter_input.notIn)
            timestamps = [int(dt.timestamp()) for dt in filter_input.notIn]
            field_conditions.append(f"{alias}.{column} NOT IN ({placeholders})")
            params.extend(timestamps)
        if filter_input.between is not None and len(filter_input.between) == 2:
            timestamps = [int(dt.timestamp()) for dt in filter_input.between]
            field_conditions.append(f"{alias}.{column} BETWEEN ? AND ?")
            params.extend(timestamps)
        if filter_input.notBetween is not None and len(filter_input.notBetween) == 2:
            timestamps = [int(dt.timestamp()) for dt in filter_input.notBetween]
            field_conditions.append(f"{alias}.{column} NOT BETWEEN ? AND ?")
            params.extend(timestamps)
        return " AND ".join(field_conditions) if field_conditions else ""

    # Recursive helper function to build clause for a filter object
    def _build_clause_recursively(current_filter_obj, params_list_ref):
        # params_list_ref is the main params list, modified by build_xxx_condition helpers
        
        parts_for_this_filter_obj = [] # Stores fully formed condition strings or block strings

        # 1. Process direct field filters for the current_filter_obj
        direct_field_strings = []
        for field_name, f_input_val in current_filter_obj.__dict__.items():
            if field_name in ["AND", "OR"] or f_input_val is None:
                continue
            
            cond_str = ""
            if isinstance(f_input_val, StringFilterInput):
                cond_str = build_string_condition(field_name, f_input_val) # build_string_condition uses global `params`
            elif isinstance(f_input_val, IntFilterInput):
                cond_str = build_int_condition(field_name, f_input_val)
            elif isinstance(f_input_val, DateTimeFilterInput) and field_name == "timestamp_visita":
                cond_str = build_datetime_condition(field_name, f_input_val)
            # Add other field types here if necessary
            
            if cond_str:
                # If a single field's condition string itself contains " AND " (e.g. multiple ops on one field),
                # it should be wrapped in parentheses to ensure correct precedence when combined with other direct fields.
                if " AND " in cond_str:
                    direct_field_strings.append(f"({cond_str})")
                else:
                    direct_field_strings.append(cond_str)

        if direct_field_strings:
            # If there's more than one direct field condition string, AND them together and wrap the whole group.
            # If only one, it's used as is (it's either simple like "col=?" or already wrapped like "(col>1 AND col<5)").
            if len(direct_field_strings) > 1:
                parts_for_this_filter_obj.append(f"({' AND '.join(direct_field_strings)})")
            else: # len == 1
                parts_for_this_filter_obj.append(direct_field_strings[0])

        # 2. Process AND list
        if current_filter_obj.AND:
            and_block_sub_clauses = []
            for sub_filter_item in current_filter_obj.AND:
                sub_clause_str = _build_clause_recursively(sub_filter_item, params_list_ref)
                if sub_clause_str:
                    and_block_sub_clauses.append(sub_clause_str)
            if and_block_sub_clauses:
                # Join sub-clauses with " AND " and wrap the entire AND block in parentheses.
                parts_for_this_filter_obj.append(f"({' AND '.join(and_block_sub_clauses)})")
                
        # 3. Process OR list
        if current_filter_obj.OR:
            or_block_sub_clauses = []
            for sub_filter_item in current_filter_obj.OR:
                sub_clause_str = _build_clause_recursively(sub_filter_item, params_list_ref)
                if sub_clause_str:
                    or_block_sub_clauses.append(sub_clause_str)
            if or_block_sub_clauses:
                parts_for_this_filter_obj.append(f"({' OR '.join(or_block_sub_clauses)})")
                
        # All parts generated for this filter object (direct fields block, AND block, OR block)
        # are implicitly ANDed together.
        return " AND ".join(p for p in parts_for_this_filter_obj if p)

    # Main part of build_where_clause
    if filter:
        # `params` is a global list modified by build_xxx_condition helpers
        # and _build_clause_recursively just needs to ensure they are called.
        final_clause_str = _build_clause_recursively(filter, params) # Pass params for context if helpers need it, though they use global
        if final_clause_str:
            where_clause = " WHERE " + final_clause_str
            return where_clause, params # Return the global params list
    
    return "", params # Return global params even if no clause


# Define generic InputFilter types
@strawberry.input
class StringFilterInput:
    equals: Optional[str] = None
    notEquals: Optional[str] = None
    contains: Optional[str] = None
    startsWith: Optional[str] = None
    endsWith: Optional[str] = None
    In: Optional[List[str]] = None
    notIn: Optional[List[str]] = None

@strawberry.input
class IntFilterInput:
    equals: Optional[int] = None
    notEquals: Optional[int] = None
    greaterThan: Optional[int] = None
    greaterThanOrEqual: Optional[int] = None
    lessThan: Optional[int] = None
    lessThanOrEqual: Optional[int] = None
    In: Optional[List[int]] = None
    notIn: Optional[List[int]] = None
    between: Optional[tuple[int, int]] = None
    notBetween: Optional[tuple[int, int]] = None

@strawberry.input
class DateTimeFilterInput:
    equals: Optional[datetime.datetime] = None
    notEquals: Optional[datetime.datetime] = None
    greaterThan: Optional[datetime.datetime] = None
    greaterThanOrEqual: Optional[datetime.datetime] = None
    lessThan: Optional[datetime.datetime] = None
    lessThanOrEqual: Optional[datetime.datetime] = None
    In: Optional[List[datetime.datetime]] = None
    notIn: Optional[List[datetime.datetime]] = None
    between: Optional[tuple[datetime.datetime, datetime.datetime]] = None
    notBetween: Optional[tuple[datetime.datetime, datetime.datetime]] = None

# Define the consolidated VisitaType
@strawberry.type
class VisitaType:
    id_visita: int
    timestamp_visita: datetime.datetime

    # DimDominio
    nome_dominio: str

    # DimPagina
    caminho_pagina: str

    # DimUrl
    url_completa: str

    # DimNavegador
    nome_navegador: str
    versao_navegador: Optional[str]
    motor_renderizacao_navegador: Optional[str]
    so_usuario_navegador: str

    # DimUtm
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]
    utm_term: Optional[str]
    utm_content: Optional[str]

    # DimSessao
    id_usuario_sessao: Optional[str]
    id_sessao_navegador: str

    # DimDispositivo
    tipo_dispositivo: str
    marca_dispositivo: Optional[str]
    modelo_dispositivo: Optional[str]
    resolucao_tela: Optional[str]

    # DimIp
    endereco_ip: str

    # DimTempo
    data_completa: str # Stored as TEXT in DB, expose as string
    ano: int
    mes: int
    dia: int
    dia_semana: int
    hora: int
    minuto: int

    # DimGeografia
    pais_geografia: Optional[str]
    regiao_geografia: Optional[str]
    cidade_geografia: Optional[str]

    # DimReferencia
    url_referencia: Optional[str]
    tipo_referencia: Optional[str] # Can be NULL for direct traffic, but type_referencia in DB is NOT NULL. Need to clarify. Assuming NOT NULL based on schema.sql.

# --- Relay Connection Types ---
@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None

@strawberry.type
class VisitaEdge:
    node: VisitaType
    cursor: str

@strawberry.type
class VisitaConnection:
    edges: List[VisitaEdge]
    pageInfo: PageInfo
    # totalCount: Optional[int] = None # Optional: Consider adding total count if feasible/needed

# Define the VisitaFilterInput
@strawberry.input
class VisitaFilterInput:
    id_visita: Optional[IntFilterInput] = None
    timestamp_visita: Optional[DateTimeFilterInput] = None

    # DimDominio
    nome_dominio: Optional[StringFilterInput] = None

    # DimPagina
    caminho_pagina: Optional[StringFilterInput] = None

    # DimUrl
    url_completa: Optional[StringFilterInput] = None

    # DimNavegador
    nome_navegador: Optional[StringFilterInput] = None
    versao_navegador: Optional[StringFilterInput] = None
    motor_renderizacao_navegador: Optional[StringFilterInput] = None
    so_usuario_navegador: Optional[StringFilterInput] = None

    # DimUtm
    utm_source: Optional[StringFilterInput] = None
    utm_medium: Optional[StringFilterInput] = None
    utm_campaign: Optional[StringFilterInput] = None
    utm_term: Optional[StringFilterInput] = None
    utm_content: Optional[StringFilterInput] = None

    # DimSessao
    id_usuario_sessao: Optional[StringFilterInput] = None
    id_sessao_navegador: Optional[StringFilterInput] = None

    # DimDispositivo
    tipo_dispositivo: Optional[StringFilterInput] = None
    marca_dispositivo: Optional[StringFilterInput] = None
    modelo_dispositivo: Optional[StringFilterInput] = None
    resolucao_tela: Optional[StringFilterInput] = None

    # DimIp
    endereco_ip: Optional[StringFilterInput] = None

    # DimTempo
    data_completa: Optional[StringFilterInput] = None # Stored as TEXT in DB, expose as string
    ano: Optional[IntFilterInput] = None
    mes: Optional[IntFilterInput] = None
    dia: Optional[IntFilterInput] = None
    dia_semana: Optional[IntFilterInput] = None
    hora: Optional[IntFilterInput] = None
    minuto: Optional[IntFilterInput] = None

    # DimGeografia
    pais_geografia: Optional[StringFilterInput] = None
    regiao_geografia: Optional[StringFilterInput] = None
    cidade_geografia: Optional[StringFilterInput] = None

    # DimReferencia
    url_referencia: Optional[StringFilterInput] = None
    tipo_referencia: Optional[StringFilterInput] = None

    # --- Operadores lógicos para combinar filtros ---
    # Forward declaration is needed if VisitaFilterInput refers to itself.
    # We will define VisitaFilterInputType later if needed, or rely on Strawberry's handling.
    AND: Optional[List['VisitaFilterInput']] = None
    OR: Optional[List['VisitaFilterInput']] = None
    # NOT: Optional['VisitaFilterInput'] = None # Potential future enhancement

# Define the Query type
@strawberry.type
class Query:
    @strawberry.field
    def get_visitas(
        self,
        filter: Optional[VisitaFilterInput] = None,
        first: Optional[int] = None,
        after: Optional[str] = None,
        last: Optional[int] = None,
        before: Optional[str] = None
    ) -> VisitaConnection:
        # Basic validation
        if first is not None and last is not None:
            raise ValueError("Cannot use `first` and `last` arguments together.")
        if after is not None and first is None:
             raise ValueError("`after` cursor must be used with `first` argument.")
        if before is not None and last is None:
             raise ValueError("`before` cursor must be used with `last` argument.")

        # --- Pagination Logic ---
        limit = DEFAULT_PAGE_SIZE
        order_by_clause = " ORDER BY fv.timestamp_visita ASC, fv.id_visita ASC " # Default order for forward pagination
        pagination_conditions = []
        pagination_params = []
        fetch_extra_for_page_info = False # Flag to fetch one extra item

        # Decode cursors
        after_timestamp = None
        after_id = None
        if after:
            try:
                decoded_after = base64.b64decode(after).decode('utf-8')
                after_timestamp_str, after_id_str = decoded_after.split(':')
                after_timestamp = int(after_timestamp_str)
                after_id = int(after_id_str)
            except (ValueError, TypeError):
                raise ValueError("Invalid `after` cursor format.")

        before_timestamp = None
        before_id = None
        if before:
             try:
                decoded_before = base64.b64decode(before).decode('utf-8')
                before_timestamp_str, before_id_str = decoded_before.split(':')
                before_timestamp = int(before_timestamp_str)
                before_id = int(before_id_str)
             except (ValueError, TypeError):
                raise ValueError("Invalid `before` cursor format.")

        # Determine limit and potentially reverse order for backward pagination
        if first is not None:
            limit = first + 1 # Fetch one extra to check has_next_page
            fetch_extra_for_page_info = True
            if after_timestamp is not None and after_id is not None:
                 pagination_conditions.append("(fv.timestamp_visita > ? OR (fv.timestamp_visita = ? AND fv.id_visita > ?))")
                 pagination_params.extend([after_timestamp, after_timestamp, after_id])
        elif last is not None:
            limit = last + 1 # Fetch one extra to check has_previous_page
            fetch_extra_for_page_info = True
            order_by_clause = " ORDER BY fv.timestamp_visita DESC, fv.id_visita DESC " # Reverse order for backward fetching
            if before_timestamp is not None and before_id is not None:
                 pagination_conditions.append("(fv.timestamp_visita < ? OR (fv.timestamp_visita = ? AND fv.id_visita < ?))")
                 pagination_params.extend([before_timestamp, before_timestamp, before_id])
        else:
             # No first or last provided, use default limit for first page
             limit = DEFAULT_PAGE_SIZE + 1
             fetch_extra_for_page_info = True


        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Base query parts
            select_part = """
            SELECT
                fv.id_visita,
                fv.timestamp_visita,
                dd.nome_dominio,
                dp.caminho_pagina,
                du.url_completa,
                dn.nome_navegador,
                dn.versao_navegador,
                dn.motor_renderizacao,
                dn.sistema_operacional_usuario,
                dut.utm_source,
                dut.utm_medium,
                dut.utm_campaign,
                dut.utm_term,
                dut.utm_content,
                ds.id_usuario_sessao,
                ds.id_sessao_navegador,
                ddi.tipo_dispositivo,
                ddi.marca_dispositivo,
                ddi.modelo_dispositivo,
                ddi.resolucao_tela,
                dip.endereco_ip,
                dt.data_completa,
                dt.ano,
                dt.mes,
                dt.dia,
                dt.dia_semana,
                dt.hora,
                dt.minuto,
                dg.pais AS pais_geografia,
                dg.regiao AS regiao_geografia,
                dg.cidade AS cidade_geografia,
                dr.url_referencia,
                dr.tipo_referencia
            """
            from_join_part = """
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

            # Build filter clause
            filter_where_clause, filter_params = build_where_clause(filter)

            # Combine filter and pagination conditions
            all_conditions = []
            if filter_where_clause:
                # Strip " WHERE " from the filter clause
                all_conditions.append(filter_where_clause[7:])
            if pagination_conditions:
                all_conditions.extend(pagination_conditions)

            final_where_clause = " WHERE " + " AND ".join(all_conditions) if all_conditions else ""
            all_params = filter_params + pagination_params

            # Construct final query
            final_query = select_part + from_join_part + final_where_clause + order_by_clause + f" LIMIT ?"
            all_params.append(limit)

            # For debugging
            # print(f"Executing SQL: {final_query}")
            # print(f"With params: {all_params}")

            cursor.execute(final_query, all_params)
            rows = cursor.fetchall()

            # --- Process results for Connection ---
            has_next = False
            has_previous = False
            
            if fetch_extra_for_page_info and len(rows) == limit:
                # We fetched one extra item
                if last is not None: # Backward pagination
                    has_previous = True
                    rows = rows[:-1] # Remove the extra item from the beginning (due to DESC order)
                else: # Forward pagination or no pagination args
                    has_next = True
                    rows = rows[:-1] # Remove the extra item from the end
            
            # Reverse results if backward pagination was used
            if last is not None:
                rows.reverse()

            edges = []
            for row in rows:
                node = VisitaType(
                    id_visita=row['id_visita'],
                    timestamp_visita=datetime.datetime.fromtimestamp(row['timestamp_visita']),
                    nome_dominio=row['nome_dominio'],
                    caminho_pagina=row['caminho_pagina'],
                    url_completa=row['url_completa'],
                    nome_navegador=row['nome_navegador'],
                    versao_navegador=row['versao_navegador'],
                    motor_renderizacao_navegador=row['motor_renderizacao'],
                    so_usuario_navegador=row['sistema_operacional_usuario'],
                    utm_source=row['utm_source'],
                    utm_medium=row['utm_medium'],
                    utm_campaign=row['utm_campaign'],
                    utm_term=row['utm_term'],
                    utm_content=row['utm_content'],
                    id_usuario_sessao=row['id_usuario_sessao'],
                    id_sessao_navegador=row['id_sessao_navegador'],
                    tipo_dispositivo=row['tipo_dispositivo'],
                    marca_dispositivo=row['marca_dispositivo'],
                    modelo_dispositivo=row['modelo_dispositivo'],
                    resolucao_tela=row['resolucao_tela'],
                    endereco_ip=row['endereco_ip'],
                    data_completa=row['data_completa'],
                    ano=row['ano'],
                    mes=row['mes'],
                    dia=row['dia'],
                    dia_semana=row['dia_semana'],
                    hora=row['hora'],
                    minuto=row['minuto'],
                    pais_geografia=row['pais_geografia'],
                    regiao_geografia=row['regiao_geografia'],
                    cidade_geografia=row['cidade_geografia'],
                    url_referencia=row['url_referencia'],
                    tipo_referencia=row['tipo_referencia']
                )
                # Create cursor from timestamp and id
                cursor_str = base64.b64encode(f"{row['timestamp_visita']}:{row['id_visita']}".encode('utf-8')).decode('utf-8')
                edges.append(VisitaEdge(node=node, cursor=cursor_str))

            page_info = PageInfo(
                has_next_page=has_next,
                has_previous_page=has_previous,
                start_cursor=edges[0].cursor if edges else None,
                end_cursor=edges[-1].cursor if edges else None
            )

            return VisitaConnection(edges=edges, pageInfo=page_info)

        except ValueError as e: # Catch specific validation errors
             print(f"Input error: {e}")
             # Consider raising a GraphQL error instead
             raise e # Re-raise for now, Strawberry might handle it
        except sqlite3.Error as e:
            print(f"Database error in resolver: {e}")
            # In a real API, you might want to return a GraphQL error
            return []
        finally:
            if conn:
                conn.close()

# Create the schema
schema = strawberry.Schema(query=Query)

# Note: The build_where_clause function currently assumes AND logic between different filter fields.
# More complex logic (e.g., OR) would require modifications to this function and the VisitaFilterInput structure.
# Also, the mapping between GraphQL fields and DB columns/tables is hardcoded here.
# For a larger project, a more robust mapping mechanism might be beneficial.
# The handling of Optional fields in the database (NULL values) needs to be carefully considered
# when building the WHERE clause and mapping results.
# The timestamp_visita is stored as INTEGER (Unix timestamp) in the DB and converted to datetime in the resolver.
# The data_completa in DimTempo is stored as TEXT and exposed as string.
# The type_referencia in DimReferencia is NOT NULL in schema.sql, but marked as Optional in VisitaType.
# This discrepancy should be addressed based on the intended data integrity rules.
# For now, assuming the schema.sql is the source of truth for DB constraints.
