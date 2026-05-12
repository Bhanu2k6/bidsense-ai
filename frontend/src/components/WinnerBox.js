function WinnerBox({ winner }) {
  return (
    <div className="winner-box">
      <h3>🏆 Winner: {winner.vendor_name}</h3>

      <ul>
        {winner.reasons.map((r, i) => (
          <li key={i}>{r}</li>
        ))}
      </ul>
    </div>
  );
}

export default WinnerBox;