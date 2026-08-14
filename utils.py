from passlib.context import CryptContext

pwd_context = CryptContext(
schemes=["bcrypt"],
deprecated="auto"
)
password = "mypassword"
hashed_password = pwd_context.hash("mypassword")
print("Hash:",hashed_password)
result = pwd_context.verify(
    "wrongpassword",
    hashed_password
)
print("Password correct:", result)