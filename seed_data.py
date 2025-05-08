import sqlite3
import datetime
import time
import random

DATABASE_FILE = 'database.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def insert_or_get_dim(conn, table_name, data, unique_cols):
    """Inserts data into a dimension table or returns the existing ID if data is unique."""
    cursor = conn.cursor()
    cols = ', '.join(data.keys())
    placeholders = ', '.join('?' for _ in data.values())
    values = list(data.values())

    # Check if the unique combination of columns already exists
    where_clauses = [f"{col} = ?" for col in unique_cols]
    where_sql = " AND ".join(where_clauses)
    unique_values = [data[col] for col in unique_cols]

    # Construct the correct ID column name based on table name
    # Construct the correct ID column name by replacing underscores in the table name
    id_column_name = f"id_{table_name.lower().replace('_', '')}"
    # However, the schema uses underscores, so let's match the schema exactly
    # We can create a mapping or handle specific cases. Let's refine the specific case handling.
    # A better approach is to check the schema.sql for the exact ID column names.
    # Based on schema.sql:
    # DimDominio -> id_dim_dominio
    # DimPagina -> id_dim_pagina
    # DimUrl -> id_dim_url
    # DimNavegador -> id_dim_navegador
    # DimUtm -> id_dim_utm
    # DimSessao -> id_dim_sessao
    # DimDispositivo -> id_dim_dispositivo
    # DimIp -> id_dim_ip
    # DimTempo -> id_dim_tempo
    # DimGeografia -> id_dim_geografia
    # DimReferencia -> id_dim_referencia

    # Let's create a mapping for clarity and correctness
    id_column_mapping = {
        'dimdominio': 'id_dim_dominio',
        'dimpagina': 'id_dim_pagina',
        'dimurl': 'id_dim_url',
        'dimnavegador': 'id_dim_navegador',
        'dimutm': 'id_dim_utm',
        'dimsessao': 'id_dim_sessao',
        'dimdispositivo': 'id_dim_dispositivo',
        'dimip': 'id_dim_ip',
        'dimtempo': 'id_dim_tempo',
        'dimgeografia': 'id_dim_geografia',
        'dimreferencia': 'id_dim_referencia'
    }
    lower_table_name = table_name.lower()
    id_column_name = id_column_mapping.get(lower_table_name, f"id_{lower_table_name}") # Fallback just in case, though mapping should cover all


    cursor.execute(f"SELECT {id_column_name} FROM {table_name} WHERE {where_sql}", unique_values)
    row = cursor.fetchone()

    if row:
        return row[0]
    else:
        # Insert new data
        cursor.execute(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})", values)
        return cursor.lastrowid

