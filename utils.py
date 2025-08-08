def sanitize_topic(topic_name: str):
    return (topic_name
            .replace(' ', '-')
            .replace('#', '-')
            .replace('+', '-')
            .replace('Ä', 'AE')
            .replace('Ö', 'OE')
            .replace('Ü', 'UE')
            .replace('ä', 'ae')
            .replace('ö', 'oe')
            .replace('ü', 'ue')
            .replace('ß', 'ss')
            )