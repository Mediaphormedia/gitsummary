from south.modelsinspector import add_introspection_rules
from timezones.fields import TimeZoneField, MAX_TIMEZONE_LENGTH


add_introspection_rules(rules=[(
    (TimeZoneField, ),  # Class(es) these apply to
    [],                 # Positional arguments (not used)
    {                   # Keyword argument
        "max_length": ["max_length", {"default": MAX_TIMEZONE_LENGTH}],
    }
)], patterns=['timezones\.fields\.'])
