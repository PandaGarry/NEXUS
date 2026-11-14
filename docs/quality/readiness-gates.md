# Prototype Readiness Gates

**Current decision: BLOCKED**

Operational evidence register: [NX-PROJECT-CHECKLIST-001](NX-PROJECT-CHECKLIST-001-execution-and-evidence.md).

Прототипирование не начинается, пока критические gates не имеют PASS и evidence.

| Gate | Условие допуска | Статус |
|---|---|---|
| G0 Scope | Product scope и bounded v1 decisions зафиксированы | PASS (scope baseline only) |
| G0D Documentation baseline | Cross-document consistency, indexes, PR integration plan, owner approval and evidence traceability completed | BLOCKED |
| G1 Source audit | Критичные исходники, тесты, CI, миграции, зависимости проверены | BLOCKED |
| G2 Market data | Timestamp, sequence, checksum, units, aggressor, reconnect/recovery определены | BLOCKED |
| G3 Financial correctness | Instrument specs, exact arithmetic, fees/funding и ledger semantics определены | BLOCKED |
| G4 Execution integrity | Idempotency, unknown outcome, partial fills, reconciliation и restart recovery определены | BLOCKED |
| G5 Risk independence | Independent veto, limits, kill switch и fail-closed поведение определены | BLOCKED |
| G6 Security | Threat model, vault, permissions, auth, audit и incident response определены | BLOCKED |
| G7 Simulation | Модели исполнения, ограничения и validation protocol определены | BLOCKED |
| G8 Architecture | ADR, service boundaries, deployment, persistence и observability утверждены | BLOCKED |
| G9 Verification | Тестирование, evidence и acceptance process готовы | BLOCKED |

PASS допускается только со ссылками на evidence. Отсутствие данных не равно PASS. Любой неизвестный критический риск удерживает gate в BLOCKED.


**Important distinction:** G0 scope PASS is not a documentation-freeze or architecture-approval PASS. NX-DOC-REVIEW-001 records the remaining close-out items. Prototype Readiness remains BLOCKED until all applicable gates have commit-specific evidence and required owner approvals.
