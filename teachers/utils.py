import pygsheets
import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from thefuzz import fuzz


def preprocess_name(name: Any) -> str:
    """Cleans and normalizes a name string for comparison."""
    if not isinstance(name, str):
        return "" # Return empty if not a string

    processed_name = name.lower() # Convert to lowercase

    # Remove common titles/prefixes using regex (word boundary \b is important)
    # Add more titles to the list as needed
    titles_to_remove = [r'\b(lic|dr|ing|arq|ms|msc|sr|sra|srta)\b\.?', r'\b(licenciado|doctor|ingeniero|maestro)\b']
    for title_pattern in titles_to_remove:
         processed_name = re.sub(title_pattern, '', processed_name, flags=re.IGNORECASE).strip()

    # Remove extra whitespace (multiple spaces become one)
    processed_name = re.sub(r'\s+', ' ', processed_name).strip()

    # Optional: remove punctuation if needed (might remove important hyphens in names?)
    # processed_name = re.sub(r'[^\w\s]', '', processed_name) # Example: removes non-alphanumeric/space

    return processed_name


# Corrected Type Hint
def get_pygsheets_client(service_file_path: str) -> pygsheets.client.Client:
    """
    Authorizes access to Google Sheets API using a service account file
    and returns a pygsheets client instance.

    Args:
        service_file_path: The file path to the service account JSON key file.

    Returns:
        An authorized pygsheets.Client instance ready for use.

    Raises:
        FileNotFoundError: If the service_file_path does not point to an existing file.
        pygsheets.exceptions.AuthenticationError: If authentication fails due to
            invalid credentials or insufficient permissions configured for the
            service account.
        Exception: For other potential errors during the authorization process
                   from the pygsheets library.
    """
    try:
        client = pygsheets.authorize(service_file=service_file_path)
        return client
    except FileNotFoundError:
        raise
    except pygsheets.exceptions.AuthenticationError as auth_err:
        raise
    except Exception as e:
        raise


def extract_sheet_key_from_url(url: str) -> Optional[str]:
    """
    Extracts the Google Sheet key from its URL using regular expressions.

    The key is typically the long string of characters found between
    '/spreadsheets/d/' and the next '/'.

    Args:
        url: The full URL of the Google Sheet.

    Returns:
        The extracted sheet key as a string if found, otherwise None.
        Returns None for invalid URL formats that don't match the pattern.
    """
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    if match:
        return match.group(1)
    else:
        return None


