

## 🚀 New Uploads Guide (Onboarding New Skills)

Welcome to the new uploads! This section provides guidance on how to onboard and integrate newly uploaded agent skills or components into the platform.

### 📥 How to Onboard New Uploads
1. **Directory Structure**: Ensure all new skills are placed within the `Agent Skills/` directory in their respective sub-folders.
2. **Configuration**: Update the root-level `.env.example` and `docker-compose.yml` if the new upload requires specific environment variables or services.
3. **Registration**: Ensure the new skill is correctly integrated into the main application logic if necessary.

### 🛠 Initial Local Setup Tips for New Uploads
- **Validation**: Test the new component locally before pushing.
- **Docker**: Rebuild containers to include any new dependencies:
  ```bash
  docker-compose up --build -d
  ```
