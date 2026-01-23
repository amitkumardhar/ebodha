from app.schemas.user import User
from app.models.user import UserRole

# Simulate ORM object or dict
user_data = {
    "id": "test_user",
    "name": "Test User",
    "email": "test@example.com",
    "hashed_password": "hash",
    "is_active": True,
    "discipline_code": "CSE",
    "roles": [{"role": UserRole.STUDENT}]
}

try:
    user_schema = User.from_orm(type('UserORM', (object,), user_data))
    # Or just validate dict if not strictly ORM
    # But from_orm expects an object with attributes usually, or dict if configured?
    # Pydantic v1 from_orm expects object.
    
    # Let's use parse_obj for simplicity if we treat it as dict, 
    # but to test ORM mode we should use an object.
    class MockUser:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                if k == 'roles':
                    self.roles = [type('RoleEntry', (object,), r) for r in v]
                else:
                    setattr(self, k, v)
                    
    mock_user = MockUser(**user_data)
    user_schema = User.from_orm(mock_user)
    
    print(f"Discipline Code: {user_schema.discipline_code}")
    assert user_schema.discipline_code == "CSE"
    print("Verification Successful")
except Exception as e:
    print(f"Verification Failed: {e}")
