# Security

Dust Lord controls a physical robot vacuum and may interact with smart speakers.

Do not commit:

- Roborock account tokens
- local keys
- cloud cache files
- device IDs you consider private
- home maps
- camera/home-security data
- private IPs if your threat model treats them as sensitive

Use `.env.example` as a template and keep real config in `.env` or your service manager.
