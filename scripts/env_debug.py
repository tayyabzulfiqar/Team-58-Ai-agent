"""
Environment Variable Debug Module
Use this to check if all required env vars are loaded correctly
Works in both local (.env) and Railway (environment) deployments
"""

import os


def print_env_status():
    """Print status of all critical environment variables"""
    
    print("\n" + "="*60)
    print("ENVIRONMENT VARIABLE DEBUG REPORT")
    print("="*60)
    
    keys = [
        "FIRECRAWL_API_KEY",
        "ANTHROPIC_API_KEY",
        "BASE_URL",
        "MODEL"
    ]
    
    all_found = True
    
    for key in keys:
        value = os.getenv(key)
        if value:
            # Mask the actual value for security, just show length
            masked = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
            print(f"✓ {key}: FOUND (length: {len(value)} chars)")
        else:
            print(f"✗ {key}: MISSING")
            all_found = False
    
    print("="*60)
    if all_found:
        print("STATUS: All environment variables loaded successfully")
    else:
        print("STATUS: Some environment variables are missing")
        print("HINT: Set them in Railway dashboard or local .env file")
    print("="*60 + "\n")
    
    return all_found


if __name__ == "__main__":
    print_env_status()
