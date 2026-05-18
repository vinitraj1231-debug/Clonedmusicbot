def get_progress_bar(percentage):
    completed = int(percentage / 10)
    remaining = 10 - completed
    return "▬" * completed + "🔘" + "▬" * remaining

def format_duration(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
