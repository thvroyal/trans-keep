# Appendix: Technology Cheat Sheet

**Frontend:**
```bash
npm create vite@latest -- --template react-ts
npm install react-router-dom @tanstack/react-query zustand
npm install -D @tailwindcss/vite tailwindcss@next
npm install -D eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-plugin-react eslint-plugin-react-hooks prettier eslint-config-prettier eslint-plugin-prettier
npm install pdfjs-dist
```

**Backend:**
```bash
pip install fastapi uvicorn pydantic sqlalchemy psycopg2-binary
pip install celery redis
pip install PyMuPDF deepl anthropic
pip install python-jose google-auth google-auth-oauthlib
pip install alembic
```

**Infrastructure:**
```bash
# AWS CLI commands
aws ecr create-repository --repository-name transkeep
aws rds create-db-instance --db-instance-identifier transkeep-db
aws s3 mb s3://transkeep-bucket
aws iam create-role --role-name ECSTaskRole
```

---

**Status:** Ready for Sprint Planning & Development  
**Created:** November 14, 2025  
**Track:** Enterprise Method - Greenfield  
**MVP Timeline:** 1 month

