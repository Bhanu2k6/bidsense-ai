function UploadSection({
  setTender,
  setVendors,
  analyzeBids,
  loading
}) {
  return (
    <>
      <div className="upload-grid">

        <div className="upload-card">
          <h4>Tender Document</h4>

          <input
            type="file"
            accept=".pdf"
            onChange={e => setTender(e.target.files[0])}
          />
        </div>

        <div className="upload-card">
          <h4>Vendor Bids</h4>

          <input
            type="file"
            accept=".pdf"
            multiple
            onChange={e => setVendors(Array.from(e.target.files))}
          />
        </div>

      </div>

      <button
        className="analyze-btn"
        onClick={analyzeBids}
        disabled={loading}
      >
        {loading ? (
          <span className="loading-text">
            ⏳ Analyzing Vendor Bids...
          </span>
        ) : (
          "Analyze Bids"
        )}
      </button>
    </>
  );
}

export default UploadSection;