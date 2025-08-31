import re

test_id = "user_1756207813041_h500zb5bk"
pattern = r"^[a-zA-Z0-9_.-]+$"
match = re.match(pattern, test_id)

print("Test ID:", test_id)
print("Pattern:", pattern)
print("Match result:", bool(match))

# Test each character
print("\nCharacter analysis:")
for i, c in enumerate(test_id):
    valid = c.isalnum() or c in '_.-'
    print(f"{i:2}: '{c}' -> {valid}")

print(f"\nAll characters valid: {all(c.isalnum() or c in '_.-' for c in test_id)}")

# Test the actual validation function
try:
    import sys
    sys.path.append('.')
    from utils.validation_utils import InputValidator
    
    print("\nTesting actual validation function:")
    result = InputValidator.validate_user_id(test_id)
    print(f"✅ Validation passed: {result}")
except Exception as e:
    print(f"❌ Validation failed: {e}")