def seed_data():
    """Populates the database with example data."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Example Data
        domains = ["example.com", "anothersite.org", "test.net"]
        pages = ["/", "/products", "/about", "/contact", "/blog/post-1"]
        browsers = [
            ("Chrome", "100.0", "Blink", "Windows 10"),
            ("Firefox", "98.0", "Gecko", "Ubuntu 20.04"),
            ("Safari", "15.0", "WebKit", "macOS Monterey"),
            ("Edge", "99.0", "EdgeHTML", "Windows 11")
        ]
        utms = [
            ("google", "organic", None, None, None),
            ("facebook", "social", "spring_campaign", None, "ad1"),
            ("newsletter", "email", "weekly_digest", None, None),
            (None, None, None, None, None) # Direct traffic
        ]
        sessions = [
            (None, "session_abc"),
            ("user_123", "session_def"),
            (None, "session_ghi"),
            ("user_456", "session_jkl")
        ]
        devices = [
            ("Desktop", "Dell", "XPS 15", "1920x1080"),
            ("Mobile", "Apple", "iPhone 13", "1170x2532"),
            ("Tablet", "Samsung", "Galaxy Tab S7", "2560x1600"),
            ("Desktop", "HP", "Spectre x360", "1920x1080")
        ]
        ips = ["192.168.1.1", "10.0.0.5", "172.16.0.10", "203.0.113.1"]
        geographies = [
            ("USA", "California", "Los Angeles"),
            ("Brazil", "Sao Paulo", "Sao Paulo"),
            ("Canada", "Ontario", "Toronto"),
            (None, None, None) # Unknown geography
        ]
        references = [
            ("https://www.google.com", "Organic"),
            ("https://www.facebook.com", "Social"),
            (None, "Direct"),
            ("https://otherblog.com/post", "Referral")
        ]

        # Insert Dimension Data
        dim_dominio_ids = {}
        for domain in domains:
            dim_dominio_ids[domain] = insert_or_get_dim(conn, "DimDominio", {"nome_dominio": domain}, ["nome_dominio"])

        dim_pagina_ids = {}
        for page in pages:
            dim_pagina_ids[page] = insert_or_get_dim(conn, "DimPagina", {"caminho_pagina": page}, ["caminho_pagina"])

        dim_url_ids = {}
        # Generate some example URLs based on domains and pages
        example_urls = []
        for domain in domains:
            for page in pages:
                example_urls.append(f"https://{domain}{page}")
                if page == "/products":
                    example_urls.append(f"https://{domain}{page}?id={random.randint(100, 999)}")
        for url in example_urls:
             dim_url_ids[url] = insert_or_get_dim(conn, "DimUrl", {"url_completa": url}, ["url_completa"])


        dim_navegador_ids = {}
        for browser in browsers:
            data = {"nome_navegador": browser[0], "versao_navegador": browser[1], "motor_renderizacao": browser[2], "sistema_operacional_usuario": browser[3]}
            dim_navegador_ids[browser] = insert_or_get_dim(conn, "DimNavegador", data, ["nome_navegador", "versao_navegador", "motor_renderizacao", "sistema_operacional_usuario"])

        dim_utm_ids = {}
        for utm in utms:
            data = {"utm_source": utm[0], "utm_medium": utm[1], "utm_campaign": utm[2], "utm_term": utm[3], "utm_content": utm[4]}
            dim_utm_ids[utm] = insert_or_get_dim(conn, "DimUtm", data, ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"])

        dim_sessao_ids = {}
        for session in sessions:
             data = {"id_usuario_sessao": session[0], "id_sessao_navegador": session[1]}
             dim_sessao_ids[session] = insert_or_get_dim(conn, "DimSessao", data, ["id_sessao_navegador"]) # Assuming id_sessao_navegador is the unique key

        dim_dispositivo_ids = {}
        for device in devices:
            data = {"tipo_dispositivo": device[0], "marca_dispositivo": device[1], "modelo_dispositivo": device[2], "resolucao_tela": device[3]}
            dim_dispositivo_ids[device] = insert_or_get_dim(conn, "DimDispositivo", data, ["tipo_dispositivo", "marca_dispositivo", "modelo_dispositivo", "resolucao_tela"])

        dim_ip_ids = {}
        for ip in ips:
            dim_ip_ids[ip] = insert_or_get_dim(conn, "DimIp", {"endereco_ip": ip}, ["endereco_ip"])

        dim_tempo_ids = {}
        # Generate some example time data
        start_date = datetime.datetime(2023, 1, 1, 0, 0, 0)
        for i in range(100): # Generate 100 time entries
            current_date = start_date + datetime.timedelta(minutes=i*10)
            date_str = current_date.strftime('%Y-%m-%d %H:%M:%S')
            data = {
                "data_completa": date_str,
                "ano": current_date.year,
                "mes": current_date.month,
                "dia": current_date.day,
                "dia_semana": current_date.weekday(), # Monday is 0, Sunday is 6
                "hora": current_date.hour,
                "minuto": current_date.minute
            }
            dim_tempo_ids[date_str] = insert_or_get_dim(conn, "DimTempo", data, ["data_completa"])


        dim_geografia_ids = {}
        for geo in geographies:
            data = {"pais": geo[0], "regiao": geo[1], "cidade": geo[2]}
            dim_geografia_ids[geo] = insert_or_get_dim(conn, "DimGeografia", data, ["pais", "regiao", "cidade"])

        dim_referencia_ids = {}
        for ref in references:
            data = {"url_referencia": ref[0], "tipo_referencia": ref[1]}
            dim_referencia_ids[ref] = insert_or_get_dim(conn, "DimReferencia", data, ["url_referencia", "tipo_referencia"])


        # Insert Fact Data (FatoVisitas)
        fact_data = []
        for i in range(500): # Generate 500 visits
            random_domain = random.choice(domains)
            random_page = random.choice(pages)
            random_url = random.choice(list(dim_url_ids.keys())) # Choose from generated URLs
            random_browser = random.choice(browsers)
            random_utm = random.choice(utms)
            random_session = random.choice(sessions)
            random_device = random.choice(devices)
            random_ip = random.choice(ips)
            random_time_str = random.choice(list(dim_tempo_ids.keys()))
            random_geo = random.choice(geographies)
            random_ref = random.choice(references)

            # Get dimension IDs
            id_dim_dominio = dim_dominio_ids[random_domain]
            id_dim_pagina = dim_pagina_ids[random_page]
            id_dim_url = dim_url_ids[random_url]
            id_dim_navegador = dim_navegador_ids[random_browser]
            id_dim_utm = dim_utm_ids[random_utm] if random_utm != (None, None, None, None, None) else None # Handle NULL UTM
            id_dim_sessao = dim_sessao_ids[random_session]
            id_dim_dispositivo = dim_dispositivo_ids[random_device]
            id_dim_ip = dim_ip_ids[random_ip]
            id_dim_tempo = dim_tempo_ids[random_time_str]
            id_dim_geografia = dim_geografia_ids[random_geo] if random_geo != (None, None, None) else None # Handle NULL Geo
            id_dim_referencia = dim_referencia_ids[random_ref] if random_ref != (None, "Direct") else None # Handle NULL Referencia (Direct traffic)

            # Generate a timestamp within a reasonable range
            timestamp = int(time.mktime(datetime.datetime.strptime(random_time_str, '%Y-%m-%d %H:%M:%S').timetuple())) + random.randint(0, 59) # Add random seconds

            fact_data.append((
                id_dim_dominio,
                id_dim_pagina,
                id_dim_url,
                id_dim_navegador,
                id_dim_utm,
                id_dim_sessao,
                id_dim_dispositivo,
                id_dim_ip,
                id_dim_tempo,
                id_dim_geografia,
                id_dim_referencia,
                timestamp
            ))

        cursor.executemany("""
            INSERT INTO FatoVisitas (
                id_dim_dominio, id_dim_pagina, id_dim_url, id_dim_navegador,
                id_dim_utm, id_dim_sessao, id_dim_dispositivo, id_dim_ip,
                id_dim_tempo, id_dim_geografia, id_dim_referencia, timestamp_visita
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, fact_data)

        conn.commit()
        print(f"Database '{DATABASE_FILE}' populated with example data.")

    except sqlite3.Error as e:
        print(f"Database error during seeding: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Ensure the database is initialized before seeding
    from init_db import init_db
    init_db()
    seed_data()
