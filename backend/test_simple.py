import re

test_id = "user_1756207813041_h500zb5bk"
pattern = r"^[a-zA-Z0-9_.-]+$"
match = re.match(pattern, test_id)

print("Testing regex validation:")
print("Test ID: " + test_id)
print("Pattern: " + pattern)
print("Match result: " + str(bool(match)))

# Test actual validation
try:
    import sys
    sys.path.append('.')
    from utils.validation_utils import InputValidator
    
    print("\nTesting actual validation function:")
    result = InputValidator.validate_user_id(test_id)
    print("Validation passed: " + str(result))
except Exception as e:
    print("Validation failed: " + str(e))
