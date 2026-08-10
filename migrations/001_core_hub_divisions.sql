CREATE TABLE divisions (
    division_id     SMALLSERIAL PRIMARY KEY,
    division_name   VARCHAR(50) NOT NULL UNIQUE,
    division_code   VARCHAR(10) NOT NULL UNIQUE  -- 'RETAIL', 'LOGISTICS', 'VFS', 'AGRI', 'PROPS', 'GROUP'
);