def find_valid_teacher_worksheets(
    sheet_url: str,
    service_file_path: str,
    header_cell: str = 'E3',
    expected_header_value: str = 'DOCENTE',
    teacher_name_cell: str = 'E4',
    similarity_threshold: int = 80 # NEW: Similarity threshold (0-100)
) -> List[str]:
    """
    Finds worksheets using header validation and FUZZY name matching.

    Validation Steps:
    1. Checks if `header_cell` matches `expected_header_value`.
    2. Performs FUZZY matching between the cleaned teacher's name in
       `teacher_name_cell` and the cleaned name inferred from the
       spreadsheet's title. Only includes worksheets where the similarity
       score meets or exceeds `similarity_threshold`.

    Args:
        sheet_url: Full URL of the Google Spreadsheet.
        service_file_path: Path to the service account JSON file.
        header_cell: Cell for static header check (default 'E3').
        expected_header_value: Expected header string (default 'DOCENTE').
        teacher_name_cell: Cell with the teacher's name (default 'E4').
        similarity_threshold: Minimum score (0-100) from fuzzy match to
                              consider names a match (default 80).

    Returns:
        A list of titles (strings) of worksheets passing both validation steps.

    Raises:
        ValueError: If sheet key extraction fails.
        FileNotFoundError: If service file not found.
        pygsheets.exceptions.AuthenticationError: If authentication fails.
        pygsheets.SpreadsheetNotFound: If sheet not found or permission denied.
        RuntimeError: For unexpected errors during worksheet processing.
        ImportError: If 'thefuzz' library is not installed.
    """
    sheet_key = extract_sheet_key_from_url(sheet_url)
    if not sheet_key:
        raise ValueError(f"Could not extract valid sheet key from URL: {sheet_url}")

    gc = get_pygsheets_client(service_file_path)
    try:
        sh = gc.open_by_key(sheet_key)
    except pygsheets.SpreadsheetNotFound:
        raise

    valid_titles: List[str] = []
    spreadsheet_title = sh.title # Get original title

    # --- Extract and clean name part from title ---
    # Assume format NAME_EXTRAINFO or just NAME
    title_parts = spreadsheet_title.strip().split('_', 1)
    name_part_in_title_raw = title_parts[0].strip()
    # Preprocess the extracted title part
    clean_name_title = preprocess_name(name_part_in_title_raw)

    try:
        for wks in sh.worksheets():
            # --- Step 1: Header Check (Same as before) ---
            header_cell_value_raw = wks.get_value(header_cell)
            if not isinstance(header_cell_value_raw, str): continue
            header_cell_value_norm = header_cell_value_raw.strip().upper()
            if header_cell_value_norm != expected_header_value.upper(): continue

            # --- Step 2: Fuzzy Teacher Name Check ---
            name_in_cell_raw = wks.get_value(teacher_name_cell)
            if not isinstance(name_in_cell_raw, str) or not name_in_cell_raw.strip():
                # print(f"DEBUG: Skipping sheet '{wks.title}', name cell {teacher_name_cell} empty or not string.")
                continue # Skip if name cell empty/not string

            # Preprocess the name found in the cell
            clean_name_cell = preprocess_name(name_in_cell_raw)

            if not clean_name_title or not clean_name_cell:
                # If either name becomes empty after cleaning, skip comparison
                # print(f"WARN: Skipping comparison due to empty cleaned name. Title:'{clean_name_title}', Cell:'{clean_name_cell}'")
                continue

            # Calculate fuzzy similarity score using token_set_ratio
            # This handles different word orders and subsets well
            similarity_score = fuzz.token_set_ratio(clean_name_cell, clean_name_title)

            # print(f"DEBUG: Comparing '{clean_name_cell}' vs '{clean_name_title}' -> Score: {similarity_score}")

            # Check if score meets the threshold
            if similarity_score >= similarity_threshold:
                # print(f"DEBUG: Match found for worksheet '{wks.title}' (Score: {similarity_score} >= {similarity_threshold})")
                valid_titles.append(wks.title)
            # else:
                # Optional: Log low scores for debugging thresholds
                # print(f"INFO: Name mismatch below threshold for worksheet '{wks.title}'. Score: {similarity_score}")


    except ImportError:
         print("ERROR: The 'thefuzz' library is required for fuzzy matching. Please install it (`pip install thefuzz`).")
         raise # Re-raise the import error
    except Exception as e:
        # Catch other potential errors during processing
        raise RuntimeError(f"Error processing worksheets in sheet {sheet_key}") from e

    return valid_titles


def parse_percentage(value: Any) -> Optional[float]:
    """Converts string percentages like '100,00%' or '25%' to float (e.g., 100.0, 25.0)."""
    if isinstance(value, (int, float)): return float(value)
    if not isinstance(value, str): return None
    try:
        cleaned_value = value.replace(',', '.').strip().rstrip('%').strip()
        return float(cleaned_value) if cleaned_value else None
    except (ValueError, TypeError): return None

def parse_date(value: Any) -> Optional[datetime.date]:
    """Converts string dates like '6/3/25' to datetime.date objects."""
    #if isinstance(value, datetime.date): return value.date()
    if isinstance(value, date): return value
    if not isinstance(value, str): return None
    cleaned_value = value.strip()
    if not cleaned_value: return None
    try:
        return datetime.strptime(cleaned_value, '%d/%m/%y').date()
    except (ValueError, TypeError): return None

