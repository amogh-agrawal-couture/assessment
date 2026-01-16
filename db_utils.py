import csv
from psycopg2.extras import execute_values


def bulk_insert(cursor, table, columns, values, returning=None):
    """
    Generic bulk insert wrapper.

    Args:
        cursor: Database cursor
        table: Table name
        columns: List of column names
        values: List of tuples to insert
        returning: List of columns to return (None for no return)

    Returns:
        List of fetched rows if returning is specified, None otherwise
    """
    cols_str = ", ".join(columns)
    query = f"INSERT INTO {table} ({cols_str}) VALUES %s"

    if returning:
        ret_str = ", ".join(returning)
        query += f" RETURNING {ret_str}"

    execute_values(cursor, query, values)
    return cursor.fetchall() if returning else None


def bulk_update(cursor, table, set_columns, from_values, where_clause):
    """
    Generic bulk update using VALUES clause.

    Args:
        cursor: Database cursor
        table: Table name to update
        set_columns: Dict mapping column names to their source in VALUES (e.g., {'total_amount': 'c.total'})
        from_values: List of tuples for the VALUES clause
        where_clause: WHERE condition (e.g., 'o.order_id = c.order_id')
    """
    # Build SET clause
    set_clause = ", ".join([f"{col} = {val}" for col, val in set_columns.items()])

    # Build VALUES column list
    value_cols = ", ".join([f"col{i}" for i in range(len(from_values[0]))])

    query = f"""
        UPDATE {table} AS o
        SET {set_clause}
        FROM (VALUES %s) AS c({value_cols})
        WHERE {where_clause}
    """

    execute_values(cursor, query, from_values)


def write_csv(filepath, headers, rows):
    """
    Write data to CSV file.

    Args:
        filepath: Path object or string for the output file
        headers: List of column headers
        rows: List of data rows
    """
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)