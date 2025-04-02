-- Function to execute arbitrary SQL statements
-- This function is used for administrative purposes and should be used with caution

CREATE OR REPLACE FUNCTION execute_sql(
    sql TEXT
) RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
BEGIN
    -- Execute the SQL statement
    BEGIN
        EXECUTE sql;
        v_result := jsonb_build_object(
            'success', TRUE,
            'message', 'SQL executed successfully',
            'sql', sql
        );
    EXCEPTION WHEN OTHERS THEN
        v_result := jsonb_build_object(
            'success', FALSE,
            'message', 'Error executing SQL: ' || SQLERRM,
            'sql', sql
        );
    END;
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION execute_sql TO authenticated;

-- Comment on function
COMMENT ON FUNCTION execute_sql IS 'Executes arbitrary SQL statements. Use with caution.';