# Updated extraction function
def extract_worksheet_data(worksheet: pygsheets.Worksheet) -> Dict[str, List[Dict]]:
    """
    Extracts Period Progress and Topic Completion data from a validated worksheet.
    Identifies topic rows based on the presence of a title in Column E.

    Args:
        worksheet: A pygsheets.Worksheet object assumed to have passed validation.

    Returns:
        A dictionary containing two lists:
        'period_progress': List of dicts for PeriodProgress model updates.
        'topic_completion': List of dicts for TopicCompletion model updates.
    """
    results: Dict[str, List[Dict]] = {'period_progress': [], 'topic_completion': []}
    grade_level = worksheet.title # Assuming worksheet title IS the grade level

    try:
        df = worksheet.get_as_df(start='A3', end='R358',
                                 header=None,
                                 include_tailing_empty=False,
                                 numerize=False,
                                 empty_value='')
    except Exception as e:
        print(f"ERROR: Failed to get data as DataFrame from worksheet '{grade_level}': {e}")
        return results

    current_periodo = 0
    # Flag to indicate the *next* row should contain period progress %
    expect_period_progress_next = False
    paralelos = ['A', 'B', 'C', 'D']
    paralelo_indices = {'A': 14, 'B': 15, 'C': 16, 'D': 17} # O, P, Q, R

    for index, row in df.iterrows():
        row_values = list(row)

        # --- Check for Period Header ---
        # Check Column A (index 0) or G (index 6) for "PERIODO" text
        # Use default '' if index out of bounds (though unlikely with fixed range)
        cell_a = str(row_values[0]).strip().upper() if len(row_values) > 0 else ''
        cell_g = str(row_values[6]).strip().upper() if len(row_values) > 6 else ''
        period_match = re.search(r'(\d+)(?:ER|DO|ER|TO|TO|TO) PERIODO', cell_a + cell_g)

        if period_match:
            current_periodo = int(period_match.group(1))
            # Set flag: the row *after* this one should have the progress %
            expect_period_progress_next = True
            # print(f"DEBUG: Found Period {current_periodo} at df index {index}. Expecting progress next.")
            continue # Header row doesn't contain progress or topic data

        # --- Check for Period Progress ---
        # This check happens *before* the topic check for the same row
        if expect_period_progress_next:
            # print(f"DEBUG: Checking for Period {current_periodo} progress at df index {index}")
            for paralelo, col_idx in paralelo_indices.items():
                if col_idx < len(row_values):
                    progress_val = parse_percentage(row_values[col_idx])
                    if progress_val is not None and current_periodo > 0:
                        results['period_progress'].append({
                            'grade_level': grade_level,
                            'periodo': current_periodo,
                            'paralelo': paralelo,
                            'progress_percentage': progress_val,
                        })
            # Whether progress was found or not, reset the flag after checking this row
            expect_period_progress_next = False
            # Progress row doesn't contain topic data, move to next row
            continue

        # --- Check for Topic Completion Data (Triggered by Title in Column E)---
        # Ensure column E (index 4) exists and get title
        if len(row_values) > 4:
            tema_title_raw = str(row_values[4]).strip()
        else:
            tema_title_raw = '' # Column E doesn't exist on this row

        # Check if Column E has content and we know the current period
        if tema_title_raw and current_periodo > 0:
            # We found a topic title, this row likely contains topic data.
            # Get the Tema Number from Column D (index 3) on the same row.
            tema_number_raw = str(row_values[3]).strip() if len(row_values) > 3 else ''
            # print(f"DEBUG: Found Tema Title '{tema_title_raw}' (Num: '{tema_number_raw}') in Period {current_periodo} at df index {index}")

            for paralelo, col_idx in paralelo_indices.items():
                 if col_idx < len(row_values): # Ensure date column index is valid
                    completion_date = parse_date(row_values[col_idx])
                    if completion_date is not None:
                        results['topic_completion'].append({
                            'grade_level': grade_level,
                            'periodo': current_periodo,
                            'paralelo': paralelo,
                            'tema_number': tema_number_raw, # Store number found (or empty)
                            'tema_title': tema_title_raw,
                            'completion_date': completion_date,
                        })
            # This row was processed as topic data, continue to next row
            continue

        # If none of the above conditions met, it's likely a spacer row or secondary description row.
        # Reset the period progress flag if it was somehow still set (shouldn't happen with continues).
        expect_period_progress_next = False


    return results