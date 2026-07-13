import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { fetchOpportunities } from '../api'
import type { OpportunityResponse } from '../api'

function ParcelSearch() {
  const [parcelNumber, setParcelNumber] = useState('')
  const [zoning, setZoning] = useState('')
  const [neighborhood, setNeighborhood] = useState('')
  const [minSqft, setMinSqft] = useState('')
  const [yearsOwnedMin, setYearsOwnedMin] = useState('')
  const [adjacentDeveloperOwnedOnly, setAdjacentDeveloperOwnedOnly] = useState(false)
  const [taxDelinquentOnly, setTaxDelinquentOnly] = useState(false)
  const [minTaxLienAmount, setMinTaxLienAmount] = useState('')
  const [minSuggestedOffer, setMinSuggestedOffer] = useState('')
  const [maxSuggestedOffer, setMaxSuggestedOffer] = useState('')
  const [minAcres, setMinAcres] = useState('')
  const [absenteeOnly, setAbsenteeOnly] = useState(false)
  const [results, setResults] = useState<OpportunityResponse[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setLoading(true)

    const params = new URLSearchParams()
    if (parcelNumber.trim()) params.set('parcel_number', parcelNumber.trim())
    if (zoning.trim()) params.set('zoning', zoning.trim())
    if (neighborhood.trim()) params.set('neighborhood', neighborhood.trim())
    if (minSqft.trim()) params.set('min_sqft', minSqft.trim())
    if (yearsOwnedMin.trim()) params.set('years_owned_min', yearsOwnedMin.trim())
    if (adjacentDeveloperOwnedOnly) params.set('adjacent_developer_owned_only', 'true')
    if (taxDelinquentOnly) params.set('tax_delinquent_only', 'true')
    if (minTaxLienAmount.trim()) params.set('min_tax_lien_amount', minTaxLienAmount.trim())
    if (minSuggestedOffer.trim()) params.set('min_suggested_offer', minSuggestedOffer.trim())
    if (maxSuggestedOffer.trim()) params.set('max_suggested_offer', maxSuggestedOffer.trim())
    if (minAcres.trim()) params.set('min_acres', minAcres.trim())
    if (absenteeOnly) params.set('absentee_only', 'true')

    try {
      const data = await fetchOpportunities(params)
      setResults(data)
    } catch (err) {
      setError((err as Error).message)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main>
      <h1>Parcel Search</h1>
      <p>Search for parcels and open a parcel detail page to review ownership and assessment data.</p>
      <p>Opportunity results are limited to residential zoning codes: R-A, R-B, R-C, RN-A, RX-3, and RX-5.</p>
      <p>Try a parcel number such as 010001000.</p>
      <p>Suggested Offer Range sends query params: min_suggested_offer and max_suggested_offer.</p>

      <section>
        <h2>Filter Definitions</h2>
        <dl>
          <dt>VK Score</dt>
          <dd>The score runs from 0 to 100. Higher is better. A higher score means the parcel currently looks more attractive as an acquisition target.</dd>

          <dt>Absentee Only</dt>
          <dd>Only show parcels where the owner mailing address does not match the parcel address.</dd>

          <dt>Adjacent Developer-Owned Only</dt>
          <dd>Only show parcels flagged as touching at least one parcel already owned by a developer.</dd>

          <dt>Minimum Years Owned</dt>
          <dd>Only show parcels where the owner has held the property at least that many years.</dd>

          <dt>Estimated Units</dt>
          <dd>This is a heuristic estimate of how many residential units a parcel might support based on lot size and zoning assumptions. It is not a legal zoning determination.</dd>

          <dt>SIA</dt>
          <dd>SIA is not active in the current product. It is intended to be a proprietary overlay, but we do not yet have a real source loaded for it.</dd>
        </dl>
      </section>

      <form onSubmit={handleSearch}>
        <label>
          Parcel Number
          <input value={parcelNumber} onChange={(event) => setParcelNumber(event.target.value)} />
        </label>

        <label>
          Zoning
          <input value={zoning} onChange={(event) => setZoning(event.target.value)} />
        </label>

        <label>
          Neighborhood
          <input value={neighborhood} onChange={(event) => setNeighborhood(event.target.value)} />
        </label>

        <label>
          Minimum Lot Size (sq ft)
          <input type="number" value={minSqft} onChange={(event) => setMinSqft(event.target.value)} />
        </label>

        <label>
          Minimum Years Owned
          <input type="number" value={yearsOwnedMin} onChange={(event) => setYearsOwnedMin(event.target.value)} />
        </label>

        <label>
          Minimum Tax Lien Amount ($)
          <input type="number" value={minTaxLienAmount} onChange={(event) => setMinTaxLienAmount(event.target.value)} />
        </label>

        <label>
          Suggested Offer Range Min ($)
          <input type="number" value={minSuggestedOffer} onChange={(event) => setMinSuggestedOffer(event.target.value)} />
        </label>

        <label>
          Suggested Offer Range Max ($)
          <input type="number" value={maxSuggestedOffer} onChange={(event) => setMaxSuggestedOffer(event.target.value)} />
        </label>

        <label>
          Minimum Acres
          <input type="number" value={minAcres} onChange={(event) => setMinAcres(event.target.value)} />
        </label>

        <label>
          <span>
            <input
              type="checkbox"
              checked={adjacentDeveloperOwnedOnly}
              onChange={(event) => setAdjacentDeveloperOwnedOnly(event.target.checked)}
            />
            Adjacent Developer-Owned Only
          </span>
        </label>

        <label>
          <span>
            <input
              type="checkbox"
              checked={taxDelinquentOnly}
              onChange={(event) => setTaxDelinquentOnly(event.target.checked)}
            />
            Tax Delinquent Only
          </span>
        </label>

        <label>
          <span>
            <input
              type="checkbox"
              checked={absenteeOnly}
              onChange={(event) => setAbsenteeOnly(event.target.checked)}
            />
            Absentee Only
          </span>
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>

      {error ? <p role="alert">{error}</p> : null}

      {results.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Parcel</th>
              <th>Neighborhood</th>
              <th>Zoning</th>
              <th>Property Type</th>
              <th>Acres</th>
              <th>Years Owned</th>
              <th>Adj. Dev</th>
              <th>Tax Delinq.</th>
              <th>Lien Amount</th>
              <th>Absentee</th>
              <th>VK Score</th>
            </tr>
          </thead>
          <tbody>
            {results.map((item) => (
              <tr key={item.parcel_number}>
                <td>
                  <Link className="link-button" to={`/parcels/${item.parcel_number}`}>
                    {item.parcel_number}
                  </Link>
                </td>
                <td>{item.neighborhood || '-'}</td>
                <td>{item.zoning || '-'}</td>
                <td>{item.property_type || '-'}</td>
                <td>{item.acres ?? '-'}</td>
                <td>{item.years_owned ?? '-'}</td>
                <td>{item.adjacent_developer_owned ? 'Yes' : 'No'}</td>
                <td>{item.tax_delinquent ? 'Yes' : 'No'}</td>
                <td>{item.tax_lien_amount ? `$${item.tax_lien_amount.toLocaleString()}` : '-'}</td>
                <td>{item.absentee_owner ? 'Yes' : 'No'}</td>
                <td>{item.vk_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No results yet.</p>
      )}
    </main>
  )
}

export default ParcelSearch
