export const logbookColumns = [
  { key: "hours", label: "Total", unit: "hours" },
  { key: "pic", label: "PIC", unit: "hours" },
  { key: "solo", label: "Solo", unit: "hours" },
  { key: "dual", label: "Dual", unit: "hours" },
  { key: "night", label: "Night", unit: "hours" },
  { key: "crossCountry", label: "XC", unit: "hours" },
  { key: "crossCountry50", label: "XC 50nm+", unit: "hours" },
  { key: "simulatedInstrument", label: "Hood", unit: "hours" },
  { key: "actualInstrument", label: "Actual", unit: "hours" },
  { key: "simulator", label: "Sim", unit: "hours" },
  { key: "singleEngine", label: "Single", unit: "hours" },
  { key: "multiEngine", label: "Multi", unit: "hours" },
  { key: "groundTraining", label: "Ground", unit: "hours" },
  { key: "dayLandings", label: "Day LDG", unit: "count" },
  { key: "nightLandings", label: "Night LDG", unit: "count" }
];

export function aircraftType(model) {
  if (/\b(?:C150\w*|Cessna\s*150\w*)\b/i.test(model)) return "C150";
  if (/\b(?:C172\w*|Cessna\s*172\w*)\b/i.test(model)) return "C172";
  if (/Archer|PA[- ]?28[- ]?181/i.test(model)) return "PA28";
  return model;
}

export function aircraftName(model) {
  return { C150: "Cessna 150", C172: "Cessna 172", PA28: "Piper Archer" }[aircraftType(model)] ?? model;
}

// Entries are chronological; explicit owner-confirmed years override rollover
// inference when a year has no flights.
export function inferFlightDates(entries, firstYear, yearOverrides = {}) {
  let year = firstYear;
  let previous = 0;
  return entries.map((entry) => {
    const [month, day] = entry.date.split("/").map(Number);
    const ordinal = month * 100 + day;
    if (ordinal < previous) year += 1;
    if (yearOverrides[entry.sourceRow] !== undefined) year = yearOverrides[entry.sourceRow];
    previous = ordinal;
    const date = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    if (new Date(`${date}T00:00:00Z`).toISOString().slice(0, 10) !== date) {
      throw new Error(`Invalid date at row ${entry.sourceRow}`);
    }
    return { ...entry, date };
  });
}

export function summarizeFlights(entries) {
  const tenths = Object.fromEntries(logbookColumns.map(({ key }) => [key, 0]));
  const aircraft = new Map();
  const tails = new Set();
  for (const entry of entries) {
    for (const { key } of logbookColumns) {
      const value = Number(entry[key] ?? 0);
      if (!Number.isFinite(value) || value < 0) throw new Error(`Invalid ${key} at row ${entry.sourceRow}`);
      tenths[key] += Math.round(value * 10);
    }
    const type = aircraftType(entry.model);
    const group = aircraft.get(type) ?? { type, tenths: 0, flights: 0 };
    group.tenths += Math.round(entry.hours * 10);
    group.flights += 1;
    aircraft.set(type, group);
    if (entry.tail) tails.add(entry.tail);
  }
  return {
    ...Object.fromEntries(Object.entries(tenths).map(([key, value]) => [key, value / 10])),
    flights: entries.length,
    landings: (tenths.dayLandings + tenths.nightLandings) / 10,
    tails: tails.size,
    aircraft: [...aircraft.values()].map(({ tenths, ...group }) => ({ ...group, hours: tenths / 10 }))
  };
}
