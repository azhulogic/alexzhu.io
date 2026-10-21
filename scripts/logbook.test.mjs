import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { aircraftName, aircraftType, summarizeFlights, inferFlightDates } from "../src/lib/logbook.mjs";

const logbook = JSON.parse(await readFile(new URL("../src/data/logbook.json", import.meta.url), "utf8"));

test("flight entries reconcile with expected logbook totals", () => {
  const totals = summarizeFlights(logbook.entries);
  for (const [key, expected] of Object.entries(logbook.expectedTotals)) {
    assert.equal(totals[key], expected, key);
  }
  assert.equal(totals.flights, 71);
  assert.equal(totals.landings, 294);
  assert.ok(logbook.entries.every((entry) => entry.model && entry.date && entry.hours > 0));
});

test("aircraft variants combine by type without losing future Archer and 172 records", () => {
  assert.equal(aircraftType("Cessna 150H"), "C150");
  assert.equal(aircraftType("C150"), "C150");
  assert.equal(aircraftName("Cessna 150H"), "Cessna 150");
  assert.equal(aircraftName("C150"), "Cessna 150");
  assert.equal(aircraftType("Cessna 172S"), "C172");
  assert.equal(aircraftType("C172N"), "C172");
  assert.equal(aircraftType("Piper Archer II"), "PA28");
  assert.equal(aircraftType("PA-28-181"), "PA28");
  assert.equal(aircraftType("Cessna 152"), "Cessna 152");
  const totals = summarizeFlights([
    { model: "C150", hours: 0.1 }, { model: "Cessna 150H", hours: 0.2 },
    { model: "Archer", hours: 1.1 }, { model: "C172", hours: 2.2 }
  ]);
  assert.equal(totals.hours, 3.6);
  assert.equal(totals.aircraft.find((type) => type.type === "C150").hours, 0.3);
  assert.equal(totals.aircraft.length, 3);
});

test("empty and invalid imports cannot create misleading totals", () => {
  const empty = summarizeFlights([]);
  assert.equal(empty.hours, 0);
  assert.equal(empty.landings, 0);
  assert.deepEqual(empty.aircraft, []);
  assert.throws(() => summarizeFlights([{ model: "C150", hours: -1 }]), /Invalid hours/);
});

test("chronological month/day dates roll forward from the owner's first year", () => {
  const flights = inferFlightDates(logbook.entries, logbook.firstFlightYear, logbook.yearOverrides);
  assert.equal(flights[0].date, "2021-08-30");
  assert.equal(flights[19].date, "2022-02-25");
  assert.equal(flights[23].date, "2022-03-27");
  assert.equal(flights[35].date, "2023-10-10");
  assert.equal(flights[42].date, "2023-12-21");
  assert.equal(flights[49].date, "2024-04-21");
  assert.equal(flights.find((flight) => flight.sourceRow === 86).date, "2026-05-30");
  assert.equal(flights.at(-1).date, "2026-06-27");
  assert.ok(flights.every((flight) => !flight.date.startsWith("2025-")));
  assert.ok(flights.every((entry, i) => i === 0 || entry.date >= flights[i - 1].date));
});
