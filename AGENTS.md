# RoutePulse engineering rules
Keep simulation independent of HTTP and persistence. Never exceed physical capacity.
Planning uses historical seeds; evaluation uses a separate fixed scenario seed.
Validate every recommendation and retain baseline, inputs, results and seeds.
Run pytest, TypeScript checking, lint and browser workflow before delivery.
Do not replace computed results with demo constants. Document limitations honestly.
