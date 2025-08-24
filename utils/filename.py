import datetime

# For Generating a filename
def generate_filename(prefix, file_format):
    # Generate timestamp for unique filenames
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create filename with timestamp and index
    filename = f"{prefix}_{timestamp}"
    full_filename = f"{filename}.{file_format.lower()}"
    return full_filename