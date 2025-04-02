-- Function to dynamically create tables in Supabase
-- This function takes a table name, column definitions, and optional schema name
-- and creates a table with the specified structure.

CREATE OR REPLACE FUNCTION create_table_dynamic(
    p_table_name TEXT,
    p_columns JSONB,
    p_schema_name TEXT DEFAULT 'public'
) RETURNS JSONB AS $$
DECLARE
    v_sql TEXT := '';
    v_column JSONB;
    v_column_def TEXT;
    v_primary_keys TEXT[] := '{}';
    v_result JSONB;
BEGIN
    -- Start building the CREATE TABLE statement
    v_sql := 'CREATE TABLE ' || quote_ident(p_schema_name) || '.' || quote_ident(p_table_name) || ' (';
    
    -- Process each column definition
    FOR i IN 0..jsonb_array_length(p_columns) - 1 LOOP
        v_column := p_columns->i;
        
        -- Build the column definition
        v_column_def := quote_ident(v_column->>'name') || ' ' || (v_column->>'type');
        
        -- Add nullable constraint if specified
        IF v_column ? 'nullable' AND (v_column->>'nullable')::BOOLEAN = FALSE THEN
            v_column_def := v_column_def || ' NOT NULL';
        END IF;
        
        -- Add default value if specified
        IF v_column ? 'default' THEN
            v_column_def := v_column_def || ' DEFAULT ' || (v_column->>'default');
        END IF;
        
        -- Add the column definition to the SQL statement
        IF i > 0 THEN
            v_sql := v_sql || ', ';
        END IF;
        v_sql := v_sql || v_column_def;
        
        -- Collect primary key columns
        IF v_column ? 'primary_key' AND (v_column->>'primary_key')::BOOLEAN = TRUE THEN
            v_primary_keys := array_append(v_primary_keys, v_column->>'name');
        END IF;
    END LOOP;
    
    -- Add primary key constraint if any columns are marked as primary keys
    IF array_length(v_primary_keys, 1) > 0 THEN
        v_sql := v_sql || ', PRIMARY KEY (';
        FOR i IN 1..array_length(v_primary_keys, 1) LOOP
            IF i > 1 THEN
                v_sql := v_sql || ', ';
            END IF;
            v_sql := v_sql || quote_ident(v_primary_keys[i]);
        END LOOP;
        v_sql := v_sql || ')';
    END IF;
    
    -- Close the CREATE TABLE statement
    v_sql := v_sql || ')';
    
    -- Create the schema if it doesn't exist
    IF p_schema_name != 'public' THEN
        EXECUTE 'CREATE SCHEMA IF NOT EXISTS ' || quote_ident(p_schema_name);
    END IF;
    
    -- Execute the SQL statement
    BEGIN
        EXECUTE v_sql;
        v_result := jsonb_build_object(
            'success', TRUE,
            'message', 'Table created successfully',
            'table_name', p_schema_name || '.' || p_table_name,
            'sql', v_sql
        );
    EXCEPTION WHEN OTHERS THEN
        v_result := jsonb_build_object(
            'success', FALSE,
            'message', 'Error creating table: ' || SQLERRM,
            'sql', v_sql
        );
    END;
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION create_table_dynamic TO authenticated;

-- Comment on function
COMMENT ON FUNCTION create_table_dynamic IS 'Dynamically creates a table with the specified columns and constraints';
