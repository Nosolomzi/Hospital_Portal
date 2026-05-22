def login():
    # Username: Hospital2026!
    # Password: GAUTENGEMS
    
    print("\n HOSPITAL PORTAL LOGIN")
    print("-------------------------")
    
    user_input = input("Username: ").strip()
    pass_input = input("Password: ").strip()

    if user_input == "Hospital2026!" and pass_input == "GAUTENGEMS":
        print("\n LOGIN SUCCESSFUL! Accessing system...")
        return True
    else:
        print("\n ACCESS DENIED.")
        print(f"Check: You typed Username: '{user_input}' and Password: '{pass_input}'")
        return False


