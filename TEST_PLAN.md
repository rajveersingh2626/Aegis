Scenario 1: Authentication Test
Action: Try to log in with the wrong password three times.
Expected Result: System prints "Invalid credentials." (Future goal: Lockout mechanism).



Scenario 2: Relational Integrity Test
Action: Link two files. Then, use the "Delete Account" feature.
Expected Result: Both linked files and the user's account are removed from the MySQL database (verified via MySQL workbench).



Scenario 3: RBAC Test
Action: Log in as a standard user and try to enter menu option 5.
Expected Result: System prints "Invalid choice or insufficient permissions."
