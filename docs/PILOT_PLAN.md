# Proposed campus pilot

Status: research plan only. No interviews, customers, field results or willingness-to-pay measurements have been collected.

## User and buyer hypothesis

Daily user: campus dispatcher or transport supervisor. Beneficiary: students and staff waiting at stops, including transfer passengers. Potential buyer: the university transport or facilities office. A paid campus software subscription is a hypothesis to test after demonstrating value; no price, market size or savings forecast is assumed.

## Discovery evidence to gather

Interview one transport supervisor, two drivers and five riders across different stops. Ask about the last actual missed connection or overloaded queue, how the supervisor responded, what information was available, and what operational rules prevented a change. Observe a morning peak with permission. Record anonymous notes, date, role, direct observation versus reported experience, and contradictions. Do not treat the proposed sample as representative proof.

Questions for the supervisor: Who can approve reassignment? Which duty or labor constraints are missing here? Are nominal passenger capacities safe operating limits? What is the cost of a late departure? What action would you decline even if aggregate service improves? Who owns the budget and data integrations?

Questions for riders: Where and when did you wait? How many vehicles passed before boarding? Did you transfer? What would make a prediction useful? Avoid leading questions asking whether they like the product.

## Data and staged evaluation

1. Acquire approved, de-identified historical GPS traces, stop boarding/alighting counts, route geometry, timetables, capacities and outage logs. Do not collect rider identities for aggregate planning.
2. Use an earlier contiguous period for calibration and a later period for evaluation. Preserve the split and version the data. Model road conditions, dwell and operational constraints missing from this MVP.
3. Run in shadow mode: generate proposals without dispatching. Compare arrival errors, completion, wait distributions and transfers against measured history. A simulator counterfactual remains modeled, not an observed causal benefit.
4. Agree on a supervised trial with the transport office only after data and feasibility review. Predefine comparable periods and operational exceptions; preserve manual control and rollback.

## Proposed acceptance criteria to agree before the trial

- Zero capacity violations or assignments that break confirmed operating rules.
- Lower average and upper-tail wait while tracking completed journeys and cancellations.
- Explicit maximum permitted transfer regression and stop-level service loss, agreed with the operator.
- Measured ETA error and empirical interval coverage on the held-out data.
- Dispatchers can understand, accept or reject a proposal and explain why.
- Integration, support and operating costs measured before claiming net savings.

The current rush validation shows why the transfer threshold matters: a service-first plan can improve overall journeys while worsening connections. The shadow pilot must decide whether that trade-off is acceptable, rather than assuming aggregate gains are sufficient.
