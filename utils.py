def sanitize_topic(topic_name: str):
    return topic_name.replace(' ', '_').replace('#', '-').replace('+', '-')