# Безопасность\n\n## Threat model\n- [NX-SEC-001 — Threat Model & Credential Isolation](NX-SEC-001-threat-model-credential-isolation.md) — Proposed; design baseline only, no controls implemented or tested.

Security design — блокирующая часть допуска к прототипу и live.

Обязательные темы:
- threat model и trust boundaries;
- exchange API key vault, минимальные permissions, отсутствие withdrawal;
- изоляция AI Orchestrator от credentials и прямого execution;
- независимый Risk Engine;
- MFA / step-up authentication для чувствительных действий;
- audit log без секретов;
- kill switch и safe shutdown;
- защита от replay, duplicate commands и compromised clients;
- backup, restore и disaster recovery;
- dependency/supply-chain и license review;
- incident response и key rotation.

Ни один секрет, API key, token, пароль, seed или приватный конфигурационный файл не должен попадать в git, issue, logs или release artifacts.
