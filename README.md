# Aegis: A Secure Access Gateway CLI

**A modular, Python-based command-line security system demonstrating enterprise-grade architecture and access control.**

\This project moves beyond a simple script to feature a professional, modular design integrating core security concepts:

| Category | Feature | Technical Implementation |
| :--- | :--- | :--- |
| **Security Core** | Password Hashing | **`bcrypt`** (via `core/auth.py`) for secure, salted password storage. |
| **Confidentiality** | Resource Encryption | **`Fernet` symmetric encryption** (via `core/encryption.py`) to protect resource paths stored in the MySQL database. |
| **Access Control** | Role-Based Access (RBAC) | Distinguishes between `admin` and `standard` users, restricting critical audit and maintenance features. |
| **System Design** | Modular Structure | Strict separation of concerns between the **`core/`** (business logic) and **`cli/`** (user interface) packages. |
| **Traceability** | Audit Logging | Logs all critical actions (Login Success/Fail, Resource Access/Fail, Admin Resets) to a timestamped file (`logs/audit.log`). |
| **Engineering** | Configuration | Uses the **`.aegisconfig`** file to externalize and secure database credentials and the encryption key. |

---


### Prerequisites

* **Python 3.8+**
* **MySQL Server** (Ensure your server is running before starting Aegis.)

### 1. Get the Code

```bash
git clone https://github.com/rajveersingh2626/Aegis
cd aegis
```

# IMPORTANT
Also make a .aegisconfig file in the following directory with certain details in the root directory once you clone/download the project

[MYSQL]
HOST = localhost
USER = [YOUR root USERNAME]
PASSWORD = [YOUR PASSWORD]
DATABASE = aegis_db

[SECURITY]
ENCRYPTION_KEY = DWw4aC3k7hGoFnC5huSMJVSOwMPtphy03Lw_WKRiAbA=


