import duckdb # type: ignore
import os
import shutil
from typing import List, Tuple, Dict

class LookupEngine:
    """
    High-Performance Lookup Engine using DuckDB for out-of-core processing.
    Supports Multi-File Chain Joining (Data Enrichment).
    """
    def __init__(self, temp_dir: str = "duckdb_temp"):
        self.temp_dir = temp_dir
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        
        # Initialize connection
        self.con = duckdb.connect(database=':memory:')
        
        # Load extensions
        try:
            self.con.execute("LOAD spatial;")
        except Exception:
            try:
                self.con.execute("INSTALL spatial; LOAD spatial;")
            except Exception as e:
                print(f"Extension install warning: {e}")

        self.con.execute(f"SET temp_directory='{self.temp_dir}'")
        self.con.execute("SET preserve_insertion_order=false")
        
    def _read_func(self, file_path: str) -> str:
        """Determines the correct DuckDB read function based on file extension."""
        if not file_path:
            return ""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.parquet':
            return f"read_parquet('{file_path}')"
        elif ext == '.csv':
            return f"read_csv_auto('{file_path}', ignore_errors=True)"
        elif ext in ['.xlsx', '.xls']:
            return f"spatial.st_read('{file_path}')"
        elif ext in ['.txt', '.tsv']:
            return f"read_csv_auto('{file_path}', sep='\\t', ignore_errors=True)"
        else:
            return f"read_csv_auto('{file_path}', ignore_errors=True)"

    def get_columns(self, file_path: str) -> List[str]:
        """Scans the header of a file without loading data into memory."""
        if not file_path or not os.path.exists(file_path):
            return []
        
        try:
            read_stmt = self._read_func(file_path)
            res = self.con.execute(f"SELECT * FROM {read_stmt} LIMIT 0").description
            return [col[0] for col in res]
        except Exception as e:
            print(f"Error scanning columns: {e}")
            return []

    def _generate_multi_join_query(self, 
                                  file_a: str, 
                                  ref_files: List[Dict]) -> str:
        """
        Generates a SQL query for a chain of LEFT JOINs.
        ref_files structure: [{'path': str, 'match_pairs': List[Tuple], 'pull_cols': List[str]}]
        """
        read_a = self._read_func(file_a)
        
        # Start building the SELECT and FROM clauses
        select_parts = ["A.*"]
        from_clause = f"{read_a} AS A"
        
        for i, ref in enumerate(ref_files):
            alias = f"R{i}"
            read_ref = self._read_func(ref['path'])
            
            # Add columns to pull
            for col in ref['pull_cols']:
                # Alias to avoid collisions: R0_email, R1_phone etc
                select_parts.append(f"{alias}.\"{col}\" AS \"{alias}_{col}\"") # type: ignore
            
            # Build JOIN condition
            join_conds = []
            for pair in ref['match_pairs']:
                join_conds.append(f"A.\"{pair[0]}\" = {alias}.\"{pair[1]}\"") # type: ignore
            
            join_clause = " AND ".join(join_conds)
            from_clause += f" LEFT JOIN {read_ref} AS {alias} ON {join_clause}" # type: ignore
            
        query = f"SELECT {', '.join(select_parts)} FROM {from_clause}" # type: ignore
        return query

    def execute_multi_join(self, 
                           file_a: str, 
                           ref_files: List[Dict], 
                           output_path: str,
                           output_format: str = 'csv'):
        """Performs disk-to-disk multi-file join."""
        query = self._generate_multi_join_query(file_a, ref_files)
        
        try:
            if output_format.lower() == 'parquet':
                self.con.execute(f"COPY ({query}) TO '{output_path}' (FORMAT PARQUET)")
            else:
                self.con.execute(f"COPY ({query}) TO '{output_path}' (FORMAT CSV, HEADER)")
            return True, f"Success! Chain join completed."
        except Exception as e:
            return False, f"SQL Error: {str(e)}"

    def get_multi_preview(self, 
                          file_a: str, 
                          ref_files: List[Dict], 
                          limit: int = 10):
        """Generates a preview for the chain join."""
        query = self._generate_multi_join_query(file_a, ref_files)
        query += f" LIMIT {limit}"
        try:
            return self.con.execute(query).df()
        except Exception as e:
            print(f"Preview error: {e}")
            return None

    def cleanup(self):
        """Closes connection and removes temp files."""
        try:
            self.con.close()
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
