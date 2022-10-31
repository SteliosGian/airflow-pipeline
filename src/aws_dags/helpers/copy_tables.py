"""
SQL insert statements
"""

LOAD_DIM_CITY_POPULATION = (
    """
    COPY dim_city_population
    FROM '{{ params.location }}'
    IAM_ROLE '{{ params.iam_role }}'
    FORMAT AS PARQUET;
    """
)

LOAD_DIM_CITY_STATS = (
    """
    COPY dim_city_stats
    FROM '{{ params.location }}'
    IAM_ROLE '{{ params.iam_role }}'
    FORMAT AS PARQUET;
    """
)

LOAD_FACT_IMMIGRATION = (
    """
    COPY fact_immigration
    FROM '{{ params.location }}'
    IAM_ROLE '{{ params.iam_role }}'
    FORMAT AS PARQUET;
    """
)

LOAD_DIM_IMMIGRATION_PERSONAL = (
    """
    COPY dim_immigration_personal
    FROM '{{ params.location }}'
    IAM_ROLE '{{ params.iam_role }}'
    FORMAT AS PARQUET;
    """
)

LOAD_DIM_IMMIGRATION_AIRLINE = (
    """
    COPY dim_immigration_airline
    FROM '{{ params.location }}'
    IAM_ROLE '{{ params.iam_role }}'
    FORMAT AS PARQUET;
    """
)

LOAD_COUNTRY_CODE = (
    """
    COPY country_code
    FROM '{{ params.location }}'
    IAM_ROLE '{{ params.iam_role }}'
    FORMAT AS PARQUET;
    """
)

LOAD_CITY_CODE = (
    """
    COPY city_code
    FROM '{{ params.location }}'
    IAM_ROLE '{{ params.iam_role }}'
    FORMAT AS PARQUET;
    """
)

LOAD_STATE_CODE = (
    """
    COPY state_code
    FROM '{{ params.location }}'
    IAM_ROLE '{{ params.iam_role }}'
    FORMAT AS PARQUET;
    """
)

LOAD_DIM_IMMIGRATION_TEMPERATURE = (
    """
    COPY dim_immigration_temperature
    FROM '{{ params.location }}'
    IAM_ROLE '{{ params.iam_role }}'
    FORMAT AS PARQUET;
    """
)
