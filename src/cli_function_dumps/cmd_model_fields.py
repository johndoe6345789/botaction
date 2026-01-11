# Auto-generated extract of cli.py
# See cli.py for shared context and imports

def cmd_model_fields(args):
    """Display model property field definitions."""
    
    print(HEADERS['model_props'])
    print("=" * 60)
    print(SUBHEADERS['field_definitions'])
    print()
    
    for field_name, field_def in MODEL_PROPERTIES.items():
        print(f"\n{field_name}")
        print(f"  Type: {field_def['type']}")
        for key, value in field_def.items():
            if key != 'type':
                print(f"  {key}: {value}")
    
    print(f"\n\n{MODEL_FIELDS_LABELS['groups_header']}")
    print("-" * 40)
    for group, fields in USER_PROFILE_FIELDS.items():
        print(f"\n{group.upper()}:")
        for field in fields:
            print(f"  • {field}")
    
    return 0
