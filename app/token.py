import os
import secrets

# Generate a random API token (change the token_length as needed)
def generate_api_token(token_length=32):
    return secrets.token_hex(token_length)

# Store the generated token securely (e.g., in a configuration file or database)
def save_api_token_to_file(filename='api_token.txt'):
    api_token = generate_api_token()
    with open(filename, 'w') as token_file:
        token_file.write(api_token)
    return api_token

# Function to read the API token from the file
def read_api_token_from_file(filename='api_token.txt'):
    with open(filename, 'r') as token_file:
        api_token = token_file.read().strip()
    return api_token

# Initial generation and saving of the API token
API_TOKEN = save_api_token_to_file()
