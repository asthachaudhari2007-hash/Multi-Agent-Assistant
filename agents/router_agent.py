def route(query):

    query = query.lower()

    if "quiz" in query:
        return "assessment"

    elif "revision" in query:
        return "revision"

    else:
        return "notes"