function ResultsTable({ matches, winner }) {

  return (
    <table className="results">

      <thead>
        <tr>
          <th>#</th>
          <th>Vendor</th>
          <th>Tech</th>
          <th>Finance</th>
          <th>Risk</th>
          <th>Total</th>
        </tr>
      </thead>

      <tbody>

        {matches.map((m, i) => (

          <tr
            key={i}
            className={
              winner?.vendor_name === m.vendor_name
                ? "winner-row"
                : ""
            }
          >

            <td>{i + 1}</td>

            <td>{m.vendor_name}</td>

            <td>{m.technical_score}</td>

            <td>{m.financial_score}</td>

            {/* Risk Section */}
            <td>

              <strong>{m.risk_score}</strong>

              <div
                className={
                  m.risk_score >= 80
                    ? "risk-low"
                    : m.risk_score >= 60
                    ? "risk-medium"
                    : "risk-high"
                }
              >
                {m.risk_score >= 80
                  ? "🟢 Low Risk"
                  : m.risk_score >= 60
                  ? "🟡 Medium Risk"
                  : "🔴 High Risk"}
              </div>

              <ul>
                {m.risk_factors?.map((r, j) => (
                  <li key={j}>⚠ {r}</li>
                ))}
              </ul>

            </td>

            <td>{m.total_score}</td>

          </tr>

        ))}

      </tbody>

    </table>
  );
}

export default ResultsTable;