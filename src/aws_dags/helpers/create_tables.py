"""
SQL create tables statements
"""

CREATE_DIM_CITY_POPULATION = (
    """
    CREATE TABLE IF NOT EXISTS public.dim_city_population (
        city VARCHAR,
        state VARCHAR,
        male_population INTEGER,
        female_population INTEGER,
        num_veterans INTEGER,
        foreign_born INTEGER,
        race VARCHAR,
        population_id BIGINT NOT NULL,
        CONSTRAINT population_id_pkey PRIMARY KEY(population_id)
    );
    """
)

CREATE_DIM_CITY_STATS = (
    """
    CREATE TABLE IF NOT EXISTS public.dim_city_stats (
        city VARCHAR,
        state VARCHAR,
        median_age FLOAT,
        avg_household_size FLOAT,
        stat_id BIGINT NOT NULL,
        CONSTRAINT stat_id_pkey PRIMARY KEY(stat_id)
    );
    """
)

CREATE_FACT_IMMIGRATION = (
    """
    CREATE TABLE IF NOT EXISTS public.fact_immigration (
        cic_id BIGINT NOT NULL,
        year INTEGER,
        month INTEGER,
        city_code VARCHAR,
        state_code VARCHAR,
        arrival_date DATE,
        departure_date DATE,
        mode INTEGER,
        visa INTEGER,
        immigration_id BIGINT NOT NULL,
        country VARCHAR,
        CONSTRAINT immigration_id_pkey PRIMARY KEY(immigration_id)
    );
    """
)

CREATE_DIM_IMMIGRATION_PERSONAL = (
    """
    CREATE TABLE IF NOT EXISTS public.dim_immigration_personal (
        cic_id BIGINT NOT NULL,
        citizen_country INTEGER,
        residence_country INTEGER,
        birth_year INTEGER,
        gender VARCHAR,
        ins_num VARCHAR,
        personal_id BIGINT NOT NULL,
        CONSTRAINT personal_id_pkey PRIMARY KEY(personal_id)
    );
    """
)

CREATE_DIM_IMMIGRATION_AIRLINE = (
    """
    CREATE TABLE IF NOT EXISTS public.dim_immigration_airline (
        cic_id BIGINT NOT NULL,
        airline VARCHAR,
        admnum FLOAT,
        flight_number VARCHAR,
        visa_type VARCHAR,
        airline_id BIGINT NOT NULL,
        CONSTRAINT airline_id_pkey PRIMARY KEY(airline_id)
    );
    """
)

CREATE_COUNTRY_CODE = (
    """
    CREATE TABLE IF NOT EXISTS public.country_code (
        code VARCHAR NOT NULL,
        country VARCHAR,
        CONSTRAINT country_code_pkey PRIMARY KEY(code)
    );
    """
)

CREATE_CITY_CODE = (
    """
    CREATE TABLE IF NOT EXISTS public.city_code (
        code VARCHAR NOT NULL,
        city VARCHAR,
        CONSTRAINT city_code_pkey PRIMARY KEY(code)
    );
    """
)

CREATE_STATE_CODE = (
    """
    CREATE TABLE IF NOT EXISTS public.state_code (
        code VARCHAR NOT NULL,
        state VARCHAR,
        CONSTRAINT state_code_pkey PRIMARY KEY(code)
    );
    """
)

CREATE_DIM_IMMIGRATION_TEMPERATURE = (
    """
    CREATE TABLE IF NOT EXISTS public.dim_immigration_temperature (
        dt VARCHAR NOT NULL,
        avg_temperature NUMERIC,
        avg_temperature_uncertainty NUMERIC,
        city VARCHAR,
        country VARCHAR,
        year INTEGER,
        month INTEGER,
        CONSTRAINT dt_pkey PRIMARY KEY(dt)
    );
    """
)